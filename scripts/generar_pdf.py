#!/usr/bin/env python3
"""Genera el paper en formato PDF usando reportlab."""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
import os
from pathlib import Path

# Rutas del proyecto
BASE_DIR = Path("g:/Mi unidad/tribunal_pdf")
PAPER_DIR = BASE_DIR / "paper"
FIGURAS_DIR = PAPER_DIR / "figuras"

def crear_pdf():
    doc = SimpleDocTemplate(
        str(PAPER_DIR / "paper_metodologia.pdf"),
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    styles = getSampleStyleSheet()

    # Estilos personalizados
    styles.add(ParagraphStyle(
        name='Titulo',
        parent=styles['Heading1'],
        fontSize=14,
        alignment=TA_CENTER,
        spaceAfter=12
    ))

    styles.add(ParagraphStyle(
        name='Subtitulo',
        parent=styles['Heading2'],
        fontSize=12,
        spaceBefore=12,
        spaceAfter=6
    ))

    styles.add(ParagraphStyle(
        name='Subtitulo2',
        parent=styles['Heading3'],
        fontSize=10,
        spaceBefore=8,
        spaceAfter=4
    ))

    styles.add(ParagraphStyle(
        name='Parrafo',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=8
    ))

    styles.add(ParagraphStyle(
        name='Item',
        parent=styles['Normal'],
        fontSize=10,
        leftIndent=20,
        spaceAfter=4
    ))

    story = []

    # TITULO
    story.append(Paragraph("Sistematizacion y analisis de la jurisprudencia del<br/>Segundo Tribunal Ambiental de Chile (2013-2025)", styles['Titulo']))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<i>Metodologia de construccion de base de datos documental</i>", styles['Titulo']))
    story.append(Spacer(1, 20))

    # Metadatos
    story.append(Paragraph("Autor(es): [Nombre del investigador]", styles['Normal']))
    story.append(Paragraph("Afiliacion: [Universidad/Centro de investigacion]", styles['Normal']))
    story.append(Paragraph("Fecha: Enero 2026", styles['Normal']))
    story.append(Spacer(1, 20))

    # RESUMEN
    story.append(Paragraph("Resumen", styles['Subtitulo']))
    story.append(Paragraph(
        "El presente documento describe la metodologia empleada para la construccion de una base de datos "
        "documental que sistematiza la jurisprudencia del Segundo Tribunal Ambiental de Chile durante el "
        "periodo 2013-2025. Se recopilaron 294 documentos unicos, incluyendo sentencias, resoluciones y "
        "recursos ante la Corte Suprema, los cuales fueron clasificados mediante tecnicas de extraccion "
        "automatizada de metadatos desde el contenido de los archivos PDF. La metodologia permitio "
        "clasificar automaticamente el 94,6% de los documentos.",
        styles['Parrafo']
    ))
    story.append(Paragraph(
        "<b>Palabras clave:</b> Tribunal Ambiental, jurisprudencia, Chile, metodologia, conflictos socioambientales",
        styles['Normal']
    ))
    story.append(Spacer(1, 12))

    # 1. INTRODUCCION
    story.append(Paragraph("1. Introduccion", styles['Subtitulo']))

    story.append(Paragraph("1.1 Contexto institucional", styles['Subtitulo2']))
    story.append(Paragraph(
        "El Segundo Tribunal Ambiental (2TA) de Chile, con sede en Santiago, fue creado por la Ley N 20.600 "
        "(2012) como parte del sistema de justicia ambiental chileno. Su jurisdiccion comprende las regiones "
        "de Valparaiso, Metropolitana, O'Higgins y Maule, concentrando aproximadamente el 40% de la poblacion nacional.",
        styles['Parrafo']
    ))

    story.append(Paragraph("1.2 Competencia del tribunal", styles['Subtitulo2']))
    story.append(Paragraph(
        "De acuerdo con el articulo 17 de la Ley N 20.600, el Segundo Tribunal Ambiental conoce de:",
        styles['Parrafo']
    ))
    story.append(Paragraph("- <b>Reclamaciones (R):</b> Contra resoluciones de la SMA, SEA y Comite de Ministros", styles['Item']))
    story.append(Paragraph("- <b>Demandas por dano ambiental (D):</b> Acciones de reparacion del medio ambiente", styles['Item']))
    story.append(Paragraph("- <b>Solicitudes (S):</b> Autorizaciones para actividades provisorias", styles['Item']))
    story.append(Paragraph("- <b>Consultas (C):</b> Otras materias de competencia del tribunal", styles['Item']))

    story.append(Paragraph("1.3 Objetivos", styles['Subtitulo2']))
    story.append(Paragraph(
        "<b>Objetivo general:</b> Construir una base de datos estructurada de la jurisprudencia del "
        "Segundo Tribunal Ambiental para el periodo 2013-2025.",
        styles['Parrafo']
    ))
    story.append(Paragraph(
        "<b>Objetivos especificos:</b> (1) Recopilar la totalidad de sentencias y resoluciones disponibles; "
        "(2) Desarrollar un sistema de clasificacion automatizada; (3) Extraer metadatos relevantes de cada "
        "documento; (4) Generar estadisticas descriptivas del corpus documental.",
        styles['Parrafo']
    ))

    # 2. METODOLOGIA
    story.append(PageBreak())
    story.append(Paragraph("2. Metodologia", styles['Subtitulo']))

    story.append(Paragraph("2.1 Diseno de investigacion", styles['Subtitulo2']))
    story.append(Paragraph(
        "Se empleo un diseno de investigacion documental de caracter cuantitativo-descriptivo, orientado "
        "a la sistematizacion exhaustiva de fuentes primarias judiciales.",
        styles['Parrafo']
    ))

    story.append(Paragraph("2.2 Fuentes de informacion", styles['Subtitulo2']))
    story.append(Paragraph(
        "Los documentos fueron obtenidos del portal web oficial del Segundo Tribunal Ambiental "
        "(https://www.2ta.cl), la base de datos del Poder Judicial de Chile, y el portal de jurisprudencia "
        "de la Corte Suprema.",
        styles['Parrafo']
    ))

    story.append(Paragraph("2.3 Sistema de clasificacion automatizada", styles['Subtitulo2']))
    story.append(Paragraph(
        "Se desarrollo un sistema de clasificacion en dos fases:",
        styles['Parrafo']
    ))
    story.append(Paragraph(
        "<b>Fase 1 - Extraccion desde nombre de archivo:</b> Se disenaron expresiones regulares (regex) "
        "para capturar metadatos desde la nomenclatura de los archivos.",
        styles['Item']
    ))
    story.append(Paragraph(
        "<b>Fase 2 - Extraccion desde contenido PDF:</b> Para documentos no clasificados en la primera fase, "
        "se implemento extraccion de texto mediante la biblioteca PyMuPDF (fitz), buscando patrones "
        "especificos como 'Rol R N 232-2020' en las primeras paginas.",
        styles['Item']
    ))

    story.append(Paragraph("2.4 Variables extraidas", styles['Subtitulo2']))
    story.append(Paragraph(
        "Las variables extraidas incluyen: tipo de caso (R, D, S, C), numero de rol, ano de ingreso, "
        "fecha de sentencia, tipo de documento, indicador de Corte Suprema, roles acumulados y tamano del archivo.",
        styles['Parrafo']
    ))

    # 3. RESULTADOS
    story.append(PageBreak())
    story.append(Paragraph("3. Resultados", styles['Subtitulo']))

    story.append(Paragraph("3.1 Descripcion del corpus", styles['Subtitulo2']))
    story.append(Paragraph(
        "El corpus documental comprende 294 documentos unicos (588 archivos incluyendo duplicados), "
        "con un tamano total de 593,5 MB. El periodo cubierto abarca desde 2013 hasta 2025.",
        styles['Parrafo']
    ))

    story.append(Paragraph("3.2 Distribucion por tipo de causa", styles['Subtitulo2']))

    # Tabla de distribucion
    data_tipo = [
        ['Tipo', 'Descripcion', 'n', '%'],
        ['R', 'Reclamaciones', '166', '58,7'],
        ['S', 'Solicitudes', '76', '26,9'],
        ['D', 'Demandas por dano ambiental', '35', '12,4'],
        ['C', 'Consultas', '6', '2,1'],
    ]

    tabla_tipo = Table(data_tipo, colWidths=[50, 200, 50, 50])
    tabla_tipo.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(tabla_tipo)
    story.append(Spacer(1, 12))

    # Figura 1: Distribucion por tipo
    fig1 = FIGURAS_DIR / 'figura1_distribucion_tipo.png'
    if fig1.exists():
        story.append(Image(str(fig1), width=400, height=300))
        story.append(Spacer(1, 12))

    story.append(Paragraph("3.3 Distribucion temporal", styles['Subtitulo2']))

    # Tabla temporal
    data_temporal = [
        ['Ano', 'R', 'D', 'S', 'C', 'Total'],
        ['2013', '7', '3', '5', '3', '18'],
        ['2014', '2', '5', '7', '1', '15'],
        ['2015', '0', '2', '5', '1', '8'],
        ['2016', '0', '11', '32', '1', '44'],
        ['2017', '3', '2', '7', '0', '12'],
        ['2018', '3', '1', '5', '0', '9'],
        ['2019', '8', '1', '2', '0', '11'],
        ['2020', '25', '1', '0', '0', '26'],
        ['2021', '25', '1', '4', '0', '30'],
        ['2022', '38', '6', '0', '0', '44'],
        ['2023', '30', '1', '5', '0', '36'],
        ['2024', '16', '1', '1', '0', '18'],
        ['2025', '3', '0', '3', '0', '6'],
        ['Total', '160', '35', '76', '6', '277'],
    ]

    tabla_temp = Table(data_temporal, colWidths=[50, 40, 40, 40, 40, 50])
    tabla_temp.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(tabla_temp)
    story.append(Spacer(1, 12))

    # Figura 2: Evolucion temporal
    fig2 = FIGURAS_DIR / 'figura2_evolucion_temporal.png'
    if fig2.exists():
        story.append(Image(str(fig2), width=480, height=240))
        story.append(Spacer(1, 12))

    story.append(Paragraph("3.4 Calidad de la clasificacion", styles['Subtitulo2']))
    story.append(Paragraph("- Clasificados desde contenido PDF: 133 (45,2%) - Alta confianza", styles['Item']))
    story.append(Paragraph("- Clasificados desde nombre archivo: 145 (49,3%) - Media confianza", styles['Item']))
    story.append(Paragraph("- Requieren revision manual: 16 (5,4%)", styles['Item']))

    # Figura 4: Calidad de clasificacion
    fig4 = FIGURAS_DIR / 'figura4_calidad_clasificacion.png'
    if fig4.exists():
        story.append(Image(str(fig4), width=400, height=250))
        story.append(Spacer(1, 12))

    # 4. DISCUSION
    story.append(PageBreak())
    story.append(Paragraph("4. Discusion", styles['Subtitulo']))

    story.append(Paragraph("4.1 Tendencias observadas", styles['Subtitulo2']))
    story.append(Paragraph(
        "<b>1. Predominio de reclamaciones:</b> Las causas tipo R representan el 58,7% del corpus, "
        "lo que refleja la funcion predominante del tribunal como instancia de control de decisiones "
        "administrativas ambientales.",
        styles['Parrafo']
    ))
    story.append(Paragraph(
        "<b>2. Evolucion temporal diferenciada:</b> Las reclamaciones muestran un crecimiento sostenido "
        "desde 2019, con un peak en 2022 (38 causas). Las solicitudes (S) fueron significativas en 2016 "
        "(32 causas) pero han disminuido drasticamente.",
        styles['Parrafo']
    ))

    # Figura 3: Tendencia de reclamaciones
    fig3 = FIGURAS_DIR / 'figura3_tendencia_reclamaciones.png'
    if fig3.exists():
        story.append(Image(str(fig3), width=450, height=225))
        story.append(Spacer(1, 8))

    story.append(Paragraph(
        "<b>3. Complejidad documental:</b> El mayor tamano promedio de las reclamaciones (2,93 MB) y "
        "demandas (2,42 MB) respecto a las solicitudes (0,25 MB) sugiere mayor complejidad procesal.",
        styles['Parrafo']
    ))

    story.append(Paragraph("4.2 Limitaciones", styles['Subtitulo2']))
    story.append(Paragraph("- La base de datos depende de la disponibilidad de documentos en fuentes publicas", styles['Item']))
    story.append(Paragraph("- Algunos documentos requieren revision manual (5,4%)", styles['Item']))
    story.append(Paragraph("- No se incluyen causas en tramitacion", styles['Item']))

    # 5. CONCLUSIONES
    story.append(Spacer(1, 12))
    story.append(Paragraph("5. Conclusiones", styles['Subtitulo']))
    story.append(Paragraph(
        "Se logro construir una base de datos estructurada de 294 documentos unicos del Segundo Tribunal "
        "Ambiental, abarcando el periodo 2013-2025. El sistema de clasificacion automatizada alcanzo una "
        "efectividad del 94,6%, combinando extraccion de metadatos desde nombres de archivo y contenido PDF.",
        styles['Parrafo']
    ))
    story.append(Paragraph(
        "Los datos revelan una evolucion significativa en la actividad jurisdiccional, con un marcado "
        "incremento de reclamaciones desde 2020, lo que podria asociarse a cambios en la conflictividad "
        "socioambiental o en el acceso a la justicia ambiental.",
        styles['Parrafo']
    ))

    # 6. REFERENCIAS
    story.append(Spacer(1, 12))
    story.append(Paragraph("6. Referencias", styles['Subtitulo']))
    story.append(Paragraph("- Ley N 20.600 que crea los Tribunales Ambientales. Diario Oficial, 28 de junio de 2012.", styles['Item']))
    story.append(Paragraph("- Segundo Tribunal Ambiental. Portal de jurisprudencia. https://www.2ta.cl", styles['Item']))
    story.append(Paragraph("- Bermudez, J. (2014). Fundamentos de Derecho Ambiental. Ediciones UV.", styles['Item']))
    story.append(Paragraph("- Cordero, L. (2015). Lecciones de Derecho Administrativo. Thomson Reuters.", styles['Item']))

    # Generar PDF
    doc.build(story)
    print("PDF generado exitosamente: paper_metodologia.pdf")


if __name__ == '__main__':
    crear_pdf()
