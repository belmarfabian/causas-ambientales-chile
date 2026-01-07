#!/usr/bin/env python3
"""
Script para organizar y catalogar PDFs de sentencias de tribunales ambientales.
Proyecto: Análisis socioecológico de conflictos ambientales en el norte de Chile
"""

import os
import re
import csv
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Directorio de PDFs
PDF_DIR = Path("g:/My Drive/tribunal_pdf/tribunal_pdfs")
OUTPUT_DIR = Path("g:/My Drive/tribunal_pdf")

def extraer_metadatos(filename):
    """
    Extrae metadatos del nombre del archivo PDF.

    Patrones detectados:
    1. YYYY.MM.DD_Sentencia_R-XXX-YYYY.pdf (formato nuevo)
    2. X-XX-YYYY-DD-MM-YYYY-Sentencia.pdf (formato antiguo)
    3. R-XXX-YYYY_DD-MM-YYYY_Sentencia.pdf (formato intermedio)
    4. Casos especiales: Corte Suprema, acumulados, informes
    """

    # Limpiar nombre
    name = Path(filename).stem
    es_duplicado = name.endswith('_2')
    if es_duplicado:
        name = name[:-2]

    metadatos = {
        'archivo_original': filename,
        'nombre_limpio': name,
        'es_duplicado': es_duplicado,
        'tipo_caso': None,      # R, D, S, C
        'rol': None,            # Número de rol
        'año_rol': None,        # Año del rol
        'fecha_sentencia': None,
        'tipo_documento': None, # Sentencia, Resolución, Informe, Casación
        'roles_acumulados': [], # Para casos acumulados
        'es_corte_suprema': False,
        'notas': ''
    }

    # Detectar si es Corte Suprema
    if 'CS' in name or 'Corte-Suprema' in name or 'casacion' in name.lower() or 'Casacion' in name:
        metadatos['es_corte_suprema'] = True
        metadatos['tipo_documento'] = 'Casación'

    # Patrón 1: Formato nuevo YYYY.MM.DD_Sentencia_R-XXX-YYYY
    patron_nuevo = r'^(\d{4})\.(\d{2})\.(\d{2})_(\w+)_([RDSC])-?(\d+)[-_](\d{4})'
    match = re.match(patron_nuevo, name)
    if match:
        año, mes, dia, tipo_doc, tipo_caso, rol, año_rol = match.groups()
        metadatos['fecha_sentencia'] = f"{año}-{mes}-{dia}"
        metadatos['tipo_documento'] = tipo_doc
        metadatos['tipo_caso'] = tipo_caso
        metadatos['rol'] = int(rol)
        metadatos['año_rol'] = int(año_rol)

        # Buscar roles acumulados
        acumulados = re.findall(r'acum(?:ulada)?[_.]?([RDSC])?[-_]?(\d+)[-_]?(\d{4})?', name, re.I)
        for ac in acumulados:
            tipo_ac = ac[0] if ac[0] else tipo_caso
            rol_ac = ac[1]
            año_ac = ac[2] if ac[2] else año_rol
            metadatos['roles_acumulados'].append(f"{tipo_ac}-{rol_ac}-{año_ac}")

        # También buscar con formato R-XXX_YYY
        multiples = re.findall(r'_(\d+)[-_](\d{4})', name)
        # Ignorar el primero que ya capturamos

        return metadatos

    # Patrón 2: Formato antiguo X-XX-YYYY-DD-MM-YYYY-Tipo
    patron_antiguo = r'^([RDSC])-(\d+)-(\d{4})-(\d{2})-(\d{2})-(\d{4})-(\w+)'
    match = re.match(patron_antiguo, name)
    if match:
        tipo_caso, rol, año_rol, dia, mes, año, tipo_doc = match.groups()
        metadatos['tipo_caso'] = tipo_caso
        metadatos['rol'] = int(rol)
        metadatos['año_rol'] = int(año_rol)
        metadatos['fecha_sentencia'] = f"{año}-{mes}-{dia}"
        metadatos['tipo_documento'] = tipo_doc
        return metadatos

    # Patrón 3: Formato intermedio R-XXX-YYYY_DD-MM-YYYY_Sentencia
    patron_intermedio = r'^([RDSC])-(\d+)-(\d{4})_(\d{2})-(\d{2})-(\d{4})_(\w+)'
    match = re.match(patron_intermedio, name)
    if match:
        tipo_caso, rol, año_rol, dia, mes, año, tipo_doc = match.groups()
        metadatos['tipo_caso'] = tipo_caso
        metadatos['rol'] = int(rol)
        metadatos['año_rol'] = int(año_rol)
        metadatos['fecha_sentencia'] = f"{año}-{mes}-{dia}"
        metadatos['tipo_documento'] = tipo_doc
        return metadatos

    # Patrón 4: Solo rol R-XXX-YYYY
    patron_rol = r'([RDSC])-(\d+)-(\d{4})'
    match = re.search(patron_rol, name)
    if match:
        tipo_caso, rol, año_rol = match.groups()
        metadatos['tipo_caso'] = tipo_caso
        metadatos['rol'] = int(rol)
        metadatos['año_rol'] = int(año_rol)

        # Buscar fecha en formato YYYY.MM.DD al inicio
        fecha_match = re.match(r'^(\d{4})\.(\d{2})\.(\d{2})', name)
        if fecha_match:
            año, mes, dia = fecha_match.groups()
            metadatos['fecha_sentencia'] = f"{año}-{mes}-{dia}"

        # Detectar tipo de documento
        if 'Sentencia' in name:
            metadatos['tipo_documento'] = 'Sentencia'
        elif 'Resolucion' in name:
            metadatos['tipo_documento'] = 'Resolución'
        elif 'Informe' in name:
            metadatos['tipo_documento'] = 'Informe'

        return metadatos

    # Patrón 5: Casos de Corte Suprema con número
    patron_cs = r'(\d+)-(\d{4})'
    match = re.search(patron_cs, name)
    if match and metadatos['es_corte_suprema']:
        metadatos['rol'] = int(match.group(1))
        metadatos['año_rol'] = int(match.group(2))
        return metadatos

    # No se pudo parsear - marcar para revisión manual
    metadatos['notas'] = 'Requiere revisión manual'
    return metadatos


def analizar_directorio():
    """Analiza todos los PDFs en el directorio."""

    archivos = list(PDF_DIR.glob("*.pdf"))
    print(f"Total de archivos PDF encontrados: {len(archivos)}")

    inventario = []
    duplicados = []
    originales = []
    sin_parsear = []

    for archivo in sorted(archivos):
        meta = extraer_metadatos(archivo.name)
        meta['tamaño_bytes'] = archivo.stat().st_size
        meta['tamaño_mb'] = round(archivo.stat().st_size / (1024 * 1024), 2)

        inventario.append(meta)

        if meta['es_duplicado']:
            duplicados.append(meta)
        else:
            originales.append(meta)

        if meta['notas'] == 'Requiere revisión manual':
            sin_parsear.append(meta)

    return inventario, originales, duplicados, sin_parsear


def generar_estadisticas(inventario, originales, duplicados, sin_parsear):
    """Genera estadísticas del inventario."""

    stats = {
        'total_archivos': len(inventario),
        'originales': len(originales),
        'duplicados': len(duplicados),
        'sin_parsear': len(sin_parsear),
    }

    # Por tipo de caso
    tipos = defaultdict(int)
    for m in originales:
        if m['tipo_caso']:
            tipos[m['tipo_caso']] += 1
    stats['por_tipo'] = dict(tipos)

    # Por año de rol
    años = defaultdict(int)
    for m in originales:
        if m['año_rol']:
            años[m['año_rol']] += 1
    stats['por_año'] = dict(sorted(años.items()))

    # Por tipo de documento
    docs = defaultdict(int)
    for m in originales:
        if m['tipo_documento']:
            docs[m['tipo_documento']] += 1
    stats['por_documento'] = dict(docs)

    # Casos Corte Suprema
    cs = sum(1 for m in originales if m['es_corte_suprema'])
    stats['corte_suprema'] = cs

    # Tamaño total
    tamaño_total = sum(m['tamaño_bytes'] for m in inventario)
    stats['tamaño_total_mb'] = round(tamaño_total / (1024 * 1024), 2)

    tamaño_duplicados = sum(m['tamaño_bytes'] for m in duplicados)
    stats['tamaño_duplicados_mb'] = round(tamaño_duplicados / (1024 * 1024), 2)

    return stats


def guardar_csv(inventario, filename):
    """Guarda el inventario en CSV."""

    campos = [
        'archivo_original', 'nombre_limpio', 'es_duplicado',
        'tipo_caso', 'rol', 'año_rol', 'fecha_sentencia',
        'tipo_documento', 'es_corte_suprema', 'roles_acumulados',
        'tamaño_mb', 'notas'
    ]

    with open(OUTPUT_DIR / filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=campos, extrasaction='ignore')
        writer.writeheader()
        for item in inventario:
            row = item.copy()
            row['roles_acumulados'] = ';'.join(item['roles_acumulados'])
            writer.writerow(row)

    print(f"Guardado: {filename}")


def imprimir_reporte(stats, sin_parsear):
    """Imprime reporte formateado."""

    print("\n" + "="*60)
    print("INVENTARIO DE SENTENCIAS - TRIBUNALES AMBIENTALES")
    print("="*60)

    print(f"\n[RESUMEN GENERAL]")
    print(f"   Total archivos:     {stats['total_archivos']}")
    print(f"   Archivos unicos:    {stats['originales']}")
    print(f"   Duplicados (_2):    {stats['duplicados']}")
    print(f"   Sin parsear:        {stats['sin_parsear']}")
    print(f"   Tamano total:       {stats['tamaño_total_mb']} MB")
    print(f"   Espacio duplicados: {stats['tamaño_duplicados_mb']} MB")

    print(f"\n[POR TIPO DE CASO]")
    tipo_nombres = {
        'R': 'Reclamaciones',
        'D': 'Demandas por dano',
        'S': 'Solicitudes',
        'C': 'Consultas'
    }
    for tipo, count in sorted(stats['por_tipo'].items()):
        nombre = tipo_nombres.get(tipo, tipo)
        print(f"   {tipo} - {nombre}: {count}")

    print(f"\n[POR ANO DE ROL]")
    for ano, count in stats['por_año'].items():
        barra = "#" * (count // 2)
        print(f"   {ano}: {count:3d} {barra}")

    print(f"\n[POR TIPO DE DOCUMENTO]")
    for doc, count in stats['por_documento'].items():
        print(f"   {doc}: {count}")

    print(f"\n[Casos Corte Suprema]: {stats['corte_suprema']}")

    if sin_parsear:
        print(f"\n[!] ARCHIVOS SIN PARSEAR ({len(sin_parsear)}):")
        for m in sin_parsear[:10]:
            print(f"   - {m['archivo_original']}")
        if len(sin_parsear) > 10:
            print(f"   ... y {len(sin_parsear) - 10} mas")


def proponer_estructura():
    """Propone una estructura de carpetas organizada."""

    print("\n" + "="*60)
    print("ESTRUCTURA DE CARPETAS PROPUESTA")
    print("="*60)

    estructura = """
tribunal_pdfs/
├── originales/
│   ├── reclamaciones/          # R-XXX-YYYY
│   │   ├── 2013/
│   │   ├── 2014/
│   │   ├── ...
│   │   └── 2025/
│   ├── demandas/               # D-XXX-YYYY
│   │   ├── 2013/
│   │   └── ...
│   ├── solicitudes/            # S-XXX-YYYY
│   │   └── ...
│   ├── consultas/              # C-XXX-YYYY
│   │   └── ...
│   └── corte_suprema/          # Casaciones
│       └── ...
├── duplicados/                 # Archivos _2 (para eliminar)
├── sin_clasificar/             # Archivos sin parsear
└── inventario/
    ├── inventario_completo.csv
    ├── inventario_originales.csv
    └── estadisticas.txt
"""
    print(estructura)


if __name__ == "__main__":
    print("Analizando directorio de PDFs...")
    inventario, originales, duplicados, sin_parsear = analizar_directorio()

    print("Generando estadísticas...")
    stats = generar_estadisticas(inventario, originales, duplicados, sin_parsear)

    print("Guardando inventarios CSV...")
    guardar_csv(inventario, "inventario_completo.csv")
    guardar_csv(originales, "inventario_originales.csv")
    guardar_csv(duplicados, "inventario_duplicados.csv")

    imprimir_reporte(stats, sin_parsear)
    proponer_estructura()

    print("\n[OK] Analisis completado.")
