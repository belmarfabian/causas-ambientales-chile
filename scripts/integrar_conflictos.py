#!/usr/bin/env python3
"""
Integración de múltiples fuentes de conflictos socioecológicos en Chile.

Fuentes:
- INDH: Mapa de Conflictos Socioambientales (162 conflictos)
- EJAtlas: Environmental Justice Atlas (77 conflictos)
- OCMAL: Observatorio de Conflictos Mineros (49 conflictos)

Notas:
- OLCA: No tiene base estructurada, solo documentación cualitativa
- ACLED: Requiere API key (acceso gratuito académico en acleddata.com)

Autor: Fabián Belmar
Fecha: Enero 2026
"""

import json
import re
from datetime import datetime
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).parent.parent
DATOS_DIR = BASE_DIR / "datos" / "conflictos"


def normalizar_texto(texto):
    """Normaliza texto para comparación."""
    if not texto:
        return ""
    texto = texto.lower()
    reemplazos = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ñ': 'n', 'ü': 'u'
    }
    for old, new in reemplazos.items():
        texto = texto.replace(old, new)
    texto = re.sub(r'[^a-z0-9\s]', '', texto)
    return texto.strip()


def cargar_indh():
    """Carga y procesa datos del INDH."""
    archivo = DATOS_DIR / "indh_conflictos.json"
    if not archivo.exists():
        print(f"Archivo no encontrado: {archivo}")
        return []

    with open(archivo, encoding="utf-8") as f:
        data = json.load(f)

    conflictos = []
    for c in data:
        marca = c.get("marcaMapa", {}) or {}
        lat = marca.get("latitud")
        lon = marca.get("longitud")

        region = c.get("region", {}) or {}
        nombre_region = region.get("nombreRegion", "") if isinstance(region, dict) else region

        sector = c.get("sectorProductivo", {}) or {}
        nombre_sector = sector.get("nombreSector", "") if isinstance(sector, dict) else ""

        estado = c.get("estadoConflico", {}) or {}
        estado_conflicto = estado.get("glosa", "") if isinstance(estado, dict) else ""

        conflicto = {
            "id_interno": f"INDH-{c.get('id', 'X')}",
            "fuente": "INDH",
            "id_fuente": c.get("id"),
            "nombre": c.get("tituloConflicto", ""),
            "nombre_normalizado": normalizar_texto(c.get("tituloConflicto", "")),
            "descripcion": c.get("resumenConflicto", ""),
            "region": nombre_region or "",
            "localidad": c.get("localidadConflicto", ""),
            "latitud": lat,
            "longitud": lon,
            "sector": nombre_sector,
            "estado": estado_conflicto,
            "año_inicio": c.get("anyo"),
            "territorio_indigena": c.get("esTerritorioIndigena", False),
            "fecha_actualizacion": c.get("fechaActualizacionPublicacion"),
            "url": f"https://mapaconflictos.indh.cl/conflicto/{c.get('id')}"
        }
        conflictos.append(conflicto)

    return conflictos


def cargar_ejatlas():
    """Carga y procesa datos de EJAtlas."""
    archivo = DATOS_DIR / "ejatlas_chile_filtrado.json"
    if not archivo.exists():
        print(f"Archivo no encontrado: {archivo}")
        return []

    with open(archivo, encoding="utf-8") as f:
        data = json.load(f)

    conflictos = []
    for c in data:
        conflicto = {
            "id_interno": f"EJATLAS-{c.get('id', 'X')}",
            "fuente": "EJAtlas",
            "id_fuente": c.get("id"),
            "nombre": c.get("name", ""),
            "nombre_normalizado": normalizar_texto(c.get("name", "")),
            "descripcion": c.get("headline", ""),
            "region": "",
            "localidad": "",
            "latitud": None,
            "longitud": None,
            "sector": "",
            "estado": "",
            "año_inicio": None,
            "territorio_indigena": None,
            "fecha_actualizacion": None,
            "url": f"https://ejatlas.org/conflict/{c.get('slug', '')}"
        }
        conflictos.append(conflicto)

    return conflictos


def cargar_ocmal():
    """Carga y procesa datos de OCMAL."""
    archivo = DATOS_DIR / "ocmal_chile.json"
    if not archivo.exists():
        print(f"Archivo no encontrado: {archivo}")
        return []

    with open(archivo, encoding="utf-8") as f:
        data = json.load(f)

    conflictos = []
    for c in data:
        conflicto = {
            "id_interno": f"OCMAL-{c.get('id', 'X')}",
            "fuente": "OCMAL",
            "id_fuente": c.get("id"),
            "nombre": c.get("nombre", ""),
            "nombre_normalizado": normalizar_texto(c.get("nombre", "")),
            "descripcion": "",
            "region": c.get("region", ""),
            "localidad": c.get("ubicacion", ""),
            "latitud": None,
            "longitud": None,
            "sector": "Minería",  # OCMAL es específico de minería
            "estado": "",
            "año_inicio": c.get("año_inicio"),
            "empresa": c.get("empresa"),
            "territorio_indigena": None,
            "fecha_actualizacion": None,
            "url": "https://mapa.conflictosmineros.net/ocmal_db-v2/"
        }
        conflictos.append(conflicto)

    return conflictos


def identificar_duplicados(fuente_principal, fuente_secundaria, nombre_fuente):
    """Identifica posibles duplicados entre dos fuentes."""
    duplicados = []

    # Crear índice de palabras clave de la fuente principal
    palabras_principal = {}
    for i, c in enumerate(fuente_principal):
        nombre_norm = c["nombre_normalizado"]
        palabras = set(nombre_norm.split())
        palabras = {p for p in palabras if len(p) > 3}
        for p in palabras:
            if p not in palabras_principal:
                palabras_principal[p] = []
            palabras_principal[p].append(i)

    # Buscar coincidencias
    for c in fuente_secundaria:
        nombre_norm = c["nombre_normalizado"]
        palabras = set(nombre_norm.split())
        palabras = {p for p in palabras if len(p) > 3}

        coincidencias = Counter()
        for p in palabras:
            if p in palabras_principal:
                for idx in palabras_principal[p]:
                    coincidencias[idx] += 1

        for idx, score in coincidencias.most_common(3):
            if score >= 2:
                duplicados.append({
                    "fuente": nombre_fuente,
                    "nombre_secundario": c["nombre"],
                    "nombre_principal": fuente_principal[idx]["nombre"],
                    "score": score
                })
                break  # Solo marcar el primer duplicado encontrado

    return duplicados


def main():
    print("=" * 60)
    print("INTEGRACIÓN DE FUENTES DE CONFLICTOS SOCIOECOLÓGICOS")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    # Cargar fuentes
    print("\n1. Cargando fuentes...")
    indh = cargar_indh()
    print(f"   INDH: {len(indh)} conflictos")

    ejatlas = cargar_ejatlas()
    print(f"   EJAtlas: {len(ejatlas)} conflictos")

    ocmal = cargar_ocmal()
    print(f"   OCMAL: {len(ocmal)} conflictos")

    # Identificar duplicados
    print("\n2. Identificando posibles duplicados...")

    # EJAtlas vs INDH
    duplicados_ejatlas = identificar_duplicados(indh, ejatlas, "EJAtlas")
    print(f"   EJAtlas duplicados con INDH: {len(duplicados_ejatlas)}")

    # OCMAL vs INDH
    duplicados_ocmal = identificar_duplicados(indh, ocmal, "OCMAL")
    print(f"   OCMAL duplicados con INDH: {len(duplicados_ocmal)}")

    todos_duplicados = {
        "ejatlas_vs_indh": duplicados_ejatlas,
        "ocmal_vs_indh": duplicados_ocmal
    }

    # Generar dataset integrado
    print("\n3. Generando dataset integrado...")

    nombres_ejatlas_duplicados = {d["nombre_secundario"] for d in duplicados_ejatlas}
    nombres_ocmal_duplicados = {d["nombre_secundario"] for d in duplicados_ocmal}

    dataset = []

    # Agregar todos los de INDH
    for c in indh:
        dataset.append(c)

    # Agregar de EJAtlas solo los que no son duplicados
    ejatlas_unicos = 0
    for c in ejatlas:
        if c["nombre"] not in nombres_ejatlas_duplicados:
            dataset.append(c)
            ejatlas_unicos += 1

    # Agregar de OCMAL solo los que no son duplicados
    ocmal_unicos = 0
    for c in ocmal:
        if c["nombre"] not in nombres_ocmal_duplicados:
            dataset.append(c)
            ocmal_unicos += 1

    print(f"   Total conflictos únicos: {len(dataset)}")
    print(f"     - INDH: {len(indh)}")
    print(f"     - EJAtlas únicos: {ejatlas_unicos}")
    print(f"     - OCMAL únicos: {ocmal_unicos}")

    # Estadísticas
    print("\n4. Estadísticas del dataset integrado:")
    por_fuente = Counter(c["fuente"] for c in dataset)
    print(f"   Por fuente:")
    for fuente, n in por_fuente.most_common():
        print(f"     {fuente}: {n}")

    por_sector = Counter(c.get("sector", "Sin dato") for c in dataset if c.get("sector"))
    print(f"\n   Top 5 sectores:")
    for sector, n in por_sector.most_common(5):
        print(f"     {sector}: {n}")

    por_estado = Counter(c.get("estado", "") for c in dataset if c.get("estado"))
    print(f"\n   Estados del conflicto:")
    for estado, n in por_estado.most_common():
        print(f"     {estado}: {n}")

    # Guardar dataset
    output_file = DATOS_DIR / "conflictos_integrados.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    print(f"\n5. Dataset guardado: {output_file}")

    # Guardar duplicados identificados
    dup_file = DATOS_DIR / "duplicados_identificados.json"
    with open(dup_file, "w", encoding="utf-8") as f:
        json.dump(todos_duplicados, f, ensure_ascii=False, indent=2)
    print(f"   Duplicados guardados: {dup_file}")

    # Guardar resumen
    resumen = {
        "fecha_integracion": datetime.now().isoformat(),
        "fuentes": {
            "INDH": {
                "archivo": "indh_conflictos.json",
                "total": len(indh),
                "url": "https://mapaconflictos.indh.cl/"
            },
            "EJAtlas": {
                "archivo": "ejatlas_chile_filtrado.json",
                "total": len(ejatlas),
                "duplicados": len(duplicados_ejatlas),
                "unicos": ejatlas_unicos,
                "url": "https://ejatlas.org/country/chile"
            },
            "OCMAL": {
                "archivo": "ocmal_chile.json",
                "total": len(ocmal),
                "duplicados": len(duplicados_ocmal),
                "unicos": ocmal_unicos,
                "url": "https://mapa.conflictosmineros.net/"
            }
        },
        "notas": {
            "OLCA": "No tiene base estructurada, solo documentación cualitativa (olca.cl)",
            "ACLED": "Requiere API key, acceso gratuito académico en acleddata.com"
        },
        "integracion": {
            "total_conflictos_unicos": len(dataset),
            "por_fuente": dict(por_fuente)
        },
        "estadisticas": {
            "por_estado": dict(por_estado),
            "por_sector": dict(por_sector.most_common(10))
        }
    }

    resumen_file = DATOS_DIR / "resumen_integracion.json"
    with open(resumen_file, "w", encoding="utf-8") as f:
        json.dump(resumen, f, ensure_ascii=False, indent=2)
    print(f"   Resumen guardado: {resumen_file}")

    print("\n" + "=" * 60)
    print("INTEGRACIÓN COMPLETADA")
    print("=" * 60)

    return dataset


if __name__ == "__main__":
    main()
