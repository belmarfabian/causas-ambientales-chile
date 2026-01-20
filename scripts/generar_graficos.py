#!/usr/bin/env python3
"""
Genera gráficos para el paper de justicia ambiental
"""

import json
import sys
from pathlib import Path

# Intentar importar matplotlib
try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Backend sin GUI
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("matplotlib no disponible. Generando solo datos para gráficos.")

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

STATS_FILE = Path(r"G:\Mi unidad\tribunal_pdf\datos\estadisticas\estadisticas_corpus.json")
OUTPUT_DIR = Path(r"G:\Mi unidad\tribunal_pdf\paper\figuras")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_stats():
    """Carga estadísticas"""
    with open(STATS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def plot_by_tribunal(stats):
    """Gráfico de documentos por tribunal"""
    if not HAS_MATPLOTLIB:
        return

    tribunales = ['1TA', '2TA', '3TA']
    valores = [stats['por_tribunal'].get(t, 0) for t in tribunales]
    colores = ['#3498db', '#e74c3c', '#2ecc71']

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(tribunales, valores, color=colores, edgecolor='black')

    ax.set_xlabel('Tribunal Ambiental', fontsize=12)
    ax.set_ylabel('Número de Documentos', fontsize=12)
    ax.set_title('Distribución de Documentos por Tribunal Ambiental', fontsize=14)

    # Etiquetas en barras
    for bar, val in zip(bars, valores):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 20,
                f'{val:,}', ha='center', va='bottom', fontsize=11)

    # Nombres completos
    ax.set_xticklabels(['1TA\n(Antofagasta)', '2TA\n(Santiago)', '3TA\n(Valdivia)'])

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig1_por_tribunal.png', dpi=150)
    plt.close()
    print(f"  Guardado: fig1_por_tribunal.png")

def plot_temporal(stats):
    """Gráfico de evolución temporal"""
    if not HAS_MATPLOTLIB:
        return

    años = sorted([int(y) for y in stats['por_año'].keys()])
    valores = [stats['por_año'].get(str(y), 0) for y in años]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(años, valores, marker='o', linewidth=2, markersize=8, color='#2c3e50')
    ax.fill_between(años, valores, alpha=0.3, color='#3498db')

    ax.set_xlabel('Año', fontsize=12)
    ax.set_ylabel('Número de Documentos', fontsize=12)
    ax.set_title('Evolución Temporal de Documentos Judiciales Ambientales', fontsize=14)
    ax.set_xticks(años)
    ax.set_xticklabels(años, rotation=45)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig2_temporal.png', dpi=150)
    plt.close()
    print(f"  Guardado: fig2_temporal.png")

def plot_temporal_stacked(stats):
    """Gráfico de evolución temporal por tribunal (apilado)"""
    if not HAS_MATPLOTLIB:
        return

    años = sorted([int(y) for y in stats['por_año'].keys()])
    tribunales = ['1TA', '2TA', '3TA']
    colores = ['#3498db', '#e74c3c', '#2ecc71']

    data = {t: [stats['por_tribunal_año'].get(t, {}).get(str(y), 0) for y in años]
            for t in tribunales}

    fig, ax = plt.subplots(figsize=(10, 6))

    bottom = [0] * len(años)
    for t, color in zip(tribunales, colores):
        ax.bar(años, data[t], bottom=bottom, label=t, color=color, edgecolor='white')
        bottom = [b + d for b, d in zip(bottom, data[t])]

    ax.set_xlabel('Año', fontsize=12)
    ax.set_ylabel('Número de Documentos', fontsize=12)
    ax.set_title('Documentos por Año y Tribunal', fontsize=14)
    ax.legend(title='Tribunal')
    ax.set_xticks(años)
    ax.set_xticklabels(años, rotation=45)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig3_temporal_tribunal.png', dpi=150)
    plt.close()
    print(f"  Guardado: fig3_temporal_tribunal.png")

def plot_by_type(stats):
    """Gráfico de documentos por tipo"""
    if not HAS_MATPLOTLIB:
        return

    # Top 8 tipos
    tipos = sorted(stats['por_tipo'].items(), key=lambda x: -x[1])[:8]
    nombres = [t[0] for t in tipos]
    valores = [t[1] for t in tipos]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(nombres[::-1], valores[::-1], color='#9b59b6', edgecolor='black')

    ax.set_xlabel('Número de Documentos', fontsize=12)
    ax.set_title('Tipos de Documentos más Frecuentes', fontsize=14)

    # Etiquetas
    for bar, val in zip(bars, valores[::-1]):
        ax.text(val + 10, bar.get_y() + bar.get_height()/2,
                f'{val:,}', ha='left', va='center', fontsize=10)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig4_por_tipo.png', dpi=150)
    plt.close()
    print(f"  Guardado: fig4_por_tipo.png")

def plot_pie_tribunal(stats):
    """Gráfico de torta por tribunal"""
    if not HAS_MATPLOTLIB:
        return

    tribunales = ['1TA (Antofagasta)', '2TA (Santiago)', '3TA (Valdivia)']
    valores = [stats['por_tribunal'].get(t.split()[0], 0) for t in ['1TA', '2TA', '3TA']]
    colores = ['#3498db', '#e74c3c', '#2ecc71']

    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(valores, labels=tribunales, autopct='%1.1f%%',
                                       colors=colores, startangle=90,
                                       explode=(0.02, 0.02, 0.02))

    ax.set_title('Distribución Porcentual por Tribunal', fontsize=14)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig5_pie_tribunal.png', dpi=150)
    plt.close()
    print(f"  Guardado: fig5_pie_tribunal.png")

def generate_text_tables(stats):
    """Genera tablas en formato texto para copiar al paper"""
    output = []

    output.append("=" * 60)
    output.append("TABLAS PARA EL PAPER")
    output.append("=" * 60)

    # Tabla 1: Por tribunal
    output.append("\nTABLA 1: Documentos por Tribunal")
    output.append("-" * 40)
    total = sum(stats['por_tribunal'].values())
    for t in ['1TA', '2TA', '3TA']:
        val = stats['por_tribunal'].get(t, 0)
        pct = val / total * 100
        output.append(f"  {t}: {val:,} ({pct:.1f}%)")
    output.append(f"  TOTAL: {total:,}")

    # Tabla 2: Por año
    output.append("\nTABLA 2: Documentos por Año")
    output.append("-" * 40)
    for year in sorted(stats['por_año'].keys()):
        output.append(f"  {year}: {stats['por_año'][year]}")

    # Tabla 3: Por tipo
    output.append("\nTABLA 3: Documentos por Tipo")
    output.append("-" * 40)
    for tipo, count in sorted(stats['por_tipo'].items(), key=lambda x: -x[1]):
        pct = count / total * 100
        output.append(f"  {tipo}: {count} ({pct:.1f}%)")

    # Guardar
    with open(OUTPUT_DIR / 'tablas.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    print(f"  Guardado: tablas.txt")
    return '\n'.join(output)

def main():
    print("=" * 60)
    print("GENERANDO GRÁFICOS PARA EL PAPER")
    print("=" * 60)

    stats = load_stats()

    if HAS_MATPLOTLIB:
        print("\nGenerando gráficos...")
        plot_by_tribunal(stats)
        plot_temporal(stats)
        plot_temporal_stacked(stats)
        plot_by_type(stats)
        plot_pie_tribunal(stats)
    else:
        print("\nMatplotlib no disponible. Instalando...")
        import subprocess
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'matplotlib'], check=True)
        print("Matplotlib instalado. Ejecuta el script de nuevo.")

    print("\nGenerando tablas de texto...")
    tables = generate_text_tables(stats)
    print(tables)

    print(f"\n{'=' * 60}")
    print(f"Archivos en: {OUTPUT_DIR}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()
