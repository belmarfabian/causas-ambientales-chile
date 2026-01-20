#!/usr/bin/env python3
"""
Agrega URLs de noticias y actualiza categorías para conflictos sin datos.
"""

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATOS_DIR = BASE_DIR / "datos" / "conflictos"

# Mapeo de conflictos a noticias y categorías basado en búsqueda web
NOTICIAS_CONFLICTOS = {
    # EJAtlas sin categorías
    "Mina de oro, cobre y plata Pascua Lama, Chile": {
        "url_noticia": "https://www.ciperchile.cl/2020/11/15/pascua-lama-mientras-se-juega-su-ultima-carta-en-la-corte-suprema-el-sii-le-autoriza-credito-por-us443-millones/",
        "impactos": ["agua", "biodiversidad"],
        "actores": ["indigena", "agricultor"],
        "resistencias": ["judicial", "movilizacion"],
        "resultados": ["paralizado"]
    },
    "Ventanas Industrial Complex, Chile": {
        "url_noticia": "https://www.greenpeace.org/chile/blog/issues/climayenergia/celebramos-el-cierre-de-la-fundicion-ventanas-una-de-las-principales-fuentes-de-contaminacion-de-nuestra-historia/",
        "impactos": ["aire", "salud", "suelo"],
        "actores": ["urbano"],
        "resistencias": ["judicial", "movilizacion", "mediatica"],
        "resultados": ["paralizado"]
    },
    "ALTO MAIPO Hydroelectric Project (PHAM), Chile": {
        "url_noticia": "https://aida-americas.org/es/blog/proyecto-alto-maipo-peligroso-innecesario-y-encima-inviable",
        "impactos": ["agua", "biodiversidad"],
        "actores": ["urbano", "agricultor"],
        "resistencias": ["judicial", "institucional", "movilizacion"],
        "resultados": ["en_litigio"]
    },
    "Hidroaysén hydroelectric project, Chile": {
        "url_noticia": "https://www.ciperchile.cl/2013/07/08/el-verdadero-impacto-de-hidroaysen-frente-al-deficit-energetico-en-chile/",
        "impactos": ["agua", "biodiversidad"],
        "actores": ["urbano", "indigena"],
        "resistencias": ["judicial", "movilizacion", "mediatica", "institucional"],
        "resultados": ["paralizado"]
    },
    "Proyecto Minera Dominga, Coquimbo, Chile": {
        "url_noticia": "https://www.ciperchile.cl/2024/12/18/conservacion-desarrollo-y-conflicto-el-eterno-debate-de-la-minera-dominga/",
        "impactos": ["agua", "biodiversidad"],
        "actores": ["pescador", "urbano"],
        "resistencias": ["judicial", "institucional", "movilizacion"],
        "resultados": ["en_litigio"]
    },
    "Lithium mining in the Salar de Atacama, Chile": {
        "url_noticia": "https://es.mongabay.com/2024/11/comunidades-indigenas-interponen-denuncia-por-hundimiento-de-salar-de-atacama-por-litio-chile/",
        "impactos": ["agua", "biodiversidad", "suelo"],
        "actores": ["indigena"],
        "resistencias": ["judicial", "institucional"],
        "resultados": ["aprobado"]
    },
    "Ralco HEP and Bio Bio Watershed hydro plans, Chile": {
        "url_noticia": "https://www.memoriachilena.gob.cl/602/w3-article-96731.html",
        "impactos": ["agua", "biodiversidad"],
        "actores": ["indigena"],
        "resistencias": ["judicial", "movilizacion", "institucional"],
        "resultados": ["aprobado"]
    },
    "Cellulose Factory Celulosa Aurauco S.A., Valdivia, Chile": {
        "url_noticia": "https://www.ciperchile.cl/2023/06/16/contaminacion-fluvial-en-valdivia/",
        "impactos": ["agua", "biodiversidad"],
        "actores": ["pescador", "urbano"],
        "resistencias": ["judicial", "mediatica"],
        "resultados": ["aprobado"]
    },
    "Minera Invierno de carbón en Isla Riesco, Chile": {
        "url_noticia": "https://laderasur.com/articulo/isla-riesco-y-minera-invierno-todo-lo-que-necesitas-saber-para-comprender-el-conflicto/",
        "impactos": ["aire", "biodiversidad", "suelo"],
        "actores": ["urbano"],
        "resistencias": ["judicial", "movilizacion", "institucional"],
        "resultados": ["en_litigio"]
    },
    "The avocado agribusiness and the water crisis in Petorca, Va": {
        "url_noticia": "https://www.france24.com/es/medio-ambiente/20210616-chile-escasez-agua-petorca-cultivos-aguacate",
        "impactos": ["agua"],
        "actores": ["agricultor", "urbano"],
        "resistencias": ["movilizacion", "mediatica"],
        "resultados": ["aprobado"]
    },
    "Las Vizcachitas Mining Project, Chile": {
        "url_noticia": "https://vergara240.udp.cl/especiales/sequia-en-chile-vizcachitas-megaproyecto-minero-putaendo/",
        "impactos": ["agua", "biodiversidad"],
        "actores": ["agricultor", "urbano"],
        "resistencias": ["judicial", "movilizacion", "institucional"],
        "resultados": ["en_litigio"]
    },
    "Fundicion de cobre Paipote (Videla Lira), Chile": {
        "url_noticia": "https://www.ciperchile.cl/2011/08/11/contaminacion-critica-en-tierra-amarilla-por-un-negocio-minero-en-plena-expansion/",
        "impactos": ["aire", "salud", "suelo"],
        "actores": ["urbano"],
        "resistencias": ["judicial", "movilizacion"],
        "resultados": ["paralizado"]
    },
    "Castilla Thermal Power Station, Chile": {
        "url_noticia": "https://www.elmostrador.cl/noticias/pais/2012/08/29/corte-suprema-falla-contra-castilla-y-marca-efecto-domino-en-otros-proyectos-emblematicos/",
        "impactos": ["aire", "biodiversidad", "salud"],
        "actores": ["pescador", "urbano"],
        "resistencias": ["judicial", "movilizacion"],
        "resultados": ["paralizado"]
    },
    "Green Hydrogen in the Magallanes Region, Chile": {
        "url_noticia": "https://dialogue.earth/es/energia/chile-apuesta-hidrogeno-verde-magallanes/",
        "impactos": ["agua", "biodiversidad"],
        "actores": ["urbano"],
        "resistencias": ["institucional"],
        "resultados": ["en_litigio"]
    },
    "Refiner-a y fundici-n ENAMI-CODELCO en Zona de Sacrificio Ve": {
        "url_noticia": "https://www.greenpeace.org/chile/blog/issues/climayenergia/celebramos-el-cierre-de-la-fundicion-ventanas-una-de-las-principales-fuentes-de-contaminacion-de-nuestra-historia/",
        "impactos": ["aire", "salud"],
        "actores": ["urbano"],
        "resistencias": ["judicial", "movilizacion"],
        "resultados": ["paralizado"]
    },
    "Lithium and iron mining in the dunes of Putu, Chile": {
        "url_noticia": "https://ejatlas.org/conflict/lithium-and-iron-mining-in-the-dunes-of-putu-chile",
        "impactos": ["agua", "biodiversidad", "suelo"],
        "actores": ["agricultor", "urbano"],
        "resistencias": ["movilizacion", "institucional"],
        "resultados": ["en_litigio"]
    },
    "Lithium mining and potassium Salar Maricunga, Copiap-": {
        "url_noticia": "https://ejatlas.org/conflict/lithium-mining-and-potassium-salar-maricunga-copiapo-chile",
        "impactos": ["agua", "biodiversidad"],
        "actores": ["indigena"],
        "resistencias": ["judicial", "institucional"],
        "resultados": ["en_litigio"]
    },
    "Health impacts of pesticides exposure on rural populations i": {
        "url_noticia": "https://ejatlas.org/conflict/health-impacts-of-pesticides-exposure-on-rural-populations-in-ohiggins-chile",
        "impactos": ["salud", "agua", "suelo"],
        "actores": ["agricultor"],
        "resistencias": ["mediatica"],
        "resultados": ["aprobado"]
    },
    "Living with pesticides from export crops in Monte Patria, Co": {
        "url_noticia": "https://ejatlas.org/conflict/living-with-pesticides-from-export-crops-in-monte-patria-coquimbo-chile",
        "impactos": ["salud", "agua"],
        "actores": ["agricultor", "urbano"],
        "resistencias": ["mediatica"],
        "resultados": ["aprobado"]
    },
    "Environmental threats (industrial salmon, new mining concess": {
        "url_noticia": "https://ejatlas.org/conflict/environmental-threats-industrial-salmon-new-mining-concessions-in-the-southern-austral-patagonia-chile",
        "impactos": ["agua", "biodiversidad"],
        "actores": ["indigena", "pescador"],
        "resistencias": ["movilizacion", "institucional"],
        "resultados": ["en_litigio"]
    },
    "Geothermal plant Cerro Pabellón, Chile": {
        "url_noticia": "https://ejatlas.org/conflict/geothermal-plant-cerro-pabellon-chile",
        "impactos": ["agua", "biodiversidad"],
        "actores": ["indigena"],
        "resistencias": ["institucional"],
        "resultados": ["aprobado"]
    },
    "Small-scale fisher people against contaminating industries i": {
        "url_noticia": "https://ejatlas.org/conflict/small-scale-fisher-people-against-contaminating-industries-in-mehuin-valdivia-chile",
        "impactos": ["agua", "biodiversidad"],
        "actores": ["pescador", "indigena"],
        "resistencias": ["movilizacion", "judicial"],
        "resultados": ["paralizado"]
    },
    "Yelcho Watershed targeted by Ministry of Energy-s hydro plan": {
        "url_noticia": "https://ejatlas.org/conflict/yelcho-watershed-targeted-by-ministry-of-energys-hydro-plans-chile",
        "impactos": ["agua", "biodiversidad"],
        "actores": ["urbano", "pescador"],
        "resistencias": ["movilizacion", "institucional"],
        "resultados": ["en_litigio"]
    },
    "Mediterraneo Hydroelectric plant and future exploitation pla": {
        "url_noticia": "https://ejatlas.org/conflict/mediterraneo-hydroelectric-plant-and-future-exploitation-plans-for-pascua-and-baker-rivers-chile",
        "impactos": ["agua", "biodiversidad"],
        "actores": ["urbano"],
        "resistencias": ["movilizacion"],
        "resultados": ["en_litigio"]
    },
    "Proyecto Nueva Unión en Vallenar, Chile": {
        "url_noticia": "https://ejatlas.org/conflict/nueva-union-copper-gold-mine-proyecto-minero-nueva-union-chile",
        "impactos": ["agua", "biodiversidad"],
        "actores": ["indigena", "agricultor"],
        "resistencias": ["institucional"],
        "resultados": ["en_litigio"]
    },
    "Minería de Tierras Raras en Penco, Región del Biob": {
        "url_noticia": "https://ejatlas.org/conflict/mineria-de-tierras-raras-en-penco-region-del-biobio-chile",
        "impactos": ["agua", "suelo"],
        "actores": ["urbano"],
        "resistencias": ["movilizacion", "institucional"],
        "resultados": ["en_litigio"]
    },
    "Data Center Google en Cerrillos, Santiago, Chile": {
        "url_noticia": "https://ejatlas.org/conflict/data-center-google-en-cerrillos-santiago-chile",
        "impactos": ["agua"],
        "actores": ["urbano"],
        "resistencias": ["institucional"],
        "resultados": ["aprobado"]
    },
    "Puerto Corral Pacífico Sur, Chile": {
        "url_noticia": "https://ejatlas.org/conflict/puerto-corral-pacifico-sur-chile",
        "impactos": ["biodiversidad", "agua"],
        "actores": ["pescador", "urbano"],
        "resistencias": ["movilizacion", "institucional"],
        "resultados": ["en_litigio"]
    },
    "Proyecto inmobiliario 'Maratué', Valparaíso, Chile": {
        "url_noticia": "https://ejatlas.org/conflict/proyecto-inmobiliario-maratue-valparaiso-chile",
        "impactos": ["biodiversidad"],
        "actores": ["urbano"],
        "resistencias": ["movilizacion", "judicial"],
        "resultados": ["en_litigio"]
    },
    "Lago Lleu Lleu, Chile": {
        "url_noticia": "https://ejatlas.org/conflict/lago-lleu-lleu-chile",
        "impactos": ["agua", "biodiversidad"],
        "actores": ["indigena"],
        "resistencias": ["movilizacion"],
        "resultados": ["en_litigio"]
    },
    "Conflicto internacional sobre el Rio Lauca, Bolivia": {
        "url_noticia": "https://ejatlas.org/conflict/conflicto-internacional-sobre-el-rio-lauca-bolivia-chile",
        "impactos": ["agua"],
        "actores": ["indigena", "agricultor"],
        "resistencias": ["institucional"],
        "resultados": ["aprobado"]
    },
    "Planta de Tratamiento de lodos Cabrero": {
        "url_noticia": "https://mapaconflictos.indh.cl/",
        "impactos": ["suelo", "agua"],
        "actores": ["urbano"],
        "resistencias": ["institucional"],
        "resultados": ["en_litigio"]
    },
    "Cobquecura sin acu": {
        "url_noticia": "https://mapaconflictos.indh.cl/",
        "impactos": ["biodiversidad", "agua"],
        "actores": ["pescador"],
        "resistencias": ["movilizacion"],
        "resultados": ["en_litigio"]
    },
    "Minera Manganese Atacama, Chile": {
        "url_noticia": "https://ejatlas.org/conflict/minera-manganese-atacama-chile",
        "impactos": ["agua", "suelo"],
        "actores": ["agricultor"],
        "resistencias": ["institucional"],
        "resultados": ["en_litigio"]
    },
    "Exploitation of Manganese Los Pumas, Arica, Chile": {
        "url_noticia": "https://ejatlas.org/conflict/exploitation-of-manganese-los-pumas-arica-chile",
        "impactos": ["agua", "suelo"],
        "actores": ["indigena"],
        "resistencias": ["institucional"],
        "resultados": ["en_litigio"]
    },
}

# Noticias adicionales encontradas
NOTICIAS_ADICIONALES = {
    "Minera Los Pelambres, Los Vilos, Coquimbo, Chile": {
        "url_noticia": "https://www.ciperchile.cl/2011/08/11/contaminacion-critica-en-tierra-amarilla-por-un-negocio-minero-en-plena-expansion/",
        "impactos": ["agua", "suelo"],
        "actores": ["agricultor", "urbano"],
        "resistencias": ["judicial", "movilizacion"],
        "resultados": ["aprobado"]
    },
    "Minera El Morro en Valles del Huasco, Chile": {
        "url_noticia": "https://ejatlas.org/conflict/el-morro-chile",
        "impactos": ["agua", "biodiversidad"],
        "actores": ["indigena"],
        "resistencias": ["judicial"],
        "resultados": ["paralizado"]
    },
    "Caserones, Chile": {
        "url_noticia": "https://mapa.conflictosmineros.net/ocmal_db-v2/conflicto/view/117",
        "impactos": ["agua"],
        "actores": ["agricultor", "urbano"],
        "resistencias": ["institucional"],
        "resultados": ["aprobado"]
    },
    "Conflicto del Plomo Boliden, Cerro Chuño en Arica,": {
        "url_noticia": "https://ejatlas.org/conflict/contaminacion-plomo-arica",
        "impactos": ["suelo", "salud"],
        "actores": ["urbano"],
        "resistencias": ["judicial", "movilizacion"],
        "resultados": ["aprobado"]
    },
    "Embalse La Punilla, Ñuble, Chile": {
        "url_noticia": "https://www.ciperchile.cl/2023/07/20/la-riesgosa-insistencia-en-el-embalse-nueva-la-punilla/",
        "impactos": ["agua", "biodiversidad"],
        "actores": ["agricultor", "urbano"],
        "resistencias": ["movilizacion", "institucional"],
        "resultados": ["en_litigio"]
    },
    "Proyecto Expansión Andina 244 CODELCO, Chile": {
        "url_noticia": "https://olca.cl/articulo/nota.php?id=2574",
        "impactos": ["agua", "biodiversidad"],
        "actores": ["urbano", "indigena"],
        "resistencias": ["institucional", "movilizacion"],
        "resultados": ["en_litigio"]
    },
    "Contaminación por asbesto en empresa Pizarreño, Ch": {
        "url_noticia": "https://ejatlas.org/conflict/cientos-de-enfermos-por-inhalar-asbesto",
        "impactos": ["salud", "aire"],
        "actores": ["urbano"],
        "resistencias": ["judicial"],
        "resultados": ["aprobado"]
    },
    "Neltume hydroelectric project in Panguipulli, Chil": {
        "url_noticia": "https://ejatlas.org/conflict/neltume-hydroelectric-project-in-panguipulli-chile",
        "impactos": ["agua", "biodiversidad"],
        "actores": ["indigena"],
        "resistencias": ["movilizacion", "judicial"],
        "resultados": ["paralizado"]
    },
    "Hidroñuble Hydroelectric dam, Chile": {
        "url_noticia": "https://ejatlas.org/conflict/hidronuble-hydroelectric-dam-chile",
        "impactos": ["agua", "biodiversidad"],
        "actores": ["agricultor"],
        "resistencias": ["institucional"],
        "resultados": ["aprobado"]
    },
    "Embalse La Tranca, Valle de Cogotí, Chile": {
        "url_noticia": "https://ejatlas.org/conflict/embalse-la-tranca-valle-de-cogoti-chile",
        "impactos": ["agua"],
        "actores": ["agricultor"],
        "resistencias": ["institucional"],
        "resultados": ["en_litigio"]
    },
    "Contaminación masiva de la Cuenca del Lago Villarr": {
        "url_noticia": "https://ejatlas.org/conflict/contaminacion-masiva-de-la-cuenca-del-lago-villarrica-chile",
        "impactos": ["agua", "biodiversidad"],
        "actores": ["indigena", "urbano"],
        "resistencias": ["movilizacion", "judicial"],
        "resultados": ["en_litigio"]
    },
    "Osorno water crisis and anti-privatization struggl": {
        "url_noticia": "https://ejatlas.org/conflict/osorno-water-crisis-and-anti-privatization-struggles-chile",
        "impactos": ["agua"],
        "actores": ["urbano"],
        "resistencias": ["movilizacion"],
        "resultados": ["en_litigio"]
    },
    "White Quebrada White and Quebrada Phase 2 in Tarap": {
        "url_noticia": "https://ejatlas.org/conflict/quebrada-blanca-and-quebrada-phase-2-in-tarapaca-chile",
        "impactos": ["agua", "biodiversidad"],
        "actores": ["indigena"],
        "resistencias": ["institucional"],
        "resultados": ["aprobado"]
    },
    "'Tranquilo' coal mining project, Chile": {
        "url_noticia": "https://ejatlas.org/conflict/tranquilo-coal-mining-project-chile",
        "impactos": ["aire", "biodiversidad"],
        "actores": ["urbano"],
        "resistencias": ["movilizacion"],
        "resultados": ["en_litigio"]
    },
    "Yelcho Watershed targeted by Ministry of Energy": {
        "url_noticia": "https://ejatlas.org/conflict/yelcho-watershed-targeted-by-ministry-of-energys-hydro-plans-chile",
        "impactos": ["agua", "biodiversidad"],
        "actores": ["pescador", "urbano"],
        "resistencias": ["movilizacion", "institucional"],
        "resultados": ["en_litigio"]
    },
    "Lithium mining and potassium Salar Maricunga": {
        "url_noticia": "https://ejatlas.org/conflict/lithium-mining-and-potassium-salar-maricunga-copiapo-chile",
        "impactos": ["agua", "biodiversidad"],
        "actores": ["indigena"],
        "resistencias": ["judicial", "institucional"],
        "resultados": ["en_litigio"]
    },
    "Refiner": {
        "url_noticia": "https://www.greenpeace.org/chile/blog/issues/climayenergia/celebramos-el-cierre-de-la-fundicion-ventanas-una-de-las-principales-fuentes-de-contaminacion-de-nuestra-historia/",
        "impactos": ["aire", "salud"],
        "actores": ["urbano"],
        "resistencias": ["judicial", "movilizacion"],
        "resultados": ["paralizado"]
    },
    "Rio Cuervo Hydroelectric Project": {
        "url_noticia": "https://ejatlas.org/conflict/rio-cuervo-hydroelectric-project-aysen-chile",
        "impactos": ["agua", "biodiversidad"],
        "actores": ["urbano"],
        "resistencias": ["movilizacion", "judicial"],
        "resultados": ["paralizado"]
    },
    "Monoculture plantation in Araucania": {
        "url_noticia": "https://ejatlas.org/conflict/monoculture-plantation-in-araucania-chile",
        "impactos": ["agua", "biodiversidad", "suelo"],
        "actores": ["indigena"],
        "resistencias": ["movilizacion"],
        "resultados": ["aprobado"]
    },
    "Huasco - Petcoke": {
        "url_noticia": "https://ejatlas.org/conflict/huasco-petcoke-chile",
        "impactos": ["aire", "salud"],
        "actores": ["urbano", "agricultor"],
        "resistencias": ["judicial", "movilizacion"],
        "resultados": ["aprobado"]
    },
}

# Agregar URLs para conflictos OCMAL (minería)
OCMAL_NOTICIAS = {
    "Valle del Lluta and Canal Uchusuma": {
        "url_noticia": "https://mapa.conflictosmineros.net/ocmal_db-v2/",
        "impactos": ["agua"],
        "actores": ["indigena", "agricultor"],
    },
    "Carmen de Andacollo Expansion": {
        "url_noticia": "https://mapa.conflictosmineros.net/ocmal_db-v2/",
        "impactos": ["agua", "salud", "aire"],
        "actores": ["urbano"],
    },
    "Manganeso Los Pumas": {
        "url_noticia": "https://mapa.conflictosmineros.net/ocmal_db-v2/",
        "impactos": ["agua", "suelo"],
        "actores": ["indigena"],
    },
}


def main():
    print("=" * 60)
    print("AGREGANDO NOTICIAS Y CATEGORÍAS")
    print("=" * 60)

    # Cargar dataset base
    archivo_base = DATOS_DIR / "conflictos_consolidados_ids.json"
    with open(archivo_base, encoding="utf-8") as f:
        dataset = json.load(f)

    print(f"\nDataset cargado: {len(dataset)} registros")

    # Estadísticas antes
    sin_cat_antes = sum(1 for r in dataset if not r.get('impactos') and not r.get('actores'))
    print(f"Sin categorías antes: {sin_cat_antes}")

    # Agregar URL de noticias y actualizar categorías
    actualizados = 0
    noticias_agregadas = 0

    for registro in dataset:
        nombre = registro.get("nombre", "")

        # Buscar coincidencia en el mapeo
        info = None
        for key, value in NOTICIAS_CONFLICTOS.items():
            if key in nombre or nombre in key:
                info = value
                break

        # Si no encontramos, buscar en noticias adicionales
        if not info:
            for key, value in NOTICIAS_ADICIONALES.items():
                if key in nombre or nombre in key:
                    info = value
                    break

        # Si no encontramos, buscar en OCMAL
        if not info and registro.get("fuente_principal") == "OCMAL":
            for key, value in OCMAL_NOTICIAS.items():
                if key.lower() in nombre.lower():
                    info = value
                    break

        if info:
            # Agregar URL de noticia
            if "url_noticia" in info:
                registro["url_noticia"] = info["url_noticia"]
                noticias_agregadas += 1

            # Actualizar categorías si están vacías
            if not registro.get("impactos") and info.get("impactos"):
                registro["impactos"] = info["impactos"]
                registro["impactos_fuente"] = "noticia"
                actualizados += 1

            if not registro.get("actores") and info.get("actores"):
                registro["actores"] = info["actores"]
                registro["actores_fuente"] = "noticia"

            if not registro.get("resistencias") and info.get("resistencias"):
                registro["resistencias"] = info["resistencias"]
                registro["resistencias_fuente"] = "noticia"

            if not registro.get("resultados") and info.get("resultados"):
                registro["resultados"] = info["resultados"]
                registro["resultados_fuente"] = "noticia"

        # Inferencia genérica para OCMAL sin categorías (todos son minería)
        elif registro.get("fuente_principal") == "OCMAL":
            if not registro.get("impactos"):
                registro["impactos"] = ["agua", "suelo"]
                registro["impactos_fuente"] = "inferido_mineria"
                actualizados += 1
            if not registro.get("actores"):
                # Revisar nombre para detectar comunidades indígenas
                nombre_lower = nombre.lower()
                if any(x in nombre_lower for x in ["indigenous", "indigena", "mapuche", "aymara", "diaguita", "atacame"]):
                    registro["actores"] = ["indigena"]
                else:
                    registro["actores"] = ["urbano"]
                registro["actores_fuente"] = "inferido_mineria"

    print(f"\nNoticias agregadas: {noticias_agregadas}")
    print(f"Categorías actualizadas: {actualizados}")

    # Estadísticas después
    sin_cat_despues = sum(1 for r in dataset if not r.get('impactos') and not r.get('actores'))
    print(f"Sin categorías después: {sin_cat_despues}")

    # Guardar dataset actualizado
    output_file = DATOS_DIR / "conflictos_consolidados_noticias.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    print(f"\nGuardado: {output_file}")

    # Mostrar cobertura final
    def cobertura(campo):
        return sum(1 for r in dataset if r.get(campo)) / len(dataset) * 100

    print(f"\nCobertura final:")
    for campo in ["impactos", "actores", "resistencias", "resultados", "url_noticia"]:
        print(f"  {campo}: {cobertura(campo):.1f}%")

    # Mostrar conflictos aún sin categorías
    sin_cat = [r for r in dataset if not r.get('impactos') and not r.get('actores')]
    if sin_cat:
        print(f"\n{len(sin_cat)} conflictos aún sin categorías:")
        for r in sin_cat[:20]:
            print(f"  {r['id_maestro']}: {r['nombre'][:50]}... ({r['fuente_principal']})")
        if len(sin_cat) > 20:
            print(f"  ... y {len(sin_cat) - 20} más")


if __name__ == "__main__":
    main()
