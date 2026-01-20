#!/usr/bin/env python3
"""
Verificación exhaustiva final del corpus de Tribunales Ambientales
"""

import os
import sys
import requests
import json
from pathlib import Path
from collections import defaultdict

# Fix encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = Path(r"G:\Mi unidad\tribunal_pdf\corpus\descarga_completa\documentos")

def get_api_documents(base_url, tribunal_id):
    """Obtiene todos los documentos desde la API de WordPress"""
    docs = []
    page = 1
    per_page = 100

    while True:
        try:
            url = f"{base_url}/wp-json/wp/v2/media"
            params = {"per_page": per_page, "page": page}
            resp = requests.get(url, params=params, timeout=30)

            if resp.status_code == 400:  # No more pages
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
                        "id": item.get("id"),
                        "filename": filename,
                        "url": source_url,
                        "title": item.get("title", {}).get("rendered", "")
                    })

            page += 1
            if page > 200:  # Safety limit
                break

        except Exception as e:
            print(f"    Error página {page}: {e}")
            break

    return docs

def get_downloaded_files(directory):
    """Obtiene lista de archivos descargados"""
    files = []
    if directory.exists():
        for f in directory.rglob("*"):
            if f.is_file():
                files.append({
                    "path": f,
                    "name": f.name,
                    "name_lower": f.name.lower(),
                    "size": f.stat().st_size
                })
    return files

def normalize_filename(name):
    """Normaliza nombre para comparación"""
    import urllib.parse
    name = urllib.parse.unquote(name)
    name = name.lower().strip()
    # Remover caracteres problemáticos
    for char in ['"', "'", "?", "#"]:
        name = name.replace(char, "")
    return name

def check_tribunal(tribunal_id, base_url, local_dir):
    """Verifica un tribunal completo"""
    print(f"\n{'='*60}")
    print(f"VERIFICANDO: {tribunal_id}")
    print(f"{'='*60}")

    # Obtener documentos de API
    print(f"  Consultando API: {base_url}...")
    api_docs = get_api_documents(base_url, tribunal_id)
    print(f"  Documentos en API: {len(api_docs)}")

    # Obtener archivos descargados
    print(f"  Escaneando directorio local...")
    local_files = get_downloaded_files(local_dir)
    print(f"  Archivos descargados: {len(local_files)}")

    # Crear set de nombres normalizados de archivos locales
    local_names = set()
    for f in local_files:
        local_names.add(normalize_filename(f["name"]))
        # También agregar sin extensión para matches parciales
        name_no_ext = normalize_filename(f["name"].rsplit(".", 1)[0])
        local_names.add(name_no_ext)

    # Buscar faltantes
    missing = []
    for doc in api_docs:
        api_name = normalize_filename(doc["filename"])
        api_name_no_ext = api_name.rsplit(".", 1)[0] if "." in api_name else api_name

        # Verificar si existe
        found = False
        if api_name in local_names:
            found = True
        elif api_name_no_ext in local_names:
            found = True
        else:
            # Búsqueda parcial
            for local_name in local_names:
                if api_name_no_ext in local_name or local_name in api_name_no_ext:
                    found = True
                    break

        if not found:
            missing.append(doc)

    # Verificar archivos corruptos (tamaño 0)
    corrupted = [f for f in local_files if f["size"] == 0]

    # Verificar duplicados
    name_counts = defaultdict(list)
    for f in local_files:
        name_counts[f["name_lower"]].append(f["path"])
    duplicates = {k: v for k, v in name_counts.items() if len(v) > 1}

    # Reporte
    print(f"\n  RESULTADO:")
    print(f"    En API:        {len(api_docs)}")
    print(f"    Descargados:   {len(local_files)}")
    print(f"    Faltantes:     {len(missing)}")
    print(f"    Corruptos:     {len(corrupted)}")
    print(f"    Duplicados:    {len(duplicates)}")

    if missing:
        print(f"\n  FALTANTES ({len(missing)}):")
        for doc in missing[:15]:
            print(f"    - {doc['filename'][:60]}")
        if len(missing) > 15:
            print(f"    ... y {len(missing)-15} más")

    if corrupted:
        print(f"\n  CORRUPTOS (tamaño 0):")
        for f in corrupted[:5]:
            print(f"    - {f['name']}")

    if duplicates:
        print(f"\n  DUPLICADOS:")
        for name, paths in list(duplicates.items())[:5]:
            print(f"    - {name} ({len(paths)} copias)")

    return {
        "tribunal": tribunal_id,
        "api_count": len(api_docs),
        "downloaded": len(local_files),
        "missing": missing,
        "corrupted": corrupted,
        "duplicates": duplicates
    }

def main():
    print("="*60)
    print("VERIFICACIÓN FINAL EXHAUSTIVA")
    print("="*60)

    tribunales = [
        ("1TA", "https://www.1ta.cl", BASE_DIR / "1ta"),
        ("2TA", "https://tribunalambiental.cl", BASE_DIR),  # 2TA está en raíz
        ("3TA", "https://3ta.cl", BASE_DIR / "3ta"),
    ]

    results = []
    total_api = 0
    total_downloaded = 0
    total_missing = 0

    for tid, url, directory in tribunales:
        result = check_tribunal(tid, url, directory)
        results.append(result)
        total_api += result["api_count"]
        total_downloaded += result["downloaded"]
        total_missing += len(result["missing"])

    # Resumen final
    print("\n" + "="*60)
    print("RESUMEN FINAL")
    print("="*60)
    print(f"\n  {'Tribunal':<15} {'API':>8} {'Descarg.':>10} {'Faltantes':>10} {'Status':>12}")
    print(f"  {'-'*55}")

    for r in results:
        missing_count = len(r["missing"])
        if missing_count == 0:
            status = "COMPLETO"
        elif missing_count < 10:
            status = f"{100-missing_count*100//r['api_count']}%"
        else:
            status = f"FALTAN {missing_count}"

        print(f"  {r['tribunal']:<15} {r['api_count']:>8} {r['downloaded']:>10} {missing_count:>10} {status:>12}")

    print(f"  {'-'*55}")
    print(f"  {'TOTAL':<15} {total_api:>8} {total_downloaded:>10} {total_missing:>10}")

    # Calcular completitud
    if total_api > 0:
        completitud = (total_downloaded / total_api) * 100
        print(f"\n  COMPLETITUD ESTIMADA: {completitud:.1f}%")

    # Guardar reporte detallado
    report_path = BASE_DIR.parent / "VERIFICACION_EXHAUSTIVA.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("="*60 + "\n")
        f.write("VERIFICACIÓN EXHAUSTIVA FINAL\n")
        f.write("="*60 + "\n\n")

        for r in results:
            f.write(f"\n{r['tribunal']}\n")
            f.write("-"*40 + "\n")
            f.write(f"  En API: {r['api_count']}\n")
            f.write(f"  Descargados: {r['downloaded']}\n")
            f.write(f"  Faltantes: {len(r['missing'])}\n")

            if r['missing']:
                f.write(f"\n  Documentos faltantes:\n")
                for doc in r['missing']:
                    f.write(f"    - {doc['filename']}\n")
                    f.write(f"      URL: {doc['url']}\n")

    print(f"\n  Reporte guardado en: {report_path}")

if __name__ == "__main__":
    main()
