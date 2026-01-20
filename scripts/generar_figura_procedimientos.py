#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Genera figura con los tipos de procedimientos de los Tribunales Ambientales
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

# Configuración
fig, ax = plt.subplots(1, 1, figsize=(14, 18))
ax.set_xlim(0, 14)
ax.set_ylim(0, 18)
ax.axis('off')

# Colores
color_titulo = '#1a365d'
color_r = '#c53030'  # Rojo para Reclamaciones
color_d = '#2f855a'  # Verde para Demandas
color_s = '#2b6cb0'  # Azul para Solicitudes
color_c = '#718096'  # Gris para Consultas
color_tribunal = '#4a5568'

# Función para crear cajas
def caja(x, y, w, h, color, texto, fontsize=10, bold=False, alpha=0.9):
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.1",
                          facecolor=color, edgecolor='#2d3748', linewidth=1.5, alpha=alpha)
    ax.add_patch(rect)
    weight = 'bold' if bold else 'normal'
    text_color = 'white' if color in [color_titulo, color_r, color_d, color_s, color_tribunal] else '#1a202c'
    ax.text(x + w/2, y + h/2, texto, ha='center', va='center', fontsize=fontsize,
            fontweight=weight, wrap=True, color=text_color)

# === TÍTULO PRINCIPAL ===
caja(1, 16.5, 12, 1.2, color_titulo, 'TRIBUNALES AMBIENTALES DE CHILE\n(Ley 20.600, 2012)', fontsize=14, bold=True)

# === TRIBUNALES ===
ax.text(7, 15.9, 'Tres tribunales con jurisdicción territorial', ha='center', va='center',
        fontsize=10, style='italic', color='#4a5568')

caja(1.5, 14.5, 3, 1.1, color_tribunal, '1TA - Antofagasta\n(2017)\nArica a Coquimbo', fontsize=9)
caja(5.5, 14.5, 3, 1.1, color_tribunal, '2TA - Santiago\n(2012)\nValparaíso a Biobío', fontsize=9)
caja(9.5, 14.5, 3, 1.1, color_tribunal, '3TA - Valdivia\n(2013)\nAraucanía a Magallanes', fontsize=9)

# === TIPOS DE PROCEDIMIENTOS - TÍTULO ===
ax.text(7, 13.5, 'TIPOS DE PROCEDIMIENTOS', ha='center', va='center',
        fontsize=13, fontweight='bold', color=color_titulo)
ax.plot([2, 12], [13.2, 13.2], color=color_titulo, linewidth=2)

# === R - RECLAMACIONES ===
caja(0.5, 10.5, 13, 2.5, '#fff5f5', '', alpha=0.5)  # Fondo
caja(0.7, 12.2, 2.2, 0.6, color_r, 'R - RECLAMACIONES', fontsize=10, bold=True)
ax.text(4.5, 12.35, '~70% de las causas', ha='left', va='center',
        fontsize=9, color=color_r, fontweight='bold')

ax.text(1, 11.7, 'Impugnación de actos administrativos ambientales',
        ha='left', va='center', fontsize=10, fontweight='bold', color='#1a202c')
ax.text(1, 11.2, '→ Contra resoluciones de la SMA (sanciones)',
        ha='left', va='center', fontsize=9, color='#4a5568')
ax.text(1, 10.85, '→ Contra resoluciones del SEA (RCA, DIA)',
        ha='left', va='center', fontsize=9, color='#4a5568')
ax.text(7, 11.2, '→ Contra el Comité de Ministros',
        ha='left', va='center', fontsize=9, color='#4a5568')
ax.text(7, 10.85, '→ Contra decretos supremos ambientales',
        ha='left', va='center', fontsize=9, color='#4a5568')

# === D - DEMANDAS ===
caja(0.5, 7.3, 13, 2.9, '#f0fff4', '', alpha=0.5)  # Fondo
caja(0.7, 9.4, 3.5, 0.6, color_d, 'D - DEMANDAS POR DAÑO', fontsize=10, bold=True)
ax.text(5, 9.55, '~12% de las causas', ha='left', va='center',
        fontsize=9, color=color_d, fontweight='bold')

ax.text(1, 8.9, 'Acción de reparación del daño ambiental',
        ha='left', va='center', fontsize=10, fontweight='bold', color='#1a202c')
ax.text(1, 8.45, 'Legitimados activos:', ha='left', va='center',
        fontsize=9, fontweight='bold', color='#4a5568')
ax.text(1, 8.1, '• Personas naturales afectadas', ha='left', va='center', fontsize=9, color='#4a5568')
ax.text(1, 7.75, '• Municipalidades', ha='left', va='center', fontsize=9, color='#4a5568')
ax.text(5.5, 8.1, '• Estado (CDE)', ha='left', va='center', fontsize=9, color='#4a5568')
ax.text(5.5, 7.75, '• Organizaciones ciudadanas', ha='left', va='center', fontsize=9, color='#4a5568')
ax.text(9.5, 8.3, 'Objetivo:\nREPARAR el daño\ncausado al\nmedio ambiente',
        ha='left', va='center', fontsize=9, color=color_d, fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='white', edgecolor=color_d, alpha=0.8))

# === S - SOLICITUDES ===
caja(0.5, 4.5, 13, 2.5, '#ebf8ff', '', alpha=0.5)  # Fondo
caja(0.7, 6.2, 3.2, 0.6, color_s, 'S - SOLICITUDES SMA', fontsize=10, bold=True)
ax.text(4.5, 6.35, '~12% de las causas', ha='left', va='center',
        fontsize=9, color=color_s, fontweight='bold')

ax.text(1, 5.7, 'Autorizaciones que la SMA requiere del Tribunal',
        ha='left', va='center', fontsize=10, fontweight='bold', color='#1a202c')
ax.text(1, 5.25, '→ Clausura temporal o definitiva', ha='left', va='center', fontsize=9, color='#4a5568')
ax.text(1, 4.9, '→ Revocación de RCA', ha='left', va='center', fontsize=9, color='#4a5568')
ax.text(6, 5.25, '→ Medidas provisionales urgentes', ha='left', va='center', fontsize=9, color='#4a5568')
ax.text(9, 5.5, 'Control judicial\nde la potestad\nsancionadora',
        ha='left', va='center', fontsize=9, color=color_s, fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='white', edgecolor=color_s, alpha=0.8))

# === C - CONSULTAS ===
caja(0.5, 3.3, 13, 0.9, '#f7fafc', '', alpha=0.5)  # Fondo
caja(0.7, 3.5, 2.8, 0.5, color_c, 'C - CONSULTAS', fontsize=10, bold=True)
ax.text(4, 3.65, '~1%', ha='left', va='center', fontsize=9, color=color_c, fontweight='bold')
ax.text(5, 3.65, '• Consultas de interpretación  • Procedimientos especiales',
        ha='left', va='center', fontsize=9, color='#4a5568')

# === FLUJO DE RESOLUCIÓN ===
ax.text(7, 2.7, 'RESOLUCIÓN DE CAUSAS', ha='center', va='center',
        fontsize=11, fontweight='bold', color=color_titulo)
ax.plot([2, 12], [2.45, 2.45], color=color_titulo, linewidth=1.5)

# Cajas del flujo
caja(0.8, 1.3, 2.2, 0.9, '#edf2f7', 'INGRESO\nCausa nueva', fontsize=9)
caja(3.5, 1.3, 2.5, 0.9, '#edf2f7', 'TRAMITACIÓN\nAudiencias/Pruebas', fontsize=9)
caja(6.5, 1.3, 2.5, 0.9, '#48bb78', 'SENTENCIA\nDEFINITIVA', fontsize=9, bold=True)
caja(9.5, 1.3, 2.2, 0.9, '#edf2f7', 'CASACIÓN\nCorte Suprema', fontsize=9)
caja(12, 1.3, 1.5, 0.9, '#edf2f7', 'EJECUTORIA', fontsize=9)

# Flechas del flujo
arrow_style = dict(arrowstyle='->', color='#4a5568', lw=1.5)
ax.annotate('', xy=(3.4, 1.75), xytext=(3.05, 1.75), arrowprops=arrow_style)
ax.annotate('', xy=(6.4, 1.75), xytext=(6.05, 1.75), arrowprops=arrow_style)
ax.annotate('', xy=(9.4, 1.75), xytext=(9.05, 1.75), arrowprops=arrow_style)
ax.annotate('', xy=(11.9, 1.75), xytext=(11.75, 1.75), arrowprops=arrow_style)

# === PIE ===
ax.text(7, 0.5, 'Fuente: Ley 20.600 (2012) que crea los Tribunales Ambientales',
        ha='center', va='center', fontsize=8, style='italic', color='#718096')

plt.tight_layout()
plt.savefig(r'G:\Mi unidad\tribunal_pdf\paper\figuras\fig0_tipos_procedimientos.png',
            dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
plt.close()

print('Figura guardada: paper/figuras/fig0_tipos_procedimientos.png')
