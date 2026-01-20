#!/usr/bin/env python3
"""
Descarga documentos faltantes identificados en la verificación
"""

import os
import sys
import requests
import json
import time
from pathlib import Path
from urllib.parse import unquote

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = Path(r"G:\Mi unidad\tribunal_pdf\corpus\descarga_completa\documentos")

def normalize_filename(name):
    """Normaliza nombre para comparación"""
    name = unquote(name)
    name = name.lower().strip()
    for char in ['"', "'", "?", "#"]:
        name = name.replace(char, "")
    return name

def get_local_files(directory, exclude_dirs=None):
    """Obtiene lista de archivos descargados"""
    exclude_dirs = exclude_dirs or []
    files = set()
    if directory.exists():
        for f in directory.rglob("*"):
            if f.is_file():
                # Excluir directorios específicos
                skip = False
                for exc in exclude_dirs:
                    if exc in str(f):
                        skip = True
                        break
                if not skip:
                    files.add(normalize_filename(f.name))
                    # También sin extensión
                    name_no_ext = f.name.rsplit(".", 1)[0] if "." in f.name else f.name
                    files.add(normalize_filename(name_no_ext))
    return files

def get_api_documents(base_url):
    """Obtiene todos los documentos desde la API"""
    docs = []
    page = 1
    while True:
        try:
            url = f"{base_url}/wp-json/wp/v2/media"
            params = {"per_page": 100, "page": page}
            resp = requests.get(url, params=params, timeout=30)
            if resp.status_code == 400:
                break
            resp.raise_for_status()
            data = resp.json()
            if not data:
                break
            for item in data:
                mime = item.get("mime_type", "")
                if "pdf" in mime or "document" in mime or "msword" in mime:
                    source_url = item.get("source_url", "")
                    filename = source_url.split("/")[-1] if source_url else ""
                    docs.append({
                        "filename": filename,
                        "url": source_url,
                    })
            page += 1
            if page > 200:
                break
        except Exception as e:
            print(f"  Error: {e}")
            break
    return docs

def download_file(url, dest_path, timeout=60):
    """Descarga un archivo"""
    try:
        resp = requests.get(url, timeout=timeout, stream=True)
        resp.raise_for_status()
        with open(dest_path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        return False

def process_tribunal(tid, base_url, local_dir, exclude_dirs=None):
    """Procesa un tribunal y descarga faltantes"""
    print(f"\n{'='*60}")
    print(f"PROCESANDO: {tid}")
    print(f"{'='*60}")

    # Obtener archivos locales
    print("  Escaneando archivos locales...")
    local_files = get_local_files(local_dir, exclude_dirs)
    print(f"  Archivos locales (normalizados): {len(local_files)}")

    # Obtener docs de API
    print(f"  Consultando API: {base_url}...")
    api_docs = get_api_documents(base_url)
    print(f"  Documentos en API: {len(api_docs)}")

    # Encontrar faltantes
    missing = []
    for doc in api_docs:
        api_name = normalize_filename(doc["filename"])
        api_name_no_ext = api_name.rsplit(".", 1)[0] if "." in api_name else api_name

        found = False
        if api_name in local_files or api_name_no_ext in local_files:
            found = True
        else:
            # Búsqueda parcial
            for local_name in local_files:
                if len(api_name_no_ext) > 10 and (api_name_no_ext[:20] in local_name):
                    found = True
                    break

        if not found and doc["url"]:
            missing.append(doc)

    print(f"  Faltantes: {len(missing)}")

    if not missing:
        print("  ¡Todo completo!")
        return 0, 0

    # Crear directorio para faltantes
    faltantes_dir = local_dir / "faltantes_final"
    faltantes_dir.mkdir(exist_ok=True)

    # Descargar faltantes
    print(f"\n  Descargando {len(missing)} archivos faltantes...")
    ok = 0
    fail = 0

    for i, doc in enumerate(missing, 1):
        filename = unquote(doc["filename"])
        # Limpiar nombre
        for char in ['"', '?', '<', '>', '|', '*']:
            filename = filename.replace(char, '')

        dest_path = faltantes_dir / filename

        if dest_path.exists():
            ok += 1
            continue

        success = download_file(doc["url"], dest_path)
        if success:
            ok += 1
        else:
            fail += 1

        if i % 20 == 0:
            print(f"    [{i}/{len(missing)}] OK: {ok}, FAIL: {fail}")

        time.sleep(0.3)

    print(f"\n  RESULTADO: OK={ok}, FAIL={fail}")
    return ok, fail

def main():
    print("="*60)
    print("DESCARGA DE DOCUMENTOS FALTANTES")
    print("="*60)

    results = []

    # 1TA
    ok, fail = process_tribunal(
        "1TA",
        "https://www.1ta.cl",
        BASE_DIR / "1ta"
    )
    results.append(("1TA", ok, fail))

    # 2TA (excluir carpetas 1ta y 3ta)
    ok, fail = process_tribunal(
        "2TA",
        "https://tribunalambiental.cl",
        BASE_DIR,
        exclude_dirs=["\\1ta\\", "\\3ta\\", "/1ta/", "/3ta/"]
    )
    results.append(("2TA", ok, fail))

    # 3TA
    ok, fail = process_tribunal(
        "3TA",
        "https://3ta.cl",
        BASE_DIR / "3ta"
    )
    results.append(("3TA", ok, fail))

    # Resumen
    print("\n" + "="*60)
    print("RESUMEN FINAL")
    print("="*60)
    total_ok = sum(r[1] for r in results)
    total_fail = sum(r[2] for r in results)

    for tid, ok, fail in results:
        print(f"  {tid}: OK={ok}, FAIL={fail}")

    print(f"\n  TOTAL: OK={total_ok}, FAIL={total_fail}")

if __name__ == "__main__":
    main()
