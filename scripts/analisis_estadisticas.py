#!/usr/bin/env python3
"""
Análisis estadístico del corpus de Tribunales Ambientales
"""

import os
import sys
import re
import json
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = Path(r"G:\Mi unidad\tribunal_pdf\corpus\descarga_completa\documentos")
OUTPUT_DIR = Path(r"G:\Mi unidad\tribunal_pdf\datos\estadisticas")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def extract_rol(filename):
    """Extrae número de ROL del nombre de archivo"""
    # Patrones comunes: R-123-2020, R123-2020, Rol-123-2020
    patterns = [
        r'R-?(\d+)-(\d{4})',
        r'ROL[_-]?N?[°º]?[_-]?(\d+)[_-](\d{4})',
        r'(\d+)-(\d{4})',
    ]
    for pattern in patterns:
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            num, year = match.groups()
            if 2010 <= int(year) <= 2030:
                return f"R-{num}-{year}", int(year)
    return None, None

def extract_doc_type(filename):
    """Extrae tipo de documento del nombre"""
    filename_lower = filename.lower()

    if 'sentencia' in filename_lower:
        if 'casacion' in filename_lower or 'casación' in filename_lower:
            return 'Sentencia Casación'
        elif 'reemplazo' in filename_lower:
            return 'Sentencia Reemplazo'
        else:
            return 'Sentencia'
    elif 'resolucion' in filename_lower or 'resolución' in filename_lower:
        return 'Resolución'
    elif 'informe' in filename_lower:
        if 'derecho' in filename_lower:
            return 'Informe en Derecho'
        elif 'pericial' in filename_lower or 'tecnico' in filename_lower:
            return 'Informe Técnico'
        else:
            return 'Informe'
    elif 'anuario' in filename_lower:
        return 'Anuario'
    elif 'boletin' in filename_lower or 'boletín' in filename_lower:
        return 'Boletín'
    elif 'acta' in filename_lower:
        return 'Acta'
    elif 'sintesis' in filename_lower or 'síntesis' in filename_lower:
        return 'Síntesis'
    else:
        return 'Otro'

def get_tribunal_from_path(filepath):
    """Determina el tribunal según la ruta del archivo"""
    path_str = str(filepath).lower()
    if '/1ta/' in path_str or '\\1ta\\' in path_str:
        return '1TA'
    elif '/3ta/' in path_str or '\\3ta\\' in path_str:
        return '3TA'
    else:
        return '2TA'

def analyze_corpus():
    """Analiza todo el corpus"""
    print("="*60)
    print("ANÁLISIS ESTADÍSTICO DEL CORPUS")
    print("="*60)

    stats = {
        'total_files': 0,
        'by_tribunal': defaultdict(int),
        'by_year': defaultdict(int),
        'by_type': defaultdict(int),
        'by_tribunal_year': defaultdict(lambda: defaultdict(int)),
        'by_tribunal_type': defaultdict(lambda: defaultdict(int)),
        'roles_unicos': set(),
        'files_with_rol': 0,
        'files_without_rol': 0,
        'extensions': defaultdict(int),
    }

    all_files = []

    # Escanear todos los archivos
    print("\nEscaneando archivos...")
    for filepath in BASE_DIR.rglob("*"):
        if filepath.is_file():
            stats['total_files'] += 1

            filename = filepath.name
            ext = filepath.suffix.lower()
            tribunal = get_tribunal_from_path(filepath)
            rol, year = extract_rol(filename)
            doc_type = extract_doc_type(filename)

            # Contadores
            stats['by_tribunal'][tribunal] += 1
            stats['by_type'][doc_type] += 1
            stats['extensions'][ext] += 1
            stats['by_tribunal_type'][tribunal][doc_type] += 1

            if rol:
                stats['roles_unicos'].add(rol)
                stats['files_with_rol'] += 1
                if year:
                    stats['by_year'][year] += 1
                    stats['by_tribunal_year'][tribunal][year] += 1
            else:
                stats['files_without_rol'] += 1

            all_files.append({
                'filename': filename,
                'path': str(filepath),
                'tribunal': tribunal,
                'rol': rol,
                'year': year,
                'type': doc_type,
                'extension': ext,
                'size_kb': filepath.stat().st_size / 1024
            })

    # Imprimir estadísticas
    print(f"\nTOTAL ARCHIVOS: {stats['total_files']}")

    print("\n" + "-"*40)
    print("POR TRIBUNAL:")
    for t in ['1TA', '2TA', '3TA']:
        print(f"  {t}: {stats['by_tribunal'][t]}")

    print("\n" + "-"*40)
    print("POR TIPO DE DOCUMENTO:")
    for doc_type, count in sorted(stats['by_type'].items(), key=lambda x: -x[1]):
        print(f"  {doc_type}: {count}")

    print("\n" + "-"*40)
    print("POR AÑO:")
    for year in sorted(stats['by_year'].keys()):
        print(f"  {year}: {stats['by_year'][year]}")

    print("\n" + "-"*40)
    print("ROLES ÚNICOS IDENTIFICADOS:", len(stats['roles_unicos']))
    print("Archivos con ROL:", stats['files_with_rol'])
    print("Archivos sin ROL:", stats['files_without_rol'])

    print("\n" + "-"*40)
    print("POR EXTENSIÓN:")
    for ext, count in sorted(stats['extensions'].items(), key=lambda x: -x[1]):
        print(f"  {ext}: {count}")

    # Estadísticas por tribunal y año
    print("\n" + "-"*40)
    print("DOCUMENTOS POR TRIBUNAL Y AÑO:")
    years = sorted(set(y for t in stats['by_tribunal_year'].values() for y in t.keys()))

    # Header
    print(f"{'Año':<8}", end="")
    for t in ['1TA', '2TA', '3TA']:
        print(f"{t:>8}", end="")
    print(f"{'Total':>8}")

    for year in years:
        print(f"{year:<8}", end="")
        total = 0
        for t in ['1TA', '2TA', '3TA']:
            count = stats['by_tribunal_year'][t][year]
            print(f"{count:>8}", end="")
            total += count
        print(f"{total:>8}")

    # Guardar resultados
    output = {
        'fecha_analisis': datetime.now().isoformat(),
        'total_archivos': stats['total_files'],
        'roles_unicos': len(stats['roles_unicos']),
        'por_tribunal': dict(stats['by_tribunal']),
        'por_año': dict(stats['by_year']),
        'por_tipo': dict(stats['by_type']),
        'por_tribunal_año': {t: dict(v) for t, v in stats['by_tribunal_year'].items()},
        'por_tribunal_tipo': {t: dict(v) for t, v in stats['by_tribunal_type'].items()},
        'extensiones': dict(stats['extensions']),
    }

    with open(OUTPUT_DIR / 'estadisticas_corpus.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # Guardar lista de archivos
    with open(OUTPUT_DIR / 'listado_archivos.json', 'w', encoding='utf-8') as f:
        json.dump(all_files, f, ensure_ascii=False, indent=2)

    # Crear CSV
    with open(OUTPUT_DIR / 'listado_archivos.csv', 'w', encoding='utf-8') as f:
        f.write('filename,tribunal,rol,year,type,extension,size_kb\n')
        for file in all_files:
            row = [
                file['filename'].replace('"', "'"),
                file['tribunal'],
                file['rol'] or '',
                str(file['year']) if file['year'] else '',
                file['type'],
                file['extension'],
                f"{file['size_kb']:.1f}"
            ]
            f.write('"' + '","'.join(row) + '"\n')

    print(f"\n{'='*60}")
    print("ARCHIVOS GUARDADOS:")
    print(f"  {OUTPUT_DIR / 'estadisticas_corpus.json'}")
    print(f"  {OUTPUT_DIR / 'listado_archivos.json'}")
    print(f"  {OUTPUT_DIR / 'listado_archivos.csv'}")
    print(f"{'='*60}")

    return stats, all_files

if __name__ == "__main__":
    analyze_corpus()
