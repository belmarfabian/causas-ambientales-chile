# Conflictos Socioecológicos y Tribunales Ambientales de Chile

Base de datos integrada de conflictos socioecológicos y corpus de sentencias de los Tribunales Ambientales de Chile (2012-2025).

## Base de Datos de Conflictos

Integración de 3 fuentes sobre conflictos socioecológicos en Chile:

| Fuente | Registros | Descripción |
|--------|-----------|-------------|
| [INDH](https://mapaconflictos.indh.cl/) | 162 | Mapa de Conflictos Socioambientales (oficial) |
| [EJAtlas](https://ejatlas.org/) | 77 | Environmental Justice Atlas (global) |
| [OCMAL](https://mapa.conflictosmineros.net/) | 49 | Observatorio de Conflictos Mineros |
| **Total únicos** | **244** | Después de deduplicación (-44) |

### Cobertura de campos

| Campo | Cobertura |
|-------|-----------|
| Región | 86.5% |
| Sector económico | 100% |
| Resistencias | 96.7% |
| Resultados | 95.1% |
| Año inicio | 86.9% |

### Sectores

- Minería: 106 (43%)
- Energía: 76 (31%)
- Saneamiento: 13 (5%)
- Agropecuario: 9 (4%)
- Otros: 40 (17%)

## Sistema de Justicia Ambiental

| Tribunal | Causas | Sentencias |
|----------|--------|------------|
| 1TA Antofagasta | 150 | 66 |
| 2TA Santiago | 620 | 332 |
| 3TA Valdivia | 313 | 306 |
| **Total** | **1,083** | **704** |

## Plataforma de Visualización

```bash
pip install -r requirements.txt
streamlit run plataforma_conflictos.py
```

Incluye:
- Mapa interactivo de conflictos
- Filtros por región, sector, estado
- Gráficos de distribución temporal
- Detalle de cada conflicto con fuentes

## Estructura

```
├── datos/
│   ├── conflictos/                    # Base integrada (244 registros)
│   │   ├── conflictos_consolidados_noticias.json
│   │   ├── METODOLOGIA_INTEGRACION.md
│   │   └── duplicados_identificados.json
│   ├── sentencias/                    # Causas tribunales
│   └── estadisticas/                  # Análisis
├── paper/                             # Papers académicos
│   ├── paper1_cifras_oficiales.md
│   └── figuras/
├── scripts/                           # Scripts Python
│   ├── consolidar_con_ids.py         # Integración de fuentes
│   ├── descargar_conflictos.py       # Descarga INDH
│   └── descargar_ejatlas.py          # Descarga EJAtlas
└── plataforma_conflictos.py          # Streamlit app
```

## Archivos principales

| Archivo | Descripción |
|---------|-------------|
| `datos/conflictos/conflictos_consolidados_noticias.json` | Dataset final (244 conflictos) |
| `datos/conflictos/METODOLOGIA_INTEGRACION.md` | Documentación metodológica |
| `datos/sentencias/causas_final.json` | 1,083 causas de tribunales |
| `plataforma_conflictos.py` | Visualizador Streamlit |

## Uso

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar plataforma
streamlit run plataforma_conflictos.py

# Regenerar dataset (requiere datos originales)
python scripts/consolidar_con_ids.py
```

## Papers

1. **Cifras oficiales**: Estadísticas del sistema de justicia ambiental
2. **Corpus**: Metodología de construcción del corpus
3. **Análisis**: Análisis de sentencias (en desarrollo)

## Autor

Fabián Belmar
Núcleo Milenio SODAS / Centro de Estudios Públicos

## Licencia

Datos públicos. Base de conflictos construida a partir de fuentes públicas (INDH, EJAtlas, OCMAL).

## Citar

```bibtex
@misc{belmar2026conflictos,
  author = {Belmar, Fabián},
  title = {Conflictos Socioecológicos y Tribunales Ambientales de Chile},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/belmarfabian/tribunal-ambiental-chile}
}
```
