#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Figura académica: Tipos de procedimientos de los Tribunales Ambientales
Estilo paper: sobrio, blanco/negro, formal
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

# Configuración estilo paper
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.linewidth'] = 0.5

fig, ax = plt.subplots(figsize=(10, 7))
ax.set_xlim(0, 10)
ax.set_ylim(0, 7)
ax.axis('off')

# Colores sobrios
negro = '#000000'
gris_oscuro = '#333333'
gris_medio = '#666666'
gris_claro = '#999999'
blanco = '#ffffff'
gris_fondo = '#f5f5f5'

# === TÍTULO ===
ax.text(5, 6.6, 'Competencias de los Tribunales Ambientales de Chile',
        ha='center', va='center', fontsize=12, fontweight='bold', color=negro)
ax.text(5, 6.3, '(Ley 20.600, artículos 17 y 18)',
        ha='center', va='center', fontsize=9, style='italic', color=gris_medio)

# === CAJA PRINCIPAL: TRIBUNAL AMBIENTAL ===
rect_ta = FancyBboxPatch((1, 5.2), 8, 0.8, boxstyle="round,pad=0.02,rounding_size=0.05",
                          facecolor=gris_fondo, edgecolor=negro, linewidth=1)
ax.add_patch(rect_ta)
ax.text(5, 5.6, 'TRIBUNAL AMBIENTAL', ha='center', va='center',
        fontsize=11, fontweight='bold', color=negro)

# Línea vertical desde TA
ax.plot([5, 5], [5.2, 4.8], color=negro, linewidth=1)
ax.plot([1.5, 8.5], [4.8, 4.8], color=negro, linewidth=1)

# Líneas verticales a cada tipo
for x in [1.5, 3.83, 6.17, 8.5]:
    ax.plot([x, x], [4.8, 4.5], color=negro, linewidth=1)

# === CUATRO TIPOS DE PROCEDIMIENTOS ===

# Función para caja de procedimiento
def caja_procedimiento(x, y, codigo, nombre, porcentaje, descripcion):
    # Caja del código
    rect = FancyBboxPatch((x-0.9, y), 1.8, 0.6, boxstyle="round,pad=0.01,rounding_size=0.03",
                          facecolor=blanco, edgecolor=negro, linewidth=1)
    ax.add_patch(rect)
    ax.text(x, y+0.38, codigo, ha='center', va='center', fontsize=10, fontweight='bold', color=negro)
    ax.text(x, y+0.15, f'({porcentaje})', ha='center', va='center', fontsize=8, color=gris_medio)

    # Nombre debajo
    ax.text(x, y-0.2, nombre, ha='center', va='center', fontsize=8, fontweight='bold', color=negro)

    # Descripción
    ax.text(x, y-0.5, descripcion, ha='center', va='center', fontsize=7, color=gris_oscuro,
            wrap=True, linespacing=1.2)

# R - Reclamaciones
caja_procedimiento(1.5, 3.8, 'R', 'Reclamaciones', '~70%',
                   'Impugnación de\nactos administrativos')

# D - Demandas
caja_procedimiento(3.83, 3.8, 'D', 'Demandas', '~12%',
                   'Reparación de\ndaño ambiental')

# S - Solicitudes
caja_procedimiento(6.17, 3.8, 'S', 'Solicitudes', '~12%',
                   'Autorizaciones\nrequeridas por SMA')

# C - Consultas
caja_procedimiento(8.5, 3.8, 'C', 'Consultas', '~1%',
                   'Interpretación\ny otros')

# === DETALLE DE CADA TIPO ===
y_detalle = 2.3

# Línea separadora
ax.plot([0.5, 9.5], [2.7, 2.7], color=gris_claro, linewidth=0.5, linestyle='--')

ax.text(5, 2.55, 'Detalle de procedimientos', ha='center', va='center',
        fontsize=9, fontweight='bold', color=gris_oscuro)

# R - Detalle
ax.text(1.5, y_detalle, 'R - Reclamaciones contra:', ha='center', va='top',
        fontsize=8, fontweight='bold', color=negro)
detalles_r = ['• SMA (sanciones)', '• SEA (RCA, DIA)', '• Comité de Ministros', '• Decretos supremos']
for i, d in enumerate(detalles_r):
    ax.text(1.5, y_detalle - 0.25 - i*0.22, d, ha='center', va='top', fontsize=7, color=gris_oscuro)

# D - Detalle
ax.text(3.83, y_detalle, 'D - Legitimados:', ha='center', va='top',
        fontsize=8, fontweight='bold', color=negro)
detalles_d = ['• Personas afectadas', '• Municipalidades', '• Estado (CDE)', '• Organizaciones']
for i, d in enumerate(detalles_d):
    ax.text(3.83, y_detalle - 0.25 - i*0.22, d, ha='center', va='top', fontsize=7, color=gris_oscuro)

# S - Detalle
ax.text(6.17, y_detalle, 'S - Medidas graves:', ha='center', va='top',
        fontsize=8, fontweight='bold', color=negro)
detalles_s = ['• Clausura', '• Revocación RCA', '• Medidas urgentes', '• Control judicial']
for i, d in enumerate(detalles_s):
    ax.text(6.17, y_detalle - 0.25 - i*0.22, d, ha='center', va='top', fontsize=7, color=gris_oscuro)

# C - Detalle
ax.text(8.5, y_detalle, 'C - Otros:', ha='center', va='top',
        fontsize=8, fontweight='bold', color=negro)
detalles_c = ['• Interpretación', '• Procedimientos', '  especiales']
for i, d in enumerate(detalles_c):
    ax.text(8.5, y_detalle - 0.25 - i*0.22, d, ha='center', va='top', fontsize=7, color=gris_oscuro)

# === FLUJO DE RESOLUCIÓN ===
ax.plot([0.5, 9.5], [1.0, 1.0], color=gris_claro, linewidth=0.5, linestyle='--')
ax.text(5, 0.85, 'Flujo procesal', ha='center', va='center',
        fontsize=9, fontweight='bold', color=gris_oscuro)

# Cajas del flujo
flujo_y = 0.4
flujo_items = ['Ingreso', 'Tramitación', 'Sentencia', 'Casación (CS)', 'Ejecutoria']
flujo_x = [1, 2.8, 4.8, 6.8, 8.8]

for i, (x, item) in enumerate(zip(flujo_x, flujo_items)):
    w = 1.4 if i < 4 else 1.0
    rect = FancyBboxPatch((x-w/2, flujo_y-0.15), w, 0.35,
                          boxstyle="round,pad=0.01,rounding_size=0.02",
                          facecolor=blanco if i != 2 else gris_fondo,
                          edgecolor=negro, linewidth=0.8)
    ax.add_patch(rect)
    ax.text(x, flujo_y, item, ha='center', va='center', fontsize=7,
            fontweight='bold' if i == 2 else 'normal', color=negro)

    # Flechas
    if i < len(flujo_items) - 1:
        ax.annotate('', xy=(flujo_x[i+1]-0.75, flujo_y), xytext=(x+w/2+0.05, flujo_y),
                   arrowprops=dict(arrowstyle='->', color=negro, lw=0.8))

plt.tight_layout()
plt.savefig(r'G:\Mi unidad\tribunal_pdf\paper\figuras\fig0_tipos_procedimientos.png',
            dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
plt.close()

print('Figura académica guardada: fig0_tipos_procedimientos.png')
