#!/usr/bin/env python3
"""
Análisis NLP básico de conflictos socioecológicos.

Extrae:
1. Palabras clave frecuentes
2. Empresas mencionadas
3. Sustancias contaminantes
4. Patrones de descripción
"""

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import json
import re
from pathlib import Path
from collections import Counter
from html import unescape

BASE_DIR = Path(__file__).parent.parent
DATOS_DIR = BASE_DIR / "datos" / "conflictos"
OUTPUT_DIR = BASE_DIR / "datos" / "estadisticas"

# Stopwords en español
STOPWORDS = {
    "de", "la", "el", "en", "que", "y", "a", "los", "del", "las", "un", "por",
    "con", "una", "para", "al", "es", "se", "su", "no", "lo", "como", "más",
    "pero", "sus", "le", "ha", "me", "sin", "sobre", "este", "ya", "entre",
    "cuando", "todo", "esta", "ser", "son", "dos", "también", "fue", "había",
    "era", "muy", "años", "hasta", "desde", "está", "mi", "porque", "qué",
    "sólo", "han", "yo", "hay", "vez", "puede", "todos", "así", "nos", "ni",
    "parte", "tiene", "él", "uno", "donde", "bien", "tiempo", "mismo", "ese",
    "ahora", "cada", "e", "vida", "otro", "después", "te", "otros", "aunque",
    "esa", "eso", "hace", "otra", "gobierno", "tan", "durante", "siempre",
    "día", "tanto", "ella", "tres", "si", "sido", "gran", "aquí", "caso",
    "poco", "ellos", "estos", "algo", "todas", "dijo", "nueva", "hacer",
    "cuenta", "proyecto", "proyectos", "localidad", "comuna", "año",
    "región", "chile", "chileno", "chilena", "país"
}


def limpiar_texto(texto):
    """Limpia HTML y normaliza texto."""
    if not texto:
        return ""
    texto = re.sub(r'<[^>]+>', ' ', texto)
    texto = unescape(texto)
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip().lower()


def extraer_palabras(texto):
    """Extrae palabras relevantes."""
    palabras = re.findall(r'\b[a-záéíóúüñ]{4,}\b', texto)
    return [p for p in palabras if p not in STOPWORDS]


def extraer_empresas(conflictos):
    """Extrae empresas mencionadas."""
    empresas = Counter()

    # Patrones de empresas conocidas
    empresas_conocidas = [
        "codelco", "escondida", "collahuasi", "barrick", "anglo american",
        "antofagasta minerals", "teck", "sqm", "albemarle", "enami",
        "aes gener", "colbún", "enel", "endesa", "engie",
        "arauco", "cmpc", "masisa", "celco",
        "salmones", "marine harvest", "multiexport", "camanchaca",
        "melón", "polpaico", "bio bio", "agrosuper", "ariztía"
    ]

    for c in conflictos:
        # Campo empresa si existe
        empresa = c.get("empresa", "")
        if empresa:
            empresas[empresa.lower().strip()] += 1

        # Buscar en texto
        texto = limpiar_texto(c.get("descripcion", "") + " " + c.get("nombre", ""))
        for emp in empresas_conocidas:
            if emp in texto:
                empresas[emp] += 1

    return empresas


def extraer_contaminantes(conflictos):
    """Extrae sustancias contaminantes mencionadas."""
    contaminantes = Counter()

    patrones = {
        "arsénico": r"\barsénico\b",
        "plomo": r"\bplomo\b",
        "mercurio": r"\bmercurio\b",
        "cobre": r"\bcobre\b",
        "azufre": r"\bazufre\b|so2|dióxido de azufre",
        "material particulado": r"mp2\.?5|mp10|material particulado|partículas",
        "cianuro": r"\bcianuro\b",
        "relaves": r"\brelave[s]?\b",
        "RILES": r"\briles\b|residuos.*líquidos",
        "pesticidas": r"pesticida|plaguicida|herbicida|fungicida",
        "nitrógeno": r"nitrógeno|nitrato|amonio",
        "metales pesados": r"metales pesados",
        "hidrocarburos": r"hidrocarburo|petróleo|combustible",
        "dioxinas": r"dioxina|furano",
        "antibióticos": r"antibiótico"
    }

    for c in conflictos:
        texto = limpiar_texto(c.get("descripcion", "") + " " + c.get("nombre", ""))
        for contam, patron in patrones.items():
            if re.search(patron, texto, re.IGNORECASE):
                contaminantes[contam] += 1

    return contaminantes


def extraer_impactos_salud(conflictos):
    """Extrae impactos en salud mencionados."""
    impactos = Counter()

    patrones = {
        "cáncer": r"cáncer|cancerígeno|carcinógeno|leucemia|tumor",
        "respiratorio": r"respiratori|asma|bronqu|pulmon",
        "dermatológico": r"dermat|piel|cutáneo|eccema",
        "neurológico": r"neurológic|nervios|cognitiv",
        "intoxicación": r"intoxicación|envenenam",
        "mortalidad": r"mortalidad|muerte[s]?|fallec",
        "malformaciones": r"malformación|congénit|teratogénic"
    }

    for c in conflictos:
        texto = limpiar_texto(c.get("descripcion", "") + " " + c.get("nombre", ""))
        for impacto, patron in patrones.items():
            if re.search(patron, texto, re.IGNORECASE):
                impactos[impacto] += 1

    return impactos


def analizar_longitud_descripciones(conflictos):
    """Analiza la longitud de las descripciones."""
    longitudes = []
    sin_descripcion = 0

    for c in conflictos:
        desc = c.get("descripcion", "")
        if desc:
            texto = limpiar_texto(desc)
            longitudes.append(len(texto.split()))
        else:
            sin_descripcion += 1

    if longitudes:
        return {
            "promedio_palabras": sum(longitudes) / len(longitudes),
            "min_palabras": min(longitudes),
            "max_palabras": max(longitudes),
            "con_descripcion": len(longitudes),
            "sin_descripcion": sin_descripcion
        }
    return {}


def main():
    print("=" * 60)
    print("ANÁLISIS NLP BÁSICO DE CONFLICTOS")
    print("=" * 60)

    with open(DATOS_DIR / "conflictos_categorizados.json", encoding="utf-8") as f:
        conflictos = json.load(f)

    print(f"\nTotal conflictos: {len(conflictos)}")

    # 1. Palabras más frecuentes
    print("\n" + "=" * 60)
    print("PALABRAS MÁS FRECUENTES")
    print("=" * 60)

    todas_palabras = Counter()
    for c in conflictos:
        texto = limpiar_texto(c.get("descripcion", "") + " " + c.get("nombre", ""))
        palabras = extraer_palabras(texto)
        todas_palabras.update(palabras)

    print("\nTop 30 palabras:")
    for palabra, n in todas_palabras.most_common(30):
        print(f"  {palabra:25} {n:4}")

    # 2. Empresas
    print("\n" + "=" * 60)
    print("EMPRESAS MENCIONADAS")
    print("=" * 60)

    empresas = extraer_empresas(conflictos)
    print("\nTop 20 empresas:")
    for empresa, n in empresas.most_common(20):
        print(f"  {empresa:35} {n:3}")

    # 3. Contaminantes
    print("\n" + "=" * 60)
    print("CONTAMINANTES MENCIONADOS")
    print("=" * 60)

    contaminantes = extraer_contaminantes(conflictos)
    for contam, n in contaminantes.most_common():
        pct = n / len(conflictos) * 100
        print(f"  {contam:25} {n:4} ({pct:5.1f}%)")

    # 4. Impactos en salud
    print("\n" + "=" * 60)
    print("IMPACTOS EN SALUD")
    print("=" * 60)

    impactos = extraer_impactos_salud(conflictos)
    for impacto, n in impactos.most_common():
        pct = n / len(conflictos) * 100
        print(f"  {impacto:25} {n:4} ({pct:5.1f}%)")

    # 5. Longitud de descripciones
    print("\n" + "=" * 60)
    print("ESTADÍSTICAS DE DESCRIPCIONES")
    print("=" * 60)

    stats_desc = analizar_longitud_descripciones(conflictos)
    print(f"  Con descripción: {stats_desc.get('con_descripcion', 0)}")
    print(f"  Sin descripción: {stats_desc.get('sin_descripcion', 0)}")
    print(f"  Promedio palabras: {stats_desc.get('promedio_palabras', 0):.1f}")
    print(f"  Mínimo: {stats_desc.get('min_palabras', 0)}")
    print(f"  Máximo: {stats_desc.get('max_palabras', 0)}")

    # Guardar resultados
    resultados = {
        "palabras_frecuentes": dict(todas_palabras.most_common(100)),
        "empresas": dict(empresas.most_common(50)),
        "contaminantes": dict(contaminantes),
        "impactos_salud": dict(impactos),
        "estadisticas_descripciones": stats_desc
    }

    output_file = OUTPUT_DIR / "analisis_nlp.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    print(f"\n\nResultados guardados: {output_file}")


if __name__ == "__main__":
    main()
