#!/usr/bin/env python3
"""
OCR de PDFs escaneados usando Claude MLLM (Vision)
Procesa sentencias escaneadas del Tribunal Ambiental de Chile

Uso:
    set ANTHROPIC_API_KEY=tu_api_key
    python scripts/ocr_claude_mllm.py

El script:
- Lee la lista de PDFs escaneados desde datos/pdfs_escaneados.json
- Filtra solo sentencias (archivos con "sentencia" en el nombre)
- Convierte cada página a imagen
- Envía a Claude para transcripción
- Guarda resultado en corpus/textos/
"""

import os
import sys
import json
import base64
import time
from pathlib import Path
from datetime import datetime
from io import BytesIO

try:
    import anthropic
    from pdf2image import convert_from_path
    from PIL import Image
except ImportError as e:
    print(f"Error: Falta dependencia {e}")
    print("Instalar con: pip install anthropic pdf2image pillow")
    sys.exit(1)

# Configuración
BASE_DIR = Path("G:/My Drive/tribunal_pdf")
PDFS_ESCANEADOS = BASE_DIR / "datos" / "pdfs_escaneados.json"
OUTPUT_DIR = BASE_DIR / "corpus" / "textos"
CHECKPOINT_FILE = BASE_DIR / "datos" / "ocr_checkpoint.json"
LOG_FILE = BASE_DIR / "datos" / "log_ocr.json"

# Parámetros Claude
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 4096
DPI = 150  # Resolución para conversión de PDF a imagen

def cargar_checkpoint():
    """Carga el checkpoint de progreso si existe."""
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"procesados": [], "errores": []}

def guardar_checkpoint(checkpoint):
    """Guarda el estado actual del procesamiento."""
    with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
        json.dump(checkpoint, f, ensure_ascii=False, indent=2)

def imagen_a_base64(imagen: Image.Image, formato='PNG') -> str:
    """Convierte una imagen PIL a base64."""
    buffer = BytesIO()
    # Convertir a RGB si es necesario (para evitar problemas con RGBA)
    if imagen.mode in ('RGBA', 'P'):
        imagen = imagen.convert('RGB')
    imagen.save(buffer, format=formato, optimize=True)
    return base64.standard_b64encode(buffer.getvalue()).decode('utf-8')

def extraer_texto_pagina(client, imagen: Image.Image, pagina_num: int, total_paginas: int) -> str:
    """Extrae texto de una página usando Claude Vision."""

    # Redimensionar si es muy grande (max 1568px en cualquier dimensión para Claude)
    max_dim = 1568
    if max(imagen.size) > max_dim:
        ratio = max_dim / max(imagen.size)
        new_size = (int(imagen.size[0] * ratio), int(imagen.size[1] * ratio))
        imagen = imagen.resize(new_size, Image.Resampling.LANCZOS)

    img_base64 = imagen_a_base64(imagen)

    prompt = f"""Transcribe el texto de esta imagen de un documento legal del Tribunal Ambiental de Chile (página {pagina_num}/{total_paginas}).

Instrucciones:
- Transcribe TODO el texto visible, manteniendo la estructura del documento
- Preserva los párrafos, numeraciones y formato general
- Si hay tablas, represéntalas de forma clara
- Ignora marcas de agua, sellos y elementos decorativos
- Si el texto es ilegible, indica [ilegible]
- No agregues comentarios ni interpretaciones, solo transcribe

Texto transcrito:"""

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": img_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )
        return response.content[0].text
    except anthropic.RateLimitError:
        print("    Rate limit - esperando 60s...")
        time.sleep(60)
        return extraer_texto_pagina(client, imagen, pagina_num, total_paginas)
    except Exception as e:
        print(f"    Error en página {pagina_num}: {e}")
        return f"[Error en página {pagina_num}: {str(e)}]"

def procesar_pdf(client, pdf_path: str, output_dir: Path) -> dict:
    """Procesa un PDF completo y extrae su texto."""

    pdf_path = Path(pdf_path)
    nombre_base = pdf_path.stem
    output_file = output_dir / f"{nombre_base}.txt"

    # Si ya existe, saltar
    if output_file.exists():
        return {"status": "exists", "archivo": str(output_file)}

    try:
        # Convertir PDF a imágenes
        imagenes = convert_from_path(str(pdf_path), dpi=DPI)
        total_paginas = len(imagenes)

        print(f"  Convirtiendo {total_paginas} páginas...")

        # Extraer texto de cada página
        textos = []
        for i, imagen in enumerate(imagenes, 1):
            print(f"    Página {i}/{total_paginas}...", end=" ", flush=True)
            texto = extraer_texto_pagina(client, imagen, i, total_paginas)
            textos.append(texto)
            print("OK")

            # Pequeña pausa entre páginas para evitar rate limits
            if i < total_paginas:
                time.sleep(0.5)

        # Combinar textos
        texto_completo = f"""# {nombre_base}
# Transcrito con Claude MLLM el {datetime.now().strftime('%Y-%m-%d')}
# Páginas: {total_paginas}

{"="*60}

"""
        for i, texto in enumerate(textos, 1):
            texto_completo += f"\n--- Página {i} ---\n\n{texto}\n"

        # Guardar
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(texto_completo)

        return {
            "status": "success",
            "archivo": str(output_file),
            "paginas": total_paginas
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def main():
    # Verificar API key
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("Error: ANTHROPIC_API_KEY no configurada")
        print("Configurar con: set ANTHROPIC_API_KEY=tu_api_key")
        sys.exit(1)

    # Inicializar cliente
    client = anthropic.Anthropic(api_key=api_key)

    # Cargar lista de PDFs escaneados
    if not PDFS_ESCANEADOS.exists():
        print(f"Error: No se encontró {PDFS_ESCANEADOS}")
        sys.exit(1)

    with open(PDFS_ESCANEADOS, 'r', encoding='utf-8') as f:
        pdfs = json.load(f)

    # Filtrar solo sentencias
    sentencias = [p for p in pdfs if 'sentencia' in p['archivo'].lower()]
    total_sentencias = len(sentencias)
    total_paginas = sum(s['paginas'] for s in sentencias)

    print(f"=" * 60)
    print(f"OCR de Sentencias con Claude MLLM")
    print(f"=" * 60)
    print(f"Sentencias a procesar: {total_sentencias}")
    print(f"Total páginas: {total_paginas}")
    print(f"Modelo: {MODEL}")
    print(f"=" * 60)

    # Cargar checkpoint
    checkpoint = cargar_checkpoint()
    procesados_prev = set(checkpoint.get("procesados", []))

    # Crear directorio de salida
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Procesar sentencias
    resultados = {
        "inicio": datetime.now().isoformat(),
        "exitosos": 0,
        "errores": 0,
        "omitidos": 0,
        "detalles": []
    }

    for i, sent in enumerate(sentencias, 1):
        archivo = sent['archivo']
        nombre = Path(archivo).name

        # Saltar si ya fue procesado
        if archivo in procesados_prev:
            print(f"[{i}/{total_sentencias}] SKIP {nombre}")
            resultados["omitidos"] += 1
            continue

        print(f"[{i}/{total_sentencias}] Procesando {nombre} ({sent['paginas']} págs)...")

        resultado = procesar_pdf(client, archivo, OUTPUT_DIR)

        if resultado["status"] == "success":
            print(f"  -> OK: {resultado['archivo']}")
            resultados["exitosos"] += 1
            checkpoint["procesados"].append(archivo)
        elif resultado["status"] == "exists":
            print(f"  -> Ya existe")
            resultados["omitidos"] += 1
            checkpoint["procesados"].append(archivo)
        else:
            print(f"  -> ERROR: {resultado.get('error', 'desconocido')}")
            resultados["errores"] += 1
            checkpoint["errores"].append({"archivo": archivo, "error": resultado.get("error")})

        resultados["detalles"].append({"archivo": nombre, **resultado})

        # Guardar checkpoint cada 5 documentos
        if i % 5 == 0:
            guardar_checkpoint(checkpoint)
            print(f"  [Checkpoint guardado]")

    # Guardar resultados finales
    resultados["fin"] = datetime.now().isoformat()
    guardar_checkpoint(checkpoint)

    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"Resumen:")
    print(f"  Exitosos: {resultados['exitosos']}")
    print(f"  Errores: {resultados['errores']}")
    print(f"  Omitidos: {resultados['omitidos']}")
    print(f"Log guardado en: {LOG_FILE}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
