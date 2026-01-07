#!/usr/bin/env python3
"""
Script para reorganizar fisicamente los PDFs en carpetas estructuradas.
Proyecto: Analisis socioecologico de conflictos ambientales en el norte de Chile
"""

import os
import shutil
import csv
from pathlib import Path

# Directorios
BASE_DIR = Path("g:/My Drive/tribunal_pdf")
PDF_DIR = BASE_DIR / "tribunal_pdfs"
OUTPUT_DIR = BASE_DIR / "tribunal_pdfs_organizado"

# Mapeo de tipos de caso a carpetas
TIPO_CARPETA = {
    'R': 'reclamaciones',
    'D': 'demandas',
    'S': 'solicitudes',
    'C': 'consultas'
}

def crear_estructura():
    """Crea la estructura de carpetas."""

    carpetas = [
        OUTPUT_DIR / "originales" / "reclamaciones",
        OUTPUT_DIR / "originales" / "demandas",
        OUTPUT_DIR / "originales" / "solicitudes",
        OUTPUT_DIR / "originales" / "consultas",
        OUTPUT_DIR / "originales" / "corte_suprema",
        OUTPUT_DIR / "duplicados",
        OUTPUT_DIR / "sin_clasificar",
    ]

    # Crear subcarpetas por ano (2013-2025)
    for tipo in ['reclamaciones', 'demandas', 'solicitudes', 'consultas']:
        for ano in range(2013, 2026):
            carpetas.append(OUTPUT_DIR / "originales" / tipo / str(ano))

    for ano in range(2013, 2026):
        carpetas.append(OUTPUT_DIR / "originales" / "corte_suprema" / str(ano))

    for carpeta in carpetas:
        carpeta.mkdir(parents=True, exist_ok=True)

    print(f"Estructura creada en: {OUTPUT_DIR}")


def cargar_inventario():
    """Carga el inventario desde CSV."""

    inventario = []
    csv_path = BASE_DIR / "inventario_completo.csv"

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            inventario.append(row)

    return inventario


def determinar_destino(item):
    """Determina la carpeta destino para un archivo."""

    es_duplicado = item['es_duplicado'] == 'True'
    tipo_caso = item['tipo_caso']
    ano_rol = item['año_rol']
    es_corte_suprema = item['es_corte_suprema'] == 'True'
    requiere_revision = 'Requiere' in item.get('notas', '')

    # Duplicados van a carpeta separada
    if es_duplicado:
        return OUTPUT_DIR / "duplicados"

    # Sin clasificar
    if requiere_revision or not tipo_caso:
        if es_corte_suprema and ano_rol:
            return OUTPUT_DIR / "originales" / "corte_suprema" / str(ano_rol)
        return OUTPUT_DIR / "sin_clasificar"

    # Corte Suprema
    if es_corte_suprema:
        if ano_rol:
            return OUTPUT_DIR / "originales" / "corte_suprema" / str(ano_rol)
        return OUTPUT_DIR / "originales" / "corte_suprema"

    # Por tipo y ano
    carpeta_tipo = TIPO_CARPETA.get(tipo_caso)
    if carpeta_tipo and ano_rol:
        return OUTPUT_DIR / "originales" / carpeta_tipo / str(ano_rol)
    elif carpeta_tipo:
        return OUTPUT_DIR / "originales" / carpeta_tipo

    return OUTPUT_DIR / "sin_clasificar"


def reorganizar(modo='copiar'):
    """
    Reorganiza los archivos.

    modo: 'copiar' (default) o 'mover'
    """

    print(f"\nModo: {modo.upper()}")
    print("="*60)

    inventario = cargar_inventario()

    stats = {
        'exitosos': 0,
        'errores': 0,
        'omitidos': 0
    }

    for item in inventario:
        archivo_origen = PDF_DIR / item['archivo_original']

        if not archivo_origen.exists():
            print(f"[!] No existe: {item['archivo_original']}")
            stats['errores'] += 1
            continue

        destino_dir = determinar_destino(item)
        archivo_destino = destino_dir / item['archivo_original']

        # Evitar sobrescribir
        if archivo_destino.exists():
            stats['omitidos'] += 1
            continue

        try:
            if modo == 'copiar':
                shutil.copy2(archivo_origen, archivo_destino)
            else:
                shutil.move(archivo_origen, archivo_destino)
            stats['exitosos'] += 1
        except Exception as e:
            print(f"[ERROR] {item['archivo_original']}: {e}")
            stats['errores'] += 1

    print(f"\n[RESULTADO]")
    print(f"   Exitosos: {stats['exitosos']}")
    print(f"   Errores:  {stats['errores']}")
    print(f"   Omitidos: {stats['omitidos']}")

    return stats


def mostrar_resumen():
    """Muestra resumen de la estructura creada."""

    print("\n[ESTRUCTURA CREADA]")
    print("="*60)

    for tipo_dir in ['reclamaciones', 'demandas', 'solicitudes', 'consultas', 'corte_suprema']:
        tipo_path = OUTPUT_DIR / "originales" / tipo_dir
        if tipo_path.exists():
            total = sum(1 for _ in tipo_path.rglob("*.pdf"))
            print(f"   {tipo_dir}: {total} archivos")

    dup_path = OUTPUT_DIR / "duplicados"
    if dup_path.exists():
        total_dup = sum(1 for _ in dup_path.glob("*.pdf"))
        print(f"   duplicados: {total_dup} archivos")

    sin_path = OUTPUT_DIR / "sin_clasificar"
    if sin_path.exists():
        total_sin = sum(1 for _ in sin_path.glob("*.pdf"))
        print(f"   sin_clasificar: {total_sin} archivos")


def preview():
    """Muestra preview de lo que se haria sin mover archivos."""

    print("\n[PREVIEW - No se moveran archivos]")
    print("="*60)

    inventario = cargar_inventario()

    destinos = {}
    for item in inventario:
        destino = determinar_destino(item)
        destino_str = str(destino.relative_to(OUTPUT_DIR))

        if destino_str not in destinos:
            destinos[destino_str] = []
        destinos[destino_str].append(item['archivo_original'])

    for destino, archivos in sorted(destinos.items()):
        print(f"\n{destino}/ ({len(archivos)} archivos)")
        for archivo in archivos[:3]:
            print(f"   - {archivo}")
        if len(archivos) > 3:
            print(f"   ... y {len(archivos) - 3} mas")


if __name__ == "__main__":
    import sys

    print("REORGANIZADOR DE PDFs - TRIBUNALES AMBIENTALES")
    print("="*60)

    if len(sys.argv) < 2:
        print("\nUso:")
        print("  python reorganizar_archivos.py preview   - Ver preview")
        print("  python reorganizar_archivos.py copiar    - Copiar archivos")
        print("  python reorganizar_archivos.py mover     - Mover archivos")
        sys.exit(0)

    accion = sys.argv[1].lower()

    if accion == 'preview':
        crear_estructura()
        preview()
    elif accion == 'copiar':
        crear_estructura()
        reorganizar(modo='copiar')
        mostrar_resumen()
    elif accion == 'mover':
        crear_estructura()
        reorganizar(modo='mover')
        mostrar_resumen()
    else:
        print(f"Accion no reconocida: {accion}")
        sys.exit(1)

    print("\n[OK] Proceso completado.")
