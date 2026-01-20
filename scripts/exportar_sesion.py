#!/usr/bin/env python3
"""
Script para exportar el histórico de la sesión 85b11f01
"""
import json
import sys
from collections import Counter
from datetime import datetime

file_path = 'C:/Users/fabia/.claude/projects/g--Mi-unidad-tribunal-pdf/85b11f01-b69d-47dd-b3cc-f076a3624f7d.jsonl'
output_path = 'G:/Mi unidad/tribunal_pdf/HISTORICO_SESION_85b11f01.md'

# Recopilar toda la información
all_user_msgs = []
all_tools = []
all_files_edited = []
all_files_read = []
summaries = []
segments_data = []

current = {'msgs': [], 'tools': [], 'files_w': [], 'files_r': [], 't0': None, 't1': None}
line_num = 0

print("Leyendo archivo de sesión...")
with open(file_path, 'r', encoding='utf-8') as f:
    for line in f:
        line_num += 1
        try:
            data = json.loads(line)

            if data.get('type') == 'summary':
                summaries.append(data.get('summary', ''))

            ts = data.get('timestamp', '')
            if ts and not current['t0']:
                current['t0'] = ts
            if ts:
                current['t1'] = ts

            msg = data.get('message', {})

            if msg.get('role') == 'user':
                content = msg.get('content', '')
                if isinstance(content, str) and len(content) > 5:
                    if not content.startswith(('/', 'This session', 'Caveat:', '<')):
                        current['msgs'].append({'ts': ts, 'msg': content})
                        all_user_msgs.append({'ts': ts, 'msg': content})

            if msg.get('role') == 'assistant':
                content = msg.get('content', [])
                if isinstance(content, list):
                    for c in content:
                        if c.get('type') == 'tool_use':
                            tool = c.get('name', '')
                            inp = c.get('input', {})
                            current['tools'].append(tool)
                            all_tools.append(tool)

                            if tool in ['Edit', 'Write']:
                                fp = inp.get('file_path', '')
                                if fp:
                                    parts = fp.replace('\\', '/').split('/')
                                    fname = parts[-1]
                                    current['files_w'].append(fname)
                                    all_files_edited.append(fp)

                            if tool == 'Read':
                                fp = inp.get('file_path', '')
                                if fp:
                                    current['files_r'].append(fp.replace('\\', '/').split('/')[-1])
                                    all_files_read.append(fp)
        except:
            pass

        if line_num % 325 == 0:
            segments_data.append(current)
            current = {'msgs': [], 'tools': [], 'files_w': [], 'files_r': [], 't0': None, 't1': None}

if current['msgs'] or current['tools']:
    segments_data.append(current)

print(f"Procesadas {line_num} líneas")

# Generar el markdown
output = []
output.append('# Histórico de Sesión: Proyecto Tribunal Ambiental')
output.append('')
output.append('**Session ID:** `85b11f01-b69d-47dd-b3cc-f076a3624f7d`')
output.append('**Período:** 7 enero 2026 04:47 - 9 enero 2026 18:01')
output.append('**Archivo original:** 645 MB, 3,245 eventos')
output.append('')
output.append('---')
output.append('')
output.append('## Resumen Ejecutivo')
output.append('')
output.append('Esta sesión abarcó el desarrollo completo del proyecto de corpus del Tribunal Ambiental de Chile:')
output.append('')
output.append('1. **Transcripción de PDFs** usando visión de Claude (MLLM)')
output.append('2. **Descarga y organización** de documentos de los 3 tribunales')
output.append('3. **Creación de 3 papers** académicos')
output.append('')
output.append('---')
output.append('')
output.append('## Estadísticas de la Sesión')
output.append('')
output.append('| Métrica | Valor |')
output.append('|---------|-------|')
output.append(f'| Mensajes del usuario | {len(all_user_msgs)} |')
output.append(f'| Uso de herramientas | {len(all_tools)} |')
output.append(f'| Archivos editados/creados | {len(set(all_files_edited))} |')
output.append(f'| Archivos leídos | {len(set(all_files_read))} |')
output.append(f'| Resúmenes de contexto | {len(summaries)} |')
output.append('')

# Herramientas más usadas
tool_counts = Counter(all_tools).most_common(10)
output.append('### Herramientas más usadas')
output.append('')
output.append('| Herramienta | Usos |')
output.append('|-------------|------|')
for tool, count in tool_counts:
    output.append(f'| {tool} | {count} |')
output.append('')

output.append('---')
output.append('')
output.append('## Cronología por Segmentos')
output.append('')

segment_titles = [
    'Transcripción MLLM de Solicitudes (2013-2016)',
    'Transcripción MLLM de Solicitudes (2016-2023)',
    'Organización y dudas sobre duplicados',
    'Problemas con límite de tokens',
    'Consolidación del corpus',
    'Descarga completa y comparación',
    'Extracción de Tribunales 1 y 3',
    'Fuentes adicionales (SNIFA, SEIA) + Inicio Paper',
    'Cifras oficiales y tipos de documentos',
    'Desarrollo de 3 papers en paralelo'
]

for i, seg in enumerate(segments_data):
    t0 = seg['t0'][:16].replace('T', ' ') if seg['t0'] else '?'
    t1 = seg['t1'][:16].replace('T', ' ') if seg['t1'] else '?'
    title = segment_titles[i] if i < len(segment_titles) else 'Continuación'

    output.append(f'### Segmento {i+1}: {title}')
    output.append(f'**Período:** {t0} → {t1}')
    output.append('')

    if seg['msgs']:
        output.append('**Conversación:**')
        for m in seg['msgs']:
            ts_short = m['ts'][11:16] if m['ts'] else ''
            msg_clean = m['msg'][:150].replace('\n', ' ')
            output.append(f'- [{ts_short}] {msg_clean}')
        output.append('')

    if seg['files_w']:
        unique = list(set(seg['files_w']))
        output.append(f'**Archivos creados/editados ({len(unique)}):** ')
        if len(unique) <= 15:
            output.append(', '.join(unique))
        else:
            output.append(', '.join(unique[:15]) + f' ... y {len(unique)-15} más')
        output.append('')

    top_tools = Counter(seg['tools']).most_common(3)
    if top_tools:
        tools_str = ', '.join([f'{t}({n})' for t,n in top_tools])
        output.append(f'**Herramientas:** {tools_str}')

    output.append('')
    output.append('---')
    output.append('')

# Archivos creados
output.append('## Archivos Principales Creados')
output.append('')

# Agrupar por tipo
all_files_names = [f.replace('\\', '/').split('/')[-1] for f in set(all_files_edited)]
scripts = sorted([f for f in all_files_names if f.endswith('.py')])
docs = sorted([f for f in all_files_names if f.endswith('.md')])
txts = sorted([f for f in all_files_names if f.endswith('.txt')])

output.append('### Scripts Python')
output.append('')
for f in scripts:
    output.append(f'- `{f}`')
output.append('')

output.append('### Documentos Markdown')
output.append('')
for f in docs:
    output.append(f'- `{f}`')
output.append('')

output.append('### Transcripciones TXT')
output.append(f'Total: {len(txts)} archivos de transcripción')
output.append('')
for f in txts[:20]:
    output.append(f'- `{f}`')
if len(txts) > 20:
    output.append(f'- ... y {len(txts)-20} más')
output.append('')

# Mensajes completos del usuario
output.append('---')
output.append('')
output.append('## Todos los Mensajes del Usuario (75 mensajes)')
output.append('')
for i, m in enumerate(all_user_msgs, 1):
    ts = m['ts'][:16].replace('T', ' ') if m['ts'] else '?'
    msg = m['msg'].replace('\n', ' ')[:200]
    output.append(f'{i:2}. **[{ts}]** {msg}')
    output.append('')

output.append('---')
output.append('')
output.append('## Decisiones Clave Tomadas')
output.append('')
output.append('1. **Consolidar transcripciones** en una sola carpeta (`corpus/textos/`)')
output.append('2. **Mantener respaldos** con prefijo `_RESPALDO_`')
output.append('3. **Descargar de los 3 tribunales** (no solo el 2TA)')
output.append('4. **Separar en 3 papers:**')
output.append('   - Paper 1: Cifras oficiales')
output.append('   - Paper 2: Corpus (data paper)')
output.append('   - Paper 3: Análisis de litigación')
output.append('5. **Usar PyMuPDF** para PDFs con texto, **visión Claude** para PDFs escaneados')
output.append('')
output.append('---')
output.append('')
output.append('## Productos Finales')
output.append('')
output.append('| Producto | Archivo | Estado |')
output.append('|----------|---------|--------|')
output.append('| Paper 1 | `paper/paper1_cifras_oficiales.md` | ✅ Completo |')
output.append('| Paper 2 | `paper/paper2_corpus.md` | ✅ Completo |')
output.append('| Paper 3 | `paper/paper3_analisis.md` | ✅ Completo |')
output.append('| Corpus PDFs | `corpus/descarga_completa/` | ✅ 3,749 docs |')
output.append('| Transcripciones | `corpus/textos/` | ✅ 308 archivos |')
output.append('| Cifras oficiales | `datos/CIFRAS_OFICIALES.md` | ✅ Completo |')
output.append('')
output.append('---')
output.append('')
output.append(f'*Archivo generado el {datetime.now().strftime("%Y-%m-%d %H:%M")}*')
output.append('')
output.append('*Este histórico fue recuperado del archivo de sesión de Claude Code después de que la sesión original se perdió al reiniciar el PC.*')

# Guardar
with open(output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print(f"Archivo guardado: {output_path}")
print(f"Total líneas generadas: {len(output)}")
