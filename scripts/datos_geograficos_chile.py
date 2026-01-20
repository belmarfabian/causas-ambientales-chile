#!/usr/bin/env python3
"""
Datos geográficos de Chile: regiones, comunas y coordenadas.
Para geocodificación de conflictos ambientales del Tribunal Ambiental.
"""

# 16 Regiones de Chile con coordenadas centroides
REGIONES_CHILE = {
    "Arica y Parinacota": {"codigo": "XV", "lat": -18.48, "lon": -70.33},
    "Tarapacá": {"codigo": "I", "lat": -20.21, "lon": -69.33},
    "Antofagasta": {"codigo": "II", "lat": -23.65, "lon": -70.40},
    "Atacama": {"codigo": "III", "lat": -27.37, "lon": -70.33},
    "Coquimbo": {"codigo": "IV", "lat": -29.95, "lon": -71.34},
    "Valparaíso": {"codigo": "V", "lat": -33.05, "lon": -71.62},
    "Metropolitana": {"codigo": "RM", "lat": -33.45, "lon": -70.67},
    "O'Higgins": {"codigo": "VI", "lat": -34.17, "lon": -70.74},
    "Maule": {"codigo": "VII", "lat": -35.43, "lon": -71.67},
    "Ñuble": {"codigo": "XVI", "lat": -36.61, "lon": -72.10},
    "Biobío": {"codigo": "VIII", "lat": -37.47, "lon": -72.35},
    "La Araucanía": {"codigo": "IX", "lat": -38.74, "lon": -72.60},
    "Los Ríos": {"codigo": "XIV", "lat": -39.81, "lon": -73.24},
    "Los Lagos": {"codigo": "X", "lat": -41.47, "lon": -72.94},
    "Aysén": {"codigo": "XI", "lat": -45.57, "lon": -72.07},
    "Magallanes": {"codigo": "XII", "lat": -53.16, "lon": -70.91},
}

# Alias para búsqueda flexible (sin tildes, variantes)
REGIONES_ALIAS = {
    "metropolitana": "Metropolitana",
    "region metropolitana": "Metropolitana",
    "santiago": "Metropolitana",
    "rm": "Metropolitana",
    "valparaiso": "Valparaíso",
    "ohiggins": "O'Higgins",
    "o'higgins": "O'Higgins",
    "libertador": "O'Higgins",
    "biobio": "Biobío",
    "bio bio": "Biobío",
    "araucania": "La Araucanía",
    "la araucania": "La Araucanía",
    "los rios": "Los Ríos",
    "los lagos": "Los Lagos",
    "aysen": "Aysén",
    "aisen": "Aysén",
    "magallanes": "Magallanes",
    "nuble": "Ñuble",
    "atacama": "Atacama",
    "coquimbo": "Coquimbo",
    "antofagasta": "Antofagasta",
    "tarapaca": "Tarapacá",
    "arica": "Arica y Parinacota",
    "arica y parinacota": "Arica y Parinacota",
    "maule": "Maule",
}

# Comunas principales de Chile (especialmente las mencionadas en conflictos ambientales)
COMUNAS_CHILE = {
    # Región Metropolitana
    "Santiago": {"region": "Metropolitana", "lat": -33.4489, "lon": -70.6693},
    "Providencia": {"region": "Metropolitana", "lat": -33.4330, "lon": -70.6100},
    "Las Condes": {"region": "Metropolitana", "lat": -33.4073, "lon": -70.5670},
    "Ñuñoa": {"region": "Metropolitana", "lat": -33.4569, "lon": -70.5975},
    "La Florida": {"region": "Metropolitana", "lat": -33.5228, "lon": -70.5975},
    "Peñalolén": {"region": "Metropolitana", "lat": -33.4917, "lon": -70.5300},
    "Maipú": {"region": "Metropolitana", "lat": -33.5167, "lon": -70.7583},
    "Pudahuel": {"region": "Metropolitana", "lat": -33.4333, "lon": -70.7500},
    "Quilicura": {"region": "Metropolitana", "lat": -33.3642, "lon": -70.7344},
    "Lampa": {"region": "Metropolitana", "lat": -33.2833, "lon": -70.8833},
    "Colina": {"region": "Metropolitana", "lat": -33.2000, "lon": -70.6667},
    "San Bernardo": {"region": "Metropolitana", "lat": -33.5922, "lon": -70.6997},
    "Puente Alto": {"region": "Metropolitana", "lat": -33.6117, "lon": -70.5758},
    "Pirque": {"region": "Metropolitana", "lat": -33.6667, "lon": -70.5000},
    "San José de Maipo": {"region": "Metropolitana", "lat": -33.6419, "lon": -70.3500},
    "Calera de Tango": {"region": "Metropolitana", "lat": -33.6333, "lon": -70.7833},
    "Talagante": {"region": "Metropolitana", "lat": -33.6667, "lon": -70.9333},
    "Peñaflor": {"region": "Metropolitana", "lat": -33.6167, "lon": -70.8833},
    "Isla de Maipo": {"region": "Metropolitana", "lat": -33.7500, "lon": -70.8833},
    "Padre Hurtado": {"region": "Metropolitana", "lat": -33.5667, "lon": -70.8167},
    "Melipilla": {"region": "Metropolitana", "lat": -33.6833, "lon": -71.2167},
    "María Pinto": {"region": "Metropolitana", "lat": -33.5167, "lon": -71.1167},
    "Curacaví": {"region": "Metropolitana", "lat": -33.4000, "lon": -71.1333},
    "San Miguel": {"region": "Metropolitana", "lat": -33.4978, "lon": -70.6517},
    "La Cisterna": {"region": "Metropolitana", "lat": -33.5333, "lon": -70.6583},
    "San Ramón": {"region": "Metropolitana", "lat": -33.5333, "lon": -70.6417},
    "La Granja": {"region": "Metropolitana", "lat": -33.5333, "lon": -70.6167},
    "Macul": {"region": "Metropolitana", "lat": -33.4833, "lon": -70.6000},
    "Recoleta": {"region": "Metropolitana", "lat": -33.4000, "lon": -70.6333},
    "Independencia": {"region": "Metropolitana", "lat": -33.4167, "lon": -70.6667},
    "Conchalí": {"region": "Metropolitana", "lat": -33.3833, "lon": -70.6750},
    "Huechuraba": {"region": "Metropolitana", "lat": -33.3667, "lon": -70.6333},
    "Vitacura": {"region": "Metropolitana", "lat": -33.3833, "lon": -70.5667},
    "Lo Barnechea": {"region": "Metropolitana", "lat": -33.3500, "lon": -70.5167},
    "Cerrillos": {"region": "Metropolitana", "lat": -33.4833, "lon": -70.7167},
    "Cerro Navia": {"region": "Metropolitana", "lat": -33.4333, "lon": -70.7333},
    "Renca": {"region": "Metropolitana", "lat": -33.4000, "lon": -70.7167},
    "Quinta Normal": {"region": "Metropolitana", "lat": -33.4333, "lon": -70.7000},
    "Lo Prado": {"region": "Metropolitana", "lat": -33.4500, "lon": -70.7167},
    "Estación Central": {"region": "Metropolitana", "lat": -33.4500, "lon": -70.6833},
    "Pedro Aguirre Cerda": {"region": "Metropolitana", "lat": -33.4833, "lon": -70.6750},
    "Lo Espejo": {"region": "Metropolitana", "lat": -33.5167, "lon": -70.6917},
    "El Bosque": {"region": "Metropolitana", "lat": -33.5667, "lon": -70.6667},
    "La Pintana": {"region": "Metropolitana", "lat": -33.5833, "lon": -70.6333},
    "San Joaquín": {"region": "Metropolitana", "lat": -33.4833, "lon": -70.6250},
    "Buin": {"region": "Metropolitana", "lat": -33.7333, "lon": -70.7500},
    "Paine": {"region": "Metropolitana", "lat": -33.8167, "lon": -70.7333},
    "Tiltil": {"region": "Metropolitana", "lat": -33.0833, "lon": -70.9333},

    # Región de Valparaíso
    "Valparaíso": {"region": "Valparaíso", "lat": -33.0458, "lon": -71.6197},
    "Viña del Mar": {"region": "Valparaíso", "lat": -33.0153, "lon": -71.5500},
    "Concón": {"region": "Valparaíso", "lat": -32.9167, "lon": -71.5167},
    "Quintero": {"region": "Valparaíso", "lat": -32.7833, "lon": -71.5333},
    "Puchuncaví": {"region": "Valparaíso", "lat": -32.7167, "lon": -71.4167},
    "Quillota": {"region": "Valparaíso", "lat": -32.8833, "lon": -71.2500},
    "San Antonio": {"region": "Valparaíso", "lat": -33.5833, "lon": -71.6167},
    "Algarrobo": {"region": "Valparaíso", "lat": -33.3667, "lon": -71.6667},
    "El Quisco": {"region": "Valparaíso", "lat": -33.4000, "lon": -71.7000},
    "El Tabo": {"region": "Valparaíso", "lat": -33.4500, "lon": -71.6667},
    "Cartagena": {"region": "Valparaíso", "lat": -33.5500, "lon": -71.6000},
    "Santo Domingo": {"region": "Valparaíso", "lat": -33.6500, "lon": -71.6333},
    "San Felipe": {"region": "Valparaíso", "lat": -32.7500, "lon": -70.7250},
    "Los Andes": {"region": "Valparaíso", "lat": -32.8333, "lon": -70.5833},
    "Putaendo": {"region": "Valparaíso", "lat": -32.6333, "lon": -70.7167},
    "Cabildo": {"region": "Valparaíso", "lat": -32.4167, "lon": -71.0667},
    "Petorca": {"region": "Valparaíso", "lat": -32.2500, "lon": -70.9333},
    "La Ligua": {"region": "Valparaíso", "lat": -32.4500, "lon": -71.2333},
    "Papudo": {"region": "Valparaíso", "lat": -32.5167, "lon": -71.4500},
    "Zapallar": {"region": "Valparaíso", "lat": -32.5500, "lon": -71.4667},
    "Casablanca": {"region": "Valparaíso", "lat": -33.3167, "lon": -71.4167},
    "Juan Fernández": {"region": "Valparaíso", "lat": -33.6167, "lon": -78.8333},
    "Isla de Pascua": {"region": "Valparaíso", "lat": -27.1500, "lon": -109.4333},
    "Villa Alemana": {"region": "Valparaíso", "lat": -33.0500, "lon": -71.3667},
    "Quilpué": {"region": "Valparaíso", "lat": -33.0500, "lon": -71.4333},
    "Limache": {"region": "Valparaíso", "lat": -33.0167, "lon": -71.2667},
    "Olmué": {"region": "Valparaíso", "lat": -32.9833, "lon": -71.2000},

    # Región de O'Higgins
    "Rancagua": {"region": "O'Higgins", "lat": -34.1708, "lon": -70.7444},
    "Machalí": {"region": "O'Higgins", "lat": -34.1833, "lon": -70.6500},
    "Codegua": {"region": "O'Higgins", "lat": -34.0333, "lon": -70.6667},
    "Graneros": {"region": "O'Higgins", "lat": -34.0667, "lon": -70.7333},
    "Mostazal": {"region": "O'Higgins", "lat": -33.9833, "lon": -70.7000},
    "Requínoa": {"region": "O'Higgins", "lat": -34.3000, "lon": -70.8167},
    "Rengo": {"region": "O'Higgins", "lat": -34.4000, "lon": -70.8667},
    "San Fernando": {"region": "O'Higgins", "lat": -34.5833, "lon": -70.9833},
    "Santa Cruz": {"region": "O'Higgins", "lat": -34.6333, "lon": -71.3667},
    "Pichilemu": {"region": "O'Higgins", "lat": -34.3833, "lon": -72.0000},
    "Navidad": {"region": "O'Higgins", "lat": -33.9500, "lon": -71.8333},
    "Litueche": {"region": "O'Higgins", "lat": -34.1167, "lon": -71.7333},
    "Paredones": {"region": "O'Higgins", "lat": -34.6500, "lon": -71.9000},
    "Lago Rapel": {"region": "O'Higgins", "lat": -34.1667, "lon": -71.4667},

    # Región del Maule
    "Talca": {"region": "Maule", "lat": -35.4264, "lon": -71.6554},
    "Curicó": {"region": "Maule", "lat": -34.9833, "lon": -71.2333},
    "Linares": {"region": "Maule", "lat": -35.8500, "lon": -71.6000},
    "Constitución": {"region": "Maule", "lat": -35.3333, "lon": -72.4167},
    "Cauquenes": {"region": "Maule", "lat": -35.9667, "lon": -72.3167},
    "Molina": {"region": "Maule", "lat": -35.1167, "lon": -71.2833},
    "San Clemente": {"region": "Maule", "lat": -35.5333, "lon": -71.4833},
    "Maule": {"region": "Maule", "lat": -35.5167, "lon": -71.7000},
    "Río Claro": {"region": "Maule", "lat": -35.2833, "lon": -71.2667},
    "Pelarco": {"region": "Maule", "lat": -35.3833, "lon": -71.4500},
    "Pencahue": {"region": "Maule", "lat": -35.3833, "lon": -71.8167},
    "Curepto": {"region": "Maule", "lat": -35.0833, "lon": -72.0333},
    "Vichuquén": {"region": "Maule", "lat": -34.8333, "lon": -72.0000},
    "Licantén": {"region": "Maule", "lat": -34.9833, "lon": -72.0167},
    "Hualañé": {"region": "Maule", "lat": -34.9667, "lon": -71.8000},
    "Rauco": {"region": "Maule", "lat": -34.9333, "lon": -71.3167},
    "Teno": {"region": "Maule", "lat": -34.8667, "lon": -71.1667},
    "Romeral": {"region": "Maule", "lat": -34.9667, "lon": -71.1333},
    "Sagrada Familia": {"region": "Maule", "lat": -35.0000, "lon": -71.3667},

    # Región del Biobío
    "Concepción": {"region": "Biobío", "lat": -36.8270, "lon": -73.0503},
    "Talcahuano": {"region": "Biobío", "lat": -36.7167, "lon": -73.1167},
    "Hualpén": {"region": "Biobío", "lat": -36.8000, "lon": -73.1167},
    "Chiguayante": {"region": "Biobío", "lat": -36.9167, "lon": -73.0333},
    "San Pedro de la Paz": {"region": "Biobío", "lat": -36.8667, "lon": -73.1167},
    "Coronel": {"region": "Biobío", "lat": -37.0333, "lon": -73.1500},
    "Lota": {"region": "Biobío", "lat": -37.0833, "lon": -73.1667},
    "Tomé": {"region": "Biobío", "lat": -36.6167, "lon": -72.9500},
    "Penco": {"region": "Biobío", "lat": -36.7333, "lon": -72.9833},
    "Los Ángeles": {"region": "Biobío", "lat": -37.4667, "lon": -72.3500},
    "Mulchén": {"region": "Biobío", "lat": -37.7167, "lon": -72.2333},
    "Nacimiento": {"region": "Biobío", "lat": -37.5000, "lon": -72.6667},
    "Arauco": {"region": "Biobío", "lat": -37.2500, "lon": -73.3167},
    "Lebu": {"region": "Biobío", "lat": -37.6167, "lon": -73.6500},
    "Cañete": {"region": "Biobío", "lat": -37.8000, "lon": -73.4000},
    "Tirúa": {"region": "Biobío", "lat": -38.3333, "lon": -73.5000},

    # Región de La Araucanía
    "Temuco": {"region": "La Araucanía", "lat": -38.7359, "lon": -72.5904},
    "Padre Las Casas": {"region": "La Araucanía", "lat": -38.7667, "lon": -72.5833},
    "Villarrica": {"region": "La Araucanía", "lat": -39.2833, "lon": -72.2167},
    "Pucón": {"region": "La Araucanía", "lat": -39.2833, "lon": -71.9667},
    "Angol": {"region": "La Araucanía", "lat": -37.7833, "lon": -72.7167},
    "Victoria": {"region": "La Araucanía", "lat": -38.2333, "lon": -72.3333},
    "Collipulli": {"region": "La Araucanía", "lat": -37.9500, "lon": -72.4333},
    "Ercilla": {"region": "La Araucanía", "lat": -38.0500, "lon": -72.3833},
    "Traiguén": {"region": "La Araucanía", "lat": -38.2500, "lon": -72.6667},
    "Lautaro": {"region": "La Araucanía", "lat": -38.5333, "lon": -72.4333},
    "Curacautín": {"region": "La Araucanía", "lat": -38.4333, "lon": -71.8833},
    "Lonquimay": {"region": "La Araucanía", "lat": -38.4333, "lon": -71.2333},
    "Carahue": {"region": "La Araucanía", "lat": -38.7000, "lon": -73.1667},
    "Nueva Imperial": {"region": "La Araucanía", "lat": -38.7333, "lon": -72.9500},
    "Freire": {"region": "La Araucanía", "lat": -38.9500, "lon": -72.6167},
    "Pitrufquén": {"region": "La Araucanía", "lat": -38.9833, "lon": -72.6500},
    "Gorbea": {"region": "La Araucanía", "lat": -39.1000, "lon": -72.6667},
    "Loncoche": {"region": "La Araucanía", "lat": -39.3667, "lon": -72.6333},
    "Cunco": {"region": "La Araucanía", "lat": -38.9333, "lon": -72.0333},
    "Melipeuco": {"region": "La Araucanía", "lat": -38.8500, "lon": -71.6833},

    # Región de Los Ríos
    "Valdivia": {"region": "Los Ríos", "lat": -39.8142, "lon": -73.2459},
    "Corral": {"region": "Los Ríos", "lat": -39.8833, "lon": -73.4333},
    "Mariquina": {"region": "Los Ríos", "lat": -39.5333, "lon": -72.9667},
    "Lanco": {"region": "Los Ríos", "lat": -39.4500, "lon": -72.7833},
    "Máfil": {"region": "Los Ríos", "lat": -39.6667, "lon": -72.9500},
    "Los Lagos": {"region": "Los Ríos", "lat": -39.8500, "lon": -72.8167},
    "Panguipulli": {"region": "Los Ríos", "lat": -39.6333, "lon": -72.3333},
    "La Unión": {"region": "Los Ríos", "lat": -40.2833, "lon": -73.0833},
    "Paillaco": {"region": "Los Ríos", "lat": -40.0667, "lon": -72.8667},
    "Futrono": {"region": "Los Ríos", "lat": -40.1333, "lon": -72.4000},
    "Río Bueno": {"region": "Los Ríos", "lat": -40.3333, "lon": -72.9500},
    "Lago Ranco": {"region": "Los Ríos", "lat": -40.3167, "lon": -72.5000},

    # Región de Los Lagos
    "Puerto Montt": {"region": "Los Lagos", "lat": -41.4693, "lon": -72.9424},
    "Puerto Varas": {"region": "Los Lagos", "lat": -41.3167, "lon": -72.9833},
    "Osorno": {"region": "Los Lagos", "lat": -40.5667, "lon": -73.1333},
    "Castro": {"region": "Los Lagos", "lat": -42.4667, "lon": -73.7667},
    "Ancud": {"region": "Los Lagos", "lat": -41.8667, "lon": -73.8333},
    "Quellón": {"region": "Los Lagos", "lat": -43.1167, "lon": -73.6167},
    "Calbuco": {"region": "Los Lagos", "lat": -41.7667, "lon": -73.1333},
    "Maullín": {"region": "Los Lagos", "lat": -41.6167, "lon": -73.6000},
    "Frutillar": {"region": "Los Lagos", "lat": -41.1167, "lon": -73.0667},
    "Llanquihue": {"region": "Los Lagos", "lat": -41.2500, "lon": -73.0000},
    "Fresia": {"region": "Los Lagos", "lat": -41.1500, "lon": -73.4167},
    "Puerto Octay": {"region": "Los Lagos", "lat": -40.9667, "lon": -72.9000},
    "Purranque": {"region": "Los Lagos", "lat": -40.9167, "lon": -73.1667},
    "Río Negro": {"region": "Los Lagos", "lat": -40.7833, "lon": -73.2333},
    "San Pablo": {"region": "Los Lagos", "lat": -40.4167, "lon": -73.0167},
    "Puyehue": {"region": "Los Lagos", "lat": -40.6667, "lon": -72.6167},
    "San Juan de la Costa": {"region": "Los Lagos", "lat": -40.5000, "lon": -73.4000},
    "Chaitén": {"region": "Los Lagos", "lat": -42.9167, "lon": -72.7167},
    "Futaleufú": {"region": "Los Lagos", "lat": -43.1833, "lon": -71.8667},
    "Palena": {"region": "Los Lagos", "lat": -43.6167, "lon": -71.8000},
    "Hualaihué": {"region": "Los Lagos", "lat": -42.0333, "lon": -72.5667},
    "Cochamó": {"region": "Los Lagos", "lat": -41.5000, "lon": -72.3167},
    "Dalcahue": {"region": "Los Lagos", "lat": -42.3833, "lon": -73.6500},
    "Curaco de Vélez": {"region": "Los Lagos", "lat": -42.4333, "lon": -73.5833},
    "Quinchao": {"region": "Los Lagos", "lat": -42.4667, "lon": -73.4833},
    "Puqueldón": {"region": "Los Lagos", "lat": -42.6000, "lon": -73.6667},
    "Quemchi": {"region": "Los Lagos", "lat": -42.1500, "lon": -73.5167},
    "Chonchi": {"region": "Los Lagos", "lat": -42.6167, "lon": -73.7667},

    # Región de Aysén
    "Coyhaique": {"region": "Aysén", "lat": -45.5752, "lon": -72.0662},
    "Aysén": {"region": "Aysén", "lat": -45.4000, "lon": -72.7000},
    "Chile Chico": {"region": "Aysén", "lat": -46.5333, "lon": -71.7333},
    "Cochrane": {"region": "Aysén", "lat": -47.2500, "lon": -72.5667},
    "Lago Verde": {"region": "Aysén", "lat": -44.2333, "lon": -71.8500},
    "Cisnes": {"region": "Aysén", "lat": -44.7333, "lon": -72.6833},
    "Guaitecas": {"region": "Aysén", "lat": -43.8833, "lon": -73.7500},
    "Río Ibáñez": {"region": "Aysén", "lat": -46.2833, "lon": -71.9333},
    "Tortel": {"region": "Aysén", "lat": -47.7833, "lon": -73.5333},
    "O'Higgins": {"region": "Aysén", "lat": -48.4667, "lon": -72.5667},

    # Región de Magallanes
    "Punta Arenas": {"region": "Magallanes", "lat": -53.1638, "lon": -70.9171},
    "Puerto Natales": {"region": "Magallanes", "lat": -51.7333, "lon": -72.5167},
    "Porvenir": {"region": "Magallanes", "lat": -53.2833, "lon": -70.3667},
    "Puerto Williams": {"region": "Magallanes", "lat": -54.9333, "lon": -67.6167},
    "Torres del Paine": {"region": "Magallanes", "lat": -51.2500, "lon": -72.3333},
    "Laguna Blanca": {"region": "Magallanes", "lat": -52.3167, "lon": -71.2500},
    "San Gregorio": {"region": "Magallanes", "lat": -52.5667, "lon": -70.0667},
    "Río Verde": {"region": "Magallanes", "lat": -52.6833, "lon": -71.4667},
    "Primavera": {"region": "Magallanes", "lat": -52.7167, "lon": -69.2500},
    "Timaukel": {"region": "Magallanes", "lat": -54.1000, "lon": -68.9500},
    "Cabo de Hornos": {"region": "Magallanes", "lat": -55.0667, "lon": -67.1333},
    "Antártica": {"region": "Magallanes", "lat": -62.2000, "lon": -58.9667},

    # Región de Atacama
    "Copiapó": {"region": "Atacama", "lat": -27.3664, "lon": -70.3314},
    "Caldera": {"region": "Atacama", "lat": -27.0667, "lon": -70.8167},
    "Chañaral": {"region": "Atacama", "lat": -26.3500, "lon": -70.6167},
    "Diego de Almagro": {"region": "Atacama", "lat": -26.3833, "lon": -70.0500},
    "Vallenar": {"region": "Atacama", "lat": -28.5667, "lon": -70.7583},
    "Huasco": {"region": "Atacama", "lat": -28.4667, "lon": -71.2167},
    "Freirina": {"region": "Atacama", "lat": -28.5000, "lon": -71.0667},
    "Alto del Carmen": {"region": "Atacama", "lat": -28.7667, "lon": -70.4833},
    "Tierra Amarilla": {"region": "Atacama", "lat": -27.4833, "lon": -70.2667},

    # Región de Coquimbo
    "La Serena": {"region": "Coquimbo", "lat": -29.9027, "lon": -71.2519},
    "Coquimbo": {"region": "Coquimbo", "lat": -29.9533, "lon": -71.3436},
    "Ovalle": {"region": "Coquimbo", "lat": -30.6000, "lon": -71.2000},
    "Illapel": {"region": "Coquimbo", "lat": -31.6333, "lon": -71.1667},
    "Salamanca": {"region": "Coquimbo", "lat": -31.7667, "lon": -70.9667},
    "Los Vilos": {"region": "Coquimbo", "lat": -31.9167, "lon": -71.5000},
    "Andacollo": {"region": "Coquimbo", "lat": -30.2333, "lon": -71.0833},
    "La Higuera": {"region": "Coquimbo", "lat": -29.4833, "lon": -71.2667},
    "Vicuña": {"region": "Coquimbo", "lat": -30.0333, "lon": -70.7000},
    "Paihuano": {"region": "Coquimbo", "lat": -30.0167, "lon": -70.5167},
    "Río Hurtado": {"region": "Coquimbo", "lat": -30.3000, "lon": -70.7000},
    "Monte Patria": {"region": "Coquimbo", "lat": -30.6833, "lon": -70.9500},
    "Combarbalá": {"region": "Coquimbo", "lat": -31.1833, "lon": -71.0000},
    "Punitaqui": {"region": "Coquimbo", "lat": -30.8333, "lon": -71.2667},
    "Canela": {"region": "Coquimbo", "lat": -31.3833, "lon": -71.4500},

    # Región de Antofagasta
    "Antofagasta": {"region": "Antofagasta", "lat": -23.6509, "lon": -70.3975},
    "Mejillones": {"region": "Antofagasta", "lat": -23.1000, "lon": -70.4500},
    "Tocopilla": {"region": "Antofagasta", "lat": -22.0833, "lon": -70.2000},
    "María Elena": {"region": "Antofagasta", "lat": -22.3500, "lon": -69.6667},
    "Calama": {"region": "Antofagasta", "lat": -22.4667, "lon": -68.9333},
    "San Pedro de Atacama": {"region": "Antofagasta", "lat": -22.9167, "lon": -68.2000},
    "Ollagüe": {"region": "Antofagasta", "lat": -21.2333, "lon": -68.2500},
    "Taltal": {"region": "Antofagasta", "lat": -25.4000, "lon": -70.4833},
    "Sierra Gorda": {"region": "Antofagasta", "lat": -22.8833, "lon": -69.3167},

    # Región de Tarapacá
    "Iquique": {"region": "Tarapacá", "lat": -20.2141, "lon": -70.1524},
    "Alto Hospicio": {"region": "Tarapacá", "lat": -20.2667, "lon": -70.1000},
    "Pozo Almonte": {"region": "Tarapacá", "lat": -20.2500, "lon": -69.7833},
    "Pica": {"region": "Tarapacá", "lat": -20.4833, "lon": -69.3333},
    "Huara": {"region": "Tarapacá", "lat": -19.9500, "lon": -69.7667},
    "Camiña": {"region": "Tarapacá", "lat": -19.3167, "lon": -69.4167},
    "Colchane": {"region": "Tarapacá", "lat": -19.2667, "lon": -68.6333},

    # Región de Arica y Parinacota
    "Arica": {"region": "Arica y Parinacota", "lat": -18.4746, "lon": -70.2979},
    "Putre": {"region": "Arica y Parinacota", "lat": -18.1833, "lon": -69.5667},
    "Camarones": {"region": "Arica y Parinacota", "lat": -19.0000, "lon": -69.9000},
    "General Lagos": {"region": "Arica y Parinacota", "lat": -17.5667, "lon": -69.5000},

    # Región de Ñuble
    "Chillán": {"region": "Ñuble", "lat": -36.6066, "lon": -72.1034},
    "Chillán Viejo": {"region": "Ñuble", "lat": -36.6333, "lon": -72.1333},
    "San Carlos": {"region": "Ñuble", "lat": -36.4167, "lon": -71.9500},
    "Quirihue": {"region": "Ñuble", "lat": -36.2833, "lon": -72.5333},
    "Bulnes": {"region": "Ñuble", "lat": -36.7333, "lon": -72.3000},
    "Yungay": {"region": "Ñuble", "lat": -37.1167, "lon": -72.0167},
    "Pemuco": {"region": "Ñuble", "lat": -36.9667, "lon": -72.1000},
    "El Carmen": {"region": "Ñuble", "lat": -36.9000, "lon": -72.0333},
    "Pinto": {"region": "Ñuble", "lat": -36.7000, "lon": -71.9000},
    "Coihueco": {"region": "Ñuble", "lat": -36.6167, "lon": -71.8333},
    "Ñiquén": {"region": "Ñuble", "lat": -36.2833, "lon": -71.9000},
    "San Fabián": {"region": "Ñuble", "lat": -36.5667, "lon": -71.5333},
    "San Nicolás": {"region": "Ñuble", "lat": -36.5000, "lon": -72.2167},
    "Ninhue": {"region": "Ñuble", "lat": -36.4000, "lon": -72.4000},
    "Portezuelo": {"region": "Ñuble", "lat": -36.5167, "lon": -72.4333},
    "Cobquecura": {"region": "Ñuble", "lat": -36.1333, "lon": -72.7833},
    "Treguaco": {"region": "Ñuble", "lat": -36.4333, "lon": -72.6667},
    "Coelemu": {"region": "Ñuble", "lat": -36.4833, "lon": -72.7000},
    "Ránquil": {"region": "Ñuble", "lat": -36.6167, "lon": -72.5667},
    "Quillón": {"region": "Ñuble", "lat": -36.7333, "lon": -72.4667},
    "San Ignacio": {"region": "Ñuble", "lat": -36.8000, "lon": -72.0333},
}

# Jurisdicción de tribunales ambientales
JURISDICCION_TRIBUNALES = {
    "1TA": {
        "sede": "Antofagasta",
        "coords": (-23.65, -70.40),
        "regiones": ["Arica y Parinacota", "Tarapacá", "Antofagasta", "Atacama", "Coquimbo"]
    },
    "2TA": {
        "sede": "Santiago",
        "coords": (-33.45, -70.67),
        "regiones": ["Valparaíso", "Metropolitana", "O'Higgins", "Maule", "Ñuble", "Biobío"]
    },
    "3TA": {
        "sede": "Valdivia",
        "coords": (-39.81, -73.24),
        "regiones": ["La Araucanía", "Los Ríos", "Los Lagos", "Aysén", "Magallanes"]
    }
}


def normalizar_nombre(nombre: str) -> str:
    """Normaliza un nombre de comuna/región para búsqueda."""
    import unicodedata
    # Quitar tildes
    nombre = unicodedata.normalize('NFKD', nombre).encode('ASCII', 'ignore').decode('ASCII')
    return nombre.lower().strip()


def buscar_region(texto: str) -> str | None:
    """Busca una región en el texto, retorna nombre normalizado o None."""
    texto_lower = texto.lower()

    # Primero buscar en alias
    for alias, region in REGIONES_ALIAS.items():
        if alias in texto_lower:
            return region

    # Luego buscar nombre exacto
    for region in REGIONES_CHILE.keys():
        if normalizar_nombre(region) in normalizar_nombre(texto):
            return region

    return None


def buscar_comuna(nombre: str) -> dict | None:
    """Busca una comuna por nombre, retorna datos o None."""
    nombre_norm = normalizar_nombre(nombre)

    for comuna, datos in COMUNAS_CHILE.items():
        if normalizar_nombre(comuna) == nombre_norm:
            return {"nombre": comuna, **datos}

    return None


def get_coords_region(region: str) -> tuple[float, float] | None:
    """Retorna coordenadas (lat, lon) de una región."""
    if region in REGIONES_CHILE:
        return (REGIONES_CHILE[region]["lat"], REGIONES_CHILE[region]["lon"])
    return None


def get_coords_comuna(comuna: str) -> tuple[float, float] | None:
    """Retorna coordenadas (lat, lon) de una comuna."""
    if comuna in COMUNAS_CHILE:
        return (COMUNAS_CHILE[comuna]["lat"], COMUNAS_CHILE[comuna]["lon"])
    return None


def get_coords_tribunal(tribunal: str) -> tuple[float, float]:
    """Retorna coordenadas de la sede del tribunal."""
    return JURISDICCION_TRIBUNALES.get(tribunal, JURISDICCION_TRIBUNALES["2TA"])["coords"]
