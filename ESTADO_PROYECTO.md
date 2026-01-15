# Estado del Proyecto: Corpus Tribunal Ambiental Chile

**Última actualización:** 2026-01-11 16:55
**Sesión actual:** Extracción de Corpus Completo (en progreso)

---

## Resumen del Proyecto

Construcción de un corpus de documentos judiciales de los Tribunales Ambientales de Chile para investigación en humanidades digitales y derecho ambiental. Proyecto vinculado al Núcleo Milenio SODAS.

---

## Estado Actual

### Corpus de Documentos

| Componente | Estado | Cantidad | Ubicación |
|------------|--------|----------|-----------|
| PDFs descargados | ✅ Completo | 3,642 | `corpus/descarga_completa/` |
| Documentos Word | ✅ Descargados | 101 | `corpus/descarga_completa/` |
| Transcripciones | 🔄 En progreso | 361 / 3,743 (9.6%) | `corpus/textos/` |
| Estadísticas WP | ✅ Completo | ~3,475 posts | `corpus/estadisticas/` |
| Links SNIFA | ✅ Guardados | 7 datasets | `corpus/snifa/` |
| Info SEIA | ✅ Parcial | CSV/JSON | `corpus/seia/` |

### Papers Académicos

| Paper | Archivo | Estado | Páginas |
|-------|---------|--------|---------|
| Paper 1: Cifras Oficiales | `paper/paper1_cifras_oficiales.tex` | ✅ **Completo** | 17 |
| Paper 2: Corpus | `paper/paper2_corpus.md` | 📝 Borrador | - |
| Paper 3: Análisis | `paper/paper3_analisis.md` | 📝 Borrador | - |

### Paper 1 - Detalles

**Archivo:** `paper/paper1_cifras_oficiales.tex` (LaTeX)
**PDF:** `paper/paper1_cifras_oficiales.pdf` (17 páginas)

**Contenido:**
- Introducción con contexto internacional (Pring & Pring 2016)
- Diagrama TikZ de arquitectura institucional
- Estadísticas de los 3 tribunales (1,083 causas, 704 sentencias)
- Casos emblemáticos (Pascua Lama, Dominga)
- Zonas de sacrificio (Quintero-Puchuncaví)
- Análisis exploratorio de sentencias (sectores, resultados)
- 16 referencias académicas

**Figuras incluidas:**
1. Arquitectura institucional (TikZ)
2. Distribución por tribunal
3. Evolución temporal
4. Mapa territorial
5. Gráfico de torta

**Tablas incluidas:**
1. Estadísticas 3TA (2014-2025)
2. Estadísticas 2TA (2013-2024)
3. Estadísticas 1TA (2017-2024)
4. Consolidado del sistema
5. Productividad por tribunal
6. Sectores económicos (n=308)
7. Resultados de sentencias (n=201)

### Datos y Estadísticas

| Archivo | Descripción |
|---------|-------------|
| `datos/CIFRAS_OFICIALES.md` | Datos oficiales verificados de los 3 tribunales |
| `datos/TIPOS_DOCUMENTOS_LEGALES.md` | Clasificación de tipos de documentos |
| `datos/inventario_mejorado.csv` | Índice principal del corpus |
| `datos/estadisticas/estadisticas_corpus.json` | Estadísticas del corpus |
| `datos/estadisticas/sectores_economicos.json` | Sectores por sentencia |
| `datos/estadisticas/resultados_sentencias.json` | Resultados acoge/rechaza |

### Geocodificación

| Archivo | Descripción |
|---------|-------------|
| `datos/geografico/geocodificacion.json` | Coordenadas de 604 causas |
| `datos/geografico/ubicaciones_extraidas.json` | Detalle de ubicaciones por causa |
| `paper/figuras/fig6_mapa_tribunales.png` | Mapa por tribunal |
| `paper/figuras/fig7_mapa_comunas.png` | Mapa por comuna |
| `paper/figuras/mapa_interactivo.html` | Mapa interactivo |

---

## Estructura del Proyecto

```
tribunal_pdf/
├── .gitignore
├── README.md
├── requirements.txt
├── ESTADO_PROYECTO.md              # Este archivo
├── CLAUDE.md                       # Instrucciones de estilo
├── HISTORICO_SESION_*.md           # Históricos de sesiones
├── Tribunal_Ambiental.ipynb        # Notebook original
│
├── corpus/                         # DATOS PRINCIPALES
│   ├── descarga_completa/          # 3,642 PDFs organizados por tipo
│   ├── textos/                     # 308 transcripciones .txt
│   ├── estadisticas/               # Posts WordPress 1ta/2ta
│   ├── seia/                       # Datos SEIA
│   ├── snifa/                      # Links SNIFA
│   └── RESUMEN_FUENTES_COMPLETO.md
│
├── datos/                          # METADATOS Y ESTADÍSTICAS
│   ├── CIFRAS_OFICIALES.md
│   ├── TIPOS_DOCUMENTOS_LEGALES.md
│   ├── inventario_mejorado.csv
│   ├── estadisticas/
│   │   ├── estadisticas_corpus.json
│   │   ├── sectores_economicos.json
│   │   └── resultados_sentencias.json
│   ├── sentencias/
│   └── geografico/
│
├── paper/                          # PAPERS ACADÉMICOS
│   ├── paper1_cifras_oficiales.tex # ✅ PAPER PRINCIPAL (17 pp)
│   ├── paper1_cifras_oficiales.pdf
│   ├── paper2_corpus.md
│   ├── paper3_analisis.md
│   └── figuras/
│       ├── fig1_por_tribunal.png
│       ├── fig2_temporal.png
│       ├── fig3_temporal_tribunal.png
│       ├── fig4_por_tipo.png
│       ├── fig5_pie_tribunal.png
│       ├── fig6_mapa_tribunales.png
│       ├── fig7_mapa_comunas.png
│       └── arquitectura_sistema.tex
│
├── scripts/                        # SCRIPTS
│   ├── descargar_tribunales.py
│   ├── descargar_todo.py
│   ├── extraer_texto_pdf.py
│   ├── generar_graficos.py
│   └── desarrollo/
│
└── _RESPALDO_antiguos/             # ARCHIVOS OBSOLETOS
```

---

## Hallazgos Principales (Paper 1)

### Estadísticas del Sistema
- **Total causas:** ~1.320 (2012-2025)
- **Total sentencias:** ~704
- **Promedio anual:** 54 sentencias

### Distribución por Tribunal
| Tribunal | Causas | % |
|----------|--------|---|
| 2TA Santiago | ~620 | 47% |
| 3TA Valdivia | 549 | 42% |
| 1TA Antofagasta | ~150 | 11% |

### Sectores Económicos (n=308 sentencias)
| Sector | % |
|--------|---|
| Minería | 41,6% |
| Energía | 39,3% |
| Industrial | 36,7% |
| Inmobiliario | 33,1% |
| Residuos | 33,1% |

### Resultados (n=201 sentencias)
| Resultado | % |
|-----------|---|
| Acoge | 48,8% |
| Rechaza | 47,3% |
| Inadmisible | 2,0% |
| Sin lugar | 2,0% |

---

## Histórico de Sesiones

| Fecha | Archivo | Descripción |
|-------|---------|-------------|
| 2026-01-08 | `HISTORICO_SESION_85b11f01.md` | Construcción inicial del corpus |
| 2026-01-09 | (en ESTADO anterior) | Limpieza y consolidación |
| 2026-01-10 | (en ESTADO anterior) | Geocodificación |
| 2026-01-11 | `HISTORICO_SESION_20260111.md` | Finalización Paper 1 |

---

## Tarea en Progreso: Extracción de Corpus Completo

**Script:** `scripts/extraer_corpus_completo.py`

**Estrategia híbrida:**
- PDFs con texto embebido → pdfplumber (extracción directa)
- PDFs escaneados → Claude MLLM (visión, posterior)
- Documentos Word → python-docx

**Progreso actual:**
- Total documentos: 3,743
- Ya transcritos: 361 (9.6%)
- Pendientes: 3,382
- Log: `datos/log_extraccion.json`

**Comando para continuar:**
```bash
cd "G:\Mi unidad\tribunal_pdf"
python scripts/extraer_corpus_completo.py
```

El script detecta automáticamente transcripciones existentes y continúa donde quedó.

---

## Próximos Pasos

### Inmediato (URGENTE)
- [ ] **Continuar extracción de corpus en PC más rápido**
- [ ] Procesar los 3,382 documentos pendientes
- [ ] Identificar PDFs escaneados que requieren Claude MLLM

### Paper 1 (✅ completado)
- [x] Reescritura según estilo CLAUDE.md
- [x] Diagrama de arquitectura institucional
- [x] Sección zonas de sacrificio
- [x] Análisis exploratorio de sentencias
- [x] Referencias académicas completas
- [ ] Revisión final de estilo (opcional)

### Paper 2 (pendiente - requiere corpus completo)
- [ ] Convertir a LaTeX
- [ ] Documentar metodología de construcción del corpus
- [ ] Agregar estadísticas descriptivas del corpus completo
- [ ] Sección sobre PDFs escaneados vs texto embebido

### Paper 3 (pendiente - requiere corpus completo)
- [ ] Convertir a LaTeX
- [ ] Análisis de texto de sentencias con NLP
- [ ] Clasificación automática por sector económico
- [ ] Visualizaciones adicionales

### Extensiones posibles
- [ ] Base de datos SQLite del corpus
- [ ] API de consulta del corpus
- [ ] Análisis de redes de citación jurisprudencial
- [ ] Modelo de clasificación automática de sentencias

---

## Cómo Continuar

```bash
# Continuar última sesión
claude --continue

# Nueva sesión con contexto
claude
# Luego: "Lee ESTADO_PROYECTO.md y CLAUDE.md"

# Compilar Paper 1
cd paper && pdflatex paper1_cifras_oficiales.tex
```

---

*Actualizar este archivo al finalizar cada sesión de trabajo*
