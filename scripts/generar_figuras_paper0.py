#!/usr/bin/env python3
"""
Genera figuras para Paper 0: Conflictos Socioecológicos en Chile.
"""

import json
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# Configuración para español
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 11

BASE_DIR = Path(__file__).parent.parent
DATOS_DIR = BASE_DIR / "datos" / "conflictos"
OUTPUT_DIR = BASE_DIR / "paper" / "figuras"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def cargar_datos():
    """Carga datos de conflictos."""
    with open(DATOS_DIR / "indh_conflictos.json", encoding="utf-8") as f:
        return json.load(f)

def figura_sectores(data):
    """Genera figura de conflictos por sector económico."""
    from collections import Counter

    sectores = Counter()
    for c in data:
        sector = c.get('sectorProductivo', {})
        if isinstance(sector, dict):
            nombre = sector.get('nombreSector', 'Sin dato')
        else:
            nombre = 'Sin dato'
        sectores[nombre] += 1

    # Top 8 sectores
    top = sectores.most_common(8)
    nombres = [s[0] for s in top]
    valores = [s[1] for s in top]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(range(len(nombres)), valores, color='#2E86AB')
    ax.set_yticks(range(len(nombres)))
    ax.set_yticklabels(nombres)
    ax.invert_yaxis()
    ax.set_xlabel('Número de conflictos')
    ax.set_title('Conflictos socioambientales por sector económico (INDH, 2026)')

    # Añadir valores
    for bar, val in zip(bars, valores):
        ax.text(val + 0.5, bar.get_y() + bar.get_height()/2, str(val),
                va='center', fontsize=10)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "conflictos_sector.pdf", dpi=300, bbox_inches='tight')
    plt.savefig(OUTPUT_DIR / "conflictos_sector.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Guardado: conflictos_sector.pdf")

def figura_estados(data):
    """Genera figura de conflictos por estado."""
    from collections import Counter

    estados = Counter()
    for c in data:
        estado = c.get('estadoConflico', {})
        if isinstance(estado, dict):
            nombre = estado.get('glosa', 'Sin dato')
        else:
            nombre = 'Sin dato'
        estados[nombre] += 1

    # Ordenar
    orden = ['Activo', 'Latente', 'Cerrado', 'Archivado']
    nombres = [e for e in orden if e in estados]
    valores = [estados[e] for e in nombres]
    colores = ['#E63946', '#F4A261', '#2A9D8F', '#264653']

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(nombres, valores, color=colores[:len(nombres)])
    ax.set_ylabel('Número de conflictos')
    ax.set_title('Estado de los conflictos socioambientales (INDH, 2026)')

    # Añadir valores
    for bar, val in zip(bars, valores):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, str(val),
                ha='center', fontsize=11, fontweight='bold')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "conflictos_estado.pdf", dpi=300, bbox_inches='tight')
    plt.savefig(OUTPUT_DIR / "conflictos_estado.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Guardado: conflictos_estado.pdf")

def figura_regiones(data):
    """Genera figura de conflictos por región."""
    from collections import Counter

    regiones = Counter()
    for c in data:
        region = c.get('region', {})
        if isinstance(region, dict):
            nombre = region.get('nombreRegion', None)
        else:
            nombre = region
        if nombre:
            # Abreviar nombres largos
            abrev = {
                'Metropolitana de Santiago': 'Metropolitana',
                'Magallanes y la Antártica Chilena': 'Magallanes',
                'Arica y Parinacota': 'Arica y Parinacota',
            }
            nombre = abrev.get(nombre, nombre)
            regiones[nombre] += 1

    # Ordenar de norte a sur (aproximado)
    orden_ns = [
        'Arica y Parinacota', 'Tarapacá', 'Antofagasta', 'Atacama',
        'Coquimbo', 'Valparaíso', 'Metropolitana', 'O\'Higgins',
        'Maule', 'Ñuble', 'Biobío', 'La Araucanía', 'Los Ríos',
        'Los Lagos', 'Aysén', 'Magallanes'
    ]

    nombres = [r for r in orden_ns if r in regiones]
    valores = [regiones[r] for r in nombres]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(range(len(nombres)), valores, color='#457B9D')
    ax.set_xticks(range(len(nombres)))
    ax.set_xticklabels(nombres, rotation=45, ha='right', fontsize=9)
    ax.set_ylabel('Número de conflictos')
    ax.set_title('Distribución geográfica de conflictos socioambientales (INDH, 2026)')

    # Añadir valores
    for bar, val in zip(bars, valores):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3, str(val),
                    ha='center', fontsize=9)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "conflictos_region.pdf", dpi=300, bbox_inches='tight')
    plt.savefig(OUTPUT_DIR / "conflictos_region.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Guardado: conflictos_region.pdf")

def main():
    print("Generando figuras para Paper 0...")
    data = cargar_datos()
    print(f"Cargados {len(data)} conflictos del INDH")

    figura_sectores(data)
    figura_estados(data)
    figura_regiones(data)

    print(f"\nFiguras guardadas en: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
