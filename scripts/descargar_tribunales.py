"""
Descargador de los 3 Tribunales Ambientales de Chile.

Uso:
    python scripts/descargar_tribunales.py [1|2|3|todos]

    1     - Solo 1er Tribunal (Antofagasta)
    2     - Solo 2do Tribunal (Santiago)
    3     - Solo 3er Tribunal (Valdivia)
    todos - Los 3 tribunales (default)
"""

import csv
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote
from typing import Dict, List, Set
from datetime import datetime
from collections import Counter

import requests
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

# -----------------------------
# Configuracion
# -----------------------------
BASE_DIR = Path(__file__).parent.parent
OUT_DIR = BASE_DIR / "corpus" / "descarga_completa"

SLEEP_SECONDS = 0.3
TIMEOUT = 60

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "es-CL,es;q=0.9,en;q=0.8",
}

# Configuracion de tribunales
TRIBUNALES = {
    "1TA": {
        "nombre": "1er Tribunal Ambiental (Antofagasta)",
        "base_url": "https://www.1ta.cl",
        "paginas": [
            ("sentencias", "/sentencias/"),
            ("jurisprudencia", "/jurisprudencia/"),
            ("publicaciones", "/publicaciones/"),
            ("anuarios", "/anuario/"),
            ("actas", "/actas/"),
        ],
    },
    "2TA": {
        "nombre": "2do Tribunal Ambiental (Santiago)",
        "base_url": "https://tribunalambiental.cl",
        "paginas": [
            ("sentencias", "/sentencias-e-informes/sentencias/"),
            ("informes_derecho", "/sentencias-e-informes/informes-de-derecho/"),
            ("anuarios", "/informacion-institucional/sobre-el-tribunal-ambiental/anuario/"),
            ("informes_visitadores", "/informes-de-los-ministrosas-visitadores-de-la-corte-suprema/"),
            ("actas", "/actas/"),
        ],
    },
    "3TA": {
        "nombre": "3er Tribunal Ambiental (Valdivia)",
        "base_url": "https://3ta.cl",
        "paginas": [
            ("sentencias", "/sentencias/"),
            ("publicaciones", "/publicaciones/"),
            ("anuarios", "/anuario/"),
            ("jurisprudencia", "/jurisprudencia/"),
        ],
    },
}

EXTENSIONES_DESCARGA = ['.pdf', '.doc', '.docx', '.xls', '.xlsx']


# -----------------------------
# Helpers
# -----------------------------
def log(msg: str):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}")


def sanitize_filename(name: str) -> str:
    name = unquote(name)
    name = name.strip().replace("\n", " ").replace("\r", " ")
    name = re.sub(r"[^\w\-.() \[\]]+", "_", name, flags=re.UNICODE)
    name = re.sub(r"\s+", " ", name).strip()
    if len(name) > 160:
        base, ext = os.path.splitext(name)
        name = base[:140] + ext
    return name


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    root = path.stem
    ext = path.suffix
    i = 2
    while True:
        cand = path.parent / f"{root}_{i}{ext}"
        if not cand.exists():
            return cand
        i += 1


def get_extension(url: str) -> str:
    path = urlparse(url).path.lower()
    for ext in EXTENSIONES_DESCARGA:
        if path.endswith(ext):
            return ext
    return ""


# -----------------------------
# Descarga
# -----------------------------
def extraer_enlaces_documentos(session: requests.Session, url: str) -> List[Dict]:
    """Extrae todos los enlaces a documentos de una pagina."""
    documentos = []
    try:
        r = session.get(url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        for a in soup.find_all("a", href=True):
            href = a.get("href", "").strip()
            if not href:
                continue

            abs_url = urljoin(url, href)
            ext = get_extension(abs_url)

            if ext:
                texto = a.get_text(strip=True)[:200]
                documentos.append({
                    "url": abs_url,
                    "extension": ext,
                    "texto_enlace": texto,
                })
    except Exception as e:
        log(f"  Error en {url}: {e}")

    return documentos


def descargar_documento(session: requests.Session, url: str, out_dir: Path) -> Dict:
    """Descarga un documento."""
    rec = {
        "url": url,
        "status": "",
        "archivo": "",
        "bytes": 0,
        "error": "",
    }

    try:
        with session.get(url, headers=HEADERS, timeout=TIMEOUT, stream=True, allow_redirects=True) as r:
            rec["status"] = str(r.status_code)

            if r.status_code != 200:
                rec["error"] = f"HTTP {r.status_code}"
                return rec

            fname = unquote(urlparse(r.url).path.split("/")[-1])
            fname = sanitize_filename(fname)

            if not fname:
                fname = f"documento_{hashlib.sha1(url.encode()).hexdigest()[:8]}"

            ext = get_extension(url)
            if ext and not fname.lower().endswith(ext):
                fname += ext

            fpath = unique_path(out_dir / fname)
            tmp = fpath.with_suffix(".part")

            total = 0
            with open(tmp, "wb") as f:
                for chunk in r.iter_content(chunk_size=256*1024):
                    if chunk:
                        f.write(chunk)
                        total += len(chunk)

            tmp.rename(fpath)
            rec["archivo"] = str(fpath.name)
            rec["bytes"] = total

    except Exception as e:
        rec["error"] = str(e)[:200]

    return rec


def descargar_desde_api(session: requests.Session, base_url: str, out_dir: Path, tribunal_id: str) -> List[Dict]:
    """Descarga documentos desde la API de WordPress."""
    log(f"  Obteniendo documentos desde API...")

    documentos = []
    page = 1

    while True:
        try:
            url = f"{base_url}/wp-json/wp/v2/media?per_page=100&page={page}"
            r = session.get(url, headers=HEADERS, timeout=TIMEOUT)

            if r.status_code != 200:
                break

            items = r.json()
            if not items:
                break

            for item in items:
                mime = item.get("mime_type", "")
                source = item.get("source_url", "")

                if any(t in mime for t in ["pdf", "word", "document", "excel"]):
                    documentos.append({
                        "url": source,
                        "titulo": item.get("title", {}).get("rendered", ""),
                        "fecha": item.get("date", ""),
                        "mime": mime,
                    })

            if page % 10 == 0:
                log(f"    Pagina {page}: {len(documentos)} documentos")
            page += 1
            time.sleep(SLEEP_SECONDS)

        except Exception as e:
            log(f"    Error en pagina {page}: {e}")
            break

    log(f"    Total documentos en API: {len(documentos)}")
    return documentos


def procesar_tribunal(tribunal_id: str, session: requests.Session):
    """Procesa un tribunal completo."""
    config = TRIBUNALES[tribunal_id]
    log("")
    log("=" * 60)
    log(f"{config['nombre']}")
    log("=" * 60)

    # Crear directorio
    tribunal_dir = OUT_DIR / "documentos" / tribunal_id.lower()
    tribunal_dir.mkdir(parents=True, exist_ok=True)

    datos_dir = OUT_DIR / "datos"
    datos_dir.mkdir(parents=True, exist_ok=True)

    stats = {
        "tribunal": tribunal_id,
        "nombre": config["nombre"],
        "documentos_descargados": 0,
        "documentos_fallidos": 0,
        "bytes_totales": 0,
        "por_categoria": {},
        "por_extension": Counter(),
    }

    manifest = []
    urls_descargadas = set()

    # Fase 1: Descargar desde paginas web
    log("")
    log("Fase 1: Escaneando paginas web...")

    todos_docs = []
    for categoria, path in config["paginas"]:
        url = config["base_url"] + path
        log(f"  {categoria}: {url}")

        docs = extraer_enlaces_documentos(session, url)
        for d in docs:
            d["categoria"] = categoria
        todos_docs.extend(docs)
        log(f"    Encontrados: {len(docs)} documentos")
        time.sleep(SLEEP_SECONDS)

    # Deduplicar
    docs_unicos = []
    for d in todos_docs:
        if d["url"] not in urls_descargadas:
            urls_descargadas.add(d["url"])
            docs_unicos.append(d)

    log(f"  Total unicos: {len(docs_unicos)}")

    # Descargar
    log("")
    log("Descargando documentos de paginas...")
    for i, doc in enumerate(docs_unicos, 1):
        cat_dir = tribunal_dir / doc["categoria"]
        cat_dir.mkdir(exist_ok=True)

        rec = descargar_documento(session, doc["url"], cat_dir)
        rec["categoria"] = doc["categoria"]
        manifest.append(rec)

        if rec["archivo"]:
            stats["documentos_descargados"] += 1
            stats["bytes_totales"] += rec["bytes"]
            stats["por_extension"][get_extension(doc["url"])] += 1
            stats["por_categoria"][doc["categoria"]] = stats["por_categoria"].get(doc["categoria"], 0) + 1
        else:
            stats["documentos_fallidos"] += 1

        if i % 20 == 0 or i == len(docs_unicos):
            log(f"  [{i}/{len(docs_unicos)}] OK: {stats['documentos_descargados']}, FAIL: {stats['documentos_fallidos']}")

        time.sleep(SLEEP_SECONDS)

    # Fase 2: Descargar desde API
    log("")
    log("Fase 2: Documentos adicionales desde API...")

    api_dir = tribunal_dir / "api_medios"
    api_dir.mkdir(exist_ok=True)

    docs_api = descargar_desde_api(session, config["base_url"], api_dir, tribunal_id)

    # Filtrar ya descargados
    docs_api_nuevos = [d for d in docs_api if d["url"] not in urls_descargadas]
    log(f"  Documentos nuevos: {len(docs_api_nuevos)}")

    for i, doc in enumerate(docs_api_nuevos, 1):
        rec = descargar_documento(session, doc["url"], api_dir)
        rec["categoria"] = "api_medios"
        manifest.append(rec)

        if rec["archivo"]:
            stats["documentos_descargados"] += 1
            stats["bytes_totales"] += rec["bytes"]
        else:
            stats["documentos_fallidos"] += 1

        if i % 20 == 0 or i == len(docs_api_nuevos):
            log(f"  [{i}/{len(docs_api_nuevos)}] OK: {stats['documentos_descargados']}")

        time.sleep(SLEEP_SECONDS)

    # Guardar manifest
    manifest_path = datos_dir / f"manifest_{tribunal_id.lower()}.csv"
    with open(manifest_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["url", "categoria", "status", "archivo", "bytes", "error"])
        writer.writeheader()
        writer.writerows(manifest)

    # Guardar stats
    stats["por_extension"] = dict(stats["por_extension"])
    stats_path = datos_dir / f"estadisticas_{tribunal_id.lower()}.json"
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    log("")
    log(f"Completado {tribunal_id}:")
    log(f"  Descargados: {stats['documentos_descargados']}")
    log(f"  Fallidos: {stats['documentos_fallidos']}")
    log(f"  Tamano: {stats['bytes_totales']/1024/1024:.1f} MB")

    return stats


def main():
    # Parsear argumentos
    arg = sys.argv[1] if len(sys.argv) > 1 else "todos"

    if arg == "1":
        tribunales = ["1TA"]
    elif arg == "2":
        tribunales = ["2TA"]
    elif arg == "3":
        tribunales = ["3TA"]
    elif arg == "todos":
        tribunales = ["1TA", "2TA", "3TA"]
    else:
        print("Uso: python scripts/descargar_tribunales.py [1|2|3|todos]")
        sys.exit(1)

    log("=" * 60)
    log("DESCARGA DE TRIBUNALES AMBIENTALES DE CHILE")
    log("=" * 60)
    log(f"Tribunales a procesar: {', '.join(tribunales)}")

    # Crear directorios
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    all_stats = []

    with requests.Session() as session:
        for tribunal_id in tribunales:
            try:
                stats = procesar_tribunal(tribunal_id, session)
                all_stats.append(stats)
            except Exception as e:
                log(f"Error procesando {tribunal_id}: {e}")

    # Resumen final
    log("")
    log("=" * 60)
    log("RESUMEN FINAL")
    log("=" * 60)

    total_docs = sum(s["documentos_descargados"] for s in all_stats)
    total_bytes = sum(s["bytes_totales"] for s in all_stats)

    for s in all_stats:
        log(f"{s['tribunal']}: {s['documentos_descargados']} docs ({s['bytes_totales']/1024/1024:.1f} MB)")

    log("")
    log(f"TOTAL: {total_docs} documentos ({total_bytes/1024/1024:.1f} MB)")
    log(f"Ubicacion: {OUT_DIR}")


if __name__ == "__main__":
    main()
