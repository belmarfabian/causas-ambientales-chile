#!/usr/bin/env python3
"""
Descarga conflictos de Chile desde EJAtlas API.
"""

import json
import time
from pathlib import Path

import requests

BASE_DIR = Path(__file__).parent.parent
OUTPUT_FILE = BASE_DIR / "datos" / "conflictos" / "ejatlas_chile.json"

def main():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    base_url = "https://ejatlas.org/api/v1/conflicts?country=Chile"

    all_conflicts = []
    url = base_url
    page = 1

    print("Descargando conflictos de EJAtlas para Chile...")

    while url:
        print(f"Página {page}...", end=" ", flush=True)
        try:
            r = requests.get(url, headers=headers, timeout=60)
            r.raise_for_status()
            data = r.json()

            if page == 1:
                total = data.get("count", "?")
                print(f"(Total: {total})")

            results = data.get("results", [])
            all_conflicts.extend(results)
            print(f"{len(results)} conflictos")

            url = data.get("next")
            page += 1
            time.sleep(1)  # Pausa entre requests

        except Exception as e:
            print(f"Error: {e}")
            break

    print(f"\nTotal descargados: {len(all_conflicts)}")

    if all_conflicts:
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(all_conflicts, f, ensure_ascii=False, indent=2)
        print(f"Guardado: {OUTPUT_FILE}")

        # Estadísticas
        print("\n=== ESTADÍSTICAS ===")
        categorias = {}
        for c in all_conflicts:
            cat = c.get("category", {}).get("name", "Sin categoría")
            categorias[cat] = categorias.get(cat, 0) + 1

        print("Categorías:")
        for cat, n in sorted(categorias.items(), key=lambda x: -x[1]):
            print(f"  {cat}: {n}")

if __name__ == "__main__":
    main()
