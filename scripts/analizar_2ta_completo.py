#!/usr/bin/env python3
"""
Análisis completo 2TA - todos los tipos de causa
"""

import os
import sys
import re
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = Path(r"G:\Mi unidad\tribunal_pdf\corpus\descarga_completa\documentos\sentencias")

def extract_rol_completo(filename):
    """Extrae ROL de cualquier tipo: R, S, D, C"""
    fn = filename.replace('_', '-')

    # Patrones para diferentes tipos
    patterns = [
        # R-344-2022
        (r'R-(\d{1,3})-(\d{4})', 'R'),
        # S-80-2023 (solicitudes)
        (r'S-(\d{1,3})-(\d{4})', 'S'),
        # D-74-2022 (demandas)
        (r'D-(\d{1,3})-(\d{4})', 'D'),
        # C-01-2013 (otro tipo)
        (r'C-(\d{1,2})-(\d{4})', 'C'),
        # Rol-348-2022
        (r'Rol-(\d{1,3})-(\d{4})', 'R'),
        # Patrón sin tipo explícito pero con año
        (r'[-_](\d{1,3})[-_](\d{4})[-_]', 'R'),
    ]

    for pattern, tipo in patterns:
        match = re.search(pattern, fn, re.IGNORECASE)
        if match:
            num = int(match.group(1))
            year = int(match.group(2))
            if 2012 <= year <= 2030:
                return f"{tipo}-{num}-{year}", tipo, num, year

    # Patrón: archivo empieza con año YYYY.MM.DD...R-XXX
    match = re.search(r'^(\d{4})\.\d{2}\.\d{2}.*?([RSDC])[-_]?(\d{1,3})', fn, re.IGNORECASE)
    if match:
        year = int(match.group(1))
        tipo = match.group(2).upper()
        num = int(match.group(3))
        if 2012 <= year <= 2030:
            return f"{tipo}-{num}-{year}", tipo, num, year

    # Patrón Corte Suprema: XXXXX-YYYY
    match = re.search(r'^(\d{4,6})-(\d{4})', fn)
    if match:
        rol_cs = match.group(1)
        year = int(match.group(2))
        if 2012 <= year <= 2030:
            return f"CS-{rol_cs}-{year}", 'CS', int(rol_cs), year

    return None, None, None, None

def main():
    print("="*60)
    print("ANÁLISIS COMPLETO 2TA")
    print("="*60)

    por_tipo = defaultdict(dict)  # tipo -> {rol: [archivos]}
    sin_rol = []
    total_archivos = 0

    for filepath in BASE_DIR.glob("*"):
        if not filepath.is_file():
            continue

        total_archivos += 1
        filename = filepath.name
        fname_lower = filename.lower()

        # Excluir algunos
        if 'boletin' in fname_lower or 'sintesis' in fname_lower:
            continue

        rol, tipo, num, year = extract_rol_completo(filename)

        if rol:
            if rol not in por_tipo[tipo]:
                por_tipo[tipo][rol] = []
            por_tipo[tipo][rol].append(filename)
        else:
            sin_rol.append(filename)

    print(f"\nTotal archivos: {total_archivos}")

    # Resumen por tipo
    print("\n" + "="*60)
    print("CAUSAS POR TIPO:")
    print("="*60)

    total_causas = 0
    for tipo in ['R', 'S', 'D', 'C', 'CS']:
        if tipo in por_tipo:
            count = len(por_tipo[tipo])
            total_causas += count
            print(f"  {tipo}: {count} causas únicas")

    print(f"\nTOTAL CAUSAS: {total_causas}")
    print(f"Sin ROL: {len(sin_rol)}")

    # Distribución por año (solo R)
    print("\n" + "="*60)
    print("RECLAMACIONES (R) POR AÑO:")
    print("="*60)

    r_por_año = defaultdict(int)
    for rol in por_tipo.get('R', {}).keys():
        match = re.search(r'-(\d{4})$', rol)
        if match:
            r_por_año[match.group(1)] += 1

    for year in sorted(r_por_año.keys()):
        print(f"  {year}: {r_por_año[year]}")
    print(f"\n  TOTAL R: {sum(r_por_año.values())}")

    # Otros tipos por año
    for tipo in ['S', 'D', 'C']:
        if tipo in por_tipo and por_tipo[tipo]:
            print(f"\n{tipo} por año:")
            t_por_año = defaultdict(int)
            for rol in por_tipo[tipo].keys():
                match = re.search(r'-(\d{4})$', rol)
                if match:
                    t_por_año[match.group(1)] += 1
            for year in sorted(t_por_año.keys()):
                print(f"  {year}: {t_por_año[year]}")

    # Comparación con oficiales
    print("\n" + "="*60)
    print("COMPARACIÓN CON CIFRAS OFICIALES:")
    print("="*60)
    print("Cifras oficiales 2TA:")
    print("  - 2013-2023: 287 sentencias")
    print("  - 2024: 45 sentencias")
    print("  - Total: ~332 sentencias")

    # Conteo real (solo hasta 2025)
    r_hasta_2025 = sum(v for k, v in r_por_año.items() if int(k) <= 2025)
    print(f"\nEn corpus (R hasta 2025): {r_hasta_2025}")
    print(f"Cobertura R: {r_hasta_2025/332*100:.1f}%")

    # Con todos los tipos
    todos_hasta_2025 = 0
    for tipo in ['R', 'S', 'D', 'C']:
        for rol in por_tipo.get(tipo, {}).keys():
            match = re.search(r'-(\d{4})$', rol)
            if match and int(match.group(1)) <= 2025:
                todos_hasta_2025 += 1

    print(f"Incluyendo S, D, C: {todos_hasta_2025}")

    # Sin ROL
    print("\n" + "-"*40)
    print(f"ARCHIVOS SIN ROL ({len(sin_rol)}):")
    for f in sorted(sin_rol)[:20]:
        print(f"  {f}")

if __name__ == "__main__":
    main()
