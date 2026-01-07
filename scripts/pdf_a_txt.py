#!/usr/bin/env python3
"""Extrae el texto de todos los PDFs y los guarda como archivos TXT."""

import fitz
from pathlib import Path
import sys

# Configurar encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Rutas del proyecto
BASE_DIR = Path("g:/Mi unidad/tribunal_pdf")
PDF_DIR = BASE_DIR / "tribunal_pdfs_organizado" / "originales"
TXT_DIR = BASE_DIR / "textos"

def extraer_texto_completo(pdf_path):
    """Extrae todo el texto de un PDF."""
    try:
        doc = fitz.open(str(pdf_path))
        texto_completo = []

        for num_pagina, pagina in enumerate(doc, 1):
            texto = pagina.get_text()
            if texto.strip():
                texto_completo.append(f"--- PÁGINA {num_pagina} ---\n")
                texto_completo.append(texto)
                texto_completo.append("\n")

        doc.close()
        return "\n".join(texto_completo)
    except Exception as e:
        return f"[Error al extraer texto: {e}]"

def procesar_todos():
    """Procesa todos los PDFs y los convierte a TXT."""

    # Crear directorio de salida
    TXT_DIR.mkdir(parents=True, exist_ok=True)

    # Buscar todos los PDFs
    pdfs = list(PDF_DIR.glob('**/*.pdf'))
    pdfs.sort(key=lambda x: x.name)

    print(f"Encontrados {len(pdfs)} archivos PDF")
    print(f"Destino: {TXT_DIR}")
    print("=" * 60)

    exitosos = 0
    vacios = 0
    errores = 0

    for i, pdf_path in enumerate(pdfs, 1):
        nombre_txt = pdf_path.stem + ".txt"
        txt_path = TXT_DIR / nombre_txt

        print(f"[{i}/{len(pdfs)}] {pdf_path.name[:50]}...", end=" ")

        try:
            texto = extraer_texto_completo(pdf_path)

            if texto.strip() and not texto.startswith("[Error"):
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(f"ARCHIVO ORIGINAL: {pdf_path.name}\n")
                    f.write(f"RUTA: {pdf_path.relative_to(PDF_DIR)}\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(texto)

                exitosos += 1
                print("OK")
            else:
                vacios += 1
                print("VACIO (PDF escaneado?)")
                # Guardar archivo indicando que está vacío
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(f"ARCHIVO ORIGINAL: {pdf_path.name}\n")
                    f.write(f"RUTA: {pdf_path.relative_to(PDF_DIR)}\n")
                    f.write("=" * 60 + "\n\n")
                    f.write("[PDF SIN TEXTO EXTRAIBLE - Posiblemente escaneado]\n")

        except Exception as e:
            errores += 1
            print(f"ERROR: {e}")

    print("\n" + "=" * 60)
    print(f"RESUMEN:")
    print(f"  - Exitosos: {exitosos}")
    print(f"  - Vacíos (escaneados): {vacios}")
    print(f"  - Errores: {errores}")
    print(f"  - Total: {len(pdfs)}")
    print(f"\nArchivos TXT guardados en: {TXT_DIR}")

if __name__ == '__main__':
    procesar_todos()
