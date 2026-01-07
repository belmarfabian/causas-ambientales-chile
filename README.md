# Clasificador de PDFs - Tribunal Ambiental

Sistema para clasificar y organizar documentos judiciales del Tribunal Ambiental de Chile.

## Requisitos

- Python 3.8+
- PyMuPDF

```bash
pip install -r requirements.txt
```

## Uso

### Clasificador mejorado (con lectura de contenido PDF)

```bash
python scripts/clasificador_mejorado.py
```

Opciones:
- Procesar solo N archivos: `python scripts/clasificador_mejorado.py 50`

### Salida

El script genera `datos/inventario_mejorado.csv` con los siguientes campos:

| Campo | Descripción |
|-------|-------------|
| archivo | Nombre del archivo PDF |
| estado | OK_CONTENIDO, OK_NOMBRE, OK_CORTE_SUPREMA, OK_INFORME, REVISION_MANUAL |
| tipo_caso | R (Reclamación), D (Demanda), S (Solicitud), C (Consulta) |
| rol | Número de rol |
| año_rol | Año del rol |
| fecha_sentencia | Fecha de la sentencia |
| tipo_documento | Sentencia, Resolución, Casación, Informe |
| es_corte_suprema | True si es documento de Corte Suprema |
| rol_cs | Rol de Corte Suprema (si aplica) |
| tribunal | Tribunal que emitió el documento |

## Estructura del proyecto

```
tribunal_pdf/
├── scripts/
│   ├── clasificador_mejorado.py  # Clasificador principal
│   ├── organizar_pdfs.py         # Organizador de archivos
│   └── pdf_a_txt.py              # Extractor de texto
├── datos/
│   └── inventario_mejorado.csv   # Inventario generado
├── tribunal_pdfs_organizado/     # PDFs organizados (no en git)
│   ├── originales/
│   └── duplicados/
└── requirements.txt
```

## Estadísticas actuales

- Total archivos: 588
- Clasificados correctamente: 99.0%
- Requieren revisión manual: 0.3%
