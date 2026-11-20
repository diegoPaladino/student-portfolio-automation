"""Catalogo e persistencia com redacao exclusivamente sintetica."""
import copy
import json
import sqlite3
import pytest
from PIL import Image, ImageDraw
from test_core import local, student
from test_templates import template
from src import core, pedagogy, settings
from src.template_editor import model
from src.rendering import typography
from src.rendering.preview import render_preview


def synthetic_source():
    text='🌱 PORTFÓLIO INDIVIDUAL 2026\nTÍTULO SINTÉTICO\nSubtítulo sintético\nNome da criança: ______\nIntrodução sintética com acentuação: ação, coração, ______.\n\n'
    for n in range(1,11):
        text+=f'🌱 PROJETO {n}\nTÍTULO SINTÉTICO {n}\nTema sintético {n}\n'
        if n==8: text+='Comentário editorial sintético fora da composição.\n'
        text+='ABERTURA COLETIVA\nParágrafo sintético.\n\nSegundo parágrafo com pontuação — ação!\n\n🌟 A VEZ DE ______\n'
        for p in (1,2):
            text+=f'📸 FOTO {p}: descrição sintética {n}/{p}.\n\n'
            if n<7: text+=f'Legenda:\nTexto sintético {p} para ______.\n\n'
        if n not in (4,6): text+='“Frase sintética de destaque.”\n'
    text+='💛 E EU FARIA UMA DIFERENÇA IMPORTANTE NO FINAL\nInstrução editorial sintética.\n✨ ESSE É O MEU JEITO DE APRENDER\nInstrução de fotografias sintética.\nE um texto individual:\nSíntese sintética para ______.\n\n🌈 ÚLTIMA PÁGINA\n______ , TÍTULO FINAL SINTÉTICO!\nInstrução de fotografia sintética.\nE:\n“Texto final sintético.”\nCom carinho,\nASSINATURA SINTÉTICA\n'
    return text


def test_parse_preserves_text_origins_and_missing():
    raw=synthetic_source();catalog=pedagogy.parse_content(raw)
    assert len(catalog['sections'])==13
    assert catalog['fields']['P04.title']['text']=='TÍTULO SINTÉTICO 4'
    assert catalog['fields']['P04.introduction']['text']=='Parágrafo sintético.\n\nSegundo parágrafo com pontuação — ação!'
    assert catalog['fields']['P04.evidence_1']['requirement_id']=='04-1'
    assert catalog['fields']['P04.caption_1']['personalization']==[{'token':'______','field':'student_name'}]
    assert catalog['sections']['P07']['missing']==['caption_1','caption_2']
    assert 'P07.caption_1' not in catalog['fields']
    assert all('Comentário editorial' not in field['text'] for field in catalog['fields'].values())
    lines=raw.splitlines()
    for field in catalog['fields'].values():
        origin=field['origin']
        assert field['text'] in '\n'.join(lines[origin['start_line']-1:origin['end_line']])
    assert pedagogy.personalize('______ — ______!','TESTE')=='TESTE — TESTE!'
    assert pedagogy.personalize('______',None)=='______'
    with pytest.raises(ValueError): pedagogy.parse_content(raw.replace('PROJETO 5','PROJETO 99'))


def test_catalog_import_reload_never_overwrites_edits(local):
    path=pedagogy.source_path();before=path.read_bytes()
    catalog=pedagogy.import_catalog()
    assert path.read_bytes()==before
    assert pedagogy.load_catalog()==catalog
    pedagogy.save_text('P04.title','EDIÇÃO GLOBAL SINTÉTICA')
    path.write_text(synthetic_source().replace('TÍTULO SINTÉTICO 4','ORIGINAL REVISADO'),encoding='utf-8')
    new=pedagogy.import_catalog()
    assert new['fields']['P04.title']['text']=='ORIGINAL REVISADO'
    assert pedagogy.resolve_text('P04.title')[0]=='EDIÇÃO GLOBAL SINTÉTICA'
    assert len(list((pedagogy.catalog_path().parent/'pedagogy_versions').glob('*.json')))==2


def test_precedence_history_restore_and_audit(local):
    sid=student(local)
    original=pedagogy.load_catalog()['fields']['P04.caption_1']['text']
    assert pedagogy.resolve_text('P04.caption_1',sid)==(original,'original')
    pedagogy.save_text('P04.caption_1','GLOBAL',expected_revision=0)
    pedagogy.save_text('P04.caption_1','INDIVIDUAL',sid,0)
    revision=pedagogy.current_edit('P04.caption_1',sid)['id']
    pedagogy.save_text('P04.caption_1','GLOBAL 2')
    assert pedagogy.resolve_text('P04.caption_1',sid)==('INDIVIDUAL','individual')
    with pytest.raises(ValueError): pedagogy.save_text('P04.caption_1','STALE',sid,0)
    pedagogy.save_text('P04.caption_1',None,sid,revision)
    assert pedagogy.resolve_text('P04.caption_1',sid)==('GLOBAL 2','global')
    pedagogy.save_text('P04.caption_1',None)
    assert pedagogy.resolve_text('P04.caption_1',sid)==(original,'original')
    assert [row['text'] for row in pedagogy.history('P04.caption_1',sid)]==[None,'INDIVIDUAL']
    # Reabrir conexao real conserva todas as revisoes e a auditoria pos-commit.
    with sqlite3.connect(settings.DB) as db:
        assert db.execute('SELECT COUNT(*) FROM pedagogical_edits').fetchone()[0]==5
        assert db.execute('SELECT COUNT(*) FROM audit_outbox WHERE delivered=0').fetchone()[0]==0
    with pytest.raises(ValueError): pedagogy.save_text('P04.evidence_1','NAO E LEGENDA')
    with pytest.raises(ValueError): pedagogy.save_text('P04.title','TEXTO',999)


def test_failed_edit_rolls_back_history_and_audit(local,monkeypatch):
    pedagogy.initialize()
    before=core.rows('SELECT COUNT(*) n FROM audit_outbox')[0]['n']
    def fail(*args): raise OSError('FALHA SINTETICA PRIVADA')
    monkeypatch.setattr(core,'audit',fail)
    with pytest.raises(OSError): pedagogy.save_text('P04.title','TEXTO PRIVADO')
    assert not pedagogy.history('P04.title')
    assert core.rows('SELECT COUNT(*) n FROM audit_outbox')[0]['n']==before


def semantic_template(local):
    result=template(local)
    for index, kind in enumerate(typography.PRESETS):
        field={'title':'title','subtitle':'subtitle','body_text':'introduction','caption':'caption_1','highlight':'individual_call','student_name':'individual_call'}[kind]
        result['regions'].append(dict(id='semantic_'+kind,type=kind,x=.05,y=.35+index*.09,width=.9,height=.08,
            source={'kind':'pedagogical','field_id':'P04.'+field},text_style=typography.preset(kind)))
    return result


def test_semantic_roundtrip_legacy_and_project_validation(local):
    legacy=template(local);legacy['schema_version']=1
    saved=model.save_template(legacy)
    assert saved['schema_version']==2 and legacy['schema_version']==1
    data=semantic_template(local)
    saved=model.save_template(data)
    assert model.load_template(saved['id'])==saved
    assert {r['type'] for r in saved['regions']}==set(model.TYPES)
    data['regions'][1]['source']['field_id']='P03.title'
    with pytest.raises(ValueError): model.validate_template(data)
    data['regions'][1]['source']['field_id']='P04.missing'
    with pytest.raises(ValueError): model.validate_template(data)


def test_fonts_styles_overflow_and_individual_composition(local):
    data=semantic_template(local)
    sid=student(local)
    image,warnings=render_preview(data,sid,width=400)
    assert image.size==(400,1200)
    assert core.rows('SELECT COUNT(*) n FROM evidence')[0]['n']==0
    assert typography.families()
    for family in typography.families():
        for weight in typography.WEIGHTS:
            assert typography.font(25,family,weight).getmask('ação coração çãé').getbbox()
    region=data['regions'][1]
    region['source']={'kind':'literal','text':'Texto sintético excessivo. '*100}
    region['height']=.01
    _,warnings=render_preview(data,width=400)
    assert any('cortado' in warning for warning in warnings)
    region['source']['text']='UmaLinhaHorizontalMuitoLonga'*10
    region['height']=.2;region['text_style']['wrap']=False
    assert any('cortado' in warning for warning in render_preview(data,width=400)[1])
    for key,value in [('line_height',float('nan')),('padding',-1),('letter_spacing',30),('weight','invalid'),('wrap','yes')]:
        invalid=copy.deepcopy(data);invalid['regions'][1]['text_style'][key]=value
        with pytest.raises(ValueError): model.validate_template(invalid)
    # Confirmar que mudanca de precedencia altera a composicao em memoria.
    region['height']=.08;region['text_style']['wrap']=True
    region['source']={'kind':'pedagogical','field_id':'P04.title'}
    before=render_preview(data,sid,width=400)[0].tobytes()
    pedagogy.save_text('P04.title','OUTRO TÍTULO',sid)
    assert render_preview(data,sid,width=400)[0].tobytes()!=before
