#!/usr/bin/env python3
"""
Geocodificación de conflictos ambientales del Tribunal Ambiental de Chile.
Extrae ubicaciones de sentencias y genera mapas estáticos e interactivos.

Uso:
    python geocodificar_conflictos.py
"""

import json
import re
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Agregar el directorio de scripts al path para importar módulos locales
sys.path.insert(0, str(Path(__file__).parent))

from datos_geograficos_chile import (
    COMUNAS_CHILE, REGIONES_CHILE, JURISDICCION_TRIBUNALES,
    buscar_comuna, buscar_region, get_coords_tribunal, normalizar_nombre
)

# ============================================================
# CONFIGURACIÓN
# ============================================================
BASE_DIR = Path(__file__).parent.parent
TEXTOS_DIR = BASE_DIR / "corpus" / "textos"
CAUSAS_FILE = BASE_DIR / "datos" / "sentencias" / "causas_unicas.json"
OUTPUT_DIR = BASE_DIR / "datos" / "geografico"
FIGURAS_DIR = BASE_DIR / "paper" / "figuras"

# ============================================================
# PATRONES REGEX PARA EXTRACCIÓN DE UBICACIONES
# ============================================================
PATRONES = {
    # "comuna de [NOMBRE]" o "Comuna de [NOMBRE]"
    "comuna": re.compile(
        r'[Cc]omuna\s+de\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+(?:de\s+)?[A-ZÁÉÍÓÚÑ]?[a-záéíóúñ]+)*)',
        re.UNICODE
    ),

    # "Región de [NOMBRE]" o "Región [NOMBRE]" o "Región Metropolitana"
    "region": re.compile(
        r'[Rr]egi[oó]n\s+(?:de\s+)?(?:la\s+)?([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+(?:y\s+)?[A-ZÁÉÍÓÚÑ]?[a-záéíóúñ\']+)*)',
        re.UNICODE
    ),

    # "ubicado/a en [lugar]"
    "ubicado": re.compile(
        r'ubicad[oa]\s+en\s+(?:el\s+|la\s+)?(.+?)(?:,\s*(?:comuna|provincia|[Rr]egi[oó]n)|\.)',
        re.UNICODE | re.IGNORECASE
    ),

    # "provincia de [NOMBRE]"
    "provincia": re.compile(
        r'[Pp]rovincia\s+de\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ]?[a-záéíóúñ]+)*)',
        re.UNICODE
    ),
}


def extraer_ubicaciones_texto(texto: str) -> dict:
    """
    Extrae todas las ubicaciones mencionadas en un texto de sentencia.

    Args:
        texto: Contenido del archivo de texto de la sentencia

    Returns:
        Diccionario con comunas, regiones y direcciones encontradas
    """
    resultado = {
        "comunas": [],
        "regiones": [],
        "provincias": [],
        "direcciones": [],
    }

    # Extraer comunas
    for match in PATRONES["comuna"].finditer(texto):
        comuna = match.group(1).strip()
        # Validar que existe en nuestra tabla
        if buscar_comuna(comuna):
            if comuna not in resultado["comunas"]:
                resultado["comunas"].append(comuna)

    # Extraer regiones
    for match in PATRONES["region"].finditer(texto):
        region_texto = match.group(1).strip()
        region = buscar_region(region_texto)
        if region and region not in resultado["regiones"]:
            resultado["regiones"].append(region)

    # Extraer provincias (informativo)
    for match in PATRONES["provincia"].finditer(texto):
        provincia = match.group(1).strip()
        if provincia not in resultado["provincias"]:
            resultado["provincias"].append(provincia)

    # Extraer direcciones/ubicaciones específicas (primeras 3)
    for match in PATRONES["ubicado"].finditer(texto):
        direccion = match.group(1).strip()[:200]  # Limitar longitud
        if len(direccion) > 10 and direccion not in resultado["direcciones"]:
            resultado["direcciones"].append(direccion)
            if len(resultado["direcciones"]) >= 3:
                break

    return resultado


def determinar_ubicacion_principal(ubicaciones: dict, tribunal: str) -> dict:
    """
    Determina la ubicación principal de una causa basándose en las menciones.

    Prioridad:
    1. Primera comuna mencionada
    2. Primera región mencionada
    3. Sede del tribunal

    Args:
        ubicaciones: Diccionario con comunas, regiones, etc.
        tribunal: Código del tribunal (1TA, 2TA, 3TA)

    Returns:
        Diccionario con lat, lon, precision, comuna, region
    """
    # Prioridad 1: Comuna
    if ubicaciones["comunas"]:
        comuna = ubicaciones["comunas"][0]
        datos_comuna = buscar_comuna(comuna)
        if datos_comuna:
            return {
                "lat": datos_comuna["lat"],
                "lon": datos_comuna["lon"],
                "precision": "media",
                "comuna": comuna,
                "region": datos_comuna["region"],
                "fuente": "texto_comuna"
            }

    # Prioridad 2: Región
    if ubicaciones["regiones"]:
        region = ubicaciones["regiones"][0]
        if region in REGIONES_CHILE:
            return {
                "lat": REGIONES_CHILE[region]["lat"],
                "lon": REGIONES_CHILE[region]["lon"],
                "precision": "baja",
                "comuna": None,
                "region": region,
                "fuente": "texto_region"
            }

    # Prioridad 3: Fallback a tribunal
    coords = get_coords_tribunal(tribunal)
    sede = JURISDICCION_TRIBUNALES.get(tribunal, {}).get("sede", "Santiago")
    return {
        "lat": coords[0],
        "lon": coords[1],
        "precision": "tribunal",
        "comuna": sede,
        "region": buscar_region(sede) or "Metropolitana",
        "fuente": "tribunal"
    }


def procesar_textos():
    """
    Procesa todos los textos de sentencias y extrae ubicaciones.

    Returns:
        Diccionario con ubicaciones por ROL
    """
    print(f"Buscando textos en: {TEXTOS_DIR}")

    if not TEXTOS_DIR.exists():
        print(f"ERROR: No existe el directorio {TEXTOS_DIR}")
        return {}

    textos = list(TEXTOS_DIR.glob("*.txt"))
    print(f"Encontrados {len(textos)} archivos de texto")

    resultados = {}
    stats = {"con_comuna": 0, "con_region": 0, "solo_tribunal": 0}

    for i, txt_file in enumerate(textos, 1):
        if i % 50 == 0:
            print(f"  Procesando {i}/{len(textos)}...")

        try:
            texto = txt_file.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            print(f"  Error leyendo {txt_file.name}: {e}")
            continue

        # Extraer ROL del nombre del archivo
        rol_match = re.search(r'([RDS])-?(\d+)-(\d{4})', txt_file.name)
        if rol_match:
            tipo, num, año = rol_match.groups()
            rol = f"{tipo}-{num}-{año}"
        else:
            rol = txt_file.stem

        # Determinar tribunal del nombre
        tribunal = "2TA"  # Default
        if "1ta" in txt_file.name.lower() or "s1ta" in txt_file.name.lower():
            tribunal = "1TA"
        elif "3ta" in txt_file.name.lower():
            tribunal = "3TA"

        # Extraer ubicaciones
        ubicaciones = extraer_ubicaciones_texto(texto)
        ubicacion_principal = determinar_ubicacion_principal(ubicaciones, tribunal)

        # Actualizar estadísticas
        if ubicacion_principal["precision"] == "media":
            stats["con_comuna"] += 1
        elif ubicacion_principal["precision"] == "baja":
            stats["con_region"] += 1
        else:
            stats["solo_tribunal"] += 1

        resultados[rol] = {
            "tribunal": tribunal,
            "archivo": txt_file.name,
            "comunas_mencionadas": ubicaciones["comunas"],
            "regiones_mencionadas": ubicaciones["regiones"],
            "direcciones": ubicaciones["direcciones"][:2],
            "ubicacion_principal": ubicacion_principal
        }

    print(f"\nEstadísticas de extracción:")
    print(f"  Con comuna identificada: {stats['con_comuna']}")
    print(f"  Solo región: {stats['con_region']}")
    print(f"  Fallback tribunal: {stats['solo_tribunal']}")

    return resultados


def cargar_causas_adicionales():
    """
    Carga causas del archivo causas_unicas.json que no tienen texto.
    Les asigna ubicación basada en tribunal.
    """
    if not CAUSAS_FILE.exists():
        print(f"Archivo {CAUSAS_FILE} no encontrado")
        return {}

    with open(CAUSAS_FILE, 'r', encoding='utf-8') as f:
        causas = json.load(f)

    resultados = {}
    for causa in causas:
        rol = causa.get("rol", "")
        tribunal = causa.get("tribunal", "2TA")

        if not rol:
            continue

        ubicacion = determinar_ubicacion_principal(
            {"comunas": [], "regiones": [], "provincias": [], "direcciones": []},
            tribunal
        )

        resultados[rol] = {
            "tribunal": tribunal,
            "archivo": causa.get("filename", ""),
            "comunas_mencionadas": [],
            "regiones_mencionadas": [],
            "direcciones": [],
            "ubicacion_principal": ubicacion
        }

    return resultados


def generar_geocodificacion_json(ubicaciones: dict):
    """Genera el archivo JSON con todas las coordenadas."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Preparar datos para JSON
    causas_list = []
    por_precision = {"alta": 0, "media": 0, "baja": 0, "tribunal": 0}

    for rol, datos in ubicaciones.items():
        ubi = datos["ubicacion_principal"]
        precision = ubi["precision"]
        por_precision[precision] = por_precision.get(precision, 0) + 1

        causas_list.append({
            "rol": rol,
            "tribunal": datos["tribunal"],
            "lat": ubi["lat"],
            "lon": ubi["lon"],
            "precision": precision,
            "comuna": ubi.get("comuna"),
            "region": ubi.get("region"),
            "comunas_mencionadas": datos.get("comunas_mencionadas", []),
        })

    total = len(causas_list)
    geocodificadas = total - por_precision.get("tribunal", 0)

    output = {
        "metadata": {
            "fecha_generacion": datetime.now().isoformat(),
            "total_causas": total,
            "geocodificadas": geocodificadas,
            "porcentaje": round(geocodificadas / total * 100, 1) if total > 0 else 0
        },
        "por_precision": por_precision,
        "causas": causas_list
    }

    # Guardar JSON principal
    with open(OUTPUT_DIR / "geocodificacion.json", 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # Guardar ubicaciones detalladas
    with open(OUTPUT_DIR / "ubicaciones_extraidas.json", 'w', encoding='utf-8') as f:
        json.dump(ubicaciones, f, ensure_ascii=False, indent=2)

    print(f"\nArchivos generados en {OUTPUT_DIR}:")
    print(f"  - geocodificacion.json")
    print(f"  - ubicaciones_extraidas.json")

    return output


def generar_mapa_nivel1(datos: dict):
    """
    Genera mapa estático PNG con los 3 tribunales.
    Nivel 1: Vista general por tribunal.
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
    except ImportError:
        print("matplotlib no instalado. Ejecuta: pip install matplotlib")
        return

    FIGURAS_DIR.mkdir(parents=True, exist_ok=True)

    # Contar causas por tribunal
    conteo = defaultdict(int)
    for causa in datos["causas"]:
        conteo[causa["tribunal"]] += 1

    fig, ax = plt.subplots(figsize=(8, 12))

    # Configuración de tribunales
    tribunales = [
        ("1TA", "Antofagasta", -23.65, -70.40, '#3498db', conteo.get("1TA", 0)),
        ("2TA", "Santiago", -33.45, -70.67, '#e74c3c', conteo.get("2TA", 0)),
        ("3TA", "Valdivia", -39.81, -73.24, '#2ecc71', conteo.get("3TA", 0)),
    ]

    # Dibujar puntos
    for codigo, ciudad, lat, lon, color, n_causas in tribunales:
        size = max(100, n_causas * 2)  # Tamaño proporcional
        ax.scatter(lon, lat, s=size, c=color, alpha=0.7, edgecolor='black', linewidth=1.5, zorder=5)
        ax.annotate(
            f"{codigo}\n{ciudad}\n({n_causas} causas)",
            (lon, lat),
            textcoords="offset points",
            xytext=(15, 0),
            fontsize=9,
            ha='left',
            va='center'
        )

    # Líneas de jurisdicción aproximadas
    ax.axhline(y=-27.0, color='gray', linestyle='--', alpha=0.5, label='Límite 1TA/2TA')
    ax.axhline(y=-37.5, color='gray', linestyle='--', alpha=0.5, label='Límite 2TA/3TA')

    # Configuración del gráfico
    ax.set_xlim(-76, -66)
    ax.set_ylim(-56, -17)
    ax.set_xlabel('Longitud', fontsize=10)
    ax.set_ylabel('Latitud', fontsize=10)
    ax.set_title('Distribución de Causas por Tribunal Ambiental\nChile 2012-2025', fontsize=12, fontweight='bold')
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)

    # Leyenda
    legend_elements = [
        mpatches.Patch(color='#3498db', label=f'1TA Antofagasta ({conteo.get("1TA", 0)})'),
        mpatches.Patch(color='#e74c3c', label=f'2TA Santiago ({conteo.get("2TA", 0)})'),
        mpatches.Patch(color='#2ecc71', label=f'3TA Valdivia ({conteo.get("3TA", 0)})'),
    ]
    ax.legend(handles=legend_elements, loc='lower left', fontsize=9)

    # Guardar
    output_path = FIGURAS_DIR / 'fig6_mapa_tribunales.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    print(f"Mapa Nivel 1 guardado: {output_path}")


def generar_mapa_nivel2(datos: dict):
    """
    Genera mapa estático PNG con distribución por comuna/región.
    Nivel 2: Detalle geográfico.
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib no instalado")
        return

    FIGURAS_DIR.mkdir(parents=True, exist_ok=True)

    # Agrupar por ubicación
    ubicaciones = defaultdict(lambda: {"count": 0, "tribunal": set()})

    for causa in datos["causas"]:
        key = (causa["lat"], causa["lon"])
        ubicaciones[key]["count"] += 1
        ubicaciones[key]["tribunal"].add(causa["tribunal"])
        ubicaciones[key]["comuna"] = causa.get("comuna", "")
        ubicaciones[key]["region"] = causa.get("region", "")

    fig, ax = plt.subplots(figsize=(10, 14))

    # Colores por tribunal
    colores = {'1TA': '#3498db', '2TA': '#e74c3c', '3TA': '#2ecc71'}

    # Dibujar puntos
    for (lat, lon), info in ubicaciones.items():
        # Color según tribunal predominante
        tribunal_principal = list(info["tribunal"])[0] if info["tribunal"] else "2TA"
        color = colores.get(tribunal_principal, '#888888')

        size = max(20, info["count"] * 15)
        ax.scatter(lon, lat, s=size, c=color, alpha=0.6, edgecolor='black', linewidth=0.5)

        # Etiqueta para ubicaciones con muchas causas
        if info["count"] >= 5 and info["comuna"]:
            ax.annotate(
                f'{info["comuna"]}\n({info["count"]})',
                (lon, lat),
                textcoords="offset points",
                xytext=(5, 5),
                fontsize=7,
                alpha=0.8
            )

    # Configuración
    ax.set_xlim(-76, -66)
    ax.set_ylim(-56, -17)
    ax.set_xlabel('Longitud', fontsize=10)
    ax.set_ylabel('Latitud', fontsize=10)
    ax.set_title('Distribución Geográfica de Conflictos Ambientales\nPor Comuna - Chile 2012-2025', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)

    # Estadísticas en texto
    total = datos["metadata"]["total_causas"]
    geo = datos["metadata"]["geocodificadas"]
    ax.text(
        0.02, 0.02,
        f'Total: {total} causas\nGeocod.: {geo} ({datos["metadata"]["porcentaje"]}%)',
        transform=ax.transAxes,
        fontsize=9,
        verticalalignment='bottom',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
    )

    output_path = FIGURAS_DIR / 'fig7_mapa_comunas.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    print(f"Mapa Nivel 2 guardado: {output_path}")


def generar_mapa_interactivo(datos: dict):
    """
    Genera mapa HTML interactivo con folium.
    """
    try:
        import folium
        from folium.plugins import MarkerCluster
    except ImportError:
        print("folium no instalado. Ejecuta: pip install folium")
        return

    FIGURAS_DIR.mkdir(parents=True, exist_ok=True)

    # Centro de Chile
    mapa = folium.Map(
        location=[-33.45, -70.67],
        zoom_start=5,
        tiles='CartoDB positron'
    )

    # Cluster de marcadores
    marker_cluster = MarkerCluster(name="Causas Ambientales").add_to(mapa)

    # Colores por tribunal
    colores = {'1TA': 'blue', '2TA': 'red', '3TA': 'green'}
    iconos = {'1TA': 'tint', '2TA': 'balance-scale', '3TA': 'leaf'}

    for causa in datos["causas"]:
        tribunal = causa["tribunal"]
        color = colores.get(tribunal, 'gray')

        # Popup con información
        popup_html = f"""
        <div style="font-family: Arial; width: 200px;">
            <b>ROL:</b> {causa['rol']}<br>
            <b>Tribunal:</b> {tribunal}<br>
            <b>Comuna:</b> {causa.get('comuna') or 'N/D'}<br>
            <b>Región:</b> {causa.get('region') or 'N/D'}<br>
            <b>Precisión:</b> {causa['precision']}<br>
        </div>
        """

        folium.Marker(
            location=[causa['lat'], causa['lon']],
            popup=folium.Popup(popup_html, max_width=250),
            icon=folium.Icon(color=color, icon='info-sign'),
            tooltip=f"{causa['rol']} - {tribunal}"
        ).add_to(marker_cluster)

    # Agregar leyenda
    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000;
                background-color: white; padding: 10px; border-radius: 5px;
                border: 2px solid gray; font-family: Arial;">
        <b>Tribunales Ambientales</b><br>
        <i class="fa fa-map-marker" style="color:blue"></i> 1TA Antofagasta<br>
        <i class="fa fa-map-marker" style="color:red"></i> 2TA Santiago<br>
        <i class="fa fa-map-marker" style="color:green"></i> 3TA Valdivia<br>
    </div>
    '''
    mapa.get_root().html.add_child(folium.Element(legend_html))

    # Control de capas
    folium.LayerControl().add_to(mapa)

    # Guardar
    output_path = FIGURAS_DIR / 'mapa_interactivo.html'
    mapa.save(str(output_path))

    print(f"Mapa interactivo guardado: {output_path}")


def main():
    """Función principal."""
    print("=" * 60)
    print("GEOCODIFICACIÓN DE CONFLICTOS AMBIENTALES")
    print("Tribunales Ambientales de Chile")
    print("=" * 60)

    # 1. Procesar textos de sentencias
    print("\n[1/5] Procesando textos de sentencias...")
    ubicaciones = procesar_textos()

    # 2. Cargar causas adicionales (sin texto)
    print("\n[2/5] Cargando causas adicionales...")
    causas_extra = cargar_causas_adicionales()

    # Combinar (textos tienen prioridad)
    for rol, datos in causas_extra.items():
        if rol not in ubicaciones:
            ubicaciones[rol] = datos

    print(f"Total de causas: {len(ubicaciones)}")

    # 3. Generar JSON
    print("\n[3/5] Generando archivos JSON...")
    datos_geo = generar_geocodificacion_json(ubicaciones)

    # 4. Generar mapas estáticos
    print("\n[4/5] Generando mapas estáticos (PNG)...")
    generar_mapa_nivel1(datos_geo)
    generar_mapa_nivel2(datos_geo)

    # 5. Generar mapa interactivo
    print("\n[5/5] Generando mapa interactivo (HTML)...")
    generar_mapa_interactivo(datos_geo)

    print("\n" + "=" * 60)
    print("PROCESO COMPLETADO")
    print("=" * 60)
    print(f"\nArchivos generados:")
    print(f"  - {OUTPUT_DIR / 'geocodificacion.json'}")
    print(f"  - {OUTPUT_DIR / 'ubicaciones_extraidas.json'}")
    print(f"  - {FIGURAS_DIR / 'fig6_mapa_tribunales.png'}")
    print(f"  - {FIGURAS_DIR / 'fig7_mapa_comunas.png'}")
    print(f"  - {FIGURAS_DIR / 'mapa_interactivo.html'}")


if __name__ == "__main__":
    main()
