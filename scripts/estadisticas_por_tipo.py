#!/usr/bin/env python3
"""
Estadísticas del corpus clasificadas por tipo de documento
"""

import os
import sys
import re
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DIRS = {
    '1TA': Path(r"G:\Mi unidad\tribunal_pdf\corpus\descarga_completa\documentos\1ta"),
    '2TA': Path(r"G:\Mi unidad\tribunal_pdf\corpus\descarga_completa\documentos\sentencias"),
    '3TA': Path(r"G:\Mi unidad\tribunal_pdf\corpus\descarga_completa\documentos\3ta"),
}

def clasificar_documento(filename, filepath):
    """Clasifica un documento por tipo"""
    fn = filename.lower()

    # Excluir no-documentos judiciales
    if any(x in fn for x in ['boletin', 'boletín', 'bases', 'concurso', 'programa']):
        return 'otro', None

    # Detectar tipo de resolución
    tipo_resolucion = 'sentencia_definitiva'
    if 'casacion' in fn or 'casación' in fn or 'c-suprema' in fn or 'cs-' in fn:
        tipo_resolucion = 'casacion_cs'
    elif 'reemplazo' in fn:
        tipo_resolucion = 'reemplazo_cs'
    elif 'sintesis' in fn or 'síntesis' in fn or 'resumen' in fn:
        return 'sintesis', None

    # Detectar tipo de causa
    fn_norm = filename.replace('_', '-')

    # R- Reclamación
    if re.search(r'R[-_]?\d', fn_norm, re.IGNORECASE):
        match = re.search(r'R[-_]?(\d{1,3})[-_]?(\d{4})?', fn_norm, re.IGNORECASE)
        if match:
            num = match.group(1)
            year = match.group(2) if match.group(2) else '????'
            return tipo_resolucion, f"R-{num}-{year}"

    # S- Solicitud
    if re.search(r'S[-_]?\d', fn_norm, re.IGNORECASE) and 's1ta' not in fn:
        match = re.search(r'S[-_]?(\d{1,3})[-_]?(\d{4})?', fn_norm, re.IGNORECASE)
        if match:
            num = match.group(1)
            year = match.group(2) if match.group(2) else '????'
            return tipo_resolucion, f"S-{num}-{year}"

    # D- Demanda
    if re.search(r'D[-_]?\d', fn_norm, re.IGNORECASE):
        match = re.search(r'D[-_]?(\d{1,3})[-_]?(\d{4})?', fn_norm, re.IGNORECASE)
        if match:
            num = match.group(1)
            year = match.group(2) if match.group(2) else '????'
            return tipo_resolucion, f"D-{num}-{year}"

    # C- Otras
    if re.search(r'C[-_]?\d', fn_norm, re.IGNORECASE):
        match = re.search(r'C[-_]?(\d{1,2})[-_]?(\d{4})?', fn_norm, re.IGNORECASE)
        if match:
            num = match.group(1)
            year = match.group(2) if match.group(2) else '????'
            return tipo_resolucion, f"C-{num}-{year}"

    # S1TA (1er Tribunal)
    if 's1ta' in fn:
        match = re.search(r'R[-_]?(\d{1,3})[-_]?(\d{4})?', fn_norm, re.IGNORECASE)
        if match:
            num = match.group(1)
            year = match.group(2) if match.group(2) else '????'
            return tipo_resolucion, f"R-{num}-{year}"

    # Si tiene "sentencia" pero no identificamos el tipo
    if 'sentencia' in fn:
        return tipo_resolucion, None

    return 'otro', None

def main():
    print("="*70)
    print("ESTADÍSTICAS DEL CORPUS POR TIPO DE DOCUMENTO")
    print("="*70)

    # Contadores globales
    por_tribunal = defaultdict(lambda: defaultdict(set))  # tribunal -> tipo_causa -> set(ROLs)
    por_tipo_resolucion = defaultdict(int)
    total_archivos = 0

    for tribunal, base_dir in DIRS.items():
        if not base_dir.exists():
            print(f"\n[!] Directorio no existe: {base_dir}")
            continue

        print(f"\nProcesando {tribunal}...")

        for filepath in base_dir.rglob("*"):
            if not filepath.is_file():
                continue

            total_archivos += 1
            filename = filepath.name

            tipo_res, rol = clasificar_documento(filename, filepath)

            por_tipo_resolucion[tipo_res] += 1

            if rol:
                # Extraer tipo de causa (R, S, D, C)
                tipo_causa = rol[0]
                por_tribunal[tribunal][tipo_causa].add(rol)

    # Mostrar resultados
    print("\n" + "="*70)
    print("TIPOS DE CAUSA POR TRIBUNAL (causas únicas)")
    print("="*70)

    print(f"\n{'Tribunal':<12}{'R (Reclam.)':<15}{'D (Demanda)':<15}{'S (Solic.)':<15}{'C (Otras)':<12}{'TOTAL':<10}")
    print("-"*70)

    gran_total = {'R': 0, 'D': 0, 'S': 0, 'C': 0}
    for tribunal in ['1TA', '2TA', '3TA']:
        r = len(por_tribunal[tribunal].get('R', set()))
        d = len(por_tribunal[tribunal].get('D', set()))
        s = len(por_tribunal[tribunal].get('S', set()))
        c = len(por_tribunal[tribunal].get('C', set()))
        total = r + d + s + c

        gran_total['R'] += r
        gran_total['D'] += d
        gran_total['S'] += s
        gran_total['C'] += c

        print(f"{tribunal:<12}{r:<15}{d:<15}{s:<15}{c:<12}{total:<10}")

    print("-"*70)
    print(f"{'TOTAL':<12}{gran_total['R']:<15}{gran_total['D']:<15}{gran_total['S']:<15}{gran_total['C']:<12}{sum(gran_total.values()):<10}")

    # Tipos de resolución
    print("\n" + "="*70)
    print("TIPOS DE RESOLUCIÓN (todos los archivos)")
    print("="*70)

    tipos_nombres = {
        'sentencia_definitiva': 'Sentencias Definitivas (Tribunal Ambiental)',
        'casacion_cs': 'Sentencias de Casación (Corte Suprema)',
        'reemplazo_cs': 'Sentencias de Reemplazo (Corte Suprema)',
        'sintesis': 'Síntesis/Resúmenes',
        'otro': 'Otros documentos'
    }

    for tipo, nombre in tipos_nombres.items():
        count = por_tipo_resolucion.get(tipo, 0)
        print(f"  {nombre}: {count}")

    print(f"\nTotal archivos procesados: {total_archivos}")

    # Resumen para el paper
    print("\n" + "="*70)
    print("RESUMEN PARA EL PAPER")
    print("="*70)

    print("""
El corpus contiene documentos de los tres Tribunales Ambientales de Chile:

**Por tipo de causa (causas únicas):**
- Reclamaciones (R): {} - Impugnación de actos administrativos
- Demandas (D): {} - Reparación de daño ambiental
- Solicitudes (S): {} - Autorización de medidas provisionales
- Otras (C): {} - Consultas y procedimientos especiales

**Por tipo de resolución:**
- Sentencias Definitivas: {} (resuelven el caso en el tribunal)
- Sentencias Corte Suprema: {} (casación + reemplazo)

**Total de causas únicas identificadas: {}**
    """.format(
        gran_total['R'],
        gran_total['D'],
        gran_total['S'],
        gran_total['C'],
        por_tipo_resolucion.get('sentencia_definitiva', 0),
        por_tipo_resolucion.get('casacion_cs', 0) + por_tipo_resolucion.get('reemplazo_cs', 0),
        sum(gran_total.values())
    ))

if __name__ == "__main__":
    main()
