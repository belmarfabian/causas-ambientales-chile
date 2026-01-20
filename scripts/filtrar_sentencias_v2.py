#!/usr/bin/env python3
"""
Filtra sentencias oficiales - versión mejorada
Excluye boletines y mejora extracción de ROL
"""

import os
import sys
import re
import json
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = Path(r"G:\Mi unidad\tribunal_pdf\corpus\descarga_completa\documentos")
OUTPUT_DIR = Path(r"G:\Mi unidad\tribunal_pdf\datos\sentencias")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def es_sentencia_oficial(filename):
    """Determina si es una sentencia oficial (no boletín ni síntesis)"""
    fname_lower = filename.lower()

    # Excluir boletines y compilaciones
    if 'boletin' in fname_lower or 'boletín' in fname_lower:
        return False, None

    # Excluir síntesis
    if 'sintesis' in fname_lower or 'síntesis' in fname_lower:
        return False, None

    # Debe contener "sentencia"
    if 'sentencia' not in fname_lower:
        return False, None

    # Clasificar tipo
    if 'casacion' in fname_lower or 'casación' in fname_lower:
        return True, 'casacion'
    elif 'reemplazo' in fname_lower:
        return True, 'reemplazo'
    else:
        return True, 'definitiva'

def extract_rol(filename):
    """Extrae ROL con múltiples patrones"""
    # Patrones en orden de especificidad
    patterns = [
        # R-123-2020 o R_123_2020
        r'R[-_](\d+)[-_](\d{4})',
        # ROL-N-123-2020
        r'ROL[-_]?N?[°º]?[-_]?(\d+)[-_](\d{4})',
        # Sentencia_R_123_2020
        r'sentencia[-_]R[-_](\d+)[-_](\d{4})',
        # R123-2020 sin separador
        r'R(\d+)[-_](\d{4})',
        # Solo números al inicio como 1232020
        r'^R?(\d{1,3})(\d{4})',
    ]

    for pattern in patterns:
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            num, year = match.groups()
            year_int = int(year)
            if 2012 <= year_int <= 2030:
                return f"R-{int(num)}-{year_int}", int(num), year_int

    return None, None, None

def get_tribunal(filepath):
    """Determina tribunal de la ruta"""
    path_str = str(filepath).lower()
    if '/1ta/' in path_str or '\\1ta\\' in path_str:
        return '1TA'
    elif '/3ta/' in path_str or '\\3ta\\' in path_str:
        return '3TA'
    else:
        return '2TA'

def main():
    print("="*60)
    print("FILTRADO DE SENTENCIAS OFICIALES v2")
    print("="*60)

    sentencias = []
    causas_unicas = {}  # rol -> mejor archivo
    excluidos = {'boletin': 0, 'sintesis': 0, 'sin_sentencia': 0}

    # Escanear archivos
    print("\nEscaneando corpus...")
    for filepath in BASE_DIR.rglob("*"):
        if not filepath.is_file():
            continue

        filename = filepath.name
        fname_lower = filename.lower()

        # Contar exclusiones
        if 'boletin' in fname_lower or 'boletín' in fname_lower:
            excluidos['boletin'] += 1
            continue
        if 'sintesis' in fname_lower or 'síntesis' in fname_lower:
            excluidos['sintesis'] += 1
            continue
        if 'sentencia' not in fname_lower:
            excluidos['sin_sentencia'] += 1
            continue

        es_sent, tipo = es_sentencia_oficial(filename)
        if not es_sent:
            continue

        rol, num, year = extract_rol(filename)
        tribunal = get_tribunal(filepath)
        size_kb = filepath.stat().st_size / 1024

        sentencia = {
            'filename': filename,
            'path': str(filepath),
            'tribunal': tribunal,
            'tipo': tipo,
            'rol': rol,
            'rol_num': num,
            'año': year,
            'size_kb': size_kb
        }

        sentencias.append(sentencia)

        # Guardar la mejor versión por causa (la más grande)
        if rol:
            if rol not in causas_unicas or size_kb > causas_unicas[rol]['size_kb']:
                causas_unicas[rol] = sentencia

    # Estadísticas
    print(f"\nEXCLUIDOS:")
    print(f"  Boletines: {excluidos['boletin']}")
    print(f"  Síntesis: {excluidos['sintesis']}")

    print(f"\nSENTENCIAS IDENTIFICADAS: {len(sentencias)}")
    print(f"CAUSAS ÚNICAS (con ROL): {len(causas_unicas)}")

    # Estadísticas por tipo
    por_tipo = defaultdict(int)
    por_tribunal = defaultdict(int)
    por_año = defaultdict(int)
    por_tribunal_año = defaultdict(lambda: defaultdict(int))

    for s in causas_unicas.values():
        por_tipo[s['tipo']] += 1
        por_tribunal[s['tribunal']] += 1
        if s['año']:
            por_año[s['año']] += 1
            por_tribunal_año[s['tribunal']][s['año']] += 1

    print("\n" + "-"*40)
    print("CAUSAS ÚNICAS POR TIPO:")
    for tipo in ['definitiva', 'casacion', 'reemplazo']:
        print(f"  {tipo.capitalize()}: {por_tipo[tipo]}")

    print("\n" + "-"*40)
    print("CAUSAS ÚNICAS POR TRIBUNAL:")
    for t in ['1TA', '2TA', '3TA']:
        print(f"  {t}: {por_tribunal[t]}")

    print("\n" + "-"*40)
    print("CAUSAS POR TRIBUNAL Y AÑO:")
    years = sorted(por_año.keys())

    print(f"{'Año':<8}", end="")
    for t in ['1TA', '2TA', '3TA']:
        print(f"{t:>8}", end="")
    print(f"{'Total':>8}")

    totales = {'1TA': 0, '2TA': 0, '3TA': 0}
    for year in years:
        print(f"{year:<8}", end="")
        total = 0
        for t in ['1TA', '2TA', '3TA']:
            count = por_tribunal_año[t][year]
            print(f"{count:>8}", end="")
            total += count
            totales[t] += count
        print(f"{total:>8}")

    print(f"{'-'*40}")
    print(f"{'TOTAL':<8}", end="")
    for t in ['1TA', '2TA', '3TA']:
        print(f"{totales[t]:>8}", end="")
    print(f"{sum(totales.values()):>8}")

    # Sentencias sin ROL
    sin_rol = [s for s in sentencias if not s['rol']]
    print(f"\nSENTENCIAS SIN ROL IDENTIFICABLE: {len(sin_rol)}")

    # Guardar causas únicas
    causas_lista = sorted(causas_unicas.values(),
                          key=lambda x: (x['tribunal'], x['año'] or 0, x['rol_num'] or 0))

    with open(OUTPUT_DIR / 'causas_unicas.json', 'w', encoding='utf-8') as f:
        json.dump(causas_lista, f, ensure_ascii=False, indent=2)

    with open(OUTPUT_DIR / 'causas_unicas.csv', 'w', encoding='utf-8') as f:
        f.write('rol,tribunal,tipo,año,filename,size_kb\n')
        for s in causas_lista:
            row = [
                s['rol'] or '',
                s['tribunal'],
                s['tipo'],
                str(s['año']) if s['año'] else '',
                s['filename'].replace('"', "'"),
                f"{s['size_kb']:.1f}"
            ]
            f.write('"' + '","'.join(row) + '"\n')

    # Estadísticas finales
    stats = {
        'total_sentencias': len(sentencias),
        'causas_unicas': len(causas_unicas),
        'por_tipo': dict(por_tipo),
        'por_tribunal': dict(por_tribunal),
        'por_año': {str(k): v for k, v in por_año.items()},
        'por_tribunal_año': {t: {str(k): v for k, v in d.items()}
                             for t, d in por_tribunal_año.items()}
    }

    with open(OUTPUT_DIR / 'estadisticas_sentencias_v2.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print("ARCHIVOS GUARDADOS:")
    print(f"  {OUTPUT_DIR / 'causas_unicas.json'}")
    print(f"  {OUTPUT_DIR / 'causas_unicas.csv'}")
    print(f"  {OUTPUT_DIR / 'estadisticas_sentencias_v2.json'}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
