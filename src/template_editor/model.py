"""Modelo e persistência local dos templates. Nenhuma escrita no banco do MVP 1."""
import copy
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import uuid
import threading
import warnings
from PIL import Image, ImageDraw, ImageOps
from src import settings, core, observability as obs
from src import pedagogy
from src.rendering import typography

_save_lock=threading.RLock()

TYPES = ('photo','title','subtitle','body_text','caption','highlight','student_name')


def template_dir():
    return settings.DATA / 'templates'


def asset_dir():
    return (settings.ROOT/'assets' if settings.DATA==settings.ROOT/'data' else settings.DATA/'assets')


def background_path(value):
    if not isinstance(value,str) or not re.fullmatch(r'backgrounds/[0-9a-f]{64}\.(png|jpg|webp)',value):
        raise ValueError('Referência de fundo inválida.')
    root=asset_dir().resolve()
    target=(root/value).resolve()
    if not target.is_relative_to(root):
        raise ValueError('Caminho de fundo inválido.')
    return target


@obs.operation
def import_background(content):
    if not content or len(content)>settings.MAX_BYTES:
        raise ValueError('Use imagem de até 30 MB.')
    with warnings.catch_warnings():
        warnings.simplefilter('error',Image.DecompressionBombWarning)
        try:
            with Image.open(io.BytesIO(content)) as im:
                if im.format not in ('PNG','JPEG','WEBP'):
                    raise ValueError('Formato incompatível.')
                extension={'PNG':'png','JPEG':'jpg','WEBP':'webp'}[im.format]
                raw_size=im.size
                im.verify()
            with Image.open(io.BytesIO(content)) as im:
                oriented=ImageOps.exif_transpose(im)
                oriented.load()
                size=oriented.size
                if size[0]*size[1]>40_000_000:
                    raise ValueError('Imagem excede 40 megapixels.')
        except (OSError,SyntaxError,Image.DecompressionBombError,Image.DecompressionBombWarning) as exc:
            raise ValueError('Imagem inválida ou insegura.') from exc
    digest=hashlib.sha256(content).hexdigest()
    relative=f'backgrounds/{digest}.{extension}'
    path=background_path(relative)
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        if hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
            raise ValueError('Falha de integridade no fundo.')
    else:
        with path.open('xb') as stream: stream.write(content)
    return dict(file=relative,width=size[0],height=size[1],raw_width=raw_size[0],raw_height=raw_size[1])


def new_template(background,project_id,name):
    return dict(id=uuid.uuid4().hex,schema_version=2,version=0,name=name,project_id=project_id,
                background=copy.deepcopy(background),regions=[],module_order=0,overlap=0,transition={'mode':'none'})


def fill_project_texts(template):
    """Acrescenta vinculos ausentes no rascunho sem substituir conteudo existente."""
    draft=copy.deepcopy(template)
    fields=pedagogy.text_fields(draft['project_id'],pedagogy.load_catalog())
    regions=draft['regions']
    messages=[]
    targets=[(key,field,None) for key,field in fields.items()
             if key.endswith(('.title','.introduction'))]
    photo_requirements=set()
    for photo in list(regions):
        if photo['type']!='photo': continue
        req=resolve_requirement(photo['source']['requirement_id'])['id']
        if req in photo_requirements:
            messages.append(f'{req}: mais de uma regiao de foto usa o mesmo requisito. Confira o Requisito pedagogico de cada foto; a legenda segue esse vinculo.')
        photo_requirements.add(req)
        number=int(req.split('-')[1])
        for key,field in fields.items():
            if key.endswith(f'.caption_{number}'):
                targets.append((key,field,photo))
    for key,field,photo in targets:
        kind=field['type']
        if any(r['source'].get('field_id')==key and r['source'].get('kind')=='pedagogical' for r in regions): continue
        if kind=='title' and any(r['source'].get('kind')=='project_title' for r in regions): continue
        # Texto literal preenchido e qualquer vinculo existente ficam intactos.
        empty=next((r for r in regions if r['type']==kind and r['source'].get('kind')=='literal'
                    and not r['source'].get('text','').strip()),None)
        if empty:
            empty['source']={'kind':'pedagogical','field_id':key}
            continue
        if kind!='caption' and any(r['type']==kind for r in regions): continue
        w=photo['width'] if photo else .9
        style=typography.preset(kind)
        h=.08 if kind=='title' else .19
        if photo:
            text,_=pedagogy.resolve_text(key,None)
            face=typography.font(style['font_size'],style['font_family'],style['weight'])
            pen=ImageDraw.Draw(Image.new('RGB',(1,1)))
            lines=typography.layout(text,pen,face,max(1,round(w*1080)-2*style['padding']),True,0)
            ascent,descent=face.getmetrics()
            line_height=max(ascent+descent,round(style['font_size']*style['line_height']))
            h=max(.04,(len(lines)*line_height+2*style['padding']+2)/(1080*draft['background']['height']/draft['background']['width']))
        x=photo['x'] if photo else .05
        preferred=photo['y']+photo['height']+.008 if photo else (.025 if kind=='title' else .12)
        candidates=[preferred]+[i/100 for i in range(2,98,2)]
        def available(x,y):
            return x+w<=.99 and y+h<=.99 and all(x+w<=r['x'] or r['x']+r['width']<=x or
                y+h<=r['y'] or r['y']+r['height']<=y for r in regions)
        positions=[(x,y) for y in candidates]+[(i/100,y) for y in candidates for i in range(2,98,2)]
        position=next(((x,y) for x,y in positions if available(x,y)),None)
        if position is None or len(regions)>=100:
            messages.append(f'{key}: sem espaco livre; ajuste as regioes e tente novamente.')
            continue
        x,y=position
        regions.append(dict(id=uuid.uuid4().hex,type=kind,x=x,y=y,width=w,height=h,
            source={'kind':'pedagogical','field_id':key},text_style=style))
    validate_template(draft)
    return draft,messages


def normalized_box(x,y,width,height,image_width,image_height):
    if image_width<=0 or image_height<=0:
        raise ValueError('Dimensões de imagem inválidas.')
    result=dict(x=x/image_width,y=y/image_height,width=width/image_width,height=height/image_height)
    validate_box(result)
    return result


def validate_box(box):
    for key in ('x','y','width','height'):
        value=box.get(key)
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
            raise ValueError('Coordenadas inválidas.')
    if min(box['x'],box['y'])<0 or min(box['width'],box['height'])<=0 or box['x']+box['width']>1.000001 or box['y']+box['height']>1.000001:
        raise ValueError('Região fora dos limites da imagem.')


def resolve_requirement(value):
    if not isinstance(value,str): raise ValueError('Requisito inválido.')
    match=re.fullmatch(r'P(\d{2})_F(\d{2})',value)
    canonical=f'{int(match[1]):02d}-{int(match[2])}' if match else value
    rows=core.rows('SELECT id,project_id FROM requirements WHERE id=?',(canonical,))
    if not rows: raise ValueError('Requisito pedagógico inexistente.')
    return rows[0]


def validate_template(template):
    if not isinstance(template,dict) or not re.fullmatch(r'[a-f0-9]{32}',str(template.get('id',''))):
        raise ValueError('Identificador de template inválido.')
    if template.get('schema_version') not in (1,2): raise ValueError('Versão de esquema não suportada.')
    if type(template.get('version')) is not int or template['version']<0: raise ValueError('Versão inválida.')
    if not isinstance(template.get('name'),str) or not 1<=len(template['name'].strip())<=120: raise ValueError('Informe um nome de até 120 caracteres.')
    if template.get('project_id')!=0 and not core.rows('SELECT id FROM projects WHERE id=?',(template.get('project_id'),)): raise ValueError('Projeto inexistente.')
    background=template.get('background',{})
    path=background_path(background.get('file'))
    with Image.open(path) as im:
        size=ImageOps.exif_transpose(im).size
    if tuple(background.get(k) for k in ('width','height'))!=size: raise ValueError('Dimensões do fundo divergentes.')
    regions=template.get('regions')
    if not isinstance(regions,list) or len(regions)>100: raise ValueError('Máximo de 100 regiões.')
    seen=set()
    for region in regions:
        if not isinstance(region,dict): raise ValueError('Região inválida.')
        rid=region.get('id','')
        if not isinstance(rid,str) or not re.fullmatch(r'[a-zA-Z0-9_-]{1,80}',rid) or rid in seen: raise ValueError('ID de região inválido ou repetido.')
        seen.add(rid)
        if region.get('type') not in TYPES: raise ValueError('Tipo de região inválido.')
        validate_box(region)
        source=region.get('source',{})
        if not isinstance(source,dict): raise ValueError('Origem inválida.')
        if region['type']=='photo':
            requirement=resolve_requirement(source.get('requirement_id',''))
            if requirement['project_id']!=template['project_id']: raise ValueError('Foto deve pertencer ao projeto do template.')
            if region.get('fit','contain') not in ('contain','cover'): raise ValueError('Enquadramento inválido.')
            for key in ('focus_x','focus_y'):
                value=region.get(key,.5)
                if type(value) not in (int,float) or not math.isfinite(value) or not 0<=value<=1: raise ValueError('Foco inválido.')
        elif source.get('kind') == 'pedagogical':
            field=pedagogy.text_fields(template['project_id']).get(source.get('field_id'))
            if not field: raise ValueError('Campo pedagógico não pertence ao projeto.')
        elif source.get('kind') not in ('literal','student_name','project_title'):
            raise ValueError('Origem de texto inválida.')
        if not isinstance(source.get('text',''),str) or len(source.get('text',''))>10000: raise ValueError('Texto muito longo ou inválido.')
        style=region.get('text_style',{})
        if not isinstance(style,dict): raise ValueError('Estilo inválido.')
        typography.validate(style)
        size=style.get('font_size',32)
        if type(size) not in (int,float) or not math.isfinite(size) or not 8<=size<=200: raise ValueError('Fonte fora dos limites.')
        if style.get('align','left') not in ('left','center','right') or not re.fullmatch(r'#[0-9a-fA-F]{6}',style.get('color','#243442')): raise ValueError('Estilo de texto inválido.')
    return template


def _latest_path(identifier):
    if not re.fullmatch(r'[a-f0-9]{32}',str(identifier)): raise ValueError('ID inválido.')
    root=template_dir().resolve()
    target=(root/(identifier+'.json')).resolve()
    if not target.is_relative_to(root): raise ValueError('Caminho inválido.')
    return target


@obs.operation
def save_template(template):
    with _save_lock:
        validate_template(template)
        path=_latest_path(template['id'])
        path.parent.mkdir(parents=True,exist_ok=True)
        if path.exists():
            current=json.loads(path.read_text(encoding='utf-8'))
            if current['version']!=template['version']: raise ValueError('Template foi alterado. Reabra antes de salvar.')
        elif template['version']!=0: raise ValueError('Template de origem não encontrado.')
        saved=copy.deepcopy(template)
        saved['schema_version']=2  # Migracao aditiva; versoes antigas permanecem intactas.
        history=path.parent/'versions'
        history.mkdir(exist_ok=True)
        revisions=[]
        for entry in history.glob(template['id']+'.v*.json'):
            match=re.fullmatch(template['id']+r'\.v(\d+)\.json',entry.name)
            if match: revisions.append(int(match[1]))
        saved['version']=max([template['version']]+revisions)+1
        snapshot=history/f"{saved['id']}.v{saved['version']}.json"
        content=json.dumps(saved,ensure_ascii=False,indent=2,allow_nan=False)
        if len(content.encode('utf-8'))>2_000_000: raise ValueError('Template muito grande.')
        temporary=path.with_suffix('.'+uuid.uuid4().hex+'.tmp')
        with temporary.open('x',encoding='utf-8') as stream:
            stream.write(content);stream.flush();os.fsync(stream.fileno())
        # Link exclusivo publica somente um snapshot completo; NTFS oferece suporte.
        # Em falha posterior, a revisão fica preservada e uma nova tentativa usa outro número.
        os.link(temporary,snapshot)
        os.replace(temporary,path)
        obs.emit('template_saved','save_template')
        return saved


@obs.operation
def load_template(identifier):
    path=_latest_path(identifier)
    if path.stat().st_size>2_000_000: raise ValueError('Template muito grande.')
    template=json.loads(path.read_text(encoding='utf-8'))
    if template.get('id')!=identifier: raise ValueError('Identificador divergente.')
    return validate_template(template)


@obs.operation
def list_templates():
    result=[]
    for path in sorted(template_dir().glob('*.json')):
        if re.fullmatch(r'[a-f0-9]{32}',path.stem):
            result.append(path.stem)
    return result
