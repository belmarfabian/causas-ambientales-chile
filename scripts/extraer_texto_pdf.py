"""
Script para extraer texto de PDFs del Tribunal Ambiental.
Detecta si un PDF tiene texto nativo y lo extrae directamente.
"""

import pdfplumber
import os
import re
from pathlib import Path

def limpiar_texto(texto):
    """Limpia el texto extraído de elementos no deseados."""
    # Remover footers de firma electrónica
    texto = re.sub(r'[A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12}', '', texto)
    texto = re.sub(r'Este documento incorpora una firma electrónica avanzada\..*?verificación\.', '', texto, flags=re.DOTALL)
    texto = re.sub(r'Su validez puede ser consultada en www\.tribunalambiental\.cl.*?verificación\.', '', texto, flags=re.DOTALL)

    # Remover numeración de páginas al estilo "quinientos sesenta y cuatro 564"
    texto = re.sub(r'^(cero|uno|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|once|doce|trece|catorce|quince|dieciséis|diecisiete|dieciocho|diecinueve|veinte|veintiuno|veintidós|veintitrés|veinticuatro|veinticinco|veintiséis|veintisiete|veintiocho|veintinueve|treinta|cuarenta|cincuenta|sesenta|setenta|ochenta|noventa|cien|ciento|doscientos|trescientos|cuatrocientos|quinientos|seiscientos|setecientos|ochocientos|novecientos|mil|y|\s)+\d+\s*$', '', texto, flags=re.MULTILINE | re.IGNORECASE)

    # Limpiar líneas vacías múltiples
    texto = re.sub(r'\n{3,}', '\n\n', texto)

    return texto.strip()

def tiene_texto_extraible(pdf_path, umbral_chars=100):
    """Verifica si un PDF tiene texto extraíble (no es escaneado)."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Revisar las primeras 3 páginas
            for i, page in enumerate(pdf.pages[:3]):
                texto = page.extract_text()
                if texto and len(texto.strip()) > umbral_chars:
                    return True, len(pdf.pages)
            return False, len(pdf.pages)
    except Exception as e:
        return False, 0

def extraer_pdf(pdf_path, output_path, ruta_relativa=None):
    """Extrae texto de un PDF y lo guarda en formato estándar."""
    nombre_archivo = os.path.basename(pdf_path)

    try:
        with pdfplumber.open(pdf_path) as pdf:
            num_paginas = len(pdf.pages)

            with open(output_path, 'w', encoding='utf-8') as out:
                # Header
                out.write(f'ARCHIVO ORIGINAL: {nombre_archivo}\n')
                if ruta_relativa:
                    out.write(f'RUTA: {ruta_relativa}\n')
                out.write('TRANSCRITO CON: Extracción directa (pdfplumber)\n')
                out.write('=' * 80 + '\n\n')

                for i, page in enumerate(pdf.pages):
                    texto = page.extract_text()
                    if texto:
                        texto_limpio = limpiar_texto(texto)
                        if i > 0:
                            out.write(f'\n\n--- PÁGINA {i+1} ---\n\n')
                        out.write(texto_limpio)

        return True, num_paginas
    except Exception as e:
        return False, str(e)

def procesar_directorio(input_dir, output_dir, extensiones=['.pdf']):
    """Procesa todos los PDFs en un directorio."""
    resultados = {
        'exitosos': [],
        'escaneados': [],
        'errores': []
    }

    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if any(file.lower().endswith(ext) for ext in extensiones):
                pdf_path = os.path.join(root, file)
                ruta_relativa = os.path.relpath(pdf_path, input_dir)

                # Verificar si tiene texto extraíble
                tiene_texto, num_paginas = tiene_texto_extraible(pdf_path)

                if tiene_texto:
                    # Generar nombre de salida
                    nombre_base = os.path.splitext(file)[0]
                    output_path = os.path.join(output_dir, f'{nombre_base}.txt')

                    exito, info = extraer_pdf(pdf_path, output_path, ruta_relativa)

                    if exito:
                        resultados['exitosos'].append({
                            'archivo': file,
                            'paginas': info,
                            'salida': output_path
                        })
                        print(f'✓ {file} ({info} págs)')
                    else:
                        resultados['errores'].append({
                            'archivo': file,
                            'error': info
                        })
                        print(f'✗ {file}: {info}')
                else:
                    resultados['escaneados'].append({
                        'archivo': file,
                        'paginas': num_paginas
                    })
                    print(f'⚠ {file} - PDF escaneado ({num_paginas} págs)')

    return resultados

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print('Uso: python extraer_texto_pdf.py <archivo.pdf> [salida.txt]')
        print('     python extraer_texto_pdf.py --dir <directorio_entrada> <directorio_salida>')
        sys.exit(1)

    if sys.argv[1] == '--dir':
        if len(sys.argv) < 4:
            print('Uso: python extraer_texto_pdf.py --dir <directorio_entrada> <directorio_salida>')
            sys.exit(1)
        resultados = procesar_directorio(sys.argv[2], sys.argv[3])
        print(f'\nResumen:')
        print(f'  Exitosos: {len(resultados["exitosos"])}')
        print(f'  Escaneados: {len(resultados["escaneados"])}')
        print(f'  Errores: {len(resultados["errores"])}')
    else:
        pdf_path = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else pdf_path.replace('.pdf', '.txt')

        tiene_texto, num_paginas = tiene_texto_extraible(pdf_path)
        if tiene_texto:
            exito, info = extraer_pdf(pdf_path, output_path)
            if exito:
                print(f'Extraído: {output_path} ({info} páginas)')
            else:
                print(f'Error: {info}')
        else:
            print(f'El PDF parece ser escaneado (sin texto extraíble)')
