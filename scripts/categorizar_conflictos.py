#!/usr/bin/env python3
"""
Categorización automática de conflictos socioecológicos.

Extrae categorías adicionales del texto de descripción:
- Tipo de impacto ambiental (agua, aire, suelo, salud, biodiversidad)
- Actor afectado (indígena, pescador, agricultor, urbano)
- Forma de resistencia (judicial, movilización, mediática, institucional)
- Resultado (paralizado, aprobado, en litigio)
"""

import json
import re
from pathlib import Path
from collections import Counter
from html import unescape

BASE_DIR = Path(__file__).parent.parent
DATOS_DIR = BASE_DIR / "datos" / "conflictos"

# Patrones para categorización
PATRONES_IMPACTO = {
    "agua": [
        r"agua", r"hídric[oa]", r"río", r"acuífer", r"napa", r"sequ[ií]a",
        r"contaminación.*agua", r"vertimiento", r"RILES", r"descarga",
        r"escasez.*agua", r"derechos de agua", r"caudal"
    ],
    "aire": [
        r"aire", r"emisiones?", r"material particulado", r"MP2\.?5", r"MP10",
        r"gases", r"humo", r"olor", r"polvo", r"atmósfer"
    ],
    "suelo": [
        r"suelo", r"contaminación.*tierra", r"relave", r"residuos sólidos",
        r"vertedero", r"relleno sanitario", r"erosión"
    ],
    "salud": [
        r"salud", r"enfermedad", r"cáncer", r"intoxicación", r"mortalidad",
        r"respiratori", r"dermatológic", r"neurológic", r"hospital"
    ],
    "biodiversidad": [
        r"biodiversidad", r"flora", r"fauna", r"especie", r"ecosistema",
        r"bosque", r"glaciar", r"humedal", r"área protegida", r"parque nacional"
    ]
}

PATRONES_ACTOR = {
    "indigena": [
        r"indígena", r"mapuche", r"aymara", r"atacameñ", r"diaguita",
        r"quechua", r"colla", r"rapa ?nui", r"kawésqar", r"yagán",
        r"comunidad.*ancestral", r"territorio.*ancestral", r"Convenio 169"
    ],
    "pescador": [
        r"pescador", r"pesca artesanal", r"caleta", r"sindicato.*pesca",
        r"marisca", r"borde costero"
    ],
    "agricultor": [
        r"agricultor", r"campesino", r"pequeño.*agricult", r"APR",
        r"agua potable rural", r"riego", r"cultivo", r"huerto"
    ],
    "urbano": [
        r"vecin[oa]", r"junta de vecinos", r"poblador", r"habitante",
        r"residente", r"barrio", r"población"
    ]
}

PATRONES_RESISTENCIA = {
    "judicial": [
        r"recurso de protección", r"recurso.*amparo", r"demanda", r"querella",
        r"tribunal", r"corte.*apelaciones", r"corte.*suprema", r"litigio",
        r"acción.*legal", r"defensor[ií]a"
    ],
    "movilizacion": [
        r"protesta", r"marcha", r"manifestación", r"bloqueo", r"toma",
        r"movilización", r"asamblea.*ciudadana", r"paro"
    ],
    "mediatica": [
        r"denuncia.*pública", r"campaña", r"redes sociales", r"prensa",
        r"medio.*comunicación", r"declaración.*pública"
    ],
    "institucional": [
        r"participación ciudadana", r"observaciones.*ciudadana",
        r"consulta.*indígena", r"SEIA", r"evaluación ambiental"
    ]
}

PATRONES_RESULTADO = {
    "paralizado": [
        r"paraliz", r"suspend", r"detenid", r"cancelad", r"rechazad",
        r"desistimiento", r"abandon", r"no.*aprobad"
    ],
    "aprobado": [
        r"aprobad", r"autoriza", r"RCA.*favorable", r"calificación.*favorable",
        r"permiso", r"operación"
    ],
    "en_litigio": [
        r"en.*tramitación", r"pendiente", r"espera.*fallo", r"proceso.*judicial"
    ]
}


def limpiar_html(texto):
    """Limpia tags HTML y decodifica entidades."""
    if not texto:
        return ""
    # Remover tags HTML
    texto = re.sub(r'<[^>]+>', ' ', texto)
    # Decodificar entidades HTML
    texto = unescape(texto)
    # Normalizar espacios
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()


def detectar_categorias(texto, patrones):
    """Detecta categorías presentes en el texto."""
    texto_limpio = limpiar_html(texto).lower()
    categorias_detectadas = []

    for categoria, lista_patrones in patrones.items():
        for patron in lista_patrones:
            if re.search(patron, texto_limpio, re.IGNORECASE):
                categorias_detectadas.append(categoria)
                break

    return categorias_detectadas


def analizar_conflicto(conflicto):
    """Analiza un conflicto y extrae categorías."""
    texto = conflicto.get("descripcion", "") + " " + conflicto.get("nombre", "")

    return {
        "impactos": detectar_categorias(texto, PATRONES_IMPACTO),
        "actores": detectar_categorias(texto, PATRONES_ACTOR),
        "resistencias": detectar_categorias(texto, PATRONES_RESISTENCIA),
        "resultados": detectar_categorias(texto, PATRONES_RESULTADO)
    }


def main():
    print("=" * 60)
    print("CATEGORIZACIÓN DE CONFLICTOS SOCIOECOLÓGICOS")
    print("=" * 60)

    # Cargar datos
    with open(DATOS_DIR / "conflictos_integrados.json", encoding="utf-8") as f:
        conflictos = json.load(f)

    print(f"\nTotal conflictos: {len(conflictos)}")

    # Analizar cada conflicto
    stats = {
        "impactos": Counter(),
        "actores": Counter(),
        "resistencias": Counter(),
        "resultados": Counter()
    }

    conflictos_categorizados = []

    for c in conflictos:
        categorias = analizar_conflicto(c)

        # Actualizar estadísticas
        for tipo, lista in categorias.items():
            for cat in lista:
                stats[tipo][cat] += 1

        # Agregar categorías al conflicto
        c_nuevo = c.copy()
        c_nuevo["categorias"] = categorias
        conflictos_categorizados.append(c_nuevo)

    # Mostrar resultados
    print("\n" + "=" * 60)
    print("ESTADÍSTICAS POR CATEGORÍA")
    print("=" * 60)

    print("\n1. TIPO DE IMPACTO AMBIENTAL")
    print("-" * 40)
    for cat, n in stats["impactos"].most_common():
        pct = n / len(conflictos) * 100
        print(f"   {cat.capitalize():20} {n:4} ({pct:5.1f}%)")

    print("\n2. ACTOR AFECTADO")
    print("-" * 40)
    for cat, n in stats["actores"].most_common():
        pct = n / len(conflictos) * 100
        print(f"   {cat.capitalize():20} {n:4} ({pct:5.1f}%)")

    print("\n3. FORMA DE RESISTENCIA")
    print("-" * 40)
    for cat, n in stats["resistencias"].most_common():
        pct = n / len(conflictos) * 100
        print(f"   {cat.capitalize():20} {n:4} ({pct:5.1f}%)")

    print("\n4. RESULTADO")
    print("-" * 40)
    for cat, n in stats["resultados"].most_common():
        pct = n / len(conflictos) * 100
        print(f"   {cat.capitalize():20} {n:4} ({pct:5.1f}%)")

    # Guardar conflictos categorizados (sobrescribe el archivo integrado)
    output_file = DATOS_DIR / "conflictos_integrados.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(conflictos_categorizados, f, ensure_ascii=False, indent=2)
    print(f"\nDataset consolidado actualizado: {output_file}")

    # Guardar resumen de estadísticas
    resumen = {
        "total_conflictos": len(conflictos),
        "categorias": {
            "impactos": dict(stats["impactos"]),
            "actores": dict(stats["actores"]),
            "resistencias": dict(stats["resistencias"]),
            "resultados": dict(stats["resultados"])
        }
    }

    resumen_file = DATOS_DIR / "estadisticas_categorias.json"
    with open(resumen_file, "w", encoding="utf-8") as f:
        json.dump(resumen, f, ensure_ascii=False, indent=2)
    print(f"Estadísticas guardadas: {resumen_file}")

    return conflictos_categorizados, stats


if __name__ == "__main__":
    main()
