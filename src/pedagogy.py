"""Conteudo local com origem verificavel e edicoes individuais transacionais."""
import hashlib
import json
import os
import re
import threading
import uuid
from pathlib import Path
from src import settings, core, observability as obs

_lock = threading.RLock()
SOURCE = 'PARTES-PORFOLIO-2026.txt'


def source_path():
    return Path(os.environ.get('PORTFOLIO_CONTENT_FILE', settings.ROOT/SOURCE))


def parse_content(text):
    """Importa o formato da referencia, sem completar campos ausentes."""
    lines = text.lstrip('\ufeff').splitlines()
    fields, sections, notes = {}, {}, []

    def field(section, key, start, end, kind):
        while start < end and not lines[start].strip(): start += 1
        while end > start and not lines[end-1].strip(): end -= 1
        identifier = f'{section}.{key}'
        value = '\n'.join(lines[start:end])
        if not value:
            return
        fields[identifier] = dict(id=identifier, section=section, type=kind, text=value,
            origin=dict(start_line=start+1, end_line=end),
            personalization=[dict(token=token, field='student_name') for token in sorted(set(re.findall(r'_{6,}', value)))])

    starts = [(i, int(m[1])) for i, line in enumerate(lines)
              if (m := re.search(r'PROJETO (\d+)\s*$', line))]
    if [n for _, n in starts] != list(range(1, 11)):
        raise ValueError('Referencia deve conter projetos 1 a 10, em ordem.')
    summary = next((i for i, line in enumerate(lines) if 'ESSE É O MEU JEITO DE APRENDER' in line), None)
    ending = next((i for i, line in enumerate(lines) if 'ÚLTIMA PÁGINA' in line), None)
    if summary is None or ending is None: raise ValueError('Sintese ou encerramento ausente.')
    opening = next((i for i, line in enumerate(lines) if 'PORTFÓLIO INDIVIDUAL' in line), None)
    if opening is None: raise ValueError('Abertura ausente.')
    sections['GENERAL'] = dict(project_id=0, label='Abertura geral')
    field('GENERAL', 'heading', opening, opening+1, 'highlight')
    field('GENERAL', 'title', opening+1, opening+2, 'title')
    field('GENERAL', 'subtitle', opening+2, opening+3, 'subtitle')
    field('GENERAL', 'student_name', opening+3, opening+4, 'student_name')
    field('GENERAL', 'introduction', opening+4, starts[0][0], 'body_text')
    for ix, (start, number) in enumerate(starts):
        end = starts[ix+1][0] if ix+1 < len(starts) else summary
        if number == 10:
            end = next(i for i in range(start, summary) if 'E EU FARIA' in lines[i])
            notes.append(dict(start_line=end+1, end_line=summary, category='editorial'))
        section = f'P{number:02d}'
        sections[section] = dict(project_id=number, label=f'Projeto {number}')
        field(section, 'title', start+1, start+2, 'title')
        field(section, 'subtitle', start+2, start+3, 'subtitle')
        intro = next(i for i in range(start+3, end) if lines[i].startswith('ABERTURA'))
        if intro > start+3:
            notes.append(dict(start_line=start+4, end_line=intro, category='editorial'))
        call = next(i for i in range(intro+1, end) if lines[i].startswith('🌟'))
        field(section, 'introduction', intro+1, call, 'body_text')
        field(section, 'individual_call', call, call+1, 'highlight')
        photos = [i for i in range(call+1, end) if lines[i].startswith('📸 FOTO')]
        if len(photos) != 2: raise ValueError('Projeto deve indicar duas fotografias.')
        for p, photo in enumerate(photos, 1):
            stop = photos[p] if p < len(photos) else end
            line = lines[photo]
            if ':' in line:
                # Descricao e instrucao fotografica, nunca legenda automatica.
                desc = line.split(':', 1)[1].lstrip()
                fields[f'{section}.evidence_{p}'] = dict(id=f'{section}.evidence_{p}', section=section,
                    type='evidence_description', text=desc, origin=dict(start_line=photo+1,end_line=photo+1),
                    requirement_id=f'{number:02d}-{p}', personalization=[])
                caption_start = photo+1
            else:
                desc_line = next(i for i in range(photo+1, stop) if lines[i].strip())
                field(section, f'evidence_{p}', desc_line, desc_line+1, 'evidence_description')
                fields[f'{section}.evidence_{p}']['requirement_id'] = f'{number:02d}-{p}'
                caption_start = desc_line+1
            highlight = next((i for i in range(caption_start, stop) if lines[i].startswith('“') or 'PEQUENA FRASE' in lines[i]), stop)
            if highlight < stop:
                quote = highlight+1 if 'PEQUENA FRASE' in lines[highlight] else highlight
                field(section, 'highlight', quote, stop, 'highlight')
            caption_lines = [i for i in range(caption_start, highlight) if lines[i].strip() and lines[i] != 'Legenda:']
            if caption_lines:
                field(section, f'caption_{p}', caption_lines[0], caption_lines[-1]+1, 'caption')
        sections[section]['missing'] = [key for key in ('caption_1','caption_2','highlight') if f'{section}.{key}' not in fields]
    sections['SYNTHESIS'] = dict(project_id=11, label='Síntese individual')
    field('SYNTHESIS', 'title', summary, summary+1, 'title')
    field('SYNTHESIS', 'evidence_description', summary+1, summary+2, 'evidence_description')
    individual = next(i for i in range(summary, ending) if lines[i] == 'E um texto individual:')
    notes.append(dict(start_line=summary+2, end_line=individual+1, category='editorial'))
    field('SYNTHESIS', 'introduction', individual+1, ending, 'body_text')
    sections['ENDING'] = dict(project_id=12, label='Encerramento')
    field('ENDING', 'title', ending+1, ending+2, 'title')
    field('ENDING', 'evidence_1', ending+2, ending+3, 'evidence_description')
    fields['ENDING.evidence_1']['requirement_id']='12-1'
    notes.append(dict(start_line=ending+3, end_line=ending+3, category='editorial'))
    quote = next(i for i in range(ending+2, len(lines)) if lines[i].startswith('“'))
    field('ENDING', 'introduction', quote, len(lines), 'body_text')
    return dict(schema_version=1, source=dict(file=SOURCE, sha256=hashlib.sha256(text.encode('utf-8')).hexdigest()),
                sections=sections, fields=fields, editorial_notes=notes)


def catalog_path():
    root = settings.ROOT if settings.DATA == settings.ROOT/'data' else settings.DATA
    return root/'config/conteudo_pedagogico_2026.json'


def import_catalog():
    """Snapshot imutavel por hash; publicar novo catalogo nao altera edicoes."""
    with _lock:
        original = source_path().read_bytes()
        raw = original.decode('utf-8-sig')
        catalog = parse_content(raw)
        catalog['source']['sha256'] = hashlib.sha256(original).hexdigest()
        target = catalog_path()
        target.parent.mkdir(parents=True, exist_ok=True)
        history = target.parent/'pedagogy_versions'
        history.mkdir(exist_ok=True)
        content = json.dumps(catalog, ensure_ascii=False, indent=2)
        snapshot = history/(catalog['source']['sha256']+'.json')
        if not snapshot.exists():
            with snapshot.open('x', encoding='utf-8') as stream:
                stream.write(content); stream.flush(); os.fsync(stream.fileno())
        temporary = target.with_suffix('.'+uuid.uuid4().hex+'.tmp')
        with temporary.open('x', encoding='utf-8') as stream:
            stream.write(content); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, target)
        return catalog


def load_catalog():
    path = catalog_path()
    if not path.exists(): return import_catalog()
    catalog = json.loads(path.read_text(encoding='utf-8'))
    if catalog.get('schema_version') != 1: raise ValueError('Catalogo nao suportado.')
    return catalog


def section_for(project_id, catalog=None):
    catalog = catalog or load_catalog()
    return next((key for key, value in catalog['sections'].items() if value['project_id'] == project_id), None)


def text_fields(project_id, catalog=None):
    catalog = catalog or load_catalog()
    section = section_for(project_id, catalog)
    return {key: value for key, value in catalog['fields'].items()
            if value['section'] == section and value['type'] != 'evidence_description'}


def field_label(field_id):
    key=field_id.split('.')[-1]
    labels={'title':'Título','subtitle':'Subtítulo / tema','introduction':'Abertura / apresentação',
            'individual_call':'Chamada da criança','highlight':'Frase de destaque',
            'heading':'Cabeçalho','student_name':'Nome da criança'}
    if key.startswith('caption_'): return 'Legenda da foto '+key.split('_')[-1]
    return labels.get(key,key)


def field_group(field_id):
    key=field_id.split('.')[-1]
    if key in ('title','subtitle','heading','introduction'): return 'Apresentação do projeto'
    if key.startswith('caption_'): return 'Legendas das fotos'
    return 'Chamada e destaques'


def initialize():
    with core.connection() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS pedagogical_edits(
            id INTEGER PRIMARY KEY, field_id TEXT NOT NULL, student_id INTEGER REFERENCES students(id),
            text TEXT, source_hash TEXT NOT NULL, created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)''')
        db.execute('CREATE INDEX IF NOT EXISTS pedagogy_field_scope ON pedagogical_edits(field_id,student_id,id)')


def current_edit(field_id, student_id=None):
    with core.connection() as db:
        if not db.execute("SELECT 1 FROM sqlite_master WHERE name='pedagogical_edits'").fetchone(): return None
        row = db.execute('SELECT * FROM pedagogical_edits WHERE field_id=? AND student_id IS ? ORDER BY id DESC LIMIT 1',
                         (field_id, student_id)).fetchone()
        return dict(row) if row else None


@obs.operation
def save_text(field_id, text, student_id=None, expected_revision=None):
    catalog = load_catalog()
    if field_id not in catalog['fields'] or catalog['fields'][field_id]['type'] == 'evidence_description':
        raise ValueError('Campo de texto inexistente.')
    if text is not None and (not isinstance(text, str) or len(text) > 10000): raise ValueError('Texto invalido.')
    if student_id is not None and (type(student_id) is not int or not core.rows('SELECT id FROM students WHERE id=?',(student_id,))):
        raise ValueError('Aluno inexistente.')
    initialize()
    with core.connection() as db:
        revision = db.execute('SELECT MAX(id) FROM pedagogical_edits WHERE field_id=? AND student_id IS ?', (field_id,student_id)).fetchone()[0] or 0
        if expected_revision is not None and expected_revision != revision: raise ValueError('Texto alterado; reabra antes de salvar.')
        cursor = db.execute('INSERT INTO pedagogical_edits(field_id,student_id,text,source_hash) VALUES (?,?,?,?)',
                           (field_id,student_id,text,catalog['source']['sha256']))
        core.audit(db,'pedagogical_text_saved',cursor.lastrowid)


def resolve_text(field_id, student_id=None, catalog=None):
    catalog = catalog or load_catalog()
    if field_id not in catalog['fields']: raise ValueError('Campo inexistente.')
    original = catalog['fields'][field_id]['text']
    global_edit = current_edit(field_id)
    individual = current_edit(field_id,student_id) if student_id is not None else None
    if individual and individual['text'] is not None: return individual['text'], 'individual'
    if global_edit and global_edit['text'] is not None: return global_edit['text'], 'global'
    return original, 'original'


def history(field_id, student_id=None):
    initialize()
    return core.rows('SELECT id,text,created FROM pedagogical_edits WHERE field_id=? AND student_id IS ? ORDER BY id DESC', (field_id,student_id))


def personalize(text, name):
    return re.sub(r'_{6,}', lambda match: name, text) if name else text
