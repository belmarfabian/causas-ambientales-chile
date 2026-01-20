#!/usr/bin/env python3
"""
Actualiza gráficos usando datos de causas consolidadas
"""

import json
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# Configuración estilo paper
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 10,
    'axes.linewidth': 0.5,
})

DATA_FILE = Path(r"G:\Mi unidad\tribunal_pdf\datos\causas_consolidadas.json")
OUTPUT_DIR = Path(r"G:\Mi unidad\tribunal_pdf\paper\figuras")

def load_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def fig1_por_tribunal(data):
    """Distribución por tribunal"""
    stats = data['estadisticas']['por_tribunal']
    tribunales = ['1TA', '2TA', '3TA']
    valores = [stats.get(t, 0) for t in tribunales]
    colores = ['#666666', '#333333', '#999999']

    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(tribunales, valores, color=colores, edgecolor='black', linewidth=0.5)

    ax.set_xlabel('Tribunal Ambiental', fontsize=10)
    ax.set_ylabel('Número de Causas', fontsize=10)
    ax.set_title('Distribución de Causas por Tribunal', fontsize=11, fontweight='bold')

    for bar, val in zip(bars, valores):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                f'{val}', ha='center', va='bottom', fontsize=10)

    ax.set_xticklabels(['1TA\n(Antofagasta)', '2TA\n(Santiago)', '3TA\n(Valdivia)'])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig1_por_tribunal.png', dpi=300, facecolor='white')
    plt.close()
    print("  fig1_por_tribunal.png")

def fig2_temporal(data):
    """Evolución temporal"""
    stats = data['estadisticas']['por_year']
    años = sorted([int(y) for y in stats.keys() if 2013 <= int(y) <= 2025])
    valores = [stats.get(str(y), 0) for y in años]

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(años, valores, marker='o', linewidth=1.5, markersize=6, color='#333333')
    ax.fill_between(años, valores, alpha=0.2, color='#666666')

    ax.set_xlabel('Año', fontsize=10)
    ax.set_ylabel('Causas Ingresadas', fontsize=10)
    ax.set_title('Evolución Temporal de Causas (2013-2025)', fontsize=11, fontweight='bold')
    ax.set_xticks(años)
    ax.set_xticklabels(años, rotation=45)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig2_temporal.png', dpi=300, facecolor='white')
    plt.close()
    print("  fig2_temporal.png")

def fig3_temporal_tribunal(data):
    """Evolución temporal por tribunal"""
    causas = data['causas']

    # Agrupar por año y tribunal
    por_año_tribunal = {}
    for c in causas:
        y = c.get('year', 0)
        t = c.get('tribunal', 'Unknown')
        if 2013 <= y <= 2025:
            if y not in por_año_tribunal:
                por_año_tribunal[y] = {'1TA': 0, '2TA': 0, '3TA': 0}
            if t in por_año_tribunal[y]:
                por_año_tribunal[y][t] += 1

    años = sorted(por_año_tribunal.keys())

    fig, ax = plt.subplots(figsize=(10, 5))

    for tribunal, color, marker in [('1TA', '#666666', 's'), ('2TA', '#333333', 'o'), ('3TA', '#999999', '^')]:
        valores = [por_año_tribunal[y].get(tribunal, 0) for y in años]
        ax.plot(años, valores, marker=marker, linewidth=1.5, markersize=5,
                color=color, label=tribunal)

    ax.set_xlabel('Año', fontsize=10)
    ax.set_ylabel('Causas Ingresadas', fontsize=10)
    ax.set_title('Evolución Temporal por Tribunal', fontsize=11, fontweight='bold')
    ax.set_xticks(años)
    ax.set_xticklabels(años, rotation=45)
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig3_temporal_tribunal.png', dpi=300, facecolor='white')
    plt.close()
    print("  fig3_temporal_tribunal.png")

def fig4_por_tipo(data):
    """Distribución por tipo de procedimiento"""
    stats = data['estadisticas']['por_tipo']
    tipos = ['R', 'D', 'S']
    nombres = ['Reclamaciones', 'Demandas', 'Solicitudes']
    valores = [stats.get(t, 0) for t in tipos]
    colores = ['#333333', '#666666', '#999999']

    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(nombres, valores, color=colores, edgecolor='black', linewidth=0.5)

    ax.set_ylabel('Número de Causas', fontsize=10)
    ax.set_title('Distribución por Tipo de Procedimiento', fontsize=11, fontweight='bold')

    total = sum(valores)
    for bar, val in zip(bars, valores):
        pct = val/total*100
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                f'{val}\n({pct:.1f}%)', ha='center', va='bottom', fontsize=9)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig4_por_tipo.png', dpi=300, facecolor='white')
    plt.close()
    print("  fig4_por_tipo.png")

def fig5_pie_tribunal(data):
    """Pie chart por tribunal"""
    stats = data['estadisticas']['por_tribunal']
    tribunales = ['1TA', '2TA', '3TA']
    valores = [stats.get(t, 0) for t in tribunales]
    colores = ['#666666', '#333333', '#999999']
    labels = [f'{t}\n({v})' for t, v in zip(tribunales, valores)]

    fig, ax = plt.subplots(figsize=(6, 6))
    wedges, texts, autotexts = ax.pie(valores, labels=labels, colors=colores,
                                       autopct='%1.1f%%', startangle=90,
                                       wedgeprops={'edgecolor': 'white', 'linewidth': 1})

    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(10)

    ax.set_title('Proporción de Causas por Tribunal', fontsize=11, fontweight='bold')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig5_pie_tribunal.png', dpi=300, facecolor='white')
    plt.close()
    print("  fig5_pie_tribunal.png")

if __name__ == '__main__':
    print("Actualizando gráficos con datos de causas...")
    data = load_data()

    print(f"Total causas: {data['metadata']['total_causas']}")

    fig1_por_tribunal(data)
    fig2_temporal(data)
    fig3_temporal_tribunal(data)
    fig4_por_tipo(data)
    fig5_pie_tribunal(data)

    print("\nGráficos actualizados!")
