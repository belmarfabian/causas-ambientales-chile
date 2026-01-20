#!/usr/bin/env python3
"""
Plataforma de visualización de conflictos socioecológicos en Chile.

Ejecutar con: streamlit run plataforma_conflictos.py

Fuentes integradas:
- INDH: Mapa de Conflictos Socioambientales (162)
- EJAtlas: Environmental Justice Atlas (51 únicos)
- OCMAL: Observatorio de Conflictos Mineros (31 únicos)
"""

import json
from pathlib import Path
from collections import Counter
import pandas as pd
import streamlit as st
import plotly.express as px

# Configuración de página
st.set_page_config(
    page_title="Conflictos Socioecológicos en Chile",
    page_icon="🌿",
    layout="wide"
)

# Rutas
BASE_DIR = Path(__file__).parent
DATOS_DIR = BASE_DIR / "datos" / "conflictos"


@st.cache_data(ttl=10)  # Cache expira en 10 segundos
def cargar_datos(version="noticias"):
    """
    Carga el dataset consolidado con IDs maestros.

    Args:
        version: "base" solo datos extraídos, "completo" con inferencias, "noticias" con URLs de noticias
    """
    if version == "noticias":
        archivo = DATOS_DIR / "conflictos_consolidados_noticias.json"
    elif version == "completo":
        archivo = DATOS_DIR / "conflictos_consolidados_completo.json"
    else:
        archivo = DATOS_DIR / "conflictos_consolidados_ids.json"

    with open(archivo, encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)

    # Crear columna 'fuente' compatible con el resto del código
    df['fuente'] = df['fuente_principal']

    # Limpiar datos
    df['region'] = df['region'].fillna('Sin dato')
    df['sector'] = df['sector'].fillna('Sin dato')
    df['estado'] = df['estado'].fillna('')
    if 'localidad' in df.columns:
        df['localidad'] = df['localidad'].fillna('')

    return df


@st.cache_data
def cargar_resumen():
    """Genera el resumen de integración desde el dataset consolidado."""
    with open(DATOS_DIR / "conflictos_consolidados_ids.json", encoding="utf-8") as f:
        data = json.load(f)

    # Calcular estadísticas
    total = len(data)
    indh_total = sum(1 for d in data if d.get('fuente_principal') == 'INDH')
    ejatlas_total = sum(1 for d in data if d.get('en_ejatlas'))
    ejatlas_unicos = sum(1 for d in data if d.get('fuente_principal') == 'EJAtlas')
    ocmal_total = sum(1 for d in data if d.get('en_ocmal'))
    ocmal_unicos = sum(1 for d in data if d.get('fuente_principal') == 'OCMAL')

    return {
        "integracion": {"total_conflictos_unicos": total},
        "fuentes": {
            "INDH": {"total": indh_total},
            "EJAtlas": {"total": ejatlas_total, "unicos": ejatlas_unicos},
            "OCMAL": {"total": ocmal_total, "unicos": ocmal_unicos}
        },
        "notas": {
            "OLCA": "No tiene base estructurada, solo documentación cualitativa (olca.cl)",
            "ACLED": "Requiere API key, acceso gratuito académico en acleddata.com"
        }
    }


@st.cache_data
def cargar_datos_tribunales():
    """Carga estadísticas de los Tribunales Ambientales."""
    stats_path = BASE_DIR / "datos" / "estadisticas" / "estadisticas_corpus.json"
    if stats_path.exists():
        with open(stats_path, encoding="utf-8") as f:
            return json.load(f)
    return None


def main():
    st.title("🌿 Conflictos Socioecológicos en Chile")
    st.markdown("**Base de datos integrada: INDH, EJAtlas y OCMAL**")

    # Cargar datos (versión final con noticias)
    df = cargar_datos()
    resumen = cargar_resumen()

    st.sidebar.header("Filtros")

    # Filtro por fuente
    fuentes_disponibles = df['fuente'].unique().tolist()
    fuentes_sel = st.sidebar.multiselect(
        "Fuente",
        options=fuentes_disponibles,
        default=fuentes_disponibles
    )

    # Filtro por sector
    sectores = ['Todos'] + sorted([s for s in df['sector'].unique() if s and s != 'Sin dato'])
    sector_sel = st.sidebar.selectbox("Sector económico", sectores)

    # Filtro por estado
    estados = ['Todos'] + sorted([e for e in df['estado'].unique() if e])
    estado_sel = st.sidebar.selectbox("Estado", estados)

    # Filtro por región
    regiones = ['Todas'] + sorted([r for r in df['region'].unique() if r and r != 'Sin dato' and r != ''])
    region_sel = st.sidebar.selectbox("Región", regiones)

    # Filtro territorio indígena
    territorio_ind = st.sidebar.checkbox("Solo territorios indígenas")

    # Filtros por categorías (si existen)
    st.sidebar.markdown("---")
    st.sidebar.subheader("Categorías")

    # Detectar si hay datos categorizados
    tiene_categorias = 'categorias' in df.columns

    impacto_sel = None
    actor_sel = None
    resistencia_sel = None

    if tiene_categorias:
        impacto_sel = st.sidebar.selectbox(
            "Tipo de impacto",
            ['Todos', 'agua', 'aire', 'suelo', 'salud', 'biodiversidad']
        )
        actor_sel = st.sidebar.selectbox(
            "Actor afectado",
            ['Todos', 'indigena', 'pescador', 'agricultor', 'urbano']
        )
        resistencia_sel = st.sidebar.selectbox(
            "Forma de resistencia",
            ['Todos', 'judicial', 'movilizacion', 'mediatica', 'institucional']
        )

    # Aplicar filtros
    df_filtrado = df[df['fuente'].isin(fuentes_sel)].copy()

    if sector_sel != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['sector'] == sector_sel]
    if estado_sel != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['estado'] == estado_sel]
    if region_sel != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['region'] == region_sel]
    if territorio_ind:
        df_filtrado = df_filtrado[df_filtrado['territorio_indigena'] == True]

    # Filtrar por categorías
    if tiene_categorias:
        if impacto_sel and impacto_sel != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['categorias'].apply(
                lambda x: impacto_sel in x.get('impactos', []) if isinstance(x, dict) else False
            )]
        if actor_sel and actor_sel != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['categorias'].apply(
                lambda x: actor_sel in x.get('actores', []) if isinstance(x, dict) else False
            )]
        if resistencia_sel and resistencia_sel != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['categorias'].apply(
                lambda x: resistencia_sel in x.get('resistencias', []) if isinstance(x, dict) else False
            )]

    # Métricas principales
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total", len(df_filtrado))
    with col2:
        st.metric("INDH", len(df_filtrado[df_filtrado['fuente'] == 'INDH']))
    with col3:
        st.metric("EJAtlas", len(df_filtrado[df_filtrado['fuente'] == 'EJAtlas']))
    with col4:
        st.metric("OCMAL", len(df_filtrado[df_filtrado['fuente'] == 'OCMAL']))
    with col5:
        n_activos = len(df_filtrado[df_filtrado['estado'] == 'Activo'])
        st.metric("Activos", n_activos)

    # Tabs
    if tiene_categorias:
        tab_stats, tab_cat, tab_temporal, tab_map, tab_data, tab_cross, tab_search, tab_tribunales = st.tabs(
            ["📊 Estadísticas", "🏷️ Categorías", "📈 Temporal", "🗺️ Mapa", "📋 Datos", "🔗 Fuentes Cruzadas", "🔍 Búsqueda", "⚖️ Tribunales"]
        )
    else:
        tab_stats, tab_temporal, tab_map, tab_data, tab_cross, tab_search, tab_tribunales = st.tabs(
            ["📊 Estadísticas", "📈 Temporal", "🗺️ Mapa", "📋 Datos", "🔗 Fuentes Cruzadas", "🔍 Búsqueda", "⚖️ Tribunales"]
        )
        tab_cat = None

    with tab_stats:
        col1, col2 = st.columns(2)

        with col1:
            # Por sector
            df_sector = df_filtrado['sector'].value_counts().reset_index()
            df_sector.columns = ['Sector', 'Cantidad']
            df_sector = df_sector[
                (df_sector['Sector'].notna()) &
                (df_sector['Sector'] != '') &
                (df_sector['Sector'] != 'Sin dato')
            ]

            if len(df_sector) > 0:
                fig_sector = px.bar(
                    df_sector.head(10),
                    x='Cantidad',
                    y='Sector',
                    orientation='h',
                    title='Conflictos por sector económico',
                    color='Cantidad',
                    color_continuous_scale='Viridis'
                )
                fig_sector.update_layout(yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig_sector, width='stretch')

        with col2:
            # Por estado
            df_estado = df_filtrado[df_filtrado['estado'] != '']['estado'].value_counts().reset_index()
            df_estado.columns = ['Estado', 'Cantidad']

            if len(df_estado) > 0:
                colores = {'Activo': '#E63946', 'Latente': '#F4A261', 'Cerrado': '#2A9D8F', 'Archivado': '#264653'}
                fig_estado = px.bar(
                    df_estado,
                    x='Cantidad',
                    y='Estado',
                    orientation='h',
                    title='Conflictos por estado',
                    color='Estado',
                    color_discrete_map=colores
                )
                fig_estado.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False)
                st.plotly_chart(fig_estado, width='stretch')

        # Por fuente
        col1, col2 = st.columns(2)

        with col1:
            df_fuente = df_filtrado['fuente'].value_counts().reset_index()
            df_fuente.columns = ['Fuente', 'Cantidad']
            fig_fuente = px.bar(
                df_fuente,
                x='Cantidad',
                y='Fuente',
                orientation='h',
                title='Conflictos por fuente',
                color='Fuente',
                color_discrete_map={'INDH': '#1f77b4', 'EJAtlas': '#ff7f0e', 'OCMAL': '#2ca02c'}
            )
            fig_fuente.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False)
            st.plotly_chart(fig_fuente, width='stretch')

        with col2:
            # Por región
            df_region = df_filtrado['region'].value_counts().reset_index()
            df_region.columns = ['Región', 'Cantidad']
            df_region = df_region[
                (df_region['Región'].notna()) &
                (df_region['Región'] != '') &
                (df_region['Región'] != 'Sin dato')
            ]

            if len(df_region) > 0:
                fig_region = px.bar(
                    df_region.head(10),
                    x='Cantidad',
                    y='Región',
                    orientation='h',
                    title='Top 10 regiones',
                    color='Cantidad',
                    color_continuous_scale='Blues'
                )
                fig_region.update_layout(yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig_region, width='stretch')

    # Tab de categorías (si existen)
    if tiene_categorias and tab_cat is not None:
        with tab_cat:
            st.subheader("Análisis por categorías")

            # Extraer estadísticas de categorías
            stats_cat = {
                'impactos': Counter(),
                'actores': Counter(),
                'resistencias': Counter(),
                'resultados': Counter()
            }

            for _, row in df_filtrado.iterrows():
                cat = row.get('categorias', {})
                if isinstance(cat, dict):
                    for imp in cat.get('impactos', []):
                        stats_cat['impactos'][imp] += 1
                    for act in cat.get('actores', []):
                        stats_cat['actores'][act] += 1
                    for res in cat.get('resistencias', []):
                        stats_cat['resistencias'][res] += 1
                    for res in cat.get('resultados', []):
                        stats_cat['resultados'][res] += 1

            col1, col2 = st.columns(2)

            with col1:
                # Impactos
                if stats_cat['impactos']:
                    df_imp = pd.DataFrame(
                        stats_cat['impactos'].most_common(),
                        columns=['Impacto', 'Cantidad']
                    )
                    fig_imp = px.bar(
                        df_imp, x='Cantidad', y='Impacto', orientation='h',
                        title='Tipo de impacto ambiental',
                        color='Cantidad', color_continuous_scale='Reds'
                    )
                    fig_imp.update_layout(yaxis={'categoryorder': 'total ascending'})
                    st.plotly_chart(fig_imp, width='stretch')

                # Resistencias
                if stats_cat['resistencias']:
                    df_res = pd.DataFrame(
                        stats_cat['resistencias'].most_common(),
                        columns=['Resistencia', 'Cantidad']
                    )
                    fig_res = px.bar(
                        df_res, x='Cantidad', y='Resistencia', orientation='h',
                        title='Forma de resistencia',
                        color='Cantidad', color_continuous_scale='Purples'
                    )
                    fig_res.update_layout(yaxis={'categoryorder': 'total ascending'})
                    st.plotly_chart(fig_res, width='stretch')

            with col2:
                # Actores
                if stats_cat['actores']:
                    df_act = pd.DataFrame(
                        stats_cat['actores'].most_common(),
                        columns=['Actor', 'Cantidad']
                    )
                    fig_act = px.bar(
                        df_act, x='Cantidad', y='Actor', orientation='h',
                        title='Actor afectado',
                        color='Cantidad', color_continuous_scale='Greens'
                    )
                    fig_act.update_layout(yaxis={'categoryorder': 'total ascending'})
                    st.plotly_chart(fig_act, width='stretch')

                # Resultados
                if stats_cat['resultados']:
                    df_resultado = pd.DataFrame(
                        stats_cat['resultados'].most_common(),
                        columns=['Resultado', 'Cantidad']
                    )
                    fig_resultado = px.bar(
                        df_resultado, x='Cantidad', y='Resultado', orientation='h',
                        title='Resultado del conflicto',
                        color='Resultado',
                        color_discrete_map={
                            'aprobado': '#E63946',
                            'paralizado': '#2A9D8F',
                            'en_litigio': '#F4A261'
                        }
                    )
                    fig_resultado.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False)
                    st.plotly_chart(fig_resultado, width='stretch')

    # Tab de análisis temporal
    with tab_temporal:
        st.subheader("Evolución temporal de conflictos")

        # Filtrar conflictos con año
        df_con_año = df_filtrado[df_filtrado['año_inicio'].notna()].copy()
        df_con_año['año_inicio'] = df_con_año['año_inicio'].astype(int)

        if len(df_con_año) > 0:
            col1, col2 = st.columns(2)

            with col1:
                # Conflictos por año
                df_año = df_con_año.groupby('año_inicio').size().reset_index(name='Cantidad')
                fig_año = px.bar(
                    df_año,
                    x='año_inicio',
                    y='Cantidad',
                    title='Conflictos por año de inicio',
                    labels={'año_inicio': 'Año', 'Cantidad': 'Nuevos conflictos'}
                )
                st.plotly_chart(fig_año, width='stretch')

            with col2:
                # Acumulado
                df_año_sorted = df_año.sort_values('año_inicio')
                df_año_sorted['Acumulado'] = df_año_sorted['Cantidad'].cumsum()
                fig_acum = px.area(
                    df_año_sorted,
                    x='año_inicio',
                    y='Acumulado',
                    title='Conflictos acumulados',
                    labels={'año_inicio': 'Año', 'Acumulado': 'Total acumulado'}
                )
                st.plotly_chart(fig_acum, width='stretch')

            # Por década
            df_con_año['decada'] = (df_con_año['año_inicio'] // 10) * 10
            df_decada = df_con_año.groupby('decada').size().reset_index(name='Cantidad')
            df_decada['decada'] = df_decada['decada'].astype(str) + 's'

            fig_decada = px.bar(
                df_decada,
                x='decada',
                y='Cantidad',
                title='Distribución por década',
                color='Cantidad',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig_decada, width='stretch')

            # Por sector y año
            st.markdown("### Evolución por sector")
            sectores_top = df_con_año['sector'].value_counts().head(4).index.tolist()
            df_sector_año = df_con_año[df_con_año['sector'].isin(sectores_top)]
            df_pivot = df_sector_año.groupby(['año_inicio', 'sector']).size().reset_index(name='Cantidad')

            fig_sector = px.line(
                df_pivot,
                x='año_inicio',
                y='Cantidad',
                color='sector',
                title='Conflictos por sector y año',
                labels={'año_inicio': 'Año', 'Cantidad': 'Conflictos'}
            )
            st.plotly_chart(fig_sector, width='stretch')

        else:
            st.info("No hay conflictos con año de inicio en la selección actual.")

    with tab_map:
        st.subheader("Mapa de conflictos")

        # Filtrar conflictos con coordenadas
        df_mapa = df_filtrado[
            (df_filtrado['latitud'].notna()) &
            (df_filtrado['longitud'].notna())
        ].copy()

        if len(df_mapa) > 0:
            fig_mapa = px.scatter_map(
                df_mapa,
                lat='latitud',
                lon='longitud',
                hover_name='nombre',
                hover_data=['sector', 'estado', 'region', 'fuente'],
                color='estado',
                color_discrete_map={
                    'Activo': '#E63946',
                    'Latente': '#F4A261',
                    'Cerrado': '#2A9D8F',
                    'Archivado': '#264653'
                },
                zoom=4,
                height=600,
                title=f'{len(df_mapa)} conflictos con ubicación georreferenciada'
            )
            fig_mapa.update_layout(map_style="open-street-map")
            st.plotly_chart(fig_mapa, width='stretch')
        else:
            st.info("No hay conflictos con coordenadas en la selección actual.")

    with tab_data:
        st.subheader("Tabla de datos consolidados")

        df_tabla = df_filtrado.copy()

        # Columnas del dataset consolidado con IDs y categorías
        cols_mostrar = [
            'id_maestro', 'nombre', 'fuente_principal', 'region', 'sector', 'estado', 'año_inicio',
            'impactos', 'actores', 'resistencias', 'resultados',
            'en_ejatlas', 'nombre_ejatlas', 'en_ocmal', 'nombre_ocmal'
        ]
        cols_disponibles = [c for c in cols_mostrar if c in df_tabla.columns]
        df_tabla = df_tabla[cols_disponibles]

        st.dataframe(
            df_tabla,
            width='stretch',
            height=500
        )

        # Descargar CSV completo
        csv = df_filtrado.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 Descargar CSV completo",
            data=csv,
            file_name="conflictos_consolidados.csv",
            mime="text/csv"
        )

    with tab_cross:
        st.subheader("🔗 Cobertura entre Fuentes")
        st.markdown("""
        Filtra conflictos según su presencia en múltiples fuentes.
        - **INDH** es la fuente base (162 conflictos)
        - `en_ejatlas` y `en_ocmal` indican si el conflicto también aparece en esas fuentes
        """)

        # Métricas de cobertura cruzada (usando df que ya tiene los datos consolidados)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total únicos", len(df))
        with col2:
            en_ejatlas = df['en_ejatlas'].sum()
            st.metric("También en EJAtlas", int(en_ejatlas))
        with col3:
            en_ocmal = df['en_ocmal'].sum()
            st.metric("También en OCMAL", int(en_ocmal))
        with col4:
            en_ambos = ((df['en_ejatlas']) & (df['en_ocmal'])).sum()
            st.metric("En las 3 fuentes", int(en_ambos))

        # Filtro para ver solo los cruzados
        filtro_cruce = st.radio(
            "Mostrar:",
            ["Todos", "Solo en múltiples fuentes", "Solo INDH+EJAtlas", "Solo INDH+OCMAL", "En las 3 fuentes"],
            horizontal=True
        )

        df_mostrar = df.copy()
        if filtro_cruce == "Solo en múltiples fuentes":
            df_mostrar = df_mostrar[(df_mostrar['en_ejatlas']) | (df_mostrar['en_ocmal'])]
        elif filtro_cruce == "Solo INDH+EJAtlas":
            df_mostrar = df_mostrar[(df_mostrar['en_ejatlas']) & (df_mostrar['fuente_principal'] == 'INDH')]
        elif filtro_cruce == "Solo INDH+OCMAL":
            df_mostrar = df_mostrar[(df_mostrar['en_ocmal']) & (df_mostrar['fuente_principal'] == 'INDH')]
        elif filtro_cruce == "En las 3 fuentes":
            df_mostrar = df_mostrar[(df_mostrar['en_ejatlas']) & (df_mostrar['en_ocmal'])]

        st.write(f"**{len(df_mostrar)} conflictos**")

        # Tabla con categorías
        cols_mostrar = ['id_maestro', 'nombre', 'fuente_principal', 'region', 'sector',
                       'impactos', 'actores', 'resistencias', 'resultados',
                       'en_ejatlas', 'nombre_ejatlas', 'en_ocmal', 'nombre_ocmal']
        cols_disponibles = [c for c in cols_mostrar if c in df_mostrar.columns]

        st.dataframe(
            df_mostrar[cols_disponibles],
            width='stretch',
            height=500
        )

        # Descargar
        csv_cross = df_mostrar.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 Descargar CSV filtrado",
            data=csv_cross,
            file_name="conflictos_filtrados.csv",
            mime="text/csv"
        )

    with tab_search:
        st.subheader("Búsqueda de conflictos")

        busqueda = st.text_input("Buscar por nombre o descripción")

        if busqueda:
            mascara = (
                df_filtrado['nombre'].str.contains(busqueda, case=False, na=False) |
                df_filtrado['descripcion'].str.contains(busqueda, case=False, na=False)
            )
            resultados = df_filtrado[mascara]

            st.write(f"**{len(resultados)} resultados encontrados**")

            for _, row in resultados.iterrows():
                with st.expander(f"📍 {row['nombre']} ({row['fuente']})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Fuente:** {row['fuente']}")
                        st.write(f"**Sector:** {row.get('sector', 'N/A')}")
                        st.write(f"**Estado:** {row.get('estado', 'N/A')}")
                    with col2:
                        st.write(f"**Región:** {row.get('region', 'N/A')}")
                        st.write(f"**Localidad:** {row.get('localidad', 'N/A')}")
                        st.write(f"**Año:** {row.get('año_inicio', 'N/A')}")

                    if row.get('descripcion'):
                        st.write("**Descripción:**")
                        desc = str(row['descripcion'])
                        st.write(desc[:500] + "..." if len(desc) > 500 else desc)

                    if row.get('url'):
                        st.markdown(f"[Ver en fuente original]({row['url']})")

    with tab_tribunales:
        st.subheader("⚖️ Tribunales Ambientales de Chile")
        st.markdown("Estadísticas del corpus de documentos judiciales (2013-2025)")

        datos_tribunales = cargar_datos_tribunales()

        if datos_tribunales:
            # Métricas principales
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total documentos", f"{datos_tribunales['total_archivos']:,}")
            with col2:
                st.metric("Causas únicas", datos_tribunales['roles_unicos'])
            with col3:
                st.metric("Sentencias", datos_tribunales['por_tipo'].get('Sentencia', 0))
            with col4:
                st.metric("Actas", datos_tribunales['por_tipo'].get('Acta', 0))

            col1, col2 = st.columns(2)

            with col1:
                # Por tribunal
                df_trib = pd.DataFrame([
                    {'Tribunal': k, 'Documentos': v}
                    for k, v in datos_tribunales['por_tribunal'].items()
                ])
                fig_trib = px.bar(
                    df_trib, x='Tribunal', y='Documentos',
                    title='Documentos por Tribunal',
                    color='Tribunal',
                    color_discrete_map={'1TA': '#1f77b4', '2TA': '#ff7f0e', '3TA': '#2ca02c'}
                )
                fig_trib.update_layout(showlegend=False)
                st.plotly_chart(fig_trib, use_container_width=True)

            with col2:
                # Por tipo de documento
                tipos_principales = ['Sentencia', 'Acta', 'Resolución', 'Informe', 'Boletín']
                df_tipo = pd.DataFrame([
                    {'Tipo': k, 'Cantidad': v}
                    for k, v in datos_tribunales['por_tipo'].items()
                    if k in tipos_principales
                ])
                df_tipo = df_tipo.sort_values('Cantidad', ascending=True)
                fig_tipo = px.bar(
                    df_tipo, x='Cantidad', y='Tipo', orientation='h',
                    title='Documentos por tipo',
                    color='Cantidad', color_continuous_scale='Blues'
                )
                st.plotly_chart(fig_tipo, use_container_width=True)

            # Evolución temporal
            st.markdown("### Evolución temporal")
            df_año = pd.DataFrame([
                {'Año': int(k), 'Documentos': v}
                for k, v in datos_tribunales['por_año'].items()
            ]).sort_values('Año')

            fig_temporal = px.area(
                df_año, x='Año', y='Documentos',
                title='Documentos por año',
                line_shape='spline'
            )
            fig_temporal.update_traces(fill='tozeroy')
            st.plotly_chart(fig_temporal, use_container_width=True)

            # Por tribunal y año
            st.markdown("### Detalle por tribunal y año")
            datos_cruzados = []
            for trib, años in datos_tribunales['por_tribunal_año'].items():
                for año, cant in años.items():
                    if cant > 0:
                        datos_cruzados.append({'Tribunal': trib, 'Año': int(año), 'Documentos': cant})

            if datos_cruzados:
                df_cruzado = pd.DataFrame(datos_cruzados)
                fig_cruzado = px.line(
                    df_cruzado, x='Año', y='Documentos', color='Tribunal',
                    title='Evolución por tribunal',
                    color_discrete_map={'1TA': '#1f77b4', '2TA': '#ff7f0e', '3TA': '#2ca02c'},
                    markers=True
                )
                st.plotly_chart(fig_cruzado, use_container_width=True)

            # Info de tribunales
            st.markdown("""
            ---
            **Tribunales Ambientales de Chile:**
            - **1TA** (Antofagasta): Regiones de Arica y Parinacota, Tarapacá, Antofagasta, Atacama y Coquimbo
            - **2TA** (Santiago): Regiones de Valparaíso, Metropolitana, O'Higgins, Maule, Ñuble y Biobío
            - **3TA** (Valdivia): Regiones de La Araucanía, Los Ríos, Los Lagos, Aysén y Magallanes
            """)
        else:
            st.warning("No se encontraron datos de tribunales. Verifica que exista el archivo datos/estadisticas/estadisticas_corpus.json")

    # Footer
    st.markdown("---")

    # Info de fuentes
    st.markdown(f"""
    **Fuentes de datos ({resumen['integracion']['total_conflictos_unicos']} conflictos únicos):**
    - [INDH - Mapa de Conflictos Socioambientales](https://mapaconflictos.indh.cl/) ({resumen['fuentes']['INDH']['total']} conflictos)
    - [EJAtlas - Environmental Justice Atlas](https://ejatlas.org/country/chile) ({resumen['fuentes']['EJAtlas']['unicos']} únicos de {resumen['fuentes']['EJAtlas']['total']})
    - [OCMAL - Observatorio de Conflictos Mineros](https://mapa.conflictosmineros.net/) ({resumen['fuentes']['OCMAL']['unicos']} únicos de {resumen['fuentes']['OCMAL']['total']})

    **Notas:**
    - {resumen['notas']['OLCA']}
    - {resumen['notas']['ACLED']}

    *Proyecto: Conflictos Socioecológicos en Chile - Núcleo Milenio SODAS / CEP*
    """)


if __name__ == "__main__":
    main()
