#!/usr/bin/env python3
"""
Consolida conflictos con estructura de IDs maestros.

Estructura resultante:
- id_maestro: ID único del conflicto (basado en INDH cuando existe)
- fuente_principal: INDH, EJAtlas, o OCMAL (prioridad INDH)
- Columnas de fuentes secundarias cuando hay duplicados:
  - en_ejatlas, id_ejatlas, nombre_ejatlas
  - en_ocmal, id_ocmal, nombre_ocmal

Esto permite ver qué conflictos están documentados en múltiples fuentes.
"""

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import json
from pathlib import Path
from collections import Counter
import re

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


def cargar_fuentes_originales():
    """Carga las tres fuentes originales."""
    # INDH
    indh = []
    archivo_indh = DATOS_DIR / "indh_conflictos.json"
    if archivo_indh.exists():
        with open(archivo_indh, encoding="utf-8") as f:
            data = json.load(f)
        for c in data:
            marca = c.get("marcaMapa", {}) or {}
            region = c.get("region", {}) or {}
            sector = c.get("sectorProductivo", {}) or {}
            estado = c.get("estadoConflico", {}) or {}

            indh.append({
                "id": c.get("id"),
                "nombre": c.get("tituloConflicto", ""),
                "nombre_norm": normalizar_texto(c.get("tituloConflicto", "")),
                "descripcion": c.get("resumenConflicto", ""),
                "region": region.get("nombreRegion", "") if isinstance(region, dict) else "",
                "localidad": c.get("localidadConflicto", ""),
                "latitud": marca.get("latitud"),
                "longitud": marca.get("longitud"),
                "sector": sector.get("nombreSector", "") if isinstance(sector, dict) else "",
                "estado": estado.get("glosa", "") if isinstance(estado, dict) else "",
                "año_inicio": c.get("anyo"),
                "territorio_indigena": c.get("esTerritorioIndigena", False),
                "fecha_actualizacion": c.get("fechaActualizacionPublicacion"),
                "url": f"https://mapaconflictos.indh.cl/conflicto/{c.get('id')}"
            })

    # EJAtlas
    ejatlas = []
    archivo_ejatlas = DATOS_DIR / "ejatlas_chile_filtrado.json"
    if archivo_ejatlas.exists():
        with open(archivo_ejatlas, encoding="utf-8") as f:
            data = json.load(f)
        for c in data:
            ejatlas.append({
                "id": c.get("id"),
                "nombre": c.get("name", ""),
                "nombre_norm": normalizar_texto(c.get("name", "")),
                "descripcion": c.get("headline", ""),
                "slug": c.get("slug", ""),
                "url": f"https://ejatlas.org/conflict/{c.get('slug', '')}"
            })

    # OCMAL
    ocmal = []
    archivo_ocmal = DATOS_DIR / "ocmal_chile.json"
    if archivo_ocmal.exists():
        with open(archivo_ocmal, encoding="utf-8") as f:
            data = json.load(f)
        for c in data:
            ocmal.append({
                "id": c.get("id"),
                "nombre": c.get("nombre", ""),
                "nombre_norm": normalizar_texto(c.get("nombre", "")),
                "region": c.get("region", ""),
                "ubicacion": c.get("ubicacion", ""),
                "empresa": c.get("empresa", ""),
                "año_inicio": c.get("año_inicio"),
                "url": "https://mapa.conflictosmineros.net/ocmal_db-v2/"
            })

    return indh, ejatlas, ocmal


def cargar_duplicados():
    """Carga el archivo de duplicados identificados."""
    archivo = DATOS_DIR / "duplicados_identificados.json"
    if archivo.exists():
        with open(archivo, encoding="utf-8") as f:
            return json.load(f)
    return {"ejatlas_vs_indh": [], "ocmal_vs_indh": [], "ejatlas_vs_ocmal": []}


def limpiar_html(texto):
    """Limpia tags HTML y decodifica entidades."""
    from html import unescape
    if not texto:
        return ""
    texto = re.sub(r'<[^>]+>', ' ', texto)
    texto = unescape(texto)
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()


def detectar_categorias(texto, patrones):
    """Detecta categorías presentes en el texto."""
    texto_limpio = limpiar_html(texto).lower()
    categorias = []
    for categoria, lista_patrones in patrones.items():
        for patron in lista_patrones:
            if re.search(patron, texto_limpio, re.IGNORECASE):
                categorias.append(categoria)
                break
    return categorias


def categorizar_conflicto(nombre, descripcion):
    """Categoriza un conflicto basándose en nombre y descripción."""
    texto = (descripcion or "") + " " + (nombre or "")

    PATRONES_IMPACTO = {
        'agua': [r'agua', r'hídric[oa]', r'río', r'acuífer', r'napa', r'sequ[ií]a',
                 r'contaminación.*agua', r'vertimiento', r'RILES', r'descarga',
                 r'escasez.*agua', r'derechos de agua', r'caudal'],
        'aire': [r'aire', r'emisiones?', r'material particulado', r'MP2\.?5', r'MP10',
                 r'gases', r'humo', r'olor', r'polvo', r'atmósfer'],
        'suelo': [r'suelo', r'contaminación.*tierra', r'relave', r'residuos sólidos',
                  r'vertedero', r'relleno sanitario', r'erosión'],
        'salud': [r'salud', r'enfermedad', r'cáncer', r'intoxicación', r'mortalidad',
                  r'respiratori', r'dermatológic', r'neurológic', r'hospital'],
        'biodiversidad': [r'biodiversidad', r'flora', r'fauna', r'especie', r'ecosistema',
                          r'bosque', r'glaciar', r'humedal', r'área protegida', r'parque nacional']
    }
    PATRONES_ACTOR = {
        'indigena': [r'indígena', r'mapuche', r'aymara', r'atacameñ', r'diaguita',
                     r'quechua', r'colla', r'rapa ?nui', r'kawésqar', r'yagán',
                     r'comunidad.*ancestral', r'territorio.*ancestral', r'Convenio 169'],
        'pescador': [r'pescador', r'pesca artesanal', r'caleta', r'sindicato.*pesca',
                     r'marisca', r'borde costero'],
        'agricultor': [r'agricultor', r'campesino', r'pequeño.*agricult', r'APR',
                       r'agua potable rural', r'riego', r'cultivo', r'huerto'],
        'urbano': [r'vecin[oa]', r'junta de vecinos', r'poblador', r'habitante',
                   r'residente', r'barrio', r'población']
    }
    PATRONES_RESISTENCIA = {
        'judicial': [r'recurso de protección', r'recurso.*amparo', r'demanda', r'querella',
                     r'tribunal', r'corte.*apelaciones', r'corte.*suprema', r'litigio',
                     r'acción.*legal', r'defensor[ií]a'],
        'movilizacion': [r'protesta', r'marcha', r'manifestación', r'bloqueo', r'toma',
                         r'movilización', r'asamblea.*ciudadana', r'paro'],
        'mediatica': [r'denuncia.*pública', r'campaña', r'redes sociales', r'prensa',
                      r'medio.*comunicación', r'declaración.*pública'],
        'institucional': [r'participación ciudadana', r'observaciones.*ciudadana',
                          r'consulta.*indígena', r'SEIA', r'evaluación ambiental']
    }
    PATRONES_RESULTADO = {
        'paralizado': [r'paraliz', r'suspend', r'detenid', r'cancelad', r'rechazad',
                       r'desistimiento', r'abandon', r'no.*aprobad'],
        'aprobado': [r'aprobad', r'autoriza', r'RCA.*favorable', r'calificación.*favorable',
                     r'permiso', r'operación'],
        'en_litigio': [r'en.*tramitación', r'pendiente', r'espera.*fallo', r'proceso.*judicial']
    }

    return {
        'impactos': detectar_categorias(texto, PATRONES_IMPACTO),
        'actores': detectar_categorias(texto, PATRONES_ACTOR),
        'resistencias': detectar_categorias(texto, PATRONES_RESISTENCIA),
        'resultados': detectar_categorias(texto, PATRONES_RESULTADO)
    }


def inferir_categorias_faltantes(registro):
    """
    Infiere categorías para registros que no tienen datos.
    Aplica reglas heurísticas basadas en la fuente y el tipo de conflicto.
    """
    import copy
    reg = copy.deepcopy(registro)

    # OCMAL: todos son conflictos mineros, inferir impactos típicos
    if reg["fuente_principal"] == "OCMAL":
        if not reg["impactos"]:
            reg["impactos"] = ["agua", "suelo"]  # Típicos de minería
            reg["impactos_inferido"] = True
        if not reg["actores"]:
            # Revisar nombre para detectar comunidades
            nombre = (reg["nombre"] or "").lower()
            if any(x in nombre for x in ["mapuche", "aymara", "atacameñ", "diaguita", "colla"]):
                reg["actores"] = ["indigena"]
            else:
                reg["actores"] = ["urbano"]  # Default para comunidades afectadas
            reg["actores_inferido"] = True

    # EJAtlas: expandir patrones en inglés
    if reg["fuente_principal"] == "EJAtlas":
        desc = (reg.get("descripcion") or "").lower()
        nombre = (reg.get("nombre") or "").lower()
        texto = desc + " " + nombre

        if not reg["impactos"]:
            impactos = []
            if any(x in texto for x in ["water", "river", "aquifer", "hydro"]):
                impactos.append("agua")
            if any(x in texto for x in ["air", "emission", "pollution"]):
                impactos.append("aire")
            if any(x in texto for x in ["soil", "waste", "tailings", "mining"]):
                impactos.append("suelo")
            if any(x in texto for x in ["health", "disease", "cancer"]):
                impactos.append("salud")
            if any(x in texto for x in ["biodiversity", "species", "ecosystem", "forest"]):
                impactos.append("biodiversidad")
            if impactos:
                reg["impactos"] = impactos
                reg["impactos_inferido"] = True
            elif "mining" in texto or "mine" in texto:
                reg["impactos"] = ["agua", "suelo"]
                reg["impactos_inferido"] = True

        if not reg["actores"]:
            actores = []
            if any(x in texto for x in ["indigenous", "mapuche", "native", "ancestral"]):
                actores.append("indigena")
            if any(x in texto for x in ["fisher", "coastal", "artisanal"]):
                actores.append("pescador")
            if any(x in texto for x in ["farmer", "rural", "peasant", "agricultural"]):
                actores.append("agricultor")
            if any(x in texto for x in ["community", "resident", "neighbor", "local"]):
                actores.append("urbano")
            if actores:
                reg["actores"] = actores
                reg["actores_inferido"] = True

    return reg


def main():
    print("=" * 60)
    print("CONSOLIDACIÓN CON IDs MAESTROS")
    print("=" * 60)

    # Cargar fuentes
    indh, ejatlas, ocmal = cargar_fuentes_originales()
    duplicados = cargar_duplicados()

    print(f"\nFuentes cargadas:")
    print(f"  INDH: {len(indh)}")
    print(f"  EJAtlas: {len(ejatlas)}")
    print(f"  OCMAL: {len(ocmal)}")

    # Crear índices de nombres normalizados para EJAtlas y OCMAL
    ejatlas_por_nombre = {c["nombre"]: c for c in ejatlas}
    ocmal_por_nombre = {c["nombre"]: c for c in ocmal}

    # Crear mapeo de duplicados: nombre INDH -> info de fuente secundaria
    ejatlas_duplicados = {}  # nombre_indh -> info_ejatlas
    ocmal_duplicados = {}    # nombre_indh -> info_ocmal

    for dup in duplicados.get("ejatlas_vs_indh", []):
        nombre_indh = dup["nombre_principal"]
        nombre_ejatlas = dup["nombre_secundario"]
        if nombre_ejatlas in ejatlas_por_nombre:
            ejatlas_duplicados[nombre_indh] = ejatlas_por_nombre[nombre_ejatlas]

    for dup in duplicados.get("ocmal_vs_indh", []):
        nombre_indh = dup["nombre_principal"]
        nombre_ocmal = dup["nombre_secundario"]
        if nombre_ocmal in ocmal_por_nombre:
            ocmal_duplicados[nombre_indh] = ocmal_por_nombre[nombre_ocmal]

    # Duplicados EJAtlas vs OCMAL (para conflictos no en INDH)
    ejatlas_ocmal_duplicados = {}  # nombre_ejatlas -> info_ocmal
    for dup in duplicados.get("ejatlas_vs_ocmal", []):
        nombre_ejatlas = dup["nombre_principal"]
        nombre_ocmal = dup["nombre_secundario"]
        if nombre_ocmal in ocmal_por_nombre:
            ejatlas_ocmal_duplicados[nombre_ejatlas] = ocmal_por_nombre[nombre_ocmal]

    print(f"\nDuplicados mapeados:")
    print(f"  EJAtlas → INDH: {len(ejatlas_duplicados)}")
    print(f"  OCMAL → INDH: {len(ocmal_duplicados)}")
    print(f"  EJAtlas → OCMAL: {len(ejatlas_ocmal_duplicados)}")

    # Construir dataset consolidado
    dataset = []
    id_maestro = 1

    # 1. Agregar todos los INDH con info de duplicados
    nombres_ejatlas_usados = set()
    nombres_ocmal_usados = set()

    for c in indh:
        # Categorizar automáticamente
        cats = categorizar_conflicto(c["nombre"], c["descripcion"])

        registro = {
            "id_maestro": f"CONF-{id_maestro:04d}",
            "fuente_principal": "INDH",
            "id_indh": c["id"],
            "nombre": c["nombre"],
            "descripcion": c["descripcion"],
            "region": c["region"],
            "localidad": c["localidad"],
            "latitud": c["latitud"],
            "longitud": c["longitud"],
            "sector": c["sector"],
            "estado": c["estado"],
            "año_inicio": c["año_inicio"],
            "territorio_indigena": c["territorio_indigena"],
            "url_indh": c["url"],
            # Campos de duplicados
            "en_ejatlas": False,
            "id_ejatlas": None,
            "nombre_ejatlas": None,
            "url_ejatlas": None,
            "en_ocmal": False,
            "id_ocmal": None,
            "nombre_ocmal": None,
            "url_ocmal": None,
            # Categorías
            "impactos": cats.get("impactos", []),
            "actores": cats.get("actores", []),
            "resistencias": cats.get("resistencias", []),
            "resultados": cats.get("resultados", [])
        }

        # Verificar si está en EJAtlas
        if c["nombre"] in ejatlas_duplicados:
            info_ej = ejatlas_duplicados[c["nombre"]]
            registro["en_ejatlas"] = True
            registro["id_ejatlas"] = info_ej["id"]
            registro["nombre_ejatlas"] = info_ej["nombre"]
            registro["url_ejatlas"] = info_ej["url"]
            nombres_ejatlas_usados.add(info_ej["nombre"])

        # Verificar si está en OCMAL
        if c["nombre"] in ocmal_duplicados:
            info_oc = ocmal_duplicados[c["nombre"]]
            registro["en_ocmal"] = True
            registro["id_ocmal"] = info_oc["id"]
            registro["nombre_ocmal"] = info_oc["nombre"]
            registro["url_ocmal"] = info_oc["url"]
            nombres_ocmal_usados.add(info_oc["nombre"])

        dataset.append(registro)
        id_maestro += 1

    # 2. Agregar EJAtlas únicos (no duplicados de INDH)
    ejatlas_unicos = 0
    for c in ejatlas:
        if c["nombre"] not in nombres_ejatlas_usados:
            # Categorizar automáticamente
            cats = categorizar_conflicto(c["nombre"], c["descripcion"])

            registro = {
                "id_maestro": f"CONF-{id_maestro:04d}",
                "fuente_principal": "EJAtlas",
                "id_indh": None,
                "nombre": c["nombre"],
                "descripcion": c["descripcion"],
                "region": "",
                "localidad": "",
                "latitud": None,
                "longitud": None,
                "sector": "",
                "estado": "",
                "año_inicio": None,
                "territorio_indigena": None,
                "url_indh": None,
                "en_ejatlas": True,
                "id_ejatlas": c["id"],
                "nombre_ejatlas": c["nombre"],
                "url_ejatlas": c["url"],
                "en_ocmal": False,
                "id_ocmal": None,
                "nombre_ocmal": None,
                "url_ocmal": None,
                # Categorías
                "impactos": cats.get("impactos", []),
                "actores": cats.get("actores", []),
                "resistencias": cats.get("resistencias", []),
                "resultados": cats.get("resultados", [])
            }

            # Verificar si está en OCMAL (duplicado EJAtlas-OCMAL)
            if c["nombre"] in ejatlas_ocmal_duplicados:
                info_oc = ejatlas_ocmal_duplicados[c["nombre"]]
                registro["en_ocmal"] = True
                registro["id_ocmal"] = info_oc["id"]
                registro["nombre_ocmal"] = info_oc["nombre"]
                registro["url_ocmal"] = info_oc["url"]
                nombres_ocmal_usados.add(info_oc["nombre"])

            dataset.append(registro)
            id_maestro += 1
            ejatlas_unicos += 1

    # 3. Agregar OCMAL únicos (no duplicados)
    ocmal_unicos = 0
    for c in ocmal:
        if c["nombre"] not in nombres_ocmal_usados:
            # Categorizar automáticamente (OCMAL no tiene descripción)
            cats = categorizar_conflicto(c["nombre"], "")

            registro = {
                "id_maestro": f"CONF-{id_maestro:04d}",
                "fuente_principal": "OCMAL",
                "id_indh": None,
                "nombre": c["nombre"],
                "descripcion": "",
                "region": c.get("region", ""),
                "localidad": c.get("ubicacion", ""),
                "latitud": None,
                "longitud": None,
                "sector": "Minería",
                "estado": "",
                "año_inicio": c.get("año_inicio"),
                "territorio_indigena": None,
                "url_indh": None,
                "en_ejatlas": False,
                "id_ejatlas": None,
                "nombre_ejatlas": None,
                "url_ejatlas": None,
                "en_ocmal": True,
                "id_ocmal": c["id"],
                "nombre_ocmal": c["nombre"],
                "url_ocmal": c["url"],
                # Categorías
                "impactos": cats.get("impactos", []),
                "actores": cats.get("actores", []),
                "resistencias": cats.get("resistencias", []),
                "resultados": cats.get("resultados", [])
            }
            dataset.append(registro)
            id_maestro += 1
            ocmal_unicos += 1

    # Estadísticas
    print(f"\n" + "=" * 60)
    print("RESULTADOS")
    print("=" * 60)
    print(f"\nTotal conflictos únicos: {len(dataset)}")
    print(f"  - Base INDH: {len(indh)}")
    print(f"  - EJAtlas únicos: {ejatlas_unicos}")
    print(f"  - OCMAL únicos: {ocmal_unicos}")

    # Contar cuántos están en múltiples fuentes
    en_2_fuentes = sum(1 for d in dataset if (d["en_ejatlas"] and d["fuente_principal"] == "INDH") or
                                              (d["en_ocmal"] and d["fuente_principal"] == "INDH"))
    en_3_fuentes = sum(1 for d in dataset if d["en_ejatlas"] and d["en_ocmal"])

    # Contar EJAtlas-OCMAL (no en INDH)
    ejatlas_ocmal_sin_indh = sum(1 for d in dataset if d["en_ejatlas"] and d["en_ocmal"]
                                  and d["fuente_principal"] == "EJAtlas")

    print(f"\nCobertura cruzada:")
    print(f"  - En INDH + EJAtlas: {len(ejatlas_duplicados)}")
    print(f"  - En INDH + OCMAL: {len(ocmal_duplicados)}")
    print(f"  - En EJAtlas + OCMAL (no INDH): {ejatlas_ocmal_sin_indh}")
    print(f"  - En las 3 fuentes: {en_3_fuentes}")

    # ============================================================
    # GUARDAR DOS VERSIONES DEL DATASET
    # ============================================================

    # 1. VERSION BASE: solo categorización por regex (sin inferencias)
    output_base = DATOS_DIR / "conflictos_consolidados_ids.json"
    with open(output_base, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    print(f"\n[1] Dataset BASE guardado: {output_base}")

    # 2. VERSION COMPLETA: con categorías inferidas para registros sin datos
    dataset_completo = [inferir_categorias_faltantes(r) for r in dataset]

    output_completo = DATOS_DIR / "conflictos_consolidados_completo.json"
    with open(output_completo, "w", encoding="utf-8") as f:
        json.dump(dataset_completo, f, ensure_ascii=False, indent=2)
    print(f"[2] Dataset COMPLETO guardado: {output_completo}")

    # Estadísticas de inferencia
    inferidos_impactos = sum(1 for r in dataset_completo if r.get("impactos_inferido"))
    inferidos_actores = sum(1 for r in dataset_completo if r.get("actores_inferido"))
    print(f"\nInferencias aplicadas:")
    print(f"  - Impactos inferidos: {inferidos_impactos} registros")
    print(f"  - Actores inferidos: {inferidos_actores} registros")

    # Comparar cobertura
    def calcular_cobertura(ds, campo):
        con_datos = sum(1 for r in ds if r.get(campo))
        return con_datos / len(ds) * 100 if ds else 0

    print(f"\nCobertura de categorías:")
    print(f"  {'Campo':<15} {'Base':>10} {'Completo':>10}")
    print(f"  {'-'*35}")
    for campo in ["impactos", "actores", "resistencias", "resultados"]:
        cob_base = calcular_cobertura(dataset, campo)
        cob_comp = calcular_cobertura(dataset_completo, campo)
        print(f"  {campo:<15} {cob_base:>9.1f}% {cob_comp:>9.1f}%")

    # Guardar CSVs para ambas versiones
    import csv

    columnas = [
        "id_maestro", "fuente_principal", "nombre", "region", "sector", "estado",
        "año_inicio", "en_ejatlas", "nombre_ejatlas", "en_ocmal", "nombre_ocmal"
    ]

    csv_base = DATOS_DIR / "conflictos_consolidados_ids.csv"
    with open(csv_base, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columnas, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(dataset)
    print(f"\nCSV BASE: {csv_base}")

    csv_completo = DATOS_DIR / "conflictos_consolidados_completo.csv"
    with open(csv_completo, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columnas, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(dataset_completo)
    print(f"CSV COMPLETO: {csv_completo}")

    # Mostrar ejemplos de conflictos en múltiples fuentes
    print(f"\n" + "=" * 60)
    print("EJEMPLOS DE CONFLICTOS EN MÚLTIPLES FUENTES")
    print("=" * 60)

    multi_fuente = [d for d in dataset if d["en_ejatlas"] or d["en_ocmal"]]
    for d in multi_fuente[:10]:
        fuentes = ["INDH"] if d["fuente_principal"] == "INDH" else []
        if d["en_ejatlas"]:
            fuentes.append("EJAtlas")
        if d["en_ocmal"]:
            fuentes.append("OCMAL")
        print(f"\n{d['id_maestro']}: {d['nombre'][:50]}...")
        print(f"  Fuentes: {', '.join(fuentes)}")
        if d["nombre_ejatlas"]:
            print(f"  EJAtlas: {d['nombre_ejatlas'][:50]}...")
        if d["nombre_ocmal"]:
            print(f"  OCMAL: {d['nombre_ocmal'][:50]}...")

    return dataset


if __name__ == "__main__":
    main()
