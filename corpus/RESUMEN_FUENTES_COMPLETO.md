# Corpus Ambiental Chile - Resumen de Fuentes

## Fecha: 2026-01-08

---

## 1. TRIBUNALES AMBIENTALES (DESCARGADO)

### Documentos descargados: 3,749 archivos (~5 GB)

| Tribunal | Documentos | Tamano |
|----------|------------|--------|
| 1TA (Antofagasta) | 373 | ~1.7 GB |
| 2TA (Santiago) | 1,717 | ~1.4 GB |
| 3TA (Valdivia) | 1,659 | ~1.8 GB |

**Tipos de documentos:**
- Sentencias definitivas
- Sentencias de casacion (Corte Suprema)
- Sentencias de reemplazo
- Resoluciones
- Informes en derecho
- Informes tecnicos
- Anuarios institucionales
- Boletines de jurisprudencia
- Actas de instalacion
- Publicaciones academicas

**Ubicacion:** `corpus/descarga_completa/documentos/`

---

## 2. SNIFA - Superintendencia del Medio Ambiente (LINKS GUARDADOS)

Los datos de SNIFA estan en carpetas de Google Drive que requieren descarga manual.

**Links guardados en:** `corpus/snifa/LINKS_SNIFA.txt`

### Datasets disponibles:

1. **Termoelectricas**
   - Datos D.S. N 13/2011 desde 2014
   - https://drive.google.com/drive/folders/1CfvVC3l4tDvRFyLWv2a_4H6Q8DV58cr6

2. **Unidades Fiscalizables**
   - Catastro de unidades vigentes
   - https://drive.google.com/drive/folders/1Pos3xmMDj0OoRiqmR1W9Q2K0hsnMaEL4

3. **Sancionatorios**
   - Procesos sancionatorios historicos
   - https://drive.google.com/drive/folders/1O7o60LzQ-qH8xiK_-Ofqw_mZzti_gbEr

4. **Responsabilidad Extendida del Productor**
   - Estimacion toneladas residuos
   - https://drive.google.com/drive/folders/1nlG-tSKrkUb6Tp2ZhjUeRzDlFucPuUb1

5. **RILES**
   - Datos D.S. N 90/2000 desde 2017
   - https://drive.google.com/drive/folders/1Ne0COCkx70XOPLIqeUqpIl3uiayqfihl

6. **Fiscalizaciones**
   - Fiscalizaciones historicas
   - https://drive.google.com/drive/folders/1WAw7SSPMug3oZimgHYkEIi7_5JqLvzpb

7. **Sanciones Firmes**
   - Listado sanciones declaradas firmes
   - https://drive.google.com/drive/folders/1q6MG4sfGxLisRuusnYKpUxmi9jgkSU4F

---

## 3. SEIA - Sistema de Evaluacion de Impacto Ambiental (REQUIERE ACCESO MANUAL)

El SEIA bloquea acceso automatizado. Requiere descarga manual desde:
https://seia.sea.gob.cl/busqueda/buscarProyecto.php

**Documentos disponibles por proyecto:**
- EIA (Estudios de Impacto Ambiental) - documentos extensos 100-1000+ paginas
- DIA (Declaraciones de Impacto Ambiental)
- RCA (Resoluciones de Calificacion Ambiental)
- Adendas
- Observaciones ciudadanas
- Informes sectoriales

**Nota:** Un corpus completo del SEIA seria de varios TB de datos.

---

## 4. ESTADISTICAS WORDPRESS (DESCARGADO)

**Ubicacion:** `corpus/estadisticas/`

| Tribunal | Posts | Archivo |
|----------|-------|---------|
| 1TA | 1,429 | 1ta/posts.json |
| 2TA | 2,046 | 2ta/posts.json |

---

## 5. OTRAS FUENTES POTENCIALES

### Oficina Judicial Virtual (Poder Judicial)
- URL: https://oficinajudicialvirtual.pjud.cl
- Expedientes completos de causas
- Requiere cuenta de usuario

### Contraloria General de la Republica
- Dictamenes ambientales
- https://www.contraloria.cl

### Consejo de Defensa del Estado
- Causas ambientales donde participa el Estado
- https://www.cde.cl

### Ministerio del Medio Ambiente
- Normativa ambiental
- https://mma.gob.cl

---

## ESTRUCTURA DEL CORPUS

```
corpus/
├── descarga_completa/
│   ├── documentos/
│   │   ├── 1ta/           (373 archivos)
│   │   ├── 2ta folders/   (1,717 archivos)
│   │   └── 3ta/           (1,659 archivos)
│   └── datos/
│       └── *.json, *.csv
├── estadisticas/
│   ├── 1ta/posts.json
│   └── 2ta/posts.json
├── snifa/
│   └── LINKS_SNIFA.txt
└── seia/
    └── RESUMEN_SEIA.txt
```

---

## TOTALES

| Fuente | Estado | Documentos |
|--------|--------|------------|
| Tribunales Ambientales | COMPLETO | 3,749 |
| SNIFA | Links guardados | ~7 datasets |
| SEIA | Requiere manual | Miles de proyectos |
| Estadisticas WP | COMPLETO | 3,475 posts |

**Total documentos descargados: 3,749**
**Tamano aproximado: 5 GB**
