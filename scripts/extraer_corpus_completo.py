"""
Script para extraer texto de todo el corpus de Tribunales Ambientales.
Estrategia híbrida:
- PDFs con texto embebido: pdfplumber (rápido)
- PDFs escaneados: se marcan para procesamiento con Claude MLLM
- Documentos Word: python-docx
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Configuración
# Detectar ruta base automáticamente
SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent

CORPUS_DIR = BASE_DIR / "corpus" / "descarga_completa"
TEXTOS_DIR = BASE_DIR / "corpus" / "textos"
LOG_DIR = BASE_DIR / "datos"

def extraer_pdf_pdfplumber(pdf_path, output_path):
    """Extrae texto de PDF usando pdfplumber."""
    try:
        import pdfplumber

        with pdfplumber.open(pdf_path) as pdf:
            num_paginas = len(pdf.pages)
            texto_total = []
            chars_extraidos = 0

            for i, page in enumerate(pdf.pages):
                texto = page.extract_text()
                if texto:
                    texto_total.append(f"--- PÁGINA {i+1} ---\n{texto}")
                    chars_extraidos += len(texto)

            # Si hay muy poco texto, probablemente es escaneado
            if chars_extraidos < 100 * num_paginas:
                return False, num_paginas, "escaneado"

            # Guardar transcripción
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"ARCHIVO: {pdf_path.name}\n")
                f.write(f"MÉTODO: pdfplumber (texto embebido)\n")
                f.write(f"PÁGINAS: {num_paginas}\n")
                f.write("=" * 80 + "\n\n")
                f.write("\n\n".join(texto_total))

            return True, num_paginas, chars_extraidos

    except Exception as e:
        return False, 0, str(e)

def extraer_word(doc_path, output_path):
    """Extrae texto de documentos Word."""
    try:
        if doc_path.suffix.lower() == '.docx':
            from docx import Document
            doc = Document(doc_path)
            texto = "\n".join([p.text for p in doc.paragraphs])
        else:
            # .doc antiguo - intentar con antiword o textract
            import subprocess
            result = subprocess.run(['antiword', str(doc_path)],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                texto = result.stdout
            else:
                return False, 0, "formato .doc no soportado"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"ARCHIVO: {doc_path.name}\n")
            f.write(f"MÉTODO: python-docx\n")
            f.write("=" * 80 + "\n\n")
            f.write(texto)

        return True, 1, len(texto)

    except Exception as e:
        return False, 0, str(e)

def procesar_corpus(limite=None, solo_tipo=None):
    """Procesa todo el corpus."""

    # Crear directorio de salida
    TEXTOS_DIR.mkdir(parents=True, exist_ok=True)

    # Obtener lista de archivos ya procesados
    ya_procesados = {f.stem for f in TEXTOS_DIR.glob("*.txt")}
    print(f"Transcripciones existentes: {len(ya_procesados)}")

    # Estadísticas
    stats = {
        'procesados': 0,
        'exitosos': 0,
        'escaneados': [],
        'errores': [],
        'omitidos': 0,
        'por_tipo': {}
    }

    # Buscar archivos
    extensiones = ['.pdf', '.doc', '.docx']
    if solo_tipo:
        extensiones = [solo_tipo]

    archivos = []
    for ext in extensiones:
        archivos.extend(CORPUS_DIR.rglob(f"*{ext}"))

    total = len(archivos)
    print(f"Archivos encontrados: {total}")

    if limite:
        archivos = archivos[:limite]
        print(f"Procesando primeros {limite}")

    for i, archivo in enumerate(archivos):
        nombre_base = archivo.stem

        # Saltar si ya existe
        if nombre_base in ya_procesados:
            stats['omitidos'] += 1
            continue

        # Determinar tipo
        ext = archivo.suffix.lower()
        if ext not in stats['por_tipo']:
            stats['por_tipo'][ext] = {'exitosos': 0, 'fallidos': 0}

        output_path = TEXTOS_DIR / f"{nombre_base}.txt"

        # Procesar según tipo
        if ext == '.pdf':
            exito, paginas, info = extraer_pdf_pdfplumber(archivo, output_path)
        elif ext in ['.doc', '.docx']:
            exito, paginas, info = extraer_word(archivo, output_path)
        else:
            continue

        stats['procesados'] += 1

        if exito:
            stats['exitosos'] += 1
            stats['por_tipo'][ext]['exitosos'] += 1
            print(f"[{i+1}/{total}] OK {archivo.name} ({paginas} pags)")
        elif info == "escaneado":
            stats['escaneados'].append({
                'archivo': str(archivo),
                'paginas': paginas
            })
            stats['por_tipo'][ext]['fallidos'] += 1
            print(f"[{i+1}/{total}] SCAN {archivo.name} (escaneado, {paginas} pags)")
        else:
            stats['errores'].append({
                'archivo': str(archivo),
                'error': str(info)
            })
            stats['por_tipo'][ext]['fallidos'] += 1
            print(f"[{i+1}/{total}] ERR {archivo.name}: {info}")

        # Guardar progreso cada 100 archivos
        if stats['procesados'] % 100 == 0:
            guardar_log(stats)

    # Guardar log final
    guardar_log(stats)

    return stats

def guardar_log(stats):
    """Guarda el log de procesamiento."""
    log_path = LOG_DIR / "log_extraccion.json"

    log_data = {
        'fecha': datetime.now().isoformat(),
        'procesados': stats['procesados'],
        'exitosos': stats['exitosos'],
        'omitidos': stats['omitidos'],
        'escaneados_count': len(stats['escaneados']),
        'errores_count': len(stats['errores']),
        'por_tipo': stats['por_tipo']
    }

    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)

    # Guardar lista de escaneados para Claude
    if stats['escaneados']:
        escaneados_path = LOG_DIR / "pdfs_escaneados.json"
        with open(escaneados_path, 'w', encoding='utf-8') as f:
            json.dump(stats['escaneados'], f, indent=2, ensure_ascii=False)

def mostrar_resumen(stats):
    """Muestra resumen del procesamiento."""
    print("\n" + "=" * 60)
    print("RESUMEN DE EXTRACCIÓN")
    print("=" * 60)
    print(f"Procesados:  {stats['procesados']}")
    print(f"Exitosos:    {stats['exitosos']}")
    print(f"Escaneados:  {len(stats['escaneados'])} (requieren Claude MLLM)")
    print(f"Errores:     {len(stats['errores'])}")
    print(f"Omitidos:    {stats['omitidos']} (ya existían)")
    print()
    print("Por tipo de archivo:")
    for ext, data in stats['por_tipo'].items():
        print(f"  {ext}: {data['exitosos']} exitosos, {data['fallidos']} fallidos")
    print("=" * 60)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Extraer texto del corpus')
    parser.add_argument('--limite', type=int, help='Procesar solo N archivos')
    parser.add_argument('--tipo', type=str, help='Solo procesar un tipo (.pdf, .doc, .docx)')
    parser.add_argument('--test', action='store_true', help='Modo prueba (10 archivos)')

    args = parser.parse_args()

    limite = 10 if args.test else args.limite

    print("Iniciando extracción de texto del corpus...")
    print(f"Origen: {CORPUS_DIR}")
    print(f"Destino: {TEXTOS_DIR}")
    print()

    stats = procesar_corpus(limite=limite, solo_tipo=args.tipo)
    mostrar_resumen(stats)
