#!/usr/bin/env python3
"""Genera un informe HTML para revisar todos los documentos PDF con su transcripción."""

import fitz
from pathlib import Path
from datetime import datetime
import re
import html

# Rutas del proyecto
BASE_DIR = Path("g:/Mi unidad/tribunal_pdf")
PDF_DIR = BASE_DIR / "tribunal_pdfs_organizado" / "originales"
OUTPUT_DIR = BASE_DIR / "informes"

def extraer_texto_pdf(pdf_path, max_paginas=2):
    """Extrae texto de las primeras páginas del PDF."""
    try:
        doc = fitz.open(str(pdf_path))
        texto = ""
        for i in range(min(max_paginas, len(doc))):
            texto += doc[i].get_text()
        doc.close()
        return texto.strip()
    except Exception as e:
        return f"[Error al extraer texto: {e}]"

def extraer_clasificacion_nombre(nombre):
    """Extrae clasificación desde el nombre del archivo."""
    patrones = [
        r'([RDSC])-(\d+)-(\d{4})',
        r'([RDSC])[-_](\d+)[-_](\d{4})',
        r'_([RDSC])-(\d+)-(\d{4})',
        r'Sentencia_([RDSC])-(\d+)-(\d{4})',
    ]

    for patron in patrones:
        match = re.search(patron, nombre, re.IGNORECASE)
        if match:
            tipo = match.group(1).upper()
            rol = match.group(2)
            año = match.group(3)
            return {'tipo': tipo, 'rol': rol, 'año': año}

    return {'tipo': '?', 'rol': '?', 'año': '?'}

def buscar_rol_en_texto(texto):
    """Busca el rol del caso en el texto extraído."""
    patrones = [
        r'Rol\s+([RDSC])\s*N[°ºo]?\s*(\d+)[-/](\d{4})',
        r'Autos\s+([RDSC])[-\s]*(\d+)[-/](\d{4})',
        r'causa\s+([RDSC])[-\s]*(\d+)[-/](\d{4})',
        r'Rol\s+([RDSC])\s+(\d+)[-/](\d{4})',
    ]

    for patron in patrones:
        match = re.search(patron, texto, re.IGNORECASE)
        if match:
            return {
                'tipo': match.group(1).upper(),
                'rol': match.group(2),
                'año': match.group(3),
                'texto_encontrado': match.group(0)
            }

    return None

def generar_html():
    """Genera el informe HTML completo."""
    import sys
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    # Recopilar todos los PDFs
    pdfs = list(PDF_DIR.glob('**/*.pdf'))
    pdfs.sort(key=lambda x: x.name)

    print(f"Encontrados {len(pdfs)} archivos PDF")

    # Estilos CSS
    css = """
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }
        h1 {
            text-align: center;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .stats {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        .indice {
            background: white;
            padding: 20px;
            margin-bottom: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .indice h2 { margin-top: 0; }
        .indice-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 5px;
            max-height: 400px;
            overflow-y: auto;
        }
        .indice-item {
            font-size: 12px;
            padding: 3px 5px;
        }
        .indice-item a { text-decoration: none; color: #3498db; }
        .indice-item a:hover { text-decoration: underline; }
        .documento {
            background: white;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .doc-header {
            background: #3498db;
            color: white;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .doc-header.tipo-R { background: #3498db; }
        .doc-header.tipo-D { background: #e74c3c; }
        .doc-header.tipo-S { background: #2ecc71; }
        .doc-header.tipo-C { background: #9b59b6; }
        .doc-header.tipo-unknown { background: #95a5a6; }
        .doc-numero {
            font-size: 14px;
            opacity: 0.9;
        }
        .doc-title {
            font-size: 16px;
            font-weight: bold;
        }
        .doc-meta {
            background: #ecf0f1;
            padding: 10px 20px;
            display: flex;
            gap: 30px;
            flex-wrap: wrap;
            font-size: 14px;
        }
        .meta-item {
            display: flex;
            gap: 5px;
        }
        .meta-label {
            font-weight: bold;
            color: #666;
        }
        .meta-value { color: #333; }
        .match { color: #27ae60; font-weight: bold; }
        .no-match { color: #e74c3c; font-weight: bold; }
        .doc-content {
            padding: 20px;
            max-height: 500px;
            overflow-y: auto;
            font-size: 13px;
            line-height: 1.6;
            white-space: pre-wrap;
            font-family: 'Consolas', monospace;
            background: #fafafa;
            border-top: 1px solid #eee;
        }
        .rol-encontrado {
            background: #d4edda;
            padding: 10px 20px;
            border-left: 4px solid #28a745;
            font-size: 14px;
        }
        .rol-no-encontrado {
            background: #fff3cd;
            padding: 10px 20px;
            border-left: 4px solid #ffc107;
            font-size: 14px;
        }
        .carpeta {
            font-size: 12px;
            color: #888;
        }
        .nav-top {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #333;
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            text-decoration: none;
            font-size: 14px;
        }
        .nav-top:hover { background: #555; }
        @media print {
            .documento { page-break-inside: avoid; }
            .nav-top { display: none; }
        }
    </style>
    """

    # Generar contenido
    documentos_html = []
    estadisticas = {'R': 0, 'D': 0, 'S': 0, 'C': 0, '?': 0}
    coincidencias = 0
    total_con_rol = 0

    for i, pdf_path in enumerate(pdfs, 1):
        print(f"Procesando {i}/{len(pdfs)}: {pdf_path.name[:50]}...", end='\r')

        # Extraer información
        nombre = pdf_path.name
        carpeta_rel = pdf_path.relative_to(PDF_DIR)
        clasificacion = extraer_clasificacion_nombre(nombre)
        texto = extraer_texto_pdf(pdf_path)
        rol_texto = buscar_rol_en_texto(texto)

        tipo = clasificacion['tipo']
        estadisticas[tipo] = estadisticas.get(tipo, 0) + 1

        # Verificar coincidencia
        coincide = False
        if rol_texto:
            total_con_rol += 1
            if (rol_texto['tipo'] == clasificacion['tipo'] and
                rol_texto['rol'] == clasificacion['rol']):
                coincide = True
                coincidencias += 1

        tipo_class = f"tipo-{tipo}" if tipo in 'RDSC' else "tipo-unknown"

        # HTML del documento
        doc_html = f"""
        <div class="documento" id="doc-{i}">
            <div class="doc-header {tipo_class}">
                <div>
                    <div class="doc-numero">Documento #{i}</div>
                    <div class="doc-title">{html.escape(nombre)}</div>
                    <div class="carpeta">{html.escape(str(carpeta_rel.parent))}</div>
                </div>
                <div style="font-size: 24px; font-weight: bold;">
                    {tipo}-{clasificacion['rol']}-{clasificacion['año']}
                </div>
            </div>
            <div class="doc-meta">
                <div class="meta-item">
                    <span class="meta-label">Tipo:</span>
                    <span class="meta-value">{tipo}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Rol:</span>
                    <span class="meta-value">{clasificacion['rol']}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Año:</span>
                    <span class="meta-value">{clasificacion['año']}</span>
                </div>
            </div>
        """

        if rol_texto:
            estado = "match" if coincide else "no-match"
            estado_texto = "✓ COINCIDE" if coincide else "✗ NO COINCIDE"
            doc_html += f"""
            <div class="rol-encontrado">
                <strong>Rol encontrado en texto:</strong> {html.escape(rol_texto['texto_encontrado'])}
                <span class="{estado}"> — {estado_texto}</span>
            </div>
            """
        else:
            doc_html += """
            <div class="rol-no-encontrado">
                <strong>⚠ No se encontró patrón de Rol en el texto</strong> — Verificar manualmente
            </div>
            """

        doc_html += f"""
            <div class="doc-content">{html.escape(texto[:3000])}{'...' if len(texto) > 3000 else ''}</div>
        </div>
        """

        documentos_html.append(doc_html)

    print("\nGenerando archivo HTML...")

    # Generar índice
    indice_items = []
    for i, pdf_path in enumerate(pdfs, 1):
        nombre_corto = pdf_path.name[:50] + "..." if len(pdf_path.name) > 50 else pdf_path.name
        indice_items.append(f'<div class="indice-item"><a href="#doc-{i}">{i}. {html.escape(nombre_corto)}</a></div>')

    # HTML completo
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Revisión de Documentos - Segundo Tribunal Ambiental</title>
    {css}
</head>
<body>
    <h1 id="top">Revisión de Documentos</h1>
    <p class="stats">
        Segundo Tribunal Ambiental de Chile |
        Total: {len(pdfs)} documentos |
        Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}
    </p>

    <div class="indice">
        <h2>Resumen</h2>
        <p>
            <strong>Por tipo:</strong>
            R: {estadisticas.get('R', 0)} |
            D: {estadisticas.get('D', 0)} |
            S: {estadisticas.get('S', 0)} |
            C: {estadisticas.get('C', 0)} |
            Sin clasificar: {estadisticas.get('?', 0)}
        </p>
        <p>
            <strong>Verificación automática:</strong>
            {coincidencias}/{total_con_rol} documentos con rol detectado coinciden con nombre de archivo
            ({100*coincidencias/total_con_rol:.1f}% de coincidencia)
        </p>
        <h3>Índice de documentos</h3>
        <div class="indice-grid">
            {''.join(indice_items)}
        </div>
    </div>

    {''.join(documentos_html)}

    <a href="#top" class="nav-top">↑ Volver arriba</a>
</body>
</html>
"""

    # Guardar archivo
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / "revision_documentos.html"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"\n{'='*60}")
    print(f"Informe generado: {output_file}")
    print(f"{'='*60}")
    print(f"Total documentos: {len(pdfs)}")
    print(f"  - Reclamaciones (R): {estadisticas.get('R', 0)}")
    print(f"  - Demandas (D): {estadisticas.get('D', 0)}")
    print(f"  - Solicitudes (S): {estadisticas.get('S', 0)}")
    print(f"  - Consultas (C): {estadisticas.get('C', 0)}")
    print(f"  - Sin clasificar: {estadisticas.get('?', 0)}")
    print(f"\nVerificación: {coincidencias}/{total_con_rol} coinciden ({100*coincidencias/total_con_rol:.1f}%)")

    return output_file

if __name__ == '__main__':
    generar_html()
