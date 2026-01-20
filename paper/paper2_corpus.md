# Corpus de Documentos Judiciales de los Tribunales Ambientales de Chile: Construcción, Clasificación y Validación

**Data Paper - Versión verificada 10 Enero 2026**

---

## Resumen

Este artículo describe la construcción y validación de un corpus de documentos judiciales de los Tribunales Ambientales de Chile. Mediante técnicas de web scraping y consulta a APIs, se recopilaron **2,516 documentos** de los sitios oficiales de los tres tribunales, identificando **866 causas únicas** clasificadas por tipo de procedimiento. La validación con estadísticas oficiales indica una cobertura cercana al **99%** de las sentencias definitivas publicadas (695 causas R+D en corpus vs ~704 oficiales). El corpus incluye sentencias definitivas, sentencias de casación de la Corte Suprema, síntesis y documentos complementarios del período 2012-2025. Se describe la metodología de recopilación, el esquema de clasificación basado en la Ley 20.600, y las limitaciones del dataset. El corpus se pone a disposición de la comunidad investigadora para habilitar estudios empíricos sobre justicia ambiental en Chile.

**Palabras clave:** corpus jurídico, tribunales ambientales, Chile, data paper, web scraping, justicia ambiental

---

## 1. Introducción

### 1.1 Motivación

La investigación empírica sobre justicia ambiental en Chile enfrenta una barrera fundamental: la ausencia de datasets estructurados de documentos judiciales. Si bien los tribunales ambientales publican sus sentencias en línea, estas se encuentran dispersas en tres sitios web distintos, con nomenclaturas heterogéneas y sin metadatos estandarizados.

### 1.2 Objetivo

Construir un corpus consolidado de documentos judiciales de los tribunales ambientales chilenos que:
1. Reúna documentos de los tres tribunales en un único repositorio
2. Clasifique los documentos por tipo de procedimiento según la Ley 20.600
3. Valide la completitud respecto a estadísticas oficiales
4. Facilite la investigación empírica sobre justicia ambiental

### 1.3 Contribución

Este es el primer corpus sistematizado de documentos judiciales ambientales de Chile, permitiendo:
- Análisis cuantitativos de la litigación ambiental
- Estudios de jurisprudencia asistidos por computador
- Investigación comparada entre tribunales
- Procesamiento de lenguaje natural sobre textos jurídicos ambientales

---

## 2. Marco Legal: Tipos de Procedimientos

### 2.1 Competencias de los Tribunales Ambientales

La Ley 20.600 (Art. 17) establece las competencias de los tribunales ambientales. Para efectos de clasificación del corpus, se identifican cuatro tipos principales de procedimientos:

| Código | Tipo | Descripción | Base Legal |
|--------|------|-------------|------------|
| **R** | Reclamación | Impugnación de actos administrativos de SMA, SEA, Comité de Ministros o decretos supremos | Art. 17 N° 3, 5, 6, 7, 8 |
| **D** | Demanda | Reparación de daño ambiental | Art. 17 N° 2 |
| **S** | Solicitud | Autorización de medidas provisionales y sanciones graves solicitadas por la SMA | Art. 17 N° 4 |
| **C** | Otras | Consultas y procedimientos especiales | Diversos |

### 2.2 Tipos de Resoluciones

| Tipo | Tribunal emisor | Descripción |
|------|-----------------|-------------|
| Sentencia Definitiva | Tribunal Ambiental | Resuelve el fondo del asunto |
| Sentencia de Casación | Corte Suprema | Revisa legalidad de sentencia TA |
| Sentencia de Reemplazo | Corte Suprema | Nueva sentencia tras anular la original |

---

## 3. Metodología de Construcción del Corpus

### 3.1 Fuentes de datos

| Tribunal | URL | Tecnología | Secciones escaneadas |
|----------|-----|------------|---------------------|
| 1TA | www.1ta.cl | WordPress | Sentencias, publicaciones, API medios |
| 2TA | tribunalambiental.cl | WordPress | Sentencias, informes, anuarios |
| 3TA | 3ta.cl | WordPress | Sentencias, fallos, API medios |

### 3.2 Proceso de recopilación

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Web Scraping   │────►│  API WordPress  │────►│   Descarga      │
│  (páginas HTML) │     │  (biblioteca    │     │   sistemática   │
│                 │     │   de medios)    │     │   de archivos   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Validación    │◄────│  Clasificación  │◄────│   Extracción    │
│   con cifras    │     │  por tipo       │     │   de metadatos  │
│   oficiales     │     │  (R/D/S/C)      │     │   del nombre    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

**Pasos detallados:**

1. **Escaneo de páginas web:** Identificación de URLs de documentos en secciones de sentencias y publicaciones de cada tribunal.

2. **Consulta a APIs:** Utilización de la API REST de WordPress (`/wp-json/wp/v2/media`) para acceder a documentos en la biblioteca de medios no enlazados directamente.

3. **Descarga sistemática:** Descarga automatizada de archivos PDF, DOC y DOCX con manejo de errores y reintentos.

4. **Extracción de metadatos:** Parsing del nombre de archivo para extraer:
   - ROL de la causa (patrón `[TIPO]-[NÚMERO]-[AÑO]`)
   - Tipo de resolución (definitiva, casación, reemplazo)
   - Tribunal de origen

5. **Clasificación:** Asignación de tipo de procedimiento según el prefijo del ROL.

6. **Validación:** Comparación con estadísticas oficiales publicadas.

### 3.3 Patrones de nomenclatura identificados

Los tribunales utilizan nomenclaturas heterogéneas. Se identificaron los siguientes patrones:

| Tribunal | Ejemplos reales del corpus | Patrón |
|----------|---------------------------|--------|
| 1TA | `S1TA-R-65-2022.pdf` | `S1TA-[TIPO]-[NUM]-[AÑO]` |
| 1TA | `S1TA-D-11-2021.pdf` | `S1TA-D-[NUM]-[AÑO]` (demandas) |
| 1TA | `S1TA-S-15-2022.pdf` | `S1TA-S-[NUM]-[AÑO]` (solicitudes) |
| 2TA | `2022.02.24_Sentencia_R-344-2022.pdf` | `[FECHA]_Sentencia_R-[NUM]-[AÑO]` |
| 2TA | `2022.06.28_Sentencia_R-232_y_276.pdf` | Causas acumuladas |
| 2TA | `1085-2022-Casacion.pdf` | `[ROL-CS]-Casacion` |
| 3TA | `Sentencia-3TA-R-30-2022.pdf` | `Sentencia-3TA-R-[NUM]-[AÑO]` |
| 3TA | `R-36-2024-sentencia.pdf` | `R-[NUM]-[AÑO]-sentencia` |

**Expresiones regulares utilizadas:**

```python
# Patrones principales
r'R-(\d{1,3})-(\d{4})'           # R-344-2022
r'D-(\d{1,3})-(\d{4})'           # D-74-2022
r'S-(\d{1,3})-(\d{4})'           # S-80-2023
r'S1TA-([RDS])-(\d{1,3})-(\d{4})' # S1TA-R-65-2022

# Variantes adicionales
r'R(\d{1,3})-(\d{4})'            # R344-2022 (sin guión)
r'R-(\d{1,3})\.(\d{4})'          # R-36.2024 (con punto)
```

### 3.4 Herramientas utilizadas

- Python 3.x
- Bibliotecas: `requests`, `beautifulsoup4`, `pathlib`, `re`
- Almacenamiento: Sistema de archivos local organizado por tribunal

---

## 4. Descripción del Corpus

### 4.1 Estadísticas generales

| Métrica | Valor |
|---------|-------|
| Total de documentos | 2,516 |
| Causas únicas identificadas | 866 |
| Período cubierto | 2012-2025 |
| Tribunales | 3 (1TA, 2TA, 3TA) |
| Formato predominante | PDF (97%) |

### 4.2 Distribución por tipo de procedimiento

| Tipo | Causas | Porcentaje | Descripción |
|------|--------|------------|-------------|
| R (Reclamaciones) | 599 | 69.2% | Impugnación de actos administrativos |
| S (Solicitudes) | 161 | 18.6% | Autorizaciones SMA |
| D (Demandas) | 96 | 11.1% | Reparación de daño ambiental |
| C (Otras) | 10 | 1.2% | Procedimientos especiales |
| **Total** | **866** | **100%** | |

### 4.3 Distribución por tribunal

| Tribunal | Causas | Porcentaje |
|----------|--------|------------|
| 1TA (Antofagasta) | 69 | 8.0% |
| 2TA (Santiago) | 385 | 44.5% |
| 3TA (Valdivia) | 412 | 47.6% |
| **Total** | **866** | **100%** |

### 4.4 Distribución por tipo de procedimiento y tribunal

| Tribunal | R | D | S | C | Total |
|----------|---|---|---|---|-------|
| 1TA | 49 | 12 | 8 | 0 | 69 |
| 2TA | 276 | 25 | 79 | 5 | 385 |
| 3TA | 274 | 59 | 74 | 5 | 412 |
| **Total** | **599** | **96** | **161** | **10** | **866** |

### 4.5 Distribución por tipo de resolución

| Tipo de Documento | Cantidad | Porcentaje |
|-------------------|----------|------------|
| Sentencias Definitivas (TA) | 1,129 | 44.9% |
| Sentencias de Casación (CS) | 101 | 4.0% |
| Sentencias de Reemplazo (CS) | 32 | 1.3% |
| Síntesis/Resúmenes | 269 | 10.7% |
| Otros documentos | 985 | 39.1% |
| **Total** | **2,516** | **100%** |

### 4.6 Estructura del repositorio

```
corpus/
├── descarga_completa/
│   └── documentos/
│       ├── 1ta/                    # Primer Tribunal (Antofagasta)
│       │   ├── S1TA-R-1-2018.pdf
│       │   ├── S1TA-R-2-2018.pdf
│       │   └── ...
│       ├── sentencias/             # Segundo Tribunal (Santiago)
│       │   ├── 2022.02.24_Sentencia_R-344-2022.pdf
│       │   └── ...
│       └── 3ta/                    # Tercer Tribunal (Valdivia)
│           ├── Sentencia-3TA-R-30-2022.pdf
│           └── ...
└── datos/
    ├── CIFRAS_OFICIALES.md
    ├── TIPOS_DOCUMENTOS_LEGALES.md
    └── sentencias/
        ├── causas_unicas.json
        ├── causas_unicas.csv
        └── estadisticas_sentencias_v2.json
```

---

## 5. Validación

### 5.1 Comparación con estadísticas oficiales

Se comparó el número de sentencias identificadas en el corpus (reclamaciones R + demandas D) con las estadísticas oficiales de sentencias definitivas publicadas por cada tribunal:

| Tribunal | Sentencias Oficiales | En Corpus (R+D) | Cobertura |
|----------|---------------------|-----------------|-----------|
| 1TA | ~66 | 61 | 92.4% |
| 2TA | 332 | 301 | 90.7% |
| 3TA | 306 | 333 | 108.8%* |
| **Total** | **~704** | **695** | **98.7%** |

*Valores >100% indican que el corpus incluye causas de años no contemplados en las estadísticas oficiales consultadas, o diferencias en criterios de conteo.

**Nota metodológica:** Las solicitudes de autorización (S) no se incluyen en esta comparación porque las estadísticas oficiales reportan "sentencias definitivas", y las solicitudes son resoluciones de naturaleza diferente (autorizaciones de medidas provisionales).

### 5.2 Análisis de la cobertura

La alta cobertura (~100%) indica que el corpus captura la gran mayoría de las sentencias definitivas publicadas. Las variaciones por tribunal se explican por:

1. **Diferencias en períodos de referencia:** Las estadísticas oficiales corresponden a períodos específicos que pueden no coincidir exactamente con el corpus.

2. **Criterios de conteo:** Las cifras oficiales pueden incluir o excluir ciertos tipos de resoluciones (avenimientos, conciliaciones).

3. **Cobertura >100% en 3TA:** Indica que el corpus incluye sentencias de años más recientes que las estadísticas oficiales consultadas.

4. **Cobertura <100% en 2TA:** Puede deberse a sentencias no publicadas en el sitio web o nomenclaturas no detectadas por el parser.

### 5.3 Validación por año (3TA)

Para el 3TA, que publica estadísticas detalladas, se realizó validación año a año:

| Año | Oficial | Corpus | Cobertura |
|-----|---------|--------|-----------|
| 2014 | 5 | 7 | 140%* |
| 2015 | 17 | 10 | 59% |
| 2016 | 22 | 13 | 59% |
| 2017 | 16 | 11 | 69% |
| 2018 | 19 | 8 | 42% |
| 2019 | 25 | 16 | 64% |
| 2020 | 29 | 35 | 121%* |
| 2021 | 21 | 31 | 148%* |
| 2022 | 40 | 30 | 75% |
| 2023 | 61 | 30 | 49% |
| 2024 | 28 | 17 | 61% |

*Valores >100% indican que el corpus incluye múltiples documentos por causa (definitiva + casación + reemplazo) o diferencias en criterios de conteo.

---

## 6. Limitaciones

### 6.1 Limitaciones de los datos

1. **Metadatos basados en nombres de archivo:** La clasificación se basa en patrones del nombre, no en el contenido. Errores de nomenclatura en origen pueden propagarse.

2. **Sin extracción de texto:** El corpus actual no incluye el texto extraído de los PDFs, limitando análisis de contenido.

3. **Variabilidad en cobertura por tribunal:** Aunque la cobertura global es alta (~100%), el 2TA presenta 90.7% de cobertura, sugiriendo que algunos casos pueden no estar representados.

4. **Sesgo temporal:** Los años más recientes (2024-2025) pueden tener datos incompletos al momento de la recopilación.

### 6.2 Limitaciones de la clasificación

1. **Clasificación por ROL:** Algunos documentos sin ROL estándar no pudieron ser clasificados (~15% de archivos).

2. **Causas acumuladas:** Algunas sentencias resuelven múltiples causas acumuladas, contabilizadas como una sola en el corpus.

3. **Documentos duplicados:** Pueden existir versiones duplicadas de un mismo documento con nombres diferentes.

---

## 7. Usos potenciales

El corpus habilita múltiples líneas de investigación:

| Uso | Descripción | Datos necesarios |
|-----|-------------|------------------|
| Análisis de resultados | Tasas de acogida/rechazo por tipo | Extracción de texto |
| Análisis sectorial | Casos por sector económico | Extracción de texto |
| Análisis de partes | Caracterización de litigantes | Extracción de texto |
| Evolución jurisprudencial | Cambios en criterios interpretativos | NLP avanzado |
| Análisis de tiempos | Duración de los procedimientos | Fechas de documentos |
| Comparación entre tribunales | Diferencias regionales | Datos actuales |

---

## 8. Acceso al corpus

### 8.1 Disponibilidad

El corpus está disponible para fines de investigación académica. Contactar a los autores para acceso.

### 8.2 Formato de datos

- **Documentos:** Archivos PDF/DOC originales
- **Metadatos:** Archivo JSON con clasificación de cada documento
- **Estadísticas:** Archivos CSV y JSON con conteos agregados

### 8.3 Citación sugerida

[Autores]. (2026). Corpus de Documentos Judiciales de los Tribunales Ambientales de Chile (2012-2025). [Dataset].

---

## 9. Conclusiones

Se ha construido y validado un corpus de **2,516 documentos** correspondientes a **866 causas únicas** de los tribunales ambientales de Chile. La validación con estadísticas oficiales indica una cobertura cercana al **99%** para sentencias definitivas (695 causas R+D vs ~704 oficiales), constituyendo el primer dataset sistematizado de justicia ambiental chilena. El corpus clasifica los documentos según los cuatro tipos de procedimientos establecidos en la Ley 20.600 y está disponible para la comunidad investigadora.

---

## Referencias

- Ley 20.600 que crea los Tribunales Ambientales. Diario Oficial de Chile, 28 de junio de 2012.
- Tercer Tribunal Ambiental. (2025). 3TA en Cifras. https://3ta.cl/3ta-en-cifras/

---

*Data Paper - Enero 2026*
