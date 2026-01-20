#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Genera tabla de procedimientos como imagen PNG para previsualización
"""

import matplotlib.pyplot as plt
import numpy as np

# Configuración estilo paper
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif', 'serif'],
    'font.size': 9,
})

fig, ax = plt.subplots(figsize=(7, 3))
ax.axis('off')

# Datos de la tabla
columnas = ['Código', 'Tipo', 'Proporción', 'Descripción']
datos = [
    ['R', 'Reclamaciones', '70%', 'Impugnación de actos administrativos (SMA, SEA, etc.)'],
    ['D', 'Demandas', '12%', 'Acción de reparación por daño ambiental'],
    ['S', 'Solicitudes', '12%', 'Autorizaciones requeridas por la SMA'],
    ['C', 'Consultas', '<1%', 'Consultas de interpretación y procedimientos especiales'],
]

# Crear tabla
tabla = ax.table(
    cellText=datos,
    colLabels=columnas,
    loc='center',
    cellLoc='left',
    colWidths=[0.1, 0.18, 0.12, 0.6]
)

# Estilo
tabla.auto_set_font_size(False)
tabla.set_fontsize(9)
tabla.scale(1, 1.8)

# Encabezados en negrita y gris claro
for i, col in enumerate(columnas):
    cell = tabla[(0, i)]
    cell.set_text_props(fontweight='bold')
    cell.set_facecolor('#e5e5e5')

# Bordes
for key, cell in tabla.get_celld().items():
    cell.set_edgecolor('#333333')
    cell.set_linewidth(0.5)

ax.set_title('Tabla 1: Tipos de procedimientos ante los Tribunales Ambientales de Chile',
             fontsize=10, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig(r'G:\Mi unidad\tribunal_pdf\paper\figuras\tabla1_procedimientos.png',
            dpi=300, bbox_inches='tight', facecolor='white', pad_inches=0.2)
plt.close()

# === Segunda tabla: Cobertura ===
fig, ax = plt.subplots(figsize=(7, 2.5))
ax.axis('off')

columnas2 = ['Tribunal', 'Oficial', 'Corpus', 'Cobertura', 'Período']
datos2 = [
    ['1TA (Antofagasta)', '150', '135', '90,0%', '2017-2024'],
    ['2TA (Santiago)', '620', '583', '94,0%', '2013-2024'],
    ['3TA (Valdivia)', '549', '301', '54,8%', '2013-2024'],
    ['Total', '1.319', '1.019', '77,3%', ''],
]

tabla2 = ax.table(
    cellText=datos2,
    colLabels=columnas2,
    loc='center',
    cellLoc='center',
    colWidths=[0.28, 0.15, 0.15, 0.15, 0.18]
)

tabla2.auto_set_font_size(False)
tabla2.set_fontsize(9)
tabla2.scale(1, 1.8)

for i, col in enumerate(columnas2):
    cell = tabla2[(0, i)]
    cell.set_text_props(fontweight='bold')
    cell.set_facecolor('#e5e5e5')

# Fila total en negrita
for i in range(len(columnas2)):
    cell = tabla2[(4, i)]
    cell.set_text_props(fontweight='bold')
    cell.set_facecolor('#f5f5f5')

for key, cell in tabla2.get_celld().items():
    cell.set_edgecolor('#333333')
    cell.set_linewidth(0.5)

ax.set_title('Tabla 2: Cobertura del corpus respecto a cifras oficiales',
             fontsize=10, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig(r'G:\Mi unidad\tribunal_pdf\paper\figuras\tabla2_cobertura.png',
            dpi=300, bbox_inches='tight', facecolor='white', pad_inches=0.2)
plt.close()

print('Tablas generadas:')
print('  - tabla1_procedimientos.png')
print('  - tabla2_cobertura.png')
