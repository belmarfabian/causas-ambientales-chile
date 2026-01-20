# Corpus Tribunales Ambientales de Chile

Corpus de documentos judiciales de los Tribunales Ambientales de Chile (2012-2025) para investigación en humanidades digitales y derecho ambiental.

## Contenido del Corpus

| Componente | Cantidad | Estado |
|------------|----------|--------|
| PDFs descargados | 3,642 | ✅ Completo |
| Documentos Word | 101 | ✅ Completo |
| Transcripciones | 361 / 3,743 | 🔄 En progreso (9.6%) |
| Causas únicas | 755 | ✅ Identificadas |
| Período | 2012-2025 | |

## Estadísticas del Sistema

| Tribunal | Causas | Sentencias | % |
|----------|--------|------------|---|
| 2TA Santiago | 620 | 332 | 57% |
| 3TA Valdivia | 313 | 306 | 29% |
| 1TA Antofagasta | 150 | 66 | 14% |
| **Total** | **1,083** | **704** | 100% |

## Papers

| Paper | Archivo | Estado |
|-------|---------|--------|
| Cifras Oficiales | `paper/paper1_cifras_oficiales.pdf` | Completo (17 pp) |
| Corpus y Metodología | `paper/paper2_corpus.md` | Borrador |
| Análisis de Sentencias | `paper/paper3_analisis.md` | Borrador |

## Estructura

```
tribunal_pdf/
├── corpus/                    # Datos principales
│   ├── descarga_completa/     # 3,642 PDFs
│   └── textos/                # 308 transcripciones
├── datos/                     # Metadatos y estadísticas
│   ├── estadisticas/          # JSON con análisis
│   └── geografico/            # Geocodificación
├── paper/                     # Papers académicos
│   ├── paper1_cifras_oficiales.tex
│   └── figuras/
└── scripts/                   # Scripts Python
```

## Requisitos

```bash
pip install -r requirements.txt
```

- Python 3.8+
- PyMuPDF (extracción de texto)
- TinyTeX (compilación LaTeX)

## Uso

```bash
# Compilar Paper 1
cd paper && pdflatex paper1_cifras_oficiales.tex

# Generar gráficos
python scripts/generar_graficos.py

# Extraer texto de PDFs
python scripts/extraer_texto_pdf.py
```

## Documentación

- `ESTADO_PROYECTO.md` - Estado actual y próximos pasos
- `CLAUDE.md` - Instrucciones de estilo para escritura
- `HISTORICO_SESION_*.md` - Históricos de sesiones de trabajo

## Autor

Fabián Belmar - Núcleo Milenio SODAS / Centro de Estudios Públicos

## Licencia

Datos públicos de los Tribunales Ambientales de Chile.
