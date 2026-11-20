import copy
import io
import json
from pathlib import Path
import pytest
from PIL import Image
from test_core import local,picture,student
from src import core,settings
from src.template_editor import model
from src.rendering.preview import fit_photo,render_preview


def background(size=(400,1200)):
    output=io.BytesIO();Image.new('RGB',size,'white').save(output,format='PNG');return output.getvalue()


def template(local):
    bg=model.import_background(background())
    result=model.new_template(bg,4,'TEMPLATE SINTETICO')
    result['regions']=[dict(id='photo1',type='photo',x=.1,y=.1,width=.8,height=.2,source={'kind':'approved_photo','requirement_id':'P04_F01'},fit='contain',focus_x=.5,focus_y=.5,text_style={'font_size':32,'color':'#000000','align':'left'})]
    return result


def test_roundtrip_and_versioning(local):
    original=template(local)
    original['future_data']={'module':'preserved'}
    saved=model.save_template(original)
    assert saved['version']==1 and original['version']==0
    loaded=model.load_template(saved['id'])
    assert loaded==saved and model.list_templates()==[saved['id']]
    loaded['regions'][0]['fit']='cover'
    saved2=model.save_template(loaded)
    assert saved2['version']==2 and saved2['future_data']==original['future_data']
    assert len(list((model.template_dir()/'versions').glob('*.json')))==2
    with pytest.raises(ValueError):model.save_template(saved)
    assert model.load_template(saved['id'])==saved2


def test_normalized_coordinates_and_bounds(local):
    assert model.normalized_box(40,120,80,240,400,1200)==dict(x=.1,y=.1,width=.2,height=.2)
    for box in [dict(x=-.1,y=0,width=.1,height=.1),dict(x=.9,y=0,width=.2,height=.1),dict(x=0,y=0,width=0,height=.1),dict(x=float('nan'),y=0,width=.1,height=.1)]:
        with pytest.raises(ValueError): model.validate_box(box)
    for dimensions in [(0,1),(1,0)]:
        with pytest.raises(ValueError):model.normalized_box(0,0,1,1,*dimensions)


def test_background_original_and_path_protection(local):
    content=background((800,300));bg=model.import_background(content)
    assert model.background_path(bg['file']).read_bytes()==content
    assert (bg['width'],bg['height'])==(800,300)
    assert model.import_background(content)==bg
    for value in ['../../outside.png','backgrounds/../../x.png','/tmp/a.png']:
        with pytest.raises(ValueError):model.background_path(value)
    with pytest.raises(ValueError):model.import_background(b'not an image')
    with pytest.raises(ValueError):model.load_template('../outside')


def test_pedagogical_association(local):
    data=template(local)
    assert model.resolve_requirement('P04_F01')['id']=='04-1'
    assert model.resolve_requirement('04-2')['project_id']==4
    with pytest.raises(ValueError):model.resolve_requirement('P99_F01')
    data['regions'][0]['source']['requirement_id']='P03_F01'
    with pytest.raises(ValueError):model.validate_template(data)


@pytest.mark.parametrize('size',[(400,1200),(1000,300),(600,600)])
def test_preview_variable_proportion(local,size):
    data=model.new_template(model.import_background(background(size)),4,'SINTETICO')
    result,_=render_preview(data,width=400)
    assert result.size==(400,round(400*size[1]/size[0]))


@pytest.mark.parametrize('size',[(100,300),(300,100),(200,200)])
def test_photo_contain_cover_preserves_original(local,size):
    photo=Image.new('RGB',size,'red');original=photo.tobytes()
    contained=fit_photo(photo,(200,200),'contain')
    bbox=contained.getbbox()
    assert abs((bbox[2]-bbox[0])/(bbox[3]-bbox[1])-size[0]/size[1])<.02
    assert fit_photo(photo,(200,200),'cover').size==(200,200)
    assert photo.tobytes()==original and photo.size==size


def test_real_preview_only_approved(local):
    data=template(local);sid=student(local)
    photo=io.BytesIO();Image.new('RGB',(100,100),'red').save(photo,format='PNG')
    pid,_=core.import_photo(photo.getvalue(),'synthetic.png');core.associate(pid,sid,'04-1')
    missing,warnings=render_preview(data,sid,width=400)
    assert any('AUSENTE' in s for s in warnings)
    eid=core.rows('SELECT id FROM evidence')[0]['id']
    core.review(eid,'Aprovada')
    approved,warnings=render_preview(data,sid,width=400)
    assert not warnings
    assert approved.getpixel((200,240))==(255,0,0)
    assert core.photo_path(core.rows('SELECT path FROM photos')[0]['path']).read_bytes()==photo.getvalue()
    core.review(eid,'Rejeitada')
    assert any('AUSENTE' in s for s in render_preview(data,sid,width=400)[1])
    assert core.progress(sid)[0]['aprovadas']==0


def test_text_and_missing_evidence_synthetic(local):
    data=template(local)
    data['regions'].append(dict(id='name',type='student_name',x=.1,y=.5,width=.8,height=.05,source={'kind':'student_name'},text_style={'font_size':32,'color':'#000000','align':'center'}))
    image,messages=render_preview(data,width=400)
    assert any('SINTÉTICA' in s for s in messages)
    assert core.rows('SELECT COUNT(*) n FROM evidence')[0]['n']==0


def test_saved_template_corruption(local):
    saved=model.save_template(template(local))
    path=model.template_dir()/(saved['id']+'.json')
    path.write_text('{invalid',encoding='utf-8')
    with pytest.raises(ValueError):model.load_template(saved['id'])


def test_all_text_types_and_overflow(local):
    data=template(local)
    for i,kind in enumerate(['title','body_text','caption','student_name']):
        data['regions'].append(dict(id='text'+str(i),type=kind,x=.1,y=.4+i*.1,width=.8,height=.05,source={'kind':'literal','text':'Texto demonstrativo sem afirmação pedagógica. '*50},text_style={'font_size':30,'color':'#123456','align':'left'}))
    _,messages=render_preview(data,width=400)
    assert sum('cortado' in message for message in messages)==4


def test_editor_failure_logged_without_external_content(local):
    from src import observability as obs
    obs.configure()
    with pytest.raises(ValueError):model.import_background(b'NOME SINTETICO PRIVADO')
    errors=(obs.log_dir()/'errors.log').read_text(encoding='utf-8')
    assert 'import_background' in errors and 'PRIVADO' not in errors


def test_save_failure_preserves_previous_and_can_retry(local,monkeypatch):
    first=model.save_template(template(local))
    original=model.os.replace
    def fail(*args):raise OSError('falha sintetica de gravacao')
    monkeypatch.setattr(model.os,'replace',fail)
    with pytest.raises(OSError):model.save_template(first)
    assert model.load_template(first['id'])==first
    monkeypatch.setattr(model.os,'replace',original)
    retry=model.save_template(first)
    assert retry['version']==3 and model.load_template(retry['id'])==retry
    assert len(list((model.template_dir()/'versions').glob('*.json')))==3
