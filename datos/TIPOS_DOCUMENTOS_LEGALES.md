# Tipos de Documentos y Procedimientos en Tribunales Ambientales de Chile

## Marco Legal

Los Tribunales Ambientales fueron creados por la **Ley 20.600** (28 de junio de 2012) como tribunales especializados para resolver controversias medioambientales. Son órganos jurisdiccionales especiales, sujetos a la superintendencia de la Corte Suprema.

---

## 1. TIPOS DE CAUSAS (Competencias según Art. 17)

Los tribunales ambientales conocen tres grandes categorías de asuntos:

### 1.1 Reclamaciones (R-)

**Definición:** Acciones judiciales contra actos administrativos o normas ambientales.

**¿Qué se reclama?**
- Resoluciones de la **Superintendencia del Medio Ambiente (SMA)**
- Decisiones del **Servicio de Evaluación Ambiental (SEA)**
- Resoluciones del **Comité de Ministros**
- Decretos supremos sobre normas de calidad ambiental
- Planes de prevención o descontaminación

**Resultado posible:** El tribunal puede anular total o parcialmente el acto administrativo impugnado.

**Ejemplos en el corpus:** `R-344-2022`, `R-215-2019`, `R-263-2020`

---

### 1.2 Demandas de Reparación por Daño Ambiental (D-)

**Definición:** Acciones judiciales para obtener la reparación de un daño al medio ambiente.

**¿Qué se determina?**
1. Existencia del daño ambiental
2. Responsabilidad (culpa) del demandado
3. Medidas de reparación ambiental

**Importante:**
- El tribunal ordena la **restauración ambiental**, NO indemnizaciones monetarias
- Las indemnizaciones por perjuicios se demandan en tribunales civiles ordinarios

**Ejemplos en el corpus:** `D-74-2022`, `D-45-2019`, `D-16-2016`

---

### 1.3 Solicitudes y Autorizaciones (S-)

**Definición:** Peticiones de la SMA para que el tribunal autorice medidas graves.

**¿Qué se autoriza?**
- Clausura temporal de instalaciones
- Suspensión de funcionamiento
- Suspensión de Resolución de Calificación Ambiental (RCA)
- Medidas provisionales urgentes
- Sanciones graves (clausura definitiva, revocación de RCA)

**Nota:** Estas son medidas "preventivas" mientras se tramitan otros procedimientos.

**Ejemplos en el corpus:** `S-80-2023`, `S-84-2025`, `S-86-2025`

---

### 1.4 Otras Causas (C-)

**Definición:** Causas que no encajan en las categorías anteriores.

**Incluye:**
- Consultas de la SMA
- Procedimientos especiales
- Causas de competencia no contenciosa

**Ejemplos en el corpus:** `C-01-2013`, `C-02-2013`

---

## 2. TIPOS DE RESOLUCIONES JUDICIALES

### 2.1 Sentencia Definitiva

**Definición:** Resolución que pone fin al juicio, decidiendo el asunto controvertido.

**Contenido típico:**
- Resumen de los hechos
- Análisis jurídico
- Decisión (acoge/rechaza la demanda o reclamación)
- Medidas ordenadas (si procede)

**En el corpus:** Archivos con "sentencia", "sentencia_definitiva"

---

### 2.2 Sentencia de Casación (Corte Suprema)

**Definición:** Resolución de la Corte Suprema que revisa una sentencia del tribunal ambiental.

**¿Cuándo procede?**
- Solo por **infracción de ley** con influencia sustancial en el fallo
- Por vicios de forma graves

**Resultados posibles:**
1. **Rechaza casación:** La sentencia original queda firme
2. **Acoge casación:** Anula la sentencia y debe dictar sentencia de reemplazo

**En el corpus:** Archivos con "casacion", "CS", "Corte-Suprema"

---

### 2.3 Sentencia de Reemplazo

**Definición:** Nueva sentencia dictada por la Corte Suprema después de anular la original.

**Características:**
- Reemplaza completamente la sentencia anulada
- Resuelve el fondo del asunto
- Es definitiva (no admite más recursos)

**En el corpus:** Archivos con "reemplazo", "sentencia_de_reemplazo"

---

## 3. OTROS DOCUMENTOS EN EL CORPUS

### 3.1 Síntesis de Sentencias
Resúmenes oficiales de las sentencias para difusión pública.

### 3.2 Boletines de Jurisprudencia
Compilaciones periódicas de sentencias relevantes.

### 3.3 Amicus Curiae
Opiniones de terceros expertos presentadas al tribunal.

### 3.4 Informes de Visitadores
Informes técnicos sobre inspecciones ordenadas por el tribunal.

---

## 4. FLUJO PROCESAL TÍPICO

```
INICIO
   │
   ├── Reclamación (R) ──────────────────┐
   ├── Demanda (D) ──────────────────────┤
   └── Solicitud (S) ────────────────────┤
                                         │
                                         ▼
                              TRIBUNAL AMBIENTAL
                                         │
                                         ▼
                              SENTENCIA DEFINITIVA
                                         │
                    ┌────────────────────┴────────────────────┐
                    │                                         │
                    ▼                                         ▼
            Sin recursos                            Recurso de Casación
            (sentencia firme)                       (a Corte Suprema)
                                                              │
                                         ┌────────────────────┴────────────────┐
                                         │                                     │
                                         ▼                                     ▼
                                   Rechaza casación                    Acoge casación
                                   (sentencia firme)                           │
                                                                               ▼
                                                               SENTENCIA DE REEMPLAZO
                                                                    (definitiva)
```

---

## 5. RESUMEN PARA EL PAPER

| Código | Tipo de Causa | Descripción Simple |
|--------|---------------|-------------------|
| **R-** | Reclamación | Impugnación de decisiones administrativas |
| **D-** | Demanda | Reparación de daño ambiental |
| **S-** | Solicitud | Autorización de medidas graves |
| **C-** | Otras | Consultas y procedimientos especiales |

| Tipo de Sentencia | Tribunal | Descripción |
|-------------------|----------|-------------|
| **Definitiva** | TA | Resuelve el caso en primera instancia |
| **Casación** | CS | Revisa legalidad de la sentencia |
| **Reemplazo** | CS | Nueva sentencia tras anular la original |

---

## 6. ESTADÍSTICAS DEL CORPUS

### Por tipo de causa (causas únicas identificadas):

| Tribunal | R (Reclamaciones) | D (Demandas) | S (Solicitudes) | C (Otras) | **TOTAL** |
|----------|-------------------|--------------|-----------------|-----------|-----------|
| 1TA | 49 | 12 | 8 | 0 | 69 |
| 2TA | 276 | 25 | 79 | 5 | 385 |
| 3TA | 274 | 59 | 74 | 5 | 412 |
| **TOTAL** | **599** | **96** | **161** | **10** | **866** |

### Por tipo de resolución (archivos):

| Tipo | Cantidad |
|------|----------|
| Sentencias Definitivas (TA) | 1,129 |
| Sentencias de Casación (CS) | 101 |
| Sentencias de Reemplazo (CS) | 32 |
| Síntesis/Resúmenes | 269 |
| Otros documentos | 985 |
| **TOTAL ARCHIVOS** | **2,516** |

### Composición del corpus:

- **69%** son **Reclamaciones** (R) - el tipo más común
- **18.6%** son **Solicitudes** (S) - autorizaciones de la SMA
- **11%** son **Demandas** (D) - reparación de daño ambiental
- **1.1%** son **Otras** (C)

---

## Fuentes

- [Ley 20.600 - Biblioteca del Congreso Nacional](https://www.leychile.cl/navegar?idNorma=1041361)
- [Preguntas Frecuentes - 3TA](https://3ta.cl/preguntas-frecuentes-3ta/)
- [Funciones y Competencias - Tribunales Ambientales](https://tribunalesambientales.cl/funciones-y-competencias/)
- [Criterios jurisprudenciales - DACC UdeC](https://dacc.udec.cl/criterios-jurisprudenciales-sobre-la-via-de-impugnacion-de-la-sentencia-definitiva-en-el-contencioso-administrativo-ambiental/)
