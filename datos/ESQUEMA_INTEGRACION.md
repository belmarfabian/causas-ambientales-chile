# Esquema de Integración de Datos - Conflictos Socioecológicos Chile

**Última actualización:** 2026-01-19

## 1. Arquitectura General

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                  FUENTES PRIMARIAS (Mapeo de Conflictos)                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │   INDH     │  │  EJAtlas   │  │   OCMAL    │  │   ACLED    │            │
│  │ 162 casos  │  │  77 casos  │  │  49 casos  │  │ (pendiente)│            │
│  │ ✓ activo   │  │ ✓ activo   │  │ ✓ activo   │  │ req. API   │            │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └────────────┘            │
│        │               │               │                                    │
│        └───────────────┼───────────────┘                                    │
│                        ▼                                                    │
│        ┌───────────────────────────────────┐                               │
│        │      PROCESO DE DEDUPLICACIÓN     │                               │
│        │  - Normalización texto            │                               │
│        │  - Matching palabras (score >= 2) │                               │
│        │  - EJAtlas vs INDH: 26 dup.       │                               │
│        │  - OCMAL vs INDH: 18 dup.         │                               │
│        └─────────────────┬─────────────────┘                               │
│                          ▼                                                  │
│        ┌───────────────────────────────────┐                               │
│        │   DATASET INTEGRADO: 244 únicos   │                               │
│        │   conflictos_integrados.json      │                               │
│        └───────────────────────────────────┘                               │
│                                                                             │
│  PENDIENTES (sin datos estructurados):                                      │
│  ┌────────────┐  ┌────────────┐                                            │
│  │   OLCA     │  │  Terram    │  Requieren extracción manual               │
│  │ cualitativo│  │ cualitativo│                                            │
│  └────────────┘  └────────────┘                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│              FUENTES COMPLEMENTARIAS (Fiscalización/Litigación)             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Estas fuentes NO mapean conflictos, sino acciones estatales que pueden    │
│  cruzarse con los conflictos para enriquecer el análisis.                  │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │ SMA/SNIFA       │  │ SMA/SNIFA       │  │ SMA/SNIFA       │             │
│  │ Sancionatorios  │  │ Fiscalizaciones │  │ Sanciones Firmes│             │
│  │ 3,322 procesos  │  │ 57,105 inspecc. │  │ (PDFs)          │             │
│  │ ✓ descargado    │  │ ✓ descargado    │  │ ✓ descargado    │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│                                                                             │
│  ┌─────────────────┐                                                        │
│  │ Tribunales Amb. │  Causas judiciales ambientales                        │
│  │ 1,083 causas    │  (pueden derivar de conflictos)                       │
│  │ ✓ corpus propio │                                                        │
│  └─────────────────┘                                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 2. Clasificación de Fuentes

### Fuentes Primarias (mapean conflictos socioecológicos)

| Fuente | Tipo | Estado | Registros | Únicos |
|--------|------|--------|-----------|--------|
| INDH | Conflictos socioambientales | ✓ Integrado | 162 | 162 |
| EJAtlas | Justicia ambiental global | ✓ Integrado | 77 | 51 |
| OCMAL | Conflictos mineros | ✓ Integrado | 49 | 31 |
| ACLED | Protestas y eventos | ⏳ Requiere API | - | - |
| OLCA | Documentación cualitativa | ✗ No integrable | - | - |
| Terram | Usa datos INDH | ✗ No integrable | - | - |

**Notas sobre fuentes no integradas:**
- **ACLED**: Datos disponibles en HDX requieren registro en acleddata.com. Cobertura Chile: 2018-2026. Registra protestas y eventos de violencia política, no conflictos socioecológicos per se.
- **OLCA**: Solo documentación cualitativa (olca.cl/oca/). No tiene base de datos estructurada descargable.
- **Terram**: No mantiene base de datos propia. Sus análisis usan datos del INDH.

### Fuentes Complementarias (NO mapean conflictos)

| Fuente | Tipo | Estado | Registros |
|--------|------|--------|-----------|
| SMA Sancionatorios | Procesos administrativos | ✓ Descargado | 3,322 |
| SMA Fiscalizaciones | Inspecciones | ✓ Descargado | 57,105 |
| SMA Sanciones Firmes | Resoluciones | ✓ Descargado | 3 PDF |
| RETC | Emisiones contaminantes | ⏳ Por explorar | 17 datasets |
| Tribunales Ambientales | Causas judiciales | ✓ Corpus propio | 1,083 |

**Diferencia clave:** Las fuentes primarias identifican y documentan conflictos entre comunidades y proyectos. Las fuentes complementarias registran acciones del Estado (fiscalización, sanción, litigación) y datos de emisiones que pueden cruzarse con conflictos para análisis.

## 3. Dataset Integrado Actual

| Fuente | Total | Duplicados | Únicos | URL |
|--------|-------|------------|--------|-----|
| INDH | 162 | 0 (base) | 162 | mapaconflictos.indh.cl |
| EJAtlas | 77 | 26 | 51 | ejatlas.org/country/chile |
| OCMAL | 49 | 18 | 31 | mapa.conflictosmineros.net |
| **TOTAL** | **288** | **44** | **244** | |

## 4. Flujo de Trabajo

```
FASE 1: EXTRACCIÓN
─────────────────────────────────────────────────────
    Fuentes primarias:
    scripts/descargar_conflictos.py  → INDH
    scripts/descargar_ejatlas.py     → EJAtlas
    scripts/descargar_ocmal.py       → OCMAL (web scraping)
    [pendiente]                      → ACLED (requiere API)

    Fuentes complementarias:
    scripts/descargar_snifa.py       → SMA datos abiertos

FASE 2: INTEGRACIÓN
─────────────────────────────────────────────────────
    scripts/integrar_conflictos.py
    │
    ├── Carga fuentes primarias (INDH, EJAtlas, OCMAL)
    ├── Normaliza texto (acentos, puntuación, minúsculas)
    ├── Identifica duplicados por matching de palabras
    ├── Genera dataset único
    └── Outputs:
        ├── conflictos_integrados.json (244 registros)
        ├── duplicados_identificados.json
        └── resumen_integracion.json

FASE 3: VISUALIZACIÓN
─────────────────────────────────────────────────────
    plataforma_conflictos.py (Streamlit)
    │
    ├── Filtros: fuente, sector, estado, región
    ├── Estadísticas interactivas (Plotly)
    ├── Mapa georreferenciado
    ├── Tabla de datos exportable
    └── Búsqueda por texto

FASE 4: ANÁLISIS (pendiente)
─────────────────────────────────────────────────────
    Cruce conflictos ↔ fuentes complementarias:
    ├── SMA Sancionatorios (por empresa/ubicación)
    ├── SMA Fiscalizaciones (por coordenadas/región)
    └── Tribunales Ambientales (por caso/empresa)
```

## 5. Estructura del Registro Integrado

```json
{
  "id_interno": "INDH-123",
  "fuente": "INDH",
  "id_fuente": 123,
  "nombre": "Conflicto X",
  "nombre_normalizado": "...",
  "descripcion": "...",
  "region": "Atacama",
  "localidad": "Copiapó",
  "latitud": -27.3668,
  "longitud": -70.3323,
  "sector": "Minería",
  "estado": "Activo",
  "año_inicio": 2010,
  "territorio_indigena": false,
  "empresa": "Empresa X",
  "url": "https://..."
}
```

## 6. Estadísticas Actuales

### Por Estado
| Estado | N |
|--------|---|
| Activo | 74 |
| Latente | 33 |
| Archivado | 31 |
| Cerrado | 24 |

### Por Sector (Top 10)
| Sector | N |
|--------|---|
| Minería | 77 |
| Energía | 60 |
| Saneamiento ambiental | 12 |
| Otro | 10 |
| Pesca y acuicultura | 7 |
| Agropecuario | 6 |
| Infraestructura portuaria | 6 |
| Forestal | 5 |
| Infraestructura de transporte | 5 |
| Inmobiliario | 3 |

## 7. Archivos del Proyecto

```
datos/
├── conflictos/
│   ├── indh_conflictos.json          # Fuente INDH (162)
│   ├── ejatlas_chile_filtrado.json   # Fuente EJAtlas (77)
│   ├── ocmal_chile.json              # Fuente OCMAL (49)
│   ├── conflictos_integrados.json    # Dataset final (244)
│   ├── duplicados_identificados.json # Duplicados detectados
│   └── resumen_integracion.json      # Metadatos
│
├── snifa/
│   ├── sancionatorios/
│   │   └── Sancionatorios.csv        # 3,322 procesos
│   ├── fiscalizaciones/
│   │   └── Fiscalizaciones.csv       # 57,105 inspecciones
│   └── sanciones_firmes/
│       └── *.pdf                     # Resoluciones
│
└── ESQUEMA_INTEGRACION.md            # Este archivo

scripts/
├── descargar_conflictos.py           # Descarga INDH
├── descargar_ejatlas.py              # Descarga EJAtlas
├── descargar_ocmal.py                # Scraping OCMAL
├── descargar_snifa.py                # Descarga SMA
└── integrar_conflictos.py            # Integración

plataforma_conflictos.py              # Visualización Streamlit
```

## 8. Pendientes

### Fuentes primarias por integrar
- [ ] Registrar API key de ACLED (acleddata.com) - eventos de protesta
- [ ] Extraer datos estructurados de OLCA (manual)
- [ ] Evaluar viabilidad de estructurar Terram

### Enriquecimiento
- [ ] Geocodificar conflictos sin coordenadas (EJAtlas, OCMAL)
- [ ] Cruce SMA sancionatorios ↔ conflictos (por empresa/ubicación)
- [ ] Cruce Tribunales Ambientales ↔ conflictos (por caso/empresa)

### Paper
- [ ] Actualizar cifras en paper0 (213 → 244, incluir OCMAL)
