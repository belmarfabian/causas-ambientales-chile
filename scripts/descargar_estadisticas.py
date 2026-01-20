#!/usr/bin/env python3
"""
Descarga estadísticas y datos adicionales de los tribunales
"""

import os
import sys
import requests
from pathlib import Path
import json

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = Path(r"G:\Mi unidad\tribunal_pdf\corpus\estadisticas")
BASE_DIR.mkdir(parents=True, exist_ok=True)

def download_file(url, dest_path, description=""):
    """Descarga un archivo"""
    print(f"  Descargando {description}...")
    try:
        resp = requests.get(url, timeout=60, stream=True)
        resp.raise_for_status()

        with open(dest_path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        size_kb = dest_path.stat().st_size / 1024
        print(f"    OK: {size_kb:.1f} KB")
        return True
    except Exception as e:
        print(f"    Error: {e}")
        return False

def get_3ta_statistics():
    """Descarga estadísticas del 3er Tribunal"""
    print("\n" + "="*60)
    print("ESTADÍSTICAS 3ER TRIBUNAL AMBIENTAL")
    print("="*60)

    dir_3ta = BASE_DIR / "3ta"
    dir_3ta.mkdir(exist_ok=True)

    # Excel de estadísticas
    excel_url = "https://3ta.cl/wp-content/uploads/2024/01/Estadisticas-3TA.xlsx"
    download_file(excel_url, dir_3ta / "Estadisticas-3TA.xlsx", "Excel estadísticas")

    # Probar otras URLs posibles
    urls_3ta = [
        ("https://3ta.cl/wp-content/uploads/estadisticas.xlsx", "estadisticas.xlsx"),
        ("https://3ta.cl/wp-content/uploads/cifras-3ta.xlsx", "cifras-3ta.xlsx"),
    ]

    for url, filename in urls_3ta:
        try:
            resp = requests.head(url, timeout=10)
            if resp.status_code == 200:
                download_file(url, dir_3ta / filename, filename)
        except:
            pass

def get_wp_api_data(base_url, tribunal_id):
    """Obtiene datos adicionales de la API de WordPress"""
    print(f"\n  Obteniendo datos de API WordPress: {base_url}")

    output_dir = BASE_DIR / tribunal_id
    output_dir.mkdir(exist_ok=True)

    endpoints = [
        ("posts", "/wp-json/wp/v2/posts"),
        ("pages", "/wp-json/wp/v2/pages"),
        ("categories", "/wp-json/wp/v2/categories"),
        ("tags", "/wp-json/wp/v2/tags"),
    ]

    for name, endpoint in endpoints:
        print(f"    {name}...")
        try:
            all_items = []
            page = 1
            while page < 100:
                url = f"{base_url}{endpoint}?per_page=100&page={page}"
                resp = requests.get(url, timeout=30)
                if resp.status_code != 200:
                    break
                items = resp.json()
                if not items:
                    break
                all_items.extend(items)
                page += 1

            if all_items:
                with open(output_dir / f"{name}.json", 'w', encoding='utf-8') as f:
                    json.dump(all_items, f, ensure_ascii=False, indent=2)
                print(f"      {len(all_items)} items")

        except Exception as e:
            print(f"      Error: {e}")

def main():
    print("="*60)
    print("DESCARGA DE ESTADÍSTICAS Y DATOS ADICIONALES")
    print("="*60)

    # Estadísticas 3TA
    get_3ta_statistics()

    # Datos de API WordPress de cada tribunal
    tribunales = [
        ("https://www.1ta.cl", "1ta"),
        ("https://tribunalambiental.cl", "2ta"),
        ("https://3ta.cl", "3ta"),
    ]

    for base_url, tid in tribunales:
        print(f"\n{'='*60}")
        print(f"TRIBUNAL: {tid.upper()}")
        print(f"{'='*60}")
        get_wp_api_data(base_url, tid)

    # Resumen
    print(f"\n{'='*60}")
    print("DESCARGA COMPLETADA")
    print(f"{'='*60}")
    print(f"Archivos en: {BASE_DIR}")

    # Listar archivos descargados
    total_files = 0
    for root, dirs, files in os.walk(BASE_DIR):
        for f in files:
            total_files += 1

    print(f"Total archivos: {total_files}")

if __name__ == "__main__":
    main()
