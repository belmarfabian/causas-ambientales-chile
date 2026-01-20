#!/usr/bin/env python3
"""
Plataforma de visualización de conflictos socioecológicos y justicia ambiental en Chile.

Ejecutar con: streamlit run plataforma_conflictos.py

Dos secciones principales:
1. Conflictos Socioecológicos: Base integrada INDH, EJAtlas, OCMAL (244 conflictos)
2. Tribunales Ambientales: Corpus de causas y sentencias (2012-2025)
"""

import json
from pathlib import Path
from collections import Counter
import pandas as pd
import streamlit as st
import plotly.express as px

# Configuración de página
st.set_page_config(
    page_title="Conflictos y Justicia Ambiental - Chile",
    page_icon="🌿",
    layout="wide"
)

# Rutas
BASE_DIR = Path(__file__).parent
DATOS_DIR = BASE_DIR / "datos" / "conflictos"
STATS_DIR = BASE_DIR / "datos" / "estadisticas"


@st.cache_data(ttl=10)
def cargar_datos_conflictos():
    """Carga el dataset consolidado de conflictos."""
    archivo = DATOS_DIR / "conflictos_consolidados_noticias.json"
    with open(archivo, encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    df['fuente'] = df['fuente_principal']
    df['region'] = df['region'].fillna('Sin dato')
    df['sector'] = df['sector'].fillna('Sin dato')
    df['estado'] = df['estado'].fillna('')
    return df


@st.cache_data
def cargar_datos_tribunales():
    """Carga estadísticas de los Tribunales Ambientales."""
    stats_path = STATS_DIR / "estadisticas_corpus.json"
    if stats_path.exists():
        with open(stats_path, encoding="utf-8") as f:
            return json.load(f)
    return None


# =============================================================================
# SECCIÓN: CONFLICTOS SOCIOECOLÓGICOS
# =============================================================================
def seccion_conflictos():
    """Muestra la sección de conflictos socioecológicos."""
    st.header("🌿 Conflictos Socioecológicos")
    st.markdown("""
    **Base de datos integrada de conflictos socioecológicos en Chile (1990-2025).**

    Consolida información de tres fuentes: el [Mapa de Conflictos del INDH](https://mapaconflictos.indh.cl/),
    el [Environmental Justice Atlas](https://ejatlas.org/country/chile) y el
    [Observatorio de Conflictos Mineros (OCMAL)](https://mapa.conflictosmineros.net/).
    Incluye **244 conflictos únicos** con información sobre sector económico, región,
    actores afectados, formas de resistencia y estado actual.
    """)

    df = cargar_datos_conflictos()

    # Sidebar con filtros
    st.sidebar.header("Filtros - Conflictos")

    fuentes_sel = st.sidebar.multiselect(
        "Fuente", df['fuente'].unique().tolist(), default=df['fuente'].unique().tolist()
    )

    sectores = ['Todos'] + sorted([s for s in df['sector'].unique() if s and s != 'Sin dato'])
    sector_sel = st.sidebar.selectbox("Sector económico", sectores)

    regiones = ['Todas'] + sorted([r for r in df['region'].unique() if r and r != 'Sin dato' and r != ''])
    region_sel = st.sidebar.selectbox("Región", regiones)

    # Aplicar filtros
    df_filtrado = df[df['fuente'].isin(fuentes_sel)]
    if sector_sel != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['sector'] == sector_sel]
    if region_sel != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['region'] == region_sel]

    # Métricas
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total", len(df_filtrado))
    col2.metric("INDH", len(df_filtrado[df_filtrado['fuente'] == 'INDH']))
    col3.metric("EJAtlas", len(df_filtrado[df_filtrado['fuente'] == 'EJAtlas']))
    col4.metric("OCMAL", len(df_filtrado[df_filtrado['fuente'] == 'OCMAL']))
    col5.metric("Activos", len(df_filtrado[df_filtrado['estado'] == 'Activo']))

    # Sub-pestañas de conflictos
    tab_stats, tab_temporal, tab_mapa, tab_datos, tab_busqueda = st.tabs([
        "📊 Estadísticas", "📈 Temporal", "🗺️ Mapa", "📋 Datos", "🔍 Búsqueda"
    ])

    with tab_stats:
        col1, col2 = st.columns(2)

        with col1:
            # Por sector
            df_sector = df_filtrado['sector'].value_counts().reset_index()
            df_sector.columns = ['Sector', 'Cantidad']
            df_sector = df_sector[df_sector['Sector'] != 'Sin dato'].head(10)

            if len(df_sector) > 0:
                fig = px.bar(df_sector, x='Cantidad', y='Sector', orientation='h',
                            title='Por sector económico', text='Cantidad',
                            color='Cantidad', color_continuous_scale='Viridis')
                fig.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False)
                fig.update_traces(textposition='outside')
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Por región
            df_region = df_filtrado['region'].value_counts().reset_index()
            df_region.columns = ['Región', 'Cantidad']
            df_region = df_region[(df_region['Región'] != 'Sin dato') & (df_region['Región'] != '')].head(10)

            if len(df_region) > 0:
                fig = px.bar(df_region, x='Cantidad', y='Región', orientation='h',
                            title='Top 10 regiones', text='Cantidad',
                            color='Cantidad', color_continuous_scale='Blues')
                fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                fig.update_traces(textposition='outside')
                st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            # Por fuente
            df_fuente = df_filtrado['fuente'].value_counts().reset_index()
            df_fuente.columns = ['Fuente', 'Cantidad']
            fig = px.bar(df_fuente, x='Cantidad', y='Fuente', orientation='h',
                        title='Por fuente', text='Cantidad', color='Fuente',
                        color_discrete_map={'INDH': '#1f77b4', 'EJAtlas': '#ff7f0e', 'OCMAL': '#2ca02c'})
            fig.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False)
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Por estado
            df_estado = df_filtrado[df_filtrado['estado'] != '']['estado'].value_counts().reset_index()
            df_estado.columns = ['Estado', 'Cantidad']
            if len(df_estado) > 0:
                fig = px.bar(df_estado, x='Cantidad', y='Estado', orientation='h',
                            title='Por estado', text='Cantidad', color='Estado',
                            color_discrete_map={'Activo': '#E63946', 'Latente': '#F4A261',
                                              'Cerrado': '#2A9D8F', 'Archivado': '#264653'})
                fig.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False)
                fig.update_traces(textposition='outside')
                st.plotly_chart(fig, use_container_width=True)

    with tab_temporal:
        df_año = df_filtrado[df_filtrado['año_inicio'].notna()].copy()
        df_año['año_inicio'] = df_año['año_inicio'].astype(int)

        if len(df_año) > 0:
            col1, col2 = st.columns(2)

            with col1:
                df_count = df_año.groupby('año_inicio').size().reset_index(name='Cantidad')
                fig = px.bar(df_count, x='año_inicio', y='Cantidad',
                            title='Conflictos por año de inicio')
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                df_count = df_count.sort_values('año_inicio')
                df_count['Acumulado'] = df_count['Cantidad'].cumsum()
                fig = px.area(df_count, x='año_inicio', y='Acumulado',
                             title='Conflictos acumulados')
                st.plotly_chart(fig, use_container_width=True)

    with tab_mapa:
        df_mapa = df_filtrado[(df_filtrado['latitud'].notna()) & (df_filtrado['longitud'].notna())]

        if len(df_mapa) > 0:
            fig = px.scatter_map(df_mapa, lat='latitud', lon='longitud',
                                hover_name='nombre', hover_data=['sector', 'region', 'estado'],
                                color='sector', zoom=3.5, height=600,
                                title=f'{len(df_mapa)} conflictos georreferenciados')
            fig.update_layout(map_style='carto-positron')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay conflictos con coordenadas en la selección.")

    with tab_datos:
        cols = ['id_maestro', 'nombre', 'fuente_principal', 'region', 'sector',
                'estado', 'año_inicio', 'impactos', 'resistencias', 'resultados']
        cols_disp = [c for c in cols if c in df_filtrado.columns]
        st.dataframe(df_filtrado[cols_disp], use_container_width=True, height=500)

        csv = df_filtrado.to_csv(index=False, encoding='utf-8-sig')
        st.download_button("📥 Descargar CSV", csv, "conflictos.csv", "text/csv")

    with tab_busqueda:
        busqueda = st.text_input("Buscar por nombre o descripción")
        if busqueda:
            mask = (df_filtrado['nombre'].str.contains(busqueda, case=False, na=False) |
                   df_filtrado['descripcion'].str.contains(busqueda, case=False, na=False))
            resultados = df_filtrado[mask]
            st.write(f"**{len(resultados)} resultados**")

            for _, row in resultados.iterrows():
                with st.expander(f"📍 {row['nombre']} ({row['fuente']})"):
                    st.write(f"**Sector:** {row.get('sector', 'N/A')} | **Región:** {row.get('region', 'N/A')} | **Estado:** {row.get('estado', 'N/A')}")
                    if row.get('descripcion'):
                        st.write(str(row['descripcion'])[:500])


# =============================================================================
# SECCIÓN: TRIBUNALES AMBIENTALES
# =============================================================================
def seccion_tribunales():
    """Muestra la sección de Tribunales Ambientales."""
    st.header("⚖️ Tribunales Ambientales")
    st.markdown("""
    **Corpus de causas y sentencias de los Tribunales Ambientales de Chile (2012-2025).**

    Los Tribunales Ambientales son órganos jurisdiccionales especializados creados por la
    [Ley 20.600 (2012)](https://www.bcn.cl/leychile/navegar?idNorma=1041361) para resolver
    controversias medioambientales. Existen tres tribunales con competencia territorial:
    - **1TA** (Antofagasta): Arica y Parinacota a Coquimbo
    - **2TA** (Santiago): Valparaíso a Biobío
    - **3TA** (Valdivia): La Araucanía a Magallanes
    """)

    datos = cargar_datos_tribunales()

    if not datos:
        st.warning("No se encontraron datos de tribunales.")
        return

    # Sidebar con filtros de tribunales
    st.sidebar.header("Filtros - Tribunales")
    tribunal_filtro = st.sidebar.multiselect(
        "Tribunal",
        ["1TA (Antofagasta)", "2TA (Santiago)", "3TA (Valdivia)"],
        default=["1TA (Antofagasta)", "2TA (Santiago)", "3TA (Valdivia)"]
    )

    años_disponibles = sorted([int(k) for k in datos['por_año'].keys() if int(k) >= 2013])
    año_min, año_max = st.sidebar.select_slider(
        "Rango de años",
        options=años_disponibles,
        value=(min(años_disponibles), max(años_disponibles))
    )

    # Calcular métricas de sentencias (solo documentos legales relevantes)
    sentencias_total = datos['por_tipo'].get('Sentencia', 0)
    sentencias_reemplazo = datos['por_tipo'].get('Sentencia Reemplazo', 0)
    sentencias_casacion = datos['por_tipo'].get('Sentencia Casación', 0)
    resoluciones = datos['por_tipo'].get('Resolución', 0)

    total_docs_legales = sentencias_total + sentencias_reemplazo + sentencias_casacion + resoluciones

    # Métricas principales (datos oficiales verificados - CIFRAS_OFICIALES.md)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Sentencias oficiales", "704")
    col2.metric("Causas ingresadas", "~1,320")
    col3.metric("Tribunales", "3")
    col4.metric("Período", "2013-2025")

    # Sub-pestañas de tribunales
    tab_stats, tab_temporal, tab_tribunal = st.tabs([
        "📊 Estadísticas", "📈 Evolución temporal", "🏛️ Por tribunal"
    ])

    with tab_stats:
        # Datos oficiales verificados (CIFRAS_OFICIALES.md)
        st.markdown("### Sentencias definitivas por tribunal")
        st.caption("Fuentes: Cuentas Públicas 2024 y 3TA en Cifras")

        # Datos oficiales verificados
        df_oficial = pd.DataFrame([
            {'Tribunal': '1TA (Antofagasta)', 'Sentencias': 66, 'Causas': 150},
            {'Tribunal': '2TA (Santiago)', 'Sentencias': 332, 'Causas': 620},
            {'Tribunal': '3TA (Valdivia)', 'Sentencias': 306, 'Causas': 549},
        ])

        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(df_oficial, x='Tribunal', y='Sentencias',
                        title='704 sentencias definitivas (2013-2025)',
                        text='Sentencias',
                        color='Tribunal',
                        color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c'])
            fig.update_layout(showlegend=False, xaxis_title='', yaxis_title='Sentencias')
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.bar(df_oficial, x='Tribunal', y='Causas',
                        title='~1,320 causas ingresadas (2013-2025)',
                        text='Causas',
                        color='Tribunal',
                        color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c'])
            fig.update_layout(showlegend=False, xaxis_title='', yaxis_title='Causas')
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)

        # Distribución porcentual
        st.markdown("### Distribución del sistema")
        col1, col2 = st.columns(2)

        with col1:
            df_pct = df_oficial.copy()
            df_pct['Porcentaje'] = (df_pct['Sentencias'] / df_pct['Sentencias'].sum() * 100).round(1)
            df_pct = df_pct.sort_values('Sentencias', ascending=True)

            fig = px.bar(df_pct, x='Sentencias', y='Tribunal', orientation='h',
                        title='Sentencias por tribunal',
                        text=df_pct.apply(lambda x: f"{x['Sentencias']} ({x['Porcentaje']}%)", axis=1),
                        color='Tribunal',
                        color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c'])
            fig.update_layout(showlegend=False, xaxis_title='Sentencias', yaxis_title='')
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Productividad anual
            df_prod = pd.DataFrame([
                {'Tribunal': '1TA (Antofagasta)', 'Promedio': 9, 'Años': 7},
                {'Tribunal': '2TA (Santiago)', 'Promedio': 28, 'Años': 12},
                {'Tribunal': '3TA (Valdivia)', 'Promedio': 26, 'Años': 12},
            ])
            fig = px.bar(df_prod, x='Tribunal', y='Promedio',
                        title='Promedio sentencias/año',
                        text='Promedio',
                        color='Tribunal',
                        color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c'])
            fig.update_layout(showlegend=False, xaxis_title='', yaxis_title='Sentencias/año')
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)

        # Nota sobre fuentes
        st.info("""
        **Fuentes oficiales:**
        - 3TA: [3TA en Cifras](https://3ta.cl/3ta-en-cifras/) (actualizado 30/06/2025)
        - 2TA: [Cuenta Pública 2024](https://tribunalambiental.cl/)
        - 1TA: [Cuenta Pública 2024](https://www.1ta.cl/)
        """)

    with tab_temporal:
        # Solo años con sentencias
        st.markdown("### Sentencias dictadas por año")

        # Calcular sentencias por año (aproximación desde datos disponibles)
        df_año = pd.DataFrame([
            {'Año': int(k), 'Documentos': v}
            for k, v in datos['por_año'].items()
            if int(k) >= 2013
        ]).sort_values('Año')

        fig = px.bar(df_año, x='Año', y='Documentos',
                    title='Actividad judicial por año')
        st.plotly_chart(fig, use_container_width=True)

        # Evolución por tribunal
        st.markdown("### Evolución por tribunal")
        datos_evol = []
        for trib, años in datos['por_tribunal_año'].items():
            for año, cant in años.items():
                if cant > 0 and int(año) >= 2013:
                    datos_evol.append({
                        'Tribunal': f"{trib} ({'Antofagasta' if trib=='1TA' else 'Santiago' if trib=='2TA' else 'Valdivia'})",
                        'Año': int(año),
                        'Documentos': cant
                    })

        if datos_evol:
            df_evol = pd.DataFrame(datos_evol).sort_values(['Tribunal', 'Año'])
            fig = px.line(df_evol, x='Año', y='Documentos', color='Tribunal',
                         markers=True, title='Actividad por tribunal y año')
            st.plotly_chart(fig, use_container_width=True)

    with tab_tribunal:
        tribunal_sel = st.selectbox("Seleccionar tribunal",
                                   ["1TA (Antofagasta)", "2TA (Santiago)", "3TA (Valdivia)"])
        trib_code = tribunal_sel.split()[0]

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Total documentos", datos['por_tribunal'].get(trib_code, 0))
            st.metric("Sentencias", datos['por_tribunal_tipo'].get(trib_code, {}).get('Sentencia', 0))

        with col2:
            # Competencia territorial
            competencias = {
                '1TA': "Arica y Parinacota, Tarapacá, Antofagasta, Atacama, Coquimbo",
                '2TA': "Valparaíso, Metropolitana, O'Higgins, Maule, Ñuble, Biobío",
                '3TA': "La Araucanía, Los Ríos, Los Lagos, Aysén, Magallanes"
            }
            st.info(f"**Competencia territorial:** {competencias[trib_code]}")

        # Tipos de documento del tribunal
        tipos_trib = datos['por_tribunal_tipo'].get(trib_code, {})
        tipos_legales = {k: v for k, v in tipos_trib.items()
                        if k in ['Sentencia', 'Sentencia Reemplazo', 'Sentencia Casación', 'Resolución']}

        if tipos_legales:
            df_tipos = pd.DataFrame([
                {'Tipo': k, 'Cantidad': v} for k, v in tipos_legales.items()
            ]).sort_values('Cantidad', ascending=True)

            fig = px.bar(df_tipos, x='Cantidad', y='Tipo', orientation='h',
                        title=f'Documentos judiciales - {tribunal_sel}', text='Cantidad')
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)


# =============================================================================
# MAIN
# =============================================================================
def main():
    st.title("🌿 Conflictos y Justicia Ambiental en Chile")

    # Navegación principal con pestañas grandes
    seccion = st.radio(
        "Seleccionar sección:",
        ["🌿 Conflictos Socioecológicos", "⚖️ Tribunales Ambientales"],
        horizontal=True,
        label_visibility="collapsed"
    )

    st.markdown("---")

    if seccion == "🌿 Conflictos Socioecológicos":
        seccion_conflictos()
    else:
        seccion_tribunales()

    # Footer
    st.markdown("---")
    st.markdown("""
    *Proyecto: Conflictos Socioecológicos y Justicia Ambiental en Chile*
    *Núcleo Milenio SODAS / Centro de Estudios Públicos*
    *Fabián Belmar, 2026*
    """)


if __name__ == "__main__":
    main()
