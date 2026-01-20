#!/usr/bin/env python3
"""
Descarga datos abiertos de SNIFA (Superintendencia del Medio Ambiente)
"""

import os
import sys
import requests
import time
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = Path(r"G:\Mi unidad\tribunal_pdf\corpus\snifa")
BASE_DIR.mkdir(parents=True, exist_ok=True)

# URLs de datos abiertos de SNIFA (Google Drive folders)
SNIFA_DATASETS = {
    "termoelectricas": {
        "desc": "Datos termoeléctricas D.S. N° 13/2011 (desde 2014)",
        "drive_id": "1CfvVC3l4tDvRFyLWv2a_4H6Q8DV58cr6"
    },
    "unidades_fiscalizables": {
        "desc": "Catastro de unidades fiscalizables vigentes",
        "drive_id": "1Pos3xmMDj0OoRiqmR1W9Q2K0hsnMaEL4"
    },
    "sancionatorios": {
        "desc": "Procesos sancionatorios históricos",
        "drive_id": "1O7o60LzQ-qH8xiK_-Ofqw_mZzti_gbEr"
    },
    "rep_residuos": {
        "desc": "Responsabilidad Extendida del Productor",
        "drive_id": "1nlG-tSKrkUb6Tp2ZhjUeRzDlFucPuUb1"
    },
    "riles": {
        "desc": "Datos RILES D.S. N° 90/2000 (desde 2017)",
        "drive_id": "1Ne0COCkx70XOPLIqeUqpIl3uiayqfihl"
    },
    "fiscalizaciones": {
        "desc": "Fiscalizaciones históricas",
        "drive_id": "1WAw7SSPMug3oZimgHYkEIi7_5JqLvzpb"
    },
    "sanciones_firmes": {
        "desc": "Sanciones declaradas firmes por SMA",
        "drive_id": "1q6MG4sfGxLisRuusnYKpUxmi9jgkSU4F"
    }
}

def get_drive_folder_files(folder_id):
    """Intenta obtener lista de archivos de una carpeta de Google Drive"""
    # Método 1: Usar la API de exportación de carpeta
    url = f"https://drive.google.com/drive/folders/{folder_id}"

    try:
        resp = requests.get(url, timeout=30)
        # Buscar links de archivos en el HTML
        import re
        # Buscar IDs de archivos
        file_ids = re.findall(r'/file/d/([a-zA-Z0-9_-]+)', resp.text)
        file_ids = list(set(file_ids))
        return file_ids
    except Exception as e:
        print(f"  Error obteniendo archivos: {e}")
        return []

def download_drive_file(file_id, dest_path):
    """Descarga un archivo de Google Drive"""
    # URL de descarga directa
    url = f"https://drive.google.com/uc?export=download&id={file_id}"

    try:
        session = requests.Session()
        resp = session.get(url, stream=True, timeout=60)

        # Manejar confirmación para archivos grandes
        for key, value in resp.cookies.items():
            if key.startswith('download_warning'):
                url = f"https://drive.google.com/uc?export=download&confirm={value}&id={file_id}"
                resp = session.get(url, stream=True, timeout=60)
                break

        # Obtener nombre del archivo del header
        if 'content-disposition' in resp.headers:
            import re
            cd = resp.headers['content-disposition']
            fname = re.findall('filename="(.+)"', cd)
            if fname:
                dest_path = dest_path.parent / fname[0]

        with open(dest_path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=32768):
                if chunk:
                    f.write(chunk)

        return True, dest_path
    except Exception as e:
        print(f"  Error descargando: {e}")
        return False, None

def main():
    print("="*60)
    print("DESCARGA DE DATOS ABIERTOS - SNIFA")
    print("="*60)
    print(f"Destino: {BASE_DIR}")
    print()

    total_files = 0

    for dataset_name, info in SNIFA_DATASETS.items():
        print(f"\n{'='*60}")
        print(f"{dataset_name.upper()}")
        print(f"  {info['desc']}")
        print(f"{'='*60}")

        # Crear directorio
        dataset_dir = BASE_DIR / dataset_name
        dataset_dir.mkdir(exist_ok=True)

        # Obtener archivos
        print(f"  Escaneando carpeta de Google Drive...")
        file_ids = get_drive_folder_files(info['drive_id'])
        print(f"  Encontrados: {len(file_ids)} archivos")

        if not file_ids:
            # Guardar link para descarga manual
            with open(dataset_dir / "LINK_DESCARGA.txt", "w") as f:
                f.write(f"Carpeta Google Drive:\n")
                f.write(f"https://drive.google.com/drive/folders/{info['drive_id']}\n\n")
                f.write(f"Descripción: {info['desc']}\n")
            print(f"  Link guardado para descarga manual")
            continue

        # Descargar archivos
        ok = 0
        for i, file_id in enumerate(file_ids, 1):
            dest = dataset_dir / f"archivo_{i}"
            success, final_path = download_drive_file(file_id, dest)
            if success:
                ok += 1
                print(f"  [{i}/{len(file_ids)}] OK: {final_path.name if final_path else 'archivo'}")
            else:
                print(f"  [{i}/{len(file_ids)}] FAIL")

            time.sleep(1)  # Rate limiting

        total_files += ok
        print(f"\n  Descargados: {ok}/{len(file_ids)}")

    print(f"\n{'='*60}")
    print(f"TOTAL ARCHIVOS DESCARGADOS: {total_files}")
    print(f"{'='*60}")

    # Guardar resumen de links
    with open(BASE_DIR / "LINKS_SNIFA.txt", "w", encoding="utf-8") as f:
        f.write("DATOS ABIERTOS SNIFA - LINKS DE DESCARGA\n")
        f.write("="*50 + "\n\n")
        for name, info in SNIFA_DATASETS.items():
            f.write(f"{name}:\n")
            f.write(f"  {info['desc']}\n")
            f.write(f"  https://drive.google.com/drive/folders/{info['drive_id']}\n\n")

    print(f"\nLinks guardados en: {BASE_DIR / 'LINKS_SNIFA.txt'}")

if __name__ == "__main__":
    main()
