"""
Descargador COMPLETO del Tribunal Ambiental de Chile.
Descarga todos los documentos y extrae metadatos para análisis.

Uso:
    python scripts/descargar_todo.py
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
from typing import Dict, List, Set, Any
from datetime import datetime

import requests
from bs4 import BeautifulSoup

# Configurar encoding para Windows
sys.stdout.reconfigure(encoding='utf-8')

# -----------------------------
# Configuracion
# -----------------------------
BASE_DIR = Path(__file__).parent.parent
OUT_DIR = BASE_DIR / "corpus" / "descarga_completa"
DOCS_DIR = OUT_DIR / "documentos"
DATA_DIR = OUT_DIR / "datos"

BASE_URL = "https://tribunalambiental.cl/"
API_URL = "https://tribunalambiental.cl/wp-json/wp/v2/"

SLEEP_SECONDS = 0.3
TIMEOUT = 60

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "es-CL,es;q=0.9,en;q=0.8",
}

# Paginas con documentos
PAGINAS_DOCUMENTOS = [
    ("sentencias", "https://tribunalambiental.cl/sentencias-e-informes/sentencias/"),
    ("informes_derecho", "https://tribunalambiental.cl/sentencias-e-informes/informes-de-derecho/"),
    ("informes_tecnicos", "https://tribunalambiental.cl/sentencias-e-informes/informes-tecnicos/"),
    ("actas", "https://tribunalambiental.cl/actas/"),
    ("anuarios", "https://tribunalambiental.cl/informacion-institucional/sobre-el-tribunal-ambiental/anuario/"),
    ("informes_visitadores", "https://tribunalambiental.cl/informes-de-los-ministrosas-visitadores-de-la-corte-suprema/"),
    ("estudios_derecho", "https://tribunalambiental.cl/estudios-derecho-ambiental-vol-1/"),
    ("estudios_jurisprudencia", "https://tribunalambiental.cl/estudios-jurisprudencia-ambiental/"),
    ("amicus_curiae", "https://tribunalambiental.cl/opinion-de-amicus-curiae/"),
    ("actas_instalacion", "https://tribunalambiental.cl/actas-de-instalacion/"),
    ("transparencia_compras", "https://tribunalambiental.cl/transparencia/compras-y-adquisiciones/"),
]

# Extensiones a descargar
EXTENSIONES_DESCARGA = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']


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
    """Obtiene la extension del archivo de la URL."""
    path = urlparse(url).path.lower()
    for ext in EXTENSIONES_DESCARGA:
        if path.endswith(ext):
            return ext
    return ""


# -----------------------------
# Descarga de documentos
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
                # Obtener texto del enlace como contexto
                texto = a.get_text(strip=True)[:200]
                documentos.append({
                    "url": abs_url,
                    "extension": ext,
                    "texto_enlace": texto,
                    "pagina_origen": url,
                })
    except Exception as e:
        log(f"  Error extrayendo de {url}: {e}")

    return documentos


def descargar_documento(session: requests.Session, url: str, out_dir: Path, categoria: str) -> Dict:
    """Descarga un documento y retorna informacion."""
    rec = {
        "url": url,
        "categoria": categoria,
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

            # Obtener nombre del archivo
            fname = unquote(urlparse(r.url).path.split("/")[-1])
            fname = sanitize_filename(fname)

            if not fname:
                fname = f"documento_{hashlib.sha1(url.encode()).hexdigest()[:8]}"

            # Agregar extension si no tiene
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


def descargar_desde_api_medios(session: requests.Session, out_dir: Path) -> List[Dict]:
    """Descarga documentos desde la API de medios de WordPress."""
    log("Obteniendo lista de medios desde API WordPress...")

    documentos = []
    page = 1

    while True:
        try:
            url = f"{API_URL}media?per_page=100&page={page}"
            r = session.get(url, headers=HEADERS, timeout=TIMEOUT)

            if r.status_code != 200:
                break

            items = r.json()
            if not items:
                break

            for item in items:
                mime = item.get("mime_type", "")
                source = item.get("source_url", "")

                # Solo documentos, no imagenes
                if any(t in mime for t in ["pdf", "word", "document", "excel", "powerpoint"]):
                    documentos.append({
                        "url": source,
                        "titulo": item.get("title", {}).get("rendered", ""),
                        "fecha": item.get("date", ""),
                        "mime": mime,
                    })

            log(f"  Pagina {page}: {len(items)} items, {len(documentos)} documentos")
            page += 1
            time.sleep(SLEEP_SECONDS)

        except Exception as e:
            log(f"  Error en pagina {page}: {e}")
            break

    return documentos


# -----------------------------
# Extraccion de metadatos
# -----------------------------
def extraer_metadatos_causas(session: requests.Session) -> List[Dict]:
    """Extrae metadatos estructurados de todas las causas."""
    log("Extrayendo metadatos de causas...")

    url = "https://tribunalambiental.cl/sentencias-e-informes/sentencias/"
    r = session.get(url, headers=HEADERS, timeout=TIMEOUT)
    soup = BeautifulSoup(r.text, "html.parser")

    causas = []
    tables = soup.find_all("table")
    tipos = ["Reclamacion", "Demanda", "Consulta", "Solicitud"]

    for table, tipo in zip(tables, tipos):
        for row in table.find_all("tr")[1:]:  # Skip header
            cols = row.find_all("td")
            if len(cols) >= 2:
                rol = cols[0].get_text(strip=True)
                descripcion = cols[1].get_text(strip=True)

                # Extraer PDFs asociados
                pdfs = [a.get("href") for a in row.find_all("a", href=True)
                       if ".pdf" in a.get("href", "").lower()]

                # Parsear descripcion para extraer partes
                partes = {"demandante": "", "demandado": ""}
                match = re.search(r"(.+?)\s+(?:en contra de|con)\s+(.+?)(?:\.|$)",
                                descripcion, re.IGNORECASE)
                if match:
                    partes["demandante"] = match.group(1).strip()
                    partes["demandado"] = match.group(2).strip()

                # Extraer ano del ROL
                ano_match = re.search(r"20\d{2}", rol)
                ano = ano_match.group(0) if ano_match else ""

                # Extraer region si se menciona
                region = ""
                for r_name in ["Metropolitana", "Maule", "O'Higgins", "Atacama",
                              "Antofagasta", "Valparaiso", "Coquimbo", "Biobio",
                              "Araucania", "Los Lagos", "Los Rios", "Aysen",
                              "Magallanes", "Arica", "Tarapaca"]:
                    if r_name.lower() in descripcion.lower():
                        region = r_name
                        break

                causas.append({
                    "rol": rol,
                    "tipo": tipo,
                    "descripcion": descripcion,
                    "demandante": partes["demandante"],
                    "demandado": partes["demandado"],
                    "ano": ano,
                    "region": region,
                    "pdfs": pdfs,
                    "num_pdfs": len(pdfs),
                })

    log(f"  Extraidas {len(causas)} causas")
    return causas


def extraer_posts_wordpress(session: requests.Session) -> List[Dict]:
    """Extrae metadatos de todos los posts de WordPress."""
    log("Extrayendo posts de WordPress API...")

    posts = []
    page = 1

    # Primero obtener total
    r = session.get(f"{API_URL}posts?per_page=1", headers=HEADERS, timeout=TIMEOUT)
    total = int(r.headers.get("X-WP-Total", 0))
    log(f"  Total posts: {total}")

    while True:
        try:
            url = f"{API_URL}posts?per_page=100&page={page}"
            r = session.get(url, headers=HEADERS, timeout=TIMEOUT)

            if r.status_code != 200:
                break

            items = r.json()
            if not items:
                break

            for item in items:
                posts.append({
                    "id": item.get("id"),
                    "fecha": item.get("date", "")[:10],
                    "titulo": item.get("title", {}).get("rendered", ""),
                    "slug": item.get("slug", ""),
                    "link": item.get("link", ""),
                    "categorias": item.get("categories", []),
                    "tags": item.get("tags", []),
                    "extracto": BeautifulSoup(
                        item.get("excerpt", {}).get("rendered", ""),
                        "html.parser"
                    ).get_text(strip=True)[:500],
                })

            log(f"  Pagina {page}: {len(posts)}/{total} posts")
            page += 1
            time.sleep(SLEEP_SECONDS)

        except Exception as e:
            log(f"  Error en pagina {page}: {e}")
            break

    return posts


def extraer_categorias_tags(session: requests.Session) -> Dict:
    """Extrae categorias y tags de WordPress."""
    log("Extrayendo categorias y tags...")

    resultado = {"categorias": [], "tags": []}

    # Categorias
    r = session.get(f"{API_URL}categories?per_page=100", headers=HEADERS, timeout=TIMEOUT)
    if r.status_code == 200:
        for cat in r.json():
            resultado["categorias"].append({
                "id": cat.get("id"),
                "nombre": cat.get("name"),
                "slug": cat.get("slug"),
                "count": cat.get("count"),
            })

    # Tags
    r = session.get(f"{API_URL}tags?per_page=100", headers=HEADERS, timeout=TIMEOUT)
    if r.status_code == 200:
        for tag in r.json():
            resultado["tags"].append({
                "id": tag.get("id"),
                "nombre": tag.get("name"),
                "slug": tag.get("slug"),
                "count": tag.get("count"),
            })

    return resultado


# -----------------------------
# Main
# -----------------------------
def main():
    log("=" * 60)
    log("DESCARGA COMPLETA - TRIBUNAL AMBIENTAL DE CHILE")
    log("=" * 60)

    # Crear directorios
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Crear subdirectorios por categoria
    for cat, _ in PAGINAS_DOCUMENTOS:
        (DOCS_DIR / cat).mkdir(exist_ok=True)
    (DOCS_DIR / "api_medios").mkdir(exist_ok=True)

    stats = {
        "documentos_descargados": 0,
        "documentos_fallidos": 0,
        "bytes_totales": 0,
        "por_categoria": {},
        "por_extension": {},
    }

    manifest = []

    with requests.Session() as session:
        # =========================================
        # FASE 1: Descargar documentos de paginas
        # =========================================
        log("")
        log("FASE 1: Descargando documentos de paginas web")
        log("-" * 40)

        todos_docs = []
        for categoria, url in PAGINAS_DOCUMENTOS:
            log(f"Escaneando: {categoria}")
            docs = extraer_enlaces_documentos(session, url)
            for d in docs:
                d["categoria"] = categoria
            todos_docs.extend(docs)
            log(f"  Encontrados: {len(docs)} documentos")
            time.sleep(SLEEP_SECONDS)

        # Deduplicar por URL
        urls_vistas = set()
        docs_unicos = []
        for d in todos_docs:
            if d["url"] not in urls_vistas:
                urls_vistas.add(d["url"])
                docs_unicos.append(d)

        log(f"Total documentos unicos: {len(docs_unicos)}")

        # Descargar
        log("")
        log("Descargando documentos...")
        for i, doc in enumerate(docs_unicos, 1):
            cat_dir = DOCS_DIR / doc["categoria"]
            rec = descargar_documento(session, doc["url"], cat_dir, doc["categoria"])
            manifest.append(rec)

            if rec["archivo"]:
                stats["documentos_descargados"] += 1
                stats["bytes_totales"] += rec["bytes"]

                ext = get_extension(doc["url"])
                stats["por_extension"][ext] = stats["por_extension"].get(ext, 0) + 1
                stats["por_categoria"][doc["categoria"]] = stats["por_categoria"].get(doc["categoria"], 0) + 1
            else:
                stats["documentos_fallidos"] += 1

            if i % 20 == 0 or i == len(docs_unicos):
                log(f"  [{i}/{len(docs_unicos)}] OK: {stats['documentos_descargados']}, FAIL: {stats['documentos_fallidos']}")

            time.sleep(SLEEP_SECONDS)

        # =========================================
        # FASE 2: Documentos de API de medios
        # =========================================
        log("")
        log("FASE 2: Documentos adicionales de API WordPress")
        log("-" * 40)

        docs_api = descargar_desde_api_medios(session, DOCS_DIR / "api_medios")

        # Filtrar los que no se descargaron ya
        docs_api_nuevos = [d for d in docs_api if d["url"] not in urls_vistas]
        log(f"Documentos nuevos en API: {len(docs_api_nuevos)}")

        for i, doc in enumerate(docs_api_nuevos, 1):
            rec = descargar_documento(session, doc["url"], DOCS_DIR / "api_medios", "api_medios")
            manifest.append(rec)

            if rec["archivo"]:
                stats["documentos_descargados"] += 1
                stats["bytes_totales"] += rec["bytes"]
            else:
                stats["documentos_fallidos"] += 1

            if i % 20 == 0 or i == len(docs_api_nuevos):
                log(f"  [{i}/{len(docs_api_nuevos)}] OK: {stats['documentos_descargados']}")

            time.sleep(SLEEP_SECONDS)

        # =========================================
        # FASE 3: Extraer metadatos
        # =========================================
        log("")
        log("FASE 3: Extrayendo metadatos estructurados")
        log("-" * 40)

        # Metadatos de causas
        causas = extraer_metadatos_causas(session)

        # Posts de WordPress
        posts = extraer_posts_wordpress(session)

        # Categorias y tags
        taxonomias = extraer_categorias_tags(session)

    # =========================================
    # FASE 4: Guardar datos
    # =========================================
    log("")
    log("FASE 4: Guardando datos")
    log("-" * 40)

    # Manifest de descargas
    manifest_path = DATA_DIR / "manifest_descarga.csv"
    with open(manifest_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["url", "categoria", "status", "archivo", "bytes", "error"])
        writer.writeheader()
        writer.writerows(manifest)
    log(f"  Manifest: {manifest_path}")

    # Causas CSV
    causas_csv = DATA_DIR / "causas.csv"
    with open(causas_csv, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["rol", "tipo", "ano", "region", "demandante", "demandado", "num_pdfs", "descripcion"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for c in causas:
            writer.writerow({k: c.get(k, "") for k in fieldnames})
    log(f"  Causas CSV: {causas_csv}")

    # Causas JSON (completo con PDFs)
    causas_json = DATA_DIR / "causas.json"
    with open(causas_json, "w", encoding="utf-8") as f:
        json.dump(causas, f, ensure_ascii=False, indent=2)
    log(f"  Causas JSON: {causas_json}")

    # Posts CSV
    posts_csv = DATA_DIR / "posts.csv"
    with open(posts_csv, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["id", "fecha", "titulo", "slug", "link", "extracto"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in posts:
            writer.writerow({k: p.get(k, "") for k in fieldnames})
    log(f"  Posts CSV: {posts_csv}")

    # Posts JSON (completo)
    posts_json = DATA_DIR / "posts.json"
    with open(posts_json, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    log(f"  Posts JSON: {posts_json}")

    # Taxonomias JSON
    tax_json = DATA_DIR / "taxonomias.json"
    with open(tax_json, "w", encoding="utf-8") as f:
        json.dump(taxonomias, f, ensure_ascii=False, indent=2)
    log(f"  Taxonomias: {tax_json}")

    # Estadisticas
    stats_json = DATA_DIR / "estadisticas.json"
    stats["causas_totales"] = len(causas)
    stats["posts_totales"] = len(posts)
    with open(stats_json, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    log(f"  Estadisticas: {stats_json}")

    # =========================================
    # Resumen final
    # =========================================
    log("")
    log("=" * 60)
    log("RESUMEN FINAL")
    log("=" * 60)
    log(f"Documentos descargados: {stats['documentos_descargados']}")
    log(f"Documentos fallidos: {stats['documentos_fallidos']}")
    log(f"Bytes totales: {stats['bytes_totales'] / 1024 / 1024:.1f} MB")
    log(f"Causas extraidas: {len(causas)}")
    log(f"Posts extraidos: {len(posts)}")
    log("")
    log("Por categoria:")
    for cat, count in sorted(stats["por_categoria"].items(), key=lambda x: -x[1]):
        log(f"  {cat}: {count}")
    log("")
    log("Por extension:")
    for ext, count in sorted(stats["por_extension"].items(), key=lambda x: -x[1]):
        log(f"  {ext}: {count}")
    log("")
    log(f"Datos guardados en: {OUT_DIR}")


if __name__ == "__main__":
    main()
