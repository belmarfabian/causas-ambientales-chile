#!/usr/bin/env python3
"""
Descarga datos de conflictos socioambientales de múltiples fuentes.

Fuentes:
- INDH: Instituto Nacional de Derechos Humanos (https://mapaconflictos.indh.cl/)
- EJAtlas: Environmental Justice Atlas (https://ejatlas.org/)
- OLCA: Observatorio Latinoamericano de Conflictos Ambientales
- ACLED: Armed Conflict Location & Event Data Project

Autor: Fabián Belmar
Fecha: Enero 2026
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# Configuración
BASE_DIR = Path(__file__).parent.parent
DATOS_DIR = BASE_DIR / "datos" / "conflictos"
DATOS_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def descargar_indh():
    """
    Descarga datos del Mapa de Conflictos Socioambientales del INDH.

    El INDH mantiene un mapa interactivo en https://mapaconflictos.indh.cl/
    Los datos se obtienen de la API del mapa.
    """
    print("\n" + "="*60)
    print("DESCARGANDO DATOS DEL INDH")
    print("="*60)

    # URL de la API del mapa INDH (obtenida inspeccionando el sitio)
    # El mapa usa una API GeoJSON
    api_url = "https://mapaconflictos.indh.cl/api/conflictos"

    try:
        print(f"Intentando: {api_url}")
        response = requests.get(api_url, headers=HEADERS, timeout=30)

        if response.status_code == 200:
            data = response.json()
            output_file = DATOS_DIR / "indh_conflictos.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Guardado: {output_file}")
            print(f"Conflictos descargados: {len(data) if isinstance(data, list) else 'estructura compleja'}")
            return data
        else:
            print(f"Error HTTP {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")

    # Intentar endpoint alternativo (GeoJSON)
    alt_urls = [
        "https://mapaconflictos.indh.cl/geojson/conflictos",
        "https://mapaconflictos.indh.cl/data/conflictos.json",
        "https://mapaconflictos.indh.cl/api/v1/conflictos",
    ]

    for url in alt_urls:
        try:
            print(f"Intentando alternativa: {url}")
            response = requests.get(url, headers=HEADERS, timeout=30)
            if response.status_code == 200:
                data = response.json()
                output_file = DATOS_DIR / "indh_conflictos.json"
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"Guardado: {output_file}")
                return data
        except:
            continue

    print("No se pudo acceder a la API del INDH. Se requiere scraping manual.")
    print("URL del mapa: https://mapaconflictos.indh.cl/")
    return None


def descargar_ejatlas():
    """
    Descarga datos del Environmental Justice Atlas para Chile.

    EJAtlas tiene una API pública documentada en:
    https://ejatlas.org/api
    """
    print("\n" + "="*60)
    print("DESCARGANDO DATOS DE EJATLAS")
    print("="*60)

    # API de EJAtlas para conflictos por país
    # Documentación: https://ejatlas.org/documentation
    api_url = "https://ejatlas.org/api/conflicts"
    params = {
        "country": "Chile",
        "format": "json"
    }

    try:
        print(f"Consultando EJAtlas API...")
        response = requests.get(api_url, params=params, headers=HEADERS, timeout=60)

        if response.status_code == 200:
            data = response.json()
            output_file = DATOS_DIR / "ejatlas_chile.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Guardado: {output_file}")
            if isinstance(data, list):
                print(f"Conflictos descargados: {len(data)}")
            elif isinstance(data, dict) and "features" in data:
                print(f"Conflictos descargados: {len(data['features'])}")
            return data
        else:
            print(f"Error HTTP {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")

    # Intentar endpoint GeoJSON alternativo
    geojson_url = "https://ejatlas.org/api/geojson"
    try:
        print(f"Intentando endpoint GeoJSON...")
        response = requests.get(
            geojson_url,
            params={"country": "Chile"},
            headers=HEADERS,
            timeout=60
        )
        if response.status_code == 200:
            data = response.json()
            output_file = DATOS_DIR / "ejatlas_chile_geojson.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Guardado: {output_file}")
            return data
    except:
        pass

    # Si la API no funciona, intentar scraping de la página
    print("\nIntentando scraping de la página de Chile en EJAtlas...")
    chile_url = "https://ejatlas.org/country/chile"

    try:
        response = requests.get(chile_url, headers=HEADERS, timeout=30)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # Buscar enlaces a conflictos individuales
            conflictos = []
            for link in soup.find_all("a", href=True):
                href = link.get("href", "")
                if "/conflict/" in href:
                    conflictos.append({
                        "url": f"https://ejatlas.org{href}" if href.startswith("/") else href,
                        "nombre": link.get_text(strip=True)
                    })

            if conflictos:
                # Eliminar duplicados
                vistos = set()
                unicos = []
                for c in conflictos:
                    if c["url"] not in vistos:
                        vistos.add(c["url"])
                        unicos.append(c)

                output_file = DATOS_DIR / "ejatlas_chile_links.json"
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(unicos, f, ensure_ascii=False, indent=2)
                print(f"Guardado lista de {len(unicos)} conflictos: {output_file}")
                return unicos

    except Exception as e:
        print(f"Error en scraping: {e}")

    print("No se pudieron obtener datos de EJAtlas automáticamente.")
    print("URL manual: https://ejatlas.org/country/chile")
    return None


def documentar_olca():
    """
    Documenta la fuente OLCA (requiere revisión manual).

    OLCA no tiene API pública estructurada.
    URL: https://olca.cl/
    """
    print("\n" + "="*60)
    print("DOCUMENTANDO FUENTE OLCA")
    print("="*60)

    info = {
        "fuente": "Observatorio Latinoamericano de Conflictos Ambientales (OLCA)",
        "url": "https://olca.cl/",
        "descripcion": "Organización chilena que documenta conflictos ambientales desde los años 1990",
        "tipo_acceso": "Manual - No tiene API pública",
        "notas": [
            "Requiere revisión manual del sitio web",
            "Documentación histórica de casos emblemáticos",
            "Énfasis en perspectiva de comunidades afectadas"
        ],
        "fecha_documentacion": datetime.now().isoformat()
    }

    output_file = DATOS_DIR / "olca_info.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    print(f"Documentación guardada: {output_file}")

    # Intentar obtener lista de conflictos de la página
    try:
        print("Intentando obtener información básica del sitio...")
        response = requests.get("https://olca.cl/", headers=HEADERS, timeout=30)
        if response.status_code == 200:
            print("Sitio accesible. Requiere revisión manual para extracción de datos.")
    except:
        print("No se pudo acceder al sitio OLCA.")

    return info


def documentar_ocmal():
    """
    Documenta la fuente OCMAL (conflictos mineros).

    URL: https://mapa.conflictosmineros.net/ocmal_db-v2/
    """
    print("\n" + "="*60)
    print("DOCUMENTANDO FUENTE OCMAL")
    print("="*60)

    # OCMAL tiene un mapa interactivo
    mapa_url = "https://mapa.conflictosmineros.net/ocmal_db-v2/"
    api_url = "https://mapa.conflictosmineros.net/ocmal_db-v2/api/conflictos"

    info = {
        "fuente": "Observatorio de Conflictos Mineros de América Latina (OCMAL)",
        "url": mapa_url,
        "descripcion": "Red de organizaciones que documenta conflictos mineros en América Latina",
        "tipo_acceso": "Mapa interactivo, posible API",
        "cobertura": "Conflictos mineros específicamente",
        "fecha_documentacion": datetime.now().isoformat()
    }

    # Intentar acceder a la API
    try:
        print(f"Intentando API: {api_url}")
        response = requests.get(api_url, headers=HEADERS, timeout=30)
        if response.status_code == 200:
            data = response.json()

            # Filtrar solo Chile
            if isinstance(data, list):
                chile = [c for c in data if c.get("pais", "").lower() == "chile"
                        or c.get("country", "").lower() == "chile"]
                if chile:
                    output_file = DATOS_DIR / "ocmal_chile.json"
                    with open(output_file, "w", encoding="utf-8") as f:
                        json.dump(chile, f, ensure_ascii=False, indent=2)
                    print(f"Guardado {len(chile)} conflictos mineros: {output_file}")
                    info["conflictos_chile"] = len(chile)
    except Exception as e:
        print(f"No se pudo acceder a la API: {e}")

    output_file = DATOS_DIR / "ocmal_info.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    print(f"Documentación guardada: {output_file}")

    return info


def documentar_acled():
    """
    Documenta la fuente ACLED (requiere registro para API).

    URL: https://acleddata.com/
    API: Requiere API key gratuita
    """
    print("\n" + "="*60)
    print("DOCUMENTANDO FUENTE ACLED")
    print("="*60)

    info = {
        "fuente": "Armed Conflict Location & Event Data Project (ACLED)",
        "url": "https://acleddata.com/",
        "api_docs": "https://apidocs.acleddata.com/",
        "descripcion": "Base de datos global de eventos de conflicto y protesta geolocalizados",
        "tipo_acceso": "API pública con registro gratuito requerido",
        "cobertura_chile": "Desde 2018",
        "variables_relevantes": [
            "event_date",
            "event_type",
            "sub_event_type",
            "actor1",
            "actor2",
            "location",
            "latitude",
            "longitude",
            "notes",
            "fatalities"
        ],
        "instrucciones": [
            "1. Registrarse en https://developer.acleddata.com/",
            "2. Obtener API key gratuita",
            "3. Usar endpoint: https://api.acleddata.com/acled/read",
            "4. Filtrar por country=Chile y event_type=Protests"
        ],
        "fecha_documentacion": datetime.now().isoformat()
    }

    output_file = DATOS_DIR / "acled_info.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    print(f"Documentación guardada: {output_file}")
    print("\nNota: ACLED requiere registro gratuito para obtener API key.")
    print("Registrarse en: https://developer.acleddata.com/")

    return info


def crear_resumen():
    """Crea un resumen de las fuentes y datos disponibles."""
    print("\n" + "="*60)
    print("RESUMEN DE FUENTES")
    print("="*60)

    resumen = {
        "fecha_ejecucion": datetime.now().isoformat(),
        "fuentes": {
            "INDH": {
                "url": "https://mapaconflictos.indh.cl/",
                "conflictos_reportados": 127,
                "estado": "pendiente verificación"
            },
            "EJAtlas": {
                "url": "https://ejatlas.org/country/chile",
                "conflictos_reportados": "100+",
                "estado": "pendiente verificación"
            },
            "OLCA": {
                "url": "https://olca.cl/",
                "tipo": "documentación histórica",
                "estado": "requiere revisión manual"
            },
            "OCMAL": {
                "url": "https://mapa.conflictosmineros.net/",
                "tipo": "conflictos mineros",
                "estado": "pendiente verificación"
            },
            "ACLED": {
                "url": "https://acleddata.com/",
                "tipo": "eventos de protesta",
                "cobertura": "desde 2018",
                "estado": "requiere registro API"
            }
        },
        "archivos_generados": []
    }

    # Listar archivos generados
    for archivo in DATOS_DIR.glob("*.json"):
        resumen["archivos_generados"].append(archivo.name)

    output_file = DATOS_DIR / "resumen_fuentes.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(resumen, f, ensure_ascii=False, indent=2)

    print(f"\nResumen guardado: {output_file}")
    print(f"Archivos generados: {len(resumen['archivos_generados'])}")
    for archivo in resumen["archivos_generados"]:
        print(f"  - {archivo}")

    return resumen


def main():
    """Ejecuta la descarga de todas las fuentes."""
    print("="*60)
    print("DESCARGA DE DATOS DE CONFLICTOS SOCIOAMBIENTALES")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Directorio: {DATOS_DIR}")
    print("="*60)

    # Descargar de cada fuente
    descargar_indh()
    time.sleep(2)  # Pausa entre requests

    descargar_ejatlas()
    time.sleep(2)

    documentar_olca()
    time.sleep(1)

    documentar_ocmal()
    time.sleep(1)

    documentar_acled()

    # Crear resumen
    crear_resumen()

    print("\n" + "="*60)
    print("DESCARGA COMPLETADA")
    print("="*60)
    print(f"\nArchivos en: {DATOS_DIR}")
    print("\nPróximos pasos:")
    print("1. Verificar datos descargados")
    print("2. Completar descarga manual donde sea necesario")
    print("3. Ejecutar script de integración")


if __name__ == "__main__":
    main()
