#!/usr/bin/env python3
"""
Análisis completo 3TA - incluye demandas D- y reclamaciones R-
"""

import os
import sys
import re
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = Path(r"G:\Mi unidad\tribunal_pdf\corpus\descarga_completa\documentos\3ta")

def es_sentencia_real(filename):
    """Determina si es una sentencia real"""
    fname_lower = filename.lower()

    exclusiones = [
        'bases', 'concurso', 'boletin', 'boletín', 'sintesis', 'síntesis',
        'comentario', 'informe-', 'acta', 'programa', 'calendario',
        'presentacion', 'presentación', 'resumen', 'ficha', 'anexo',
        'inadmisible'  # No son sentencias definitivas
    ]

    for exc in exclusiones:
        if exc in fname_lower:
            return False

    if 'sentencia' in fname_lower:
        return True
    if re.match(r'^[RD][-_]?\d', filename, re.IGNORECASE):
        return True

    return False

def extract_rol_completo(filename):
    """Extrae ROL incluyendo demandas D-"""
    fn = filename.replace('_', '-')

    # Patrones para R- (reclamaciones)
    r_patterns = [
        (r'R-(\d{1,3})-(\d{4})', 'R'),
        (r'R(\d{1,3})\.(\d{4})', 'R'),
        (r'(?<![0-9])R(\d{1,3})-(\d{4})', 'R'),
        (r'(?<![0-9])R(\d{1,3})(\d{4})(?![0-9])', 'R'),
        (r'R-(\d{1,3})-(\d{2})(?![0-9])', 'R'),  # año corto
    ]

    # Patrones para D- (demandas de reparación)
    d_patterns = [
        (r'D-(\d{1,3})-(\d{4})', 'D'),
        (r'D(\d{1,3})\.(\d{4})', 'D'),
        (r'(?<![0-9])D(\d{1,3})-(\d{4})', 'D'),
        (r'D[-_](\d{1,3})[-_](\d{4})', 'D'),
        (r'3TA-D-(\d{1,3})-(\d{4})', 'D'),
    ]

    all_patterns = r_patterns + d_patterns

    for pattern, tipo in all_patterns:
        match = re.search(pattern, fn, re.IGNORECASE)
        if match:
            num = int(match.group(1))
            year = int(match.group(2))

            if year < 100:
                year = 2000 + year

            if 2012 <= year <= 2030:
                return f"{tipo}-{num}-{year}", tipo, num, year

    return None, None, None, None

def main():
    print("="*60)
    print("ANÁLISIS COMPLETO 3TA (R- y D-)")
    print("="*60)

    sentencias = []
    corte_suprema = []
    por_tipo = {'R': {}, 'D': {}}
    sin_rol = []

    for filepath in BASE_DIR.rglob("*"):
        if not filepath.is_file():
            continue

        filename = filepath.name
        fname_lower = filename.lower()

        if not es_sentencia_real(filename):
            continue

        # Detectar Corte Suprema
        if 'suprema' in fname_lower or 'c-suprema' in fname_lower or 'cs-' in fname_lower or 'c-s-' in fname_lower or 'casacion' in fname_lower or 'casación' in fname_lower:
            corte_suprema.append(filename)
            continue

        sentencias.append(filename)

        rol, tipo, num, year = extract_rol_completo(filename)

        if rol:
            if rol not in por_tipo[tipo]:
                por_tipo[tipo][rol] = []
            por_tipo[tipo][rol].append(filename)
        else:
            sin_rol.append(filename)

    # Resultados
    print(f"\nSentencias del Tribunal: {len(sentencias)}")
    print(f"Sentencias Corte Suprema: {len(corte_suprema)}")

    print(f"\nReclamaciones (R-): {len(por_tipo['R'])} causas únicas")
    print(f"Demandas reparación (D-): {len(por_tipo['D'])} causas únicas")
    print(f"Total causas únicas: {len(por_tipo['R']) + len(por_tipo['D'])}")
    print(f"Sin ROL identificado: {len(sin_rol)}")

    # Distribución por año - R
    print("\n" + "="*60)
    print("RECLAMACIONES (R-) POR AÑO:")
    print("="*60)
    r_por_año = defaultdict(int)
    for rol in por_tipo['R'].keys():
        match = re.search(r'-(\d{4})$', rol)
        if match:
            r_por_año[match.group(1)] += 1

    oficial_r = {
        '2013': 0, '2014': 5, '2015': 17, '2016': 22, '2017': 16,
        '2018': 19, '2019': 25, '2020': 29, '2021': 21, '2022': 40,
        '2023': 61, '2024': 28, '2025': 23
    }

    print(f"{'Año':<8}{'Oficial':>10}{'Corpus':>10}{'Dif':>8}")
    print("-"*36)
    for year in sorted(set(list(oficial_r.keys()) + list(r_por_año.keys()))):
        o = oficial_r.get(year, 0)
        c = r_por_año.get(year, 0)
        print(f"{year:<8}{o:>10}{c:>10}{c-o:>8}")
    print("-"*36)
    print(f"{'TOTAL':<8}{sum(oficial_r.values()):>10}{sum(r_por_año.values()):>10}{sum(r_por_año.values())-sum(oficial_r.values()):>8}")

    # Distribución por año - D
    print("\n" + "="*60)
    print("DEMANDAS REPARACIÓN (D-) POR AÑO:")
    print("="*60)
    d_por_año = defaultdict(int)
    for rol in por_tipo['D'].keys():
        match = re.search(r'-(\d{4})$', rol)
        if match:
            d_por_año[match.group(1)] += 1

    for year in sorted(d_por_año.keys()):
        print(f"  {year}: {d_por_año[year]}")
    print(f"\n  TOTAL D-: {sum(d_por_año.values())}")

    # Archivos sin ROL
    print("\n" + "="*60)
    print("ARCHIVOS SIN ROL:")
    print("="*60)
    for f in sorted(sin_rol)[:25]:
        print(f"  {f}")
    if len(sin_rol) > 25:
        print(f"  ... y {len(sin_rol)-25} más")

    # Resumen final
    print("\n" + "="*60)
    print("RESUMEN COMPARATIVO:")
    print("="*60)
    total_corpus = len(por_tipo['R']) + len(por_tipo['D'])
    total_oficial = 306  # Sentencias definitivas oficiales

    print(f"Cifra oficial 3TA (sentencias definitivas): {total_oficial}")
    print(f"")
    print(f"En corpus:")
    print(f"  - Reclamaciones (R-): {len(por_tipo['R'])}")
    print(f"  - Demandas (D-): {len(por_tipo['D'])}")
    print(f"  - Total causas únicas: {total_corpus}")
    print(f"  - Corte Suprema: {len(corte_suprema)}")
    print(f"")
    print(f"Cobertura (R- solamente): {len(por_tipo['R'])/total_oficial*100:.1f}%")
    print(f"Cobertura (R- + D-): {total_corpus/total_oficial*100:.1f}%")

    # Mostrar algunas D- para verificar
    print("\n" + "-"*40)
    print("EJEMPLO DEMANDAS (D-):")
    for rol, files in list(por_tipo['D'].items())[:10]:
        print(f"  {rol}: {files[0]}")

if __name__ == "__main__":
    main()
