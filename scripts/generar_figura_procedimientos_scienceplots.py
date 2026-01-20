#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Figura académica: Tipos de procedimientos de los Tribunales Ambientales
Estilo paper usando SciencePlots - estándar IEEE/Nature
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np

# Intentar usar SciencePlots si está disponible
try:
    import scienceplots
    plt.style.use(['science', 'no-latex'])  # Estilo científico sin LaTeX
except ImportError:
    print("SciencePlots no disponible, usando estilo manual")

# Configuración estilo paper científico
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif', 'serif'],
    'font.size': 9,
    'axes.linewidth': 0.5,
    'axes.labelsize': 9,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'legend.fontsize': 8,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'text.usetex': False,
})

fig, ax = plt.subplots(figsize=(7, 5))  # Tamaño típico de figura de journal
ax.set_xlim(0, 10)
ax.set_ylim(0, 7)
ax.axis('off')

# Colores minimalistas (escala de grises para compatibilidad B/N)
negro = '#000000'
gris_80 = '#333333'
gris_60 = '#666666'
gris_40 = '#999999'
gris_20 = '#cccccc'
gris_10 = '#e5e5e5'
blanco = '#ffffff'

# === TÍTULO ===
ax.text(5, 6.7, 'Competencias de los Tribunales Ambientales de Chile',
        ha='center', va='center', fontsize=11, fontweight='bold', color=negro)
ax.text(5, 6.45, 'Ley 20.600, artículos 17 y 18',
        ha='center', va='center', fontsize=8, style='italic', color=gris_60)

# Línea separadora título
ax.plot([1, 9], [6.25, 6.25], color=gris_40, linewidth=0.5)

# === CAJA PRINCIPAL: TRIBUNAL AMBIENTAL ===
rect_ta = Rectangle((2.5, 5.5), 5, 0.6, facecolor=gris_10,
                     edgecolor=negro, linewidth=0.8)
ax.add_patch(rect_ta)
ax.text(5, 5.8, 'TRIBUNAL AMBIENTAL', ha='center', va='center',
        fontsize=10, fontweight='bold', color=negro)

# Líneas de conexión (estilo árbol jerárquico)
ax.plot([5, 5], [5.5, 5.1], color=negro, linewidth=0.6)
ax.plot([1.5, 8.5], [5.1, 5.1], color=negro, linewidth=0.6)

# Líneas verticales a cada tipo
posiciones_x = [1.5, 3.83, 6.17, 8.5]
for x in posiciones_x:
    ax.plot([x, x], [5.1, 4.8], color=negro, linewidth=0.6)

# === CUATRO TIPOS DE PROCEDIMIENTOS ===
tipos = [
    {'x': 1.5, 'cod': 'R', 'nombre': 'Reclamaciones', 'pct': '70%',
     'desc': 'Impugnación de\nactos administrativos'},
    {'x': 3.83, 'cod': 'D', 'nombre': 'Demandas', 'pct': '12%',
     'desc': 'Reparación de\ndaño ambiental'},
    {'x': 6.17, 'cod': 'S', 'nombre': 'Solicitudes', 'pct': '12%',
     'desc': 'Autorizaciones\nrequeridas por SMA'},
    {'x': 8.5, 'cod': 'C', 'nombre': 'Consultas', 'pct': '<1%',
     'desc': 'Interpretación\ny otros'},
]

for t in tipos:
    # Caja del código
    rect = Rectangle((t['x']-0.7, 4.1), 1.4, 0.65,
                      facecolor=blanco, edgecolor=negro, linewidth=0.8)
    ax.add_patch(rect)

    # Código y porcentaje
    ax.text(t['x'], 4.55, t['cod'], ha='center', va='center',
            fontsize=12, fontweight='bold', color=negro)
    ax.text(t['x'], 4.25, f"({t['pct']})", ha='center', va='center',
            fontsize=7, color=gris_60)

    # Nombre del procedimiento
    ax.text(t['x'], 3.85, t['nombre'], ha='center', va='center',
            fontsize=8, fontweight='bold', color=negro)

    # Descripción breve
    ax.text(t['x'], 3.45, t['desc'], ha='center', va='center',
            fontsize=7, color=gris_60, linespacing=1.1)

# === SECCIÓN DE DETALLE ===
ax.plot([0.5, 9.5], [2.9, 2.9], color=gris_40, linewidth=0.5, linestyle='-')
ax.text(5, 2.7, 'Detalle de competencias', ha='center', va='center',
        fontsize=9, fontweight='bold', color=gris_80)

# Detalles por tipo
y_det = 2.3
detalles = [
    {'x': 1.5, 'titulo': 'R - Contra:',
     'items': ['SMA (sanciones)', 'SEA (RCA, DIA)', 'Comité Ministros', 'D.S. ambientales']},
    {'x': 3.83, 'titulo': 'D - Legitimados:',
     'items': ['Personas afectadas', 'Municipalidades', 'Estado (CDE)', 'Organizaciones']},
    {'x': 6.17, 'titulo': 'S - Medidas:',
     'items': ['Clausura', 'Revocación RCA', 'Medidas urgentes', 'Control judicial']},
    {'x': 8.5, 'titulo': 'C - Otros:',
     'items': ['Interpretación', 'Procedimientos', 'especiales']},
]

for d in detalles:
    ax.text(d['x'], y_det, d['titulo'], ha='center', va='top',
            fontsize=7, fontweight='bold', color=negro)
    for i, item in enumerate(d['items']):
        ax.text(d['x'], y_det - 0.22 - i*0.18, f"• {item}", ha='center', va='top',
                fontsize=6, color=gris_60)

# === FLUJO PROCESAL ===
ax.plot([0.5, 9.5], [1.05, 1.05], color=gris_40, linewidth=0.5, linestyle='-')
ax.text(5, 0.88, 'Flujo procesal', ha='center', va='center',
        fontsize=9, fontweight='bold', color=gris_80)

# Cajas del flujo
flujo_y = 0.45
flujo_items = ['Ingreso', 'Tramitación', 'Sentencia', 'Casación\n(C. Suprema)', 'Ejecutoria']
flujo_x = [1.2, 3.0, 5.0, 7.0, 8.8]

for i, (x, item) in enumerate(zip(flujo_x, flujo_items)):
    w = 1.3
    es_sentencia = (i == 2)
    rect = Rectangle((x-w/2, flujo_y-0.15), w, 0.4,
                      facecolor=gris_10 if es_sentencia else blanco,
                      edgecolor=negro, linewidth=0.6)
    ax.add_patch(rect)
    ax.text(x, flujo_y+0.05, item, ha='center', va='center', fontsize=6,
            fontweight='bold' if es_sentencia else 'normal', color=negro)

    # Flechas
    if i < len(flujo_items) - 1:
        ax.annotate('', xy=(flujo_x[i+1]-w/2-0.05, flujo_y+0.05),
                   xytext=(x+w/2+0.05, flujo_y+0.05),
                   arrowprops=dict(arrowstyle='->', color=negro, lw=0.5))

# === NOTA AL PIE ===
ax.text(5, 0.05, 'Fuente: Elaboración propia a partir de Ley 20.600 (2012)',
        ha='center', va='center', fontsize=6, style='italic', color=gris_60)

plt.tight_layout()
plt.savefig(r'G:\Mi unidad\tribunal_pdf\paper\figuras\fig0_tipos_procedimientos.png',
            dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none',
            pad_inches=0.1)
plt.savefig(r'G:\Mi unidad\tribunal_pdf\paper\figuras\fig0_tipos_procedimientos.pdf',
            bbox_inches='tight', facecolor='white', edgecolor='none',
            pad_inches=0.1)
plt.close()

print('Figuras guardadas:')
print('  - fig0_tipos_procedimientos.png (300 DPI)')
print('  - fig0_tipos_procedimientos.pdf (vectorial)')
