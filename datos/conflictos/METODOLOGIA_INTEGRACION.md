# Metodología de Integración de Base de Conflictos Socioecológicos

**Última actualización:** 20 Enero 2026

---

## 1. Fuentes de datos

Se integraron tres fuentes de información sobre conflictos socioecológicos en Chile:

| Fuente | Descripción | Registros | URL |
|--------|-------------|-----------|-----|
| **INDH** | Mapa de Conflictos Socioambientales del Instituto Nacional de Derechos Humanos | 162 | mapaconflictos.indh.cl |
| **EJAtlas** | Environmental Justice Atlas (Global Environmental Justice Atlas) | 77 | ejatlas.org |
| **OCMAL** | Observatorio de Conflictos Mineros de América Latina | 49 | mapa.conflictosmineros.net |

**Total registros originales:** 288

---

## 2. Proceso de deduplicación

### 2.1 Problema

Los mismos conflictos aparecen documentados en múltiples fuentes con nombres diferentes. Ejemplo:
- INDH: "Pascua Lama"
- EJAtlas: "Mina de oro, cobre y plata Pascua Lama, Chile"
- OCMAL: "Pascua Lama glaciares en peligro"

### 2.2 Método

Se implementó un sistema de detección de duplicados basado en **palabras clave comunes** entre nombres de conflictos:

```python
def detectar_duplicados(nombre1, nombre2):
    palabras1 = normalizar_texto(nombre1).split()
    palabras2 = normalizar_texto(nombre2).split()

    # Excluir palabras genéricas
    stopwords = {'chile', 'proyecto', 'minera', 'de', 'la', 'el', 'en', 'y'}

    palabras1 = set(palabras1) - stopwords
    palabras2 = set(palabras2) - stopwords

    comunes = palabras1 & palabras2
    return comunes if len(comunes) >= 2 else None
```

### 2.3 Duplicados identificados

| Comparación | Duplicados encontrados |
|-------------|----------------------|
| EJAtlas → INDH | 22 |
| OCMAL → INDH | 15 |
| EJAtlas → OCMAL | 7 |
| **Total** | **44** |

### 2.4 Resultado

- **Registros originales:** 288 (162 + 77 + 49)
- **Duplicados removidos:** 44
- **Conflictos únicos:** 244

---

## 3. Sistema de IDs maestros

Cada conflicto recibe un ID único con formato `CONF-XXXX`:

```
CONF-0001: Lavadero de oro en río Colico (INDH)
CONF-0002: Explotación minera de Chuquicamata (INDH)
...
CONF-0163: Data Center Google en Cerrillos (EJAtlas)
...
CONF-0218: Valle del Lluta and Canal Uchusuma (OCMAL)
```

**Prioridad de fuente principal:**
1. INDH (fuente oficial chilena, más completa)
2. EJAtlas (cuando no está en INDH)
3. OCMAL (cuando no está en INDH ni EJAtlas)

---

## 4. Clasificación de sectores económicos

### 4.1 Problema

Los registros de INDH tienen sector asignado, pero EJAtlas y OCMAL no.

### 4.2 Método

Clasificación automática por **palabras clave** en nombre y descripción:

```python
SECTORES = {
    'Minería': ['mining', 'minera', 'mina', 'lithium', 'cobre', 'copper',
                'gold', 'oro', 'coal', 'carbon', 'fundicion', 'tailings'],
    'Energía': ['hidroelectrica', 'hydroelectric', 'dam', 'represa',
                'termoelectrica', 'eolico', 'wind', 'geothermal'],
    'Pesca y acuicultura': ['salmon', 'fisher', 'pescador', 'acuicultura'],
    'Agropecuario': ['pesticide', 'agricul', 'avocado', 'plantation'],
    'Saneamiento ambiental': ['landfill', 'waste', 'contaminacion'],
    ...
}

for conflicto in sin_sector:
    texto = (conflicto['nombre'] + ' ' + conflicto['descripcion']).lower()
    for sector, keywords in SECTORES.items():
        if any(kw in texto for kw in keywords):
            conflicto['sector'] = sector
            break
```

### 4.3 Resultados

| Sector | Cantidad | % |
|--------|----------|---|
| Minería | 106 | 43.4% |
| Energía | 76 | 31.1% |
| Saneamiento ambiental | 13 | 5.3% |
| Otro | 12 | 4.9% |
| Agropecuario | 9 | 3.7% |
| Pesca y acuicultura | 7 | 2.9% |
| Infraestructura portuaria | 6 | 2.5% |
| Forestal | 5 | 2.0% |
| Infraestructura de transporte | 5 | 2.0% |
| Inmobiliario | 3 | 1.2% |
| Instalaciones fabriles | 1 | 0.4% |
| Planificación territorial | 1 | 0.4% |
| **Total** | **244** | **100%** |

---

## 5. Categorización de impactos y actores

### 5.1 Categorías extraídas

Se extrajeron cuatro dimensiones de análisis mediante expresiones regulares sobre las descripciones:

| Dimensión | Categorías |
|-----------|------------|
| **Impactos** | agua, aire, suelo, salud, biodiversidad |
| **Actores** | indígena, pescador, agricultor, urbano |
| **Resistencias** | judicial, movilización, mediática, institucional |
| **Resultados** | paralizado, aprobado, en_litigio |

### 5.2 Patrones de extracción

```python
PATRONES_IMPACTO = {
    'agua': [r'agua', r'hídric', r'río', r'acuífer', r'sequía', r'caudal'],
    'aire': [r'aire', r'emisiones?', r'material particulado', r'MP2\.?5'],
    'suelo': [r'suelo', r'relave', r'residuos sólidos', r'vertedero'],
    'salud': [r'salud', r'enfermedad', r'cáncer', r'intoxicación'],
    'biodiversidad': [r'biodiversidad', r'flora', r'fauna', r'ecosistema']
}
```

### 5.3 Inferencia para registros sin descripción

Para conflictos OCMAL (sin descripción), se aplicó inferencia:
- **Todos son minería** → impactos inferidos: agua, suelo
- **Actores** → detectados por palabras clave en nombre (mapuche, aymara, etc.)

### 5.4 Cobertura final

| Campo | Cobertura |
|-------|-----------|
| Impactos | 95.1% |
| Actores | 93.4% |
| Resistencias | 76.2% |
| Resultados | 70.9% |

---

## 6. URLs de noticias

### 6.1 Proceso

Para conflictos sin categorías completas, se buscaron noticias verificadas:

1. Búsqueda web del nombre del conflicto
2. Identificación de fuentes confiables (CIPER, Greenpeace, EJAtlas, INDH)
3. Extracción de categorías desde la noticia
4. Registro de URL para trazabilidad

### 6.2 Fuentes utilizadas

- CIPER Chile (ciperchile.cl)
- Greenpeace Chile
- EJAtlas (ejatlas.org)
- OLCA (olca.cl)
- Radio Universidad de Chile

### 6.3 Resultado

- **URLs agregadas:** 44 conflictos (18% del total)

---

## 7. Archivos generados

| Archivo | Descripción |
|---------|-------------|
| `conflictos_consolidados_noticias.json` | Dataset final (244 registros) |
| `duplicados_identificados.json` | Mapeo de duplicados entre fuentes |
| `indh_conflictos.json` | Fuente original INDH |
| `ejatlas_chile_filtrado.json` | Fuente original EJAtlas |
| `ocmal_chile.json` | Fuente original OCMAL |

---

## 8. Estructura del registro final

```json
{
  "id_maestro": "CONF-0001",
  "fuente_principal": "INDH",
  "nombre": "Lavadero de oro en río Colico",
  "descripcion": "...",
  "region": "La Araucanía",
  "sector": "Minería",
  "estado": "Activo",
  "año_inicio": 2009,
  "latitud": -38.xxx,
  "longitud": -73.xxx,
  "en_ejatlas": false,
  "en_ocmal": true,
  "nombre_ocmal": "Río Colico Mining Dispute",
  "impactos": ["agua", "suelo"],
  "actores": ["indigena"],
  "resistencias": ["judicial"],
  "resultados": ["en_litigio"],
  "url_noticia": "https://...",
  "notas_metodologia": "Descripción del proceso de completado del registro"
}
```

### 8.1 Campo `notas_metodologia`

Este campo documenta cómo se obtuvo la información de cada registro:

| Tipo de nota | Descripción |
|--------------|-------------|
| **Datos base INDH** | Información extraída directamente de mapaconflictos.indh.cl |
| **Búsqueda web verificada** | Campos completados mediante búsqueda en fuentes confiables (CIPER, Terram, Tribunales, etc.) |
| **Inferencia automática** | Región/año extraídos de descripción mediante regex; sector por palabras clave |
| **OCMAL inferido** | Conflictos mineros sin descripción; impactos agua/suelo inferidos por sector |

**Ejemplo de nota específica:**
```
"Proyecto minero en Putaendo. Búsqueda: 'Minera Vizcachitas conflicto'.
Fuentes: Ladera Sur, Radio U Chile. En litigio ante Tribunal Ambiental."
```

---

## 9. Completado de registros (Enero 2026)

### 9.1 Proceso

Se completaron 103 conflictos que tenían 2 o más campos vacíos mediante:

1. **Búsquedas web individuales** (23 conflictos emblemáticos)
   - Fuentes: CIPER, Terram, Oceana, Tribunales Ambientales, medios locales
   - Cada búsqueda documentada en `notas_metodologia`

2. **Inferencia automática** (80 conflictos EJAtlas/OCMAL)
   - Región: palabras clave geográficas en nombre/descripción
   - Año: expresiones regulares sobre texto
   - Resistencias/resultados: patrones por sector

### 9.2 Cobertura final

| Campo | Antes | Después |
|-------|-------|---------|
| Región | ~50% | **86.5%** |
| Resistencias | ~76% | **96.7%** |
| Resultados | ~71% | **95.1%** |
| Año inicio | ~50% | **86.9%** |

---

## 10. Limitaciones

1. **Deduplicación imperfecta:** Algunos duplicados pueden no detectarse si los nombres son muy diferentes.

2. **Clasificación por palabras clave:** Puede haber errores cuando el nombre es ambiguo.

3. **Sesgo de cobertura:** INDH tiene mejor cobertura de conflictos recientes; EJAtlas y OCMAL tienen sesgo hacia conflictos emblemáticos.

4. **Inferencia de categorías:** Los campos inferidos para OCMAL son aproximaciones basadas en que todos son conflictos mineros.

5. **Inferencia de región/año:** Para ~80 conflictos EJAtlas, región y año fueron inferidos de la descripción en inglés; pueden existir imprecisiones.

---

## 11. Reproducibilidad

Scripts utilizados:
- `scripts/consolidar_con_ids.py` - Integración y deduplicación
- `scripts/agregar_noticias.py` - Enriquecimiento con URLs

Ejecución:
```bash
python scripts/consolidar_con_ids.py
python scripts/agregar_noticias.py
```

**Nota:** El completado manual de enero 2026 fue realizado directamente sobre el JSON final y está documentado en el campo `notas_metodologia` de cada registro.
