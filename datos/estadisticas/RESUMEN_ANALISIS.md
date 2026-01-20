# Resumen de Análisis - Conflictos Socioecológicos Chile

**Fecha:** 2026-01-19
**Dataset:** 244 conflictos únicos (INDH + EJAtlas + OCMAL)

## 1. Categorización Automática

### Tipo de Impacto Ambiental
| Impacto | N | % |
|---------|---|---|
| Agua | 140 | 57.4% |
| Biodiversidad | 79 | 32.4% |
| Salud | 74 | 30.3% |
| Aire | 68 | 27.9% |
| Suelo | 50 | 20.5% |

### Actor Afectado
| Actor | N | % |
|-------|---|---|
| Urbano | 122 | 50.0% |
| Agricultor | 110 | 45.1% |
| Indígena | 67 | 27.5% |
| Pescador | 41 | 16.8% |

### Forma de Resistencia
| Resistencia | N | % |
|-------------|---|---|
| Judicial | 98 | 40.2% |
| Institucional | 95 | 38.9% |
| Movilización | 79 | 32.4% |
| Mediática | 44 | 18.0% |

### Resultado
| Resultado | N | % |
|-----------|---|---|
| Aprobado | 116 | 47.5% |
| Paralizado | 84 | 34.4% |
| En litigio | 49 | 20.1% |

## 2. Análisis Temporal

### Por Década
| Década | N |
|--------|---|
| 1930s | 2 |
| 1940s | 1 |
| 1950s | 2 |
| 1980s | 3 |
| 1990s | 24 |
| 2000s | 69 |
| 2010s | 91 |

**Observaciones:**
- 192/244 conflictos tienen año de inicio (79%)
- Pico en 2010 (20 conflictos)
- Aceleración desde 2006

## 3. Análisis Geográfico

### Top 5 Regiones
| Región | N | % |
|--------|---|---|
| Coquimbo | 22 | 9.0% |
| Atacama | 18 | 7.4% |
| Valparaíso | 17 | 7.0% |
| Antofagasta | 16 | 6.6% |
| Biobío | 13 | 5.3% |

### Zonas de Sacrificio
- 25 conflictos identificados en zonas de sacrificio
- Quintero-Puchuncaví, Tocopilla, Mejillones, Huasco, Coronel

### Georreferenciación
- 97/244 conflictos con coordenadas (40%)

## 4. Cruce Región-Sector

### Coquimbo (22 conflictos)
- Minería: 16 (73%)
- Energía: 4 (18%)

### Atacama (18 conflictos)
- Minería: 12 (67%)
- Energía: 3 (17%)

### Antofagasta (16 conflictos)
- Energía: 8 (50%)
- Minería: 7 (44%)

### Biobío (13 conflictos)
- Energía: 9 (69%)
- Minería: 2 (15%)

## 5. Análisis NLP

### Palabras Más Frecuentes
1. ambiental (767)
2. empresa (560)
3. central (365)
4. medio (334)
5. zona (318)
6. agua (289)
7. evaluación (287)
8. comunidades (285)
9. construcción (251)
10. contaminación (199)

### Empresas Mencionadas
| Empresa | N |
|---------|---|
| Codelco | 17 |
| ENAMI | 14 |
| Colbún | 10 |
| Endesa | 10 |
| Arauco | 9 |
| Bio Bio | 8 |
| Enel | 7 |
| Teck | 6 |

### Contaminantes Detectados
| Contaminante | N | % |
|--------------|---|---|
| Cobre | 35 | 14.3% |
| Material particulado | 27 | 11.1% |
| Relaves | 21 | 8.6% |
| Hidrocarburos | 19 | 7.8% |
| Mercurio | 19 | 7.8% |
| Arsénico | 13 | 5.3% |
| Metales pesados | 12 | 4.9% |
| Azufre (SO2) | 11 | 4.5% |
| Plomo | 10 | 4.1% |

### Impactos en Salud
| Impacto | N |
|---------|---|
| Mortalidad | 11 |
| Cáncer | 4 |
| Respiratorio | 4 |
| Intoxicación | 3 |

## 6. Cruces de Categorías

### Impacto vs Actor
- Agua afecta principalmente a: urbanos (100), agricultores (96), indígenas (53)
- Aire afecta principalmente a: urbanos (60), agricultores (43)
- Biodiversidad afecta principalmente a: urbanos (65), agricultores (62), indígenas (42)

### Resistencia vs Resultado
- Judicial: 75 aprobados, 53 paralizados, 33 en litigio
- Movilización: 61 aprobados, 42 paralizados, 32 en litigio

**Observación clave:** La resistencia judicial NO garantiza paralización.
De 98 conflictos con resistencia judicial, 75 (77%) terminaron aprobados.

## 7. Archivos Generados

```
datos/estadisticas/
├── analisis_temporal_espacial.json
├── analisis_nlp.json
└── RESUMEN_ANALISIS.md

datos/conflictos/
├── conflictos_categorizados.json
├── conflictos_categorizados.csv
└── estadisticas_categorias.json

scripts/
├── categorizar_conflictos.py
├── analisis_temporal_espacial.py
└── analisis_nlp_basico.py
```
