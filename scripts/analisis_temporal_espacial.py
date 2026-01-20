#!/usr/bin/env python3
"""
Análisis temporal y espacial de conflictos socioecológicos.

Genera:
1. Evolución temporal de conflictos por año de inicio
2. Distribución geográfica por región
3. Cruces temporales por sector
4. Mapas de calor por década
"""

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import json
from pathlib import Path
from collections import Counter, defaultdict
import pandas as pd

BASE_DIR = Path(__file__).parent.parent
DATOS_DIR = BASE_DIR / "datos" / "conflictos"
OUTPUT_DIR = BASE_DIR / "datos" / "estadisticas"
OUTPUT_DIR.mkdir(exist_ok=True)

def cargar_datos():
    """Carga el dataset categorizado."""
    with open(DATOS_DIR / "conflictos_categorizados.json", encoding="utf-8") as f:
        return json.load(f)


def analisis_temporal(conflictos):
    """Analiza la evolución temporal de los conflictos."""
    print("\n" + "=" * 60)
    print("ANÁLISIS TEMPORAL")
    print("=" * 60)

    # Conflictos con año de inicio
    con_año = [c for c in conflictos if c.get("año_inicio")]
    print(f"\nConflictos con año de inicio: {len(con_año)} / {len(conflictos)}")

    # Distribución por año
    años = Counter(c["año_inicio"] for c in con_año)
    años_ordenados = sorted(años.items())

    print("\nDistribución por año de inicio:")
    print("-" * 40)

    # Agrupar por décadas
    decadas = defaultdict(int)
    for año, n in años_ordenados:
        if año:
            decada = (año // 10) * 10
            decadas[decada] += n

    print("\nPor década:")
    for decada, n in sorted(decadas.items()):
        print(f"  {decada}s: {n:3} conflictos")

    # Por año (últimos 20)
    print("\nÚltimos 20 años:")
    for año, n in años_ordenados[-20:]:
        barra = "█" * n
        print(f"  {año}: {n:3} {barra}")

    # Evolución acumulada
    acumulado = 0
    evolucion = []
    for año, n in años_ordenados:
        acumulado += n
        evolucion.append({"año": año, "nuevos": n, "acumulado": acumulado})

    return {
        "por_año": dict(años),
        "por_decada": dict(decadas),
        "evolucion_acumulada": evolucion,
        "total_con_año": len(con_año),
        "total_sin_año": len(conflictos) - len(con_año)
    }


def analisis_temporal_por_sector(conflictos):
    """Analiza la evolución temporal por sector."""
    print("\n" + "=" * 60)
    print("EVOLUCIÓN POR SECTOR")
    print("=" * 60)

    # Sectores principales
    sectores_principales = ["Minería", "Energía", "Pesca y acuicultura", "Forestal"]

    sector_año = defaultdict(lambda: defaultdict(int))
    for c in conflictos:
        año = c.get("año_inicio")
        sector = c.get("sector", "Otro")
        if año and sector:
            sector_año[sector][año] += 1

    resultados = {}
    for sector in sectores_principales:
        if sector in sector_año:
            años = sector_año[sector]
            print(f"\n{sector}:")
            for año in sorted(años.keys())[-10:]:
                n = años[año]
                print(f"  {año}: {n}")
            resultados[sector] = dict(años)

    return resultados


def analisis_geografico(conflictos):
    """Analiza la distribución geográfica."""
    print("\n" + "=" * 60)
    print("ANÁLISIS GEOGRÁFICO")
    print("=" * 60)

    # Por región
    regiones = Counter(c.get("region") for c in conflictos if c.get("region"))

    print("\nConflictos por región:")
    print("-" * 40)
    for region, n in regiones.most_common():
        pct = n / len(conflictos) * 100
        barra = "█" * (n // 2)
        print(f"  {region[:25]:25} {n:3} ({pct:4.1f}%) {barra}")

    # Con coordenadas
    con_coords = len([c for c in conflictos
                      if c.get("latitud") and c.get("longitud")])
    print(f"\nConflictos georreferenciados: {con_coords} / {len(conflictos)}")

    # Zonas de sacrificio
    zonas_sacrificio = ["Quintero", "Puchuncaví", "Tocopilla", "Mejillones",
                        "Huasco", "Coronel", "Ventanas"]

    conflictos_zs = []
    for c in conflictos:
        localidad = (c.get("localidad") or "").lower()
        nombre = (c.get("nombre") or "").lower()
        for zona in zonas_sacrificio:
            if zona.lower() in localidad or zona.lower() in nombre:
                conflictos_zs.append(c)
                break

    print(f"\nConflictos en zonas de sacrificio: {len(conflictos_zs)}")
    for c in conflictos_zs[:10]:
        print(f"  - {c.get('nombre', 'Sin nombre')[:50]}")

    return {
        "por_region": dict(regiones),
        "georreferenciados": con_coords,
        "zonas_sacrificio": len(conflictos_zs)
    }


def analisis_region_sector(conflictos):
    """Cruza región con sector."""
    print("\n" + "=" * 60)
    print("CRUCE REGIÓN-SECTOR")
    print("=" * 60)

    cruce = defaultdict(lambda: defaultdict(int))
    for c in conflictos:
        region = c.get("region")
        sector = c.get("sector")
        if region and sector:
            cruce[region][sector] += 1

    # Top 5 regiones con sus sectores principales
    regiones_top = Counter(c.get("region") for c in conflictos
                           if c.get("region")).most_common(5)

    print("\nTop 5 regiones y sus sectores principales:")
    for region, total in regiones_top:
        print(f"\n{region} ({total} conflictos):")
        sectores = cruce[region]
        for sector, n in sorted(sectores.items(), key=lambda x: -x[1])[:3]:
            print(f"  - {sector}: {n}")

    return {region: dict(sectores) for region, sectores in cruce.items()}


def analisis_categorias_cruzado(conflictos):
    """Analiza cruces entre categorías extraídas."""
    print("\n" + "=" * 60)
    print("CRUCES DE CATEGORÍAS")
    print("=" * 60)

    # Impacto vs Actor
    impacto_actor = defaultdict(lambda: defaultdict(int))
    for c in conflictos:
        cat = c.get("categorias", {})
        impactos = cat.get("impactos", [])
        actores = cat.get("actores", [])
        for imp in impactos:
            for act in actores:
                impacto_actor[imp][act] += 1

    print("\nImpacto ambiental vs Actor afectado:")
    print("-" * 50)
    print(f"{'':15} {'Indígena':>10} {'Pescador':>10} {'Agricultor':>10} {'Urbano':>10}")
    for impacto in ["agua", "aire", "suelo", "salud", "biodiversidad"]:
        fila = f"{impacto:15}"
        for actor in ["indigena", "pescador", "agricultor", "urbano"]:
            n = impacto_actor[impacto].get(actor, 0)
            fila += f" {n:>10}"
        print(fila)

    # Resistencia vs Resultado
    resist_result = defaultdict(lambda: defaultdict(int))
    for c in conflictos:
        cat = c.get("categorias", {})
        resistencias = cat.get("resistencias", [])
        resultados = cat.get("resultados", [])
        for res in resistencias:
            for result in resultados:
                resist_result[res][result] += 1

    print("\nForma de resistencia vs Resultado:")
    print("-" * 50)
    print(f"{'':15} {'Paralizado':>12} {'Aprobado':>12} {'En litigio':>12}")
    for resist in ["judicial", "movilizacion", "mediatica", "institucional"]:
        fila = f"{resist:15}"
        for result in ["paralizado", "aprobado", "en_litigio"]:
            n = resist_result[resist].get(result, 0)
            fila += f" {n:>12}"
        print(fila)

    return {
        "impacto_actor": {k: dict(v) for k, v in impacto_actor.items()},
        "resistencia_resultado": {k: dict(v) for k, v in resist_result.items()}
    }


def main():
    print("=" * 60)
    print("ANÁLISIS TEMPORAL Y ESPACIAL DE CONFLICTOS")
    print("=" * 60)

    conflictos = cargar_datos()
    print(f"\nTotal conflictos: {len(conflictos)}")

    # Ejecutar análisis
    temporal = analisis_temporal(conflictos)
    temporal_sector = analisis_temporal_por_sector(conflictos)
    geografico = analisis_geografico(conflictos)
    region_sector = analisis_region_sector(conflictos)
    cruces = analisis_categorias_cruzado(conflictos)

    # Guardar resultados
    resultados = {
        "total_conflictos": len(conflictos),
        "temporal": temporal,
        "temporal_por_sector": temporal_sector,
        "geografico": geografico,
        "region_sector": region_sector,
        "cruces_categorias": cruces
    }

    output_file = OUTPUT_DIR / "analisis_temporal_espacial.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    print(f"\n\nResultados guardados: {output_file}")

    return resultados


if __name__ == "__main__":
    main()
