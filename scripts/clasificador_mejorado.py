#!/usr/bin/env python3
"""
Clasificador mejorado de PDFs del Tribunal Ambiental.
Lee la primera página de cada PDF para extraer metadatos con mayor precisión.
"""

import os
import re
import csv
import fitz  # PyMuPDF
from pathlib import Path
from datetime import datetime

# Rutas del proyecto
BASE_DIR = Path("g:/Mi unidad/tribunal_pdf")
PDF_DIR = BASE_DIR / "tribunal_pdfs_organizado"
OUTPUT_DIR = BASE_DIR / "datos"

# Patrones para extraer del contenido del PDF
PATRONES_CONTENIDO = {
    # Rol del tribunal: formatos variados del 2TA
    'rol_tribunal': [
        # Formato "Rol R N° 232-2020" (común en 2TA)
        r'(?:ROL|Rol|rol)\s+([RDSC])\s*(?:N[°º]?)?\s*(\d+)[-\s](\d{4})',
        # Formato "ROL N° R-123-2020"
        r'(?:ROL|Rol|rol)\s*(?:N[°º]?)?\s*([RDSC])-?(\d+)-(\d{4})',
        # Formato "R-123-2020" suelto
        r'\b([RDSC])-(\d+)-(\d{4})\b',
        # Solo número con año
        r'(?:ROL|Rol|rol)\s*(?:N[°º]?)?\s*(\d+)-(\d{4})',
        # Causa ROL
        r'(?:Causa|CAUSA|causa)\s*(?:ROL|Rol|rol)?\s*(?:N[°º]?)?\s*([RDSC])?-?(\d+)-(\d{4})',
        # Asignándosele el Rol
        r'asign[aá]ndosele\s+(?:el\s+)?(?:ROL|Rol|rol)\s+([RDSC])\s*(?:N[°º]?)?\s*(\d+)[-\s](\d{4})',
    ],
    # Rol Corte Suprema
    'rol_cs': [
        r'(?:Corte\s+Suprema|CS|C\.S\.)\s*(?:ROL|Rol)?\s*(?:N[°º]?)?\s*(\d+)-(\d{4})',
        r'(?:ROL|Rol)\s*(?:N[°º]?)?\s*(\d+)-(\d{4})\s*(?:CS|Corte\s+Suprema)',
        r'Ingreso\s*(?:Corte\s+Suprema)?\s*(?:N[°º]?)?\s*(\d+)-(\d{4})',
        # Patrón para "autos Rol Nº X.XXX-YYYY" (casaciones)
        r'autos\s+(?:ROL|Rol)\s*(?:N[°º]?)?\s*(\d+)[.\-]?(\d+)?-(\d{4})',
        r'(?:ROL|Rol)\s*(?:N[°º]?)?\s*(\d+)[.\-](\d+)-(\d{4})',  # Rol con punto (4.308-2021)
    ],
    # Fecha de sentencia
    'fecha': [
        r'Santiago,?\s+(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})',
        r'(\d{1,2})\s+de\s+(\w+)\s+(?:del?\s+)?(\d{4})',
        r'(\d{2})[/.-](\d{2})[/.-](\d{4})',
    ],
    # Tipo de documento
    'tipo_doc': [
        r'(SENTENCIA|Sentencia|RESOLUCI[OÓ]N|Resoluci[oó]n|CASACI[OÓ]N|Casaci[oó]n)',
        r'(INFORME\s+EN\s+DERECHO|Informe\s+en\s+Derecho)',
    ],
    # Tribunal
    'tribunal': [
        r'(Tribunal\s+Ambiental\s+de\s+\w+)',
        r'(Segundo\s+Tribunal\s+Ambiental)',
        r'(Tercer\s+Tribunal\s+Ambiental)',
        r'(Primer\s+Tribunal\s+Ambiental)',
        r'(Corte\s+Suprema)',
    ],
    # Materia/Tipo de caso
    'materia': [
        r'(Reclamaci[oó]n)',
        r'(Demanda\s+por\s+da[nñ]o\s+ambiental)',
        r'(Solicitud\s+de\s+autorizaci[oó]n)',
    ],
}

MESES = {
    'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
    'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
    'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
}


def extraer_texto_pdf(filepath, paginas=2):
    """Extrae texto de las primeras N páginas del PDF."""
    try:
        doc = fitz.open(filepath)
        texto = ""
        for i in range(min(paginas, len(doc))):
            texto += doc[i].get_text()
        doc.close()
        return texto
    except Exception as e:
        return f"ERROR: {e}"


def extraer_metadatos_nombre(filename):
    """Extrae metadatos del nombre del archivo (versión mejorada)."""
    name = Path(filename).stem

    metadatos = {
        'tipo_caso': None,
        'rol': None,
        'año_rol': None,
        'fecha_sentencia': None,
        'tipo_documento': None,
        'roles_acumulados': [],
        'es_corte_suprema': False,
        'es_informe': False,
        'rol_cs': None,  # Rol de Corte Suprema (diferente al del tribunal)
    }

    # Detectar Informe en Derecho (categoría especial sin rol)
    if any(x in name for x in ['Informe', 'Opinion-Legal', 'Opinion_Legal']):
        metadatos['es_informe'] = True
        metadatos['tipo_documento'] = 'Informe en Derecho'
        # Buscar rol asociado (ej: R-40-Informe)
        match = re.search(r'([RDSC])-(\d+)-', name)
        if match:
            metadatos['tipo_caso'] = match.group(1)
            metadatos['rol'] = int(match.group(2))
            # Los informes no suelen tener año en el nombre
        return metadatos

    # Detectar Corte Suprema
    if any(x in name for x in ['CS', 'Corte-Suprema', 'casacion', 'Casacion', 'SCS', 'reemplazo', 'Reemplazo']):
        metadatos['es_corte_suprema'] = True
        # Buscar rol de CS en el nombre (ej: 1085-2022, 5.374-2021)
        match = re.search(r'(\d+)[.\-](\d{4})[.\-]?(?:casacion|Casacion|reemplazo|Reemplazo|Sentencia)', name, re.I)
        if match:
            metadatos['rol_cs'] = f"{match.group(1)}-{match.group(2)}"
        # También buscar formato Rol-N_-22.343-2021
        match = re.search(r'Rol[_\-]N[_\-]?(\d+)[.\-](\d+)[.\-](\d{4})', name)
        if match:
            metadatos['rol_cs'] = f"{match.group(1)}.{match.group(2)}-{match.group(3)}"

    # Patrón mejorado: YYYY.MM.DD_Tipo_X-NNN-YYYY (acepta _ y -)
    patron1 = r'^(\d{4})[.\-](\d{2})[.\-](\d{2})[-_](\w+)[-_]([RDSC])[-_]?(\d+)[-_](\d{4})'
    match = re.match(patron1, name)
    if match:
        año, mes, dia, tipo_doc, tipo_caso, rol, año_rol = match.groups()
        metadatos['fecha_sentencia'] = f"{año}-{mes}-{dia}"
        metadatos['tipo_documento'] = tipo_doc
        metadatos['tipo_caso'] = tipo_caso
        metadatos['rol'] = int(rol)
        metadatos['año_rol'] = int(año_rol)
        return metadatos

    # Patrón para R_295-2021 (con guión bajo después de letra)
    patron2 = r'([RDSC])[_-](\d+)[_-](\d{4})'
    match = re.search(patron2, name)
    if match:
        tipo_caso, rol, año_rol = match.groups()
        metadatos['tipo_caso'] = tipo_caso
        metadatos['rol'] = int(rol)
        metadatos['año_rol'] = int(año_rol)

        # Buscar fecha al inicio
        fecha_match = re.match(r'^(\d{4})[.\-](\d{2})[.\-](\d{2})', name)
        if fecha_match:
            año, mes, dia = fecha_match.groups()
            metadatos['fecha_sentencia'] = f"{año}-{mes}-{dia}"

        # Detectar tipo documento
        if 'Sentencia' in name:
            metadatos['tipo_documento'] = 'Sentencia'
        elif 'Resolucion' in name:
            metadatos['tipo_documento'] = 'Resolución'

        return metadatos

    # Patrón especial para roles múltiples: R-297-298-299 (3+ roles seguidos sin año intermedio)
    patron_multi_3 = r'([RDSC])-(\d{2,3})-(\d{2,3})-(\d{2,3})(?:[_\-]|\.pdf|$)'
    match = re.search(patron_multi_3, name)
    if match:
        tipo, rol1, rol2, rol3 = match.groups()
        metadatos['tipo_caso'] = tipo
        metadatos['rol'] = int(rol1)
        metadatos['roles_acumulados'] = [f"{tipo}-{rol2}", f"{tipo}-{rol3}"]
        # Buscar año en otra parte del nombre
        año_match = re.search(r'(\d{4})[.\-_](\d{2})[.\-_](\d{2})', name)
        if año_match:
            # El año está en la fecha del documento, asumir año del rol es el anterior
            año_doc = int(año_match.group(1))
            metadatos['año_rol'] = año_doc - 1  # Los roles suelen ser del año anterior
            metadatos['fecha_sentencia'] = f"{año_match.group(1)}-{año_match.group(2)}-{año_match.group(3)}"
        return metadatos

    # Patrón para roles múltiples: R-289-290_ o R-232_y_276
    patron_multi_2 = r'([RDSC])-(\d{2,3})[-_](\d{2,3})(?:_|\.pdf|$)'
    match = re.search(patron_multi_2, name)
    if match:
        tipo, rol1, rol2 = match.groups()
        metadatos['tipo_caso'] = tipo
        metadatos['rol'] = int(rol1)
        metadatos['roles_acumulados'] = [f"{tipo}-{rol2}"]
        # Buscar año
        año_match = re.search(r'(\d{4})[.\-_](\d{2})[.\-_](\d{2})', name)
        if año_match:
            año_doc = int(año_match.group(1))
            metadatos['año_rol'] = año_doc - 1
            metadatos['fecha_sentencia'] = f"{año_match.group(1)}-{año_match.group(2)}-{año_match.group(3)}"
        return metadatos

    # Patrón genérico para roles múltiples: R-232_y_276, R-310_311
    patron_multi = r'([RDSC])-(\d+)(?:[_-](?:y[_-])?(\d+))?(?:[_-](\d+))?(?:[_-](\d{4}))?'
    match = re.search(patron_multi, name)
    if match:
        grupos = match.groups()
        metadatos['tipo_caso'] = grupos[0]
        metadatos['rol'] = int(grupos[1])

        # Buscar año
        año_match = re.search(r'(\d{4})(?:\.pdf)?$', name)
        if not año_match:
            año_match = re.search(r'[_-](\d{4})[_-]', name)
        if año_match:
            metadatos['año_rol'] = int(año_match.group(1))

        # Roles adicionales
        for g in grupos[2:4]:
            if g and len(g) <= 3:  # Es un rol, no un año
                metadatos['roles_acumulados'].append(f"{grupos[0]}-{g}")

    # Patrón para "Rol-348-2022" (sin letra de tipo)
    patron_rol = r'Rol[_-](\d+)[_-](\d{4})'
    match = re.search(patron_rol, name, re.I)
    if match and not metadatos['rol']:
        metadatos['rol'] = int(match.group(1))
        metadatos['año_rol'] = int(match.group(2))
        metadatos['tipo_caso'] = 'R'  # Asumir Reclamación

    # Patrón antiguo: X-XX-YYYY-DD-MM-YYYY-Tipo
    patron_antiguo = r'^([RDSC])-(\d+)-(\d{4})-(\d{2})-(\d{2})-(\d{4})-(\w+)'
    match = re.match(patron_antiguo, name)
    if match:
        tipo_caso, rol, año_rol, dia, mes, año, tipo_doc = match.groups()
        metadatos['tipo_caso'] = tipo_caso
        metadatos['rol'] = int(rol)
        metadatos['año_rol'] = int(año_rol)
        metadatos['fecha_sentencia'] = f"{año}-{mes}-{dia}"
        metadatos['tipo_documento'] = tipo_doc

    return metadatos


def extraer_metadatos_contenido(texto):
    """Extrae metadatos del contenido del PDF."""
    metadatos = {
        'rol_contenido': None,
        'tipo_caso_contenido': None,
        'año_rol_contenido': None,
        'fecha_contenido': None,
        'tipo_doc_contenido': None,
        'tribunal': None,
        'es_corte_suprema_contenido': False,
        'roles_multiples': [],
        'texto_muestra': texto[:500] if texto else ''
    }

    if not texto or texto.startswith('ERROR'):
        return metadatos

    # Buscar TODOS los roles del tribunal (puede haber varios)
    roles_encontrados = []
    for patron in PATRONES_CONTENIDO['rol_tribunal']:
        matches = re.findall(patron, texto)
        for match in matches:
            if isinstance(match, tuple):
                grupos = [g for g in match if g]  # Filtrar grupos vacíos
                if len(grupos) >= 2:
                    # Determinar qué es tipo, rol y año
                    if grupos[0] in 'RDSC':
                        tipo = grupos[0]
                        rol = int(grupos[1])
                        año = int(grupos[2]) if len(grupos) > 2 else None
                    else:
                        tipo = 'R'  # Asumir Reclamación
                        rol = int(grupos[0])
                        año = int(grupos[1])

                    if año and 2010 <= año <= 2030:  # Validar año razonable
                        roles_encontrados.append((tipo, rol, año))

    # Eliminar duplicados y ordenar
    roles_unicos = list(set(roles_encontrados))
    if roles_unicos:
        # Tomar el primer rol como principal
        tipo, rol, año = roles_unicos[0]
        metadatos['tipo_caso_contenido'] = tipo
        metadatos['rol_contenido'] = rol
        metadatos['año_rol_contenido'] = año
        # Guardar roles adicionales
        if len(roles_unicos) > 1:
            metadatos['roles_multiples'] = [f"{t}-{r}-{a}" for t, r, a in roles_unicos[1:]]

    # Buscar rol Corte Suprema
    for patron in PATRONES_CONTENIDO['rol_cs']:
        match = re.search(patron, texto)
        if match:
            metadatos['es_corte_suprema_contenido'] = True
            grupos = match.groups()
            # Construir rol de CS
            if len(grupos) >= 2:
                if len(grupos) == 3 and grupos[1]:  # Formato X.XXX-YYYY
                    metadatos['rol_cs_contenido'] = f"{grupos[0]}.{grupos[1]}-{grupos[2]}"
                else:
                    metadatos['rol_cs_contenido'] = f"{grupos[0]}-{grupos[-1]}"
            break

    # Buscar fecha
    for patron in PATRONES_CONTENIDO['fecha']:
        match = re.search(patron, texto)
        if match:
            grupos = match.groups()
            if len(grupos) == 3:
                dia, mes, año = grupos
                if mes.lower() in MESES:
                    mes = MESES[mes.lower()]
                try:
                    metadatos['fecha_contenido'] = f"{año}-{mes.zfill(2)}-{dia.zfill(2)}"
                except:
                    pass
            break

    # Buscar tipo de documento
    for patron in PATRONES_CONTENIDO['tipo_doc']:
        match = re.search(patron, texto)
        if match:
            tipo = match.group(1).lower()
            if 'sentencia' in tipo:
                metadatos['tipo_doc_contenido'] = 'Sentencia'
            elif 'resoluci' in tipo:
                metadatos['tipo_doc_contenido'] = 'Resolución'
            elif 'casaci' in tipo:
                metadatos['tipo_doc_contenido'] = 'Casación'
            elif 'informe' in tipo:
                metadatos['tipo_doc_contenido'] = 'Informe'
            break

    # Buscar tribunal
    for patron in PATRONES_CONTENIDO['tribunal']:
        match = re.search(patron, texto)
        if match:
            metadatos['tribunal'] = match.group(1)
            if 'Suprema' in match.group(1):
                metadatos['es_corte_suprema_contenido'] = True
            break

    return metadatos


def combinar_metadatos(meta_nombre, meta_contenido):
    """Combina metadatos del nombre y contenido, priorizando contenido."""
    resultado = {
        'tipo_caso': meta_contenido.get('tipo_caso_contenido') or meta_nombre.get('tipo_caso'),
        'rol': meta_contenido.get('rol_contenido') or meta_nombre.get('rol'),
        'año_rol': meta_contenido.get('año_rol_contenido') or meta_nombre.get('año_rol'),
        'fecha_sentencia': meta_contenido.get('fecha_contenido') or meta_nombre.get('fecha_sentencia'),
        'tipo_documento': meta_contenido.get('tipo_doc_contenido') or meta_nombre.get('tipo_documento'),
        'es_corte_suprema': meta_contenido.get('es_corte_suprema_contenido') or meta_nombre.get('es_corte_suprema'),
        'tribunal': meta_contenido.get('tribunal'),
        'roles_acumulados': meta_nombre.get('roles_acumulados', []),
        'fuente_datos': 'contenido' if meta_contenido.get('rol_contenido') else 'nombre',
        'es_informe': meta_nombre.get('es_informe', False),
        'rol_cs': meta_contenido.get('rol_cs_contenido') or meta_nombre.get('rol_cs'),
    }

    # Si hay roles múltiples en el contenido, agregarlos
    if meta_contenido.get('roles_multiples'):
        resultado['roles_acumulados'].extend(meta_contenido['roles_multiples'])

    # Actualizar es_corte_suprema si se encontró rol de CS
    if resultado['rol_cs']:
        resultado['es_corte_suprema'] = True

    return resultado


def procesar_archivos(limite=None):
    """Procesa todos los PDFs y genera inventario mejorado."""

    archivos = list(PDF_DIR.glob("**/*.pdf"))
    print(f"Total de archivos PDF: {len(archivos)}")

    if limite:
        archivos = archivos[:limite]
        print(f"Procesando primeros {limite} archivos...")

    resultados = []
    errores = []

    for i, archivo in enumerate(archivos):
        if (i + 1) % 20 == 0:
            print(f"  Procesando {i+1}/{len(archivos)}...")

        try:
            # Extraer del nombre
            meta_nombre = extraer_metadatos_nombre(archivo.name)

            # Extraer del contenido
            texto = extraer_texto_pdf(archivo)
            meta_contenido = extraer_metadatos_contenido(texto)

            # Combinar
            meta_final = combinar_metadatos(meta_nombre, meta_contenido)
            meta_final['archivo'] = archivo.name
            meta_final['ruta'] = str(archivo)
            meta_final['tamaño_mb'] = round(archivo.stat().st_size / (1024*1024), 2)
            meta_final['texto_muestra'] = meta_contenido.get('texto_muestra', '')[:200]

            # Determinar estado de clasificación
            if meta_final.get('es_informe'):
                # Informes en Derecho: OK si tienen rol asociado, sino categoría especial
                if meta_final['rol']:
                    meta_final['estado'] = 'OK_INFORME'
                else:
                    meta_final['estado'] = 'INFORME_SIN_ROL'
            elif meta_final.get('es_corte_suprema') and meta_final.get('rol_cs'):
                # Casaciones con rol de CS
                meta_final['estado'] = 'OK_CORTE_SUPREMA'
            elif not meta_final['rol'] or not meta_final['año_rol']:
                meta_final['estado'] = 'REVISION_MANUAL'
            elif meta_final['fuente_datos'] == 'nombre':
                meta_final['estado'] = 'OK_NOMBRE'
            else:
                meta_final['estado'] = 'OK_CONTENIDO'

            resultados.append(meta_final)

        except Exception as e:
            errores.append({'archivo': archivo.name, 'error': str(e)})

    return resultados, errores


def guardar_resultados(resultados, errores):
    """Guarda resultados en CSV."""

    # Inventario mejorado
    campos = ['archivo', 'estado', 'tipo_caso', 'rol', 'año_rol', 'fecha_sentencia',
              'tipo_documento', 'es_corte_suprema', 'rol_cs', 'es_informe', 'tribunal',
              'roles_acumulados', 'fuente_datos', 'tamaño_mb', 'texto_muestra']

    with open(OUTPUT_DIR / 'inventario_mejorado.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=campos, extrasaction='ignore')
        writer.writeheader()
        for r in resultados:
            row = r.copy()
            row['roles_acumulados'] = ';'.join(r.get('roles_acumulados', []))
            writer.writerow(row)

    print(f"\nGuardado: inventario_mejorado.csv")

    # Estadísticas
    total = len(resultados)
    ok_contenido = sum(1 for r in resultados if r['estado'] == 'OK_CONTENIDO')
    ok_nombre = sum(1 for r in resultados if r['estado'] == 'OK_NOMBRE')
    ok_cs = sum(1 for r in resultados if r['estado'] == 'OK_CORTE_SUPREMA')
    ok_informe = sum(1 for r in resultados if r['estado'] == 'OK_INFORME')
    informe_sin_rol = sum(1 for r in resultados if r['estado'] == 'INFORME_SIN_ROL')
    revision = sum(1 for r in resultados if r['estado'] == 'REVISION_MANUAL')

    clasificados = ok_contenido + ok_nombre + ok_cs + ok_informe

    print(f"\n{'='*50}")
    print("RESUMEN DE CLASIFICACION")
    print(f"{'='*50}")
    print(f"Total procesados:        {total}")
    print(f"OK (desde contenido):    {ok_contenido} ({100*ok_contenido/total:.1f}%)")
    print(f"OK (desde nombre):       {ok_nombre} ({100*ok_nombre/total:.1f}%)")
    print(f"OK (Corte Suprema):      {ok_cs} ({100*ok_cs/total:.1f}%)")
    print(f"OK (Informes):           {ok_informe} ({100*ok_informe/total:.1f}%)")
    print(f"Informes sin rol:        {informe_sin_rol}")
    print(f"Requieren revision:      {revision} ({100*revision/total:.1f}%)")
    print(f"{'='*50}")
    print(f"TOTAL CLASIFICADOS:      {clasificados} ({100*clasificados/total:.1f}%)")

    if errores:
        print(f"\nErrores: {len(errores)}")
        for e in errores[:5]:
            print(f"  - {e['archivo']}: {e['error']}")


if __name__ == "__main__":
    import sys

    limite = None
    if len(sys.argv) > 1:
        try:
            limite = int(sys.argv[1])
        except:
            pass

    print("Clasificador mejorado de PDFs del Tribunal Ambiental")
    print("=" * 50)

    resultados, errores = procesar_archivos(limite)
    guardar_resultados(resultados, errores)

    print("\n[OK] Proceso completado.")
