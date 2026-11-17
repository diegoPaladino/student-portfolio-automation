import io
import pytest
from PIL import Image
from src import core,settings

@pytest.fixture
def local(tmp_path,monkeypatch):
    monkeypatch.setattr(settings,'DATA',tmp_path)
    monkeypatch.setattr(settings,'DB',tmp_path/'test.sqlite3')
    monkeypatch.setattr(settings,'IMAGES',tmp_path/'images')
    core.initialize()
    return tmp_path

def picture(i=0):
    out=io.BytesIO()
    Image.new('RGB',(20,20),(i,0,0)).save(out,format='PNG')
    return out.getvalue()

def student(local):
    path=local/'students.txt'
    path.write_text('Matrícula\nNome do Aluno\n100\nCRIANCA TESTE\nQuantidade de Alunos: 1',encoding='utf-8')
    assert core.import_students(path)==1
    assert core.import_students(path)==0
    return core.rows('SELECT id FROM students')[0]['id']

def test_students(local):
    sid=student(local)
    core.save_student('100','NOME TESTE',sid)
    with pytest.raises(Exception): core.save_student('100','OUTRO TESTE')
    assert core.rows('SELECT name FROM students')[0]['name']=='NOME TESTE'

def test_catalog(local):
    core.initialize()
    assert len(core.rows('SELECT * FROM projects'))==12
    req=core.rows('SELECT * FROM requirements')
    assert len(req)==27
    assert sum(r['required'] for r in req)==25

def test_photo(local):
    content=picture()
    pid,new=core.import_photo(content,'../../foto.png')
    assert new
    assert core.import_photo(content,'outra.png')==(pid,False)
    photo=core.rows('SELECT * FROM photos')[0]
    assert core.photo_path(photo['path']).read_bytes()==content
    assert core.preview(photo['path']).size==(20,20)
    with pytest.raises(ValueError): core.import_photo(b'invalido','x.png')
    with pytest.raises(ValueError): core.photo_path('../../outside.png')

def test_workflow_persistence_and_completion(local):
    sid=student(local)
    for i,r in enumerate(core.rows('SELECT * FROM requirements')):
        pid,_=core.import_photo(picture(i),'foto.png')
        core.associate(pid,sid,r['id'])
        eid=core.rows('SELECT id FROM evidence WHERE photo_id=?',(pid,))[0]['id']
        assert core.progress(sid)[0]['aprovadas']==min(i,20)+min(max(i-20,0),4)+min(max(i-26,0),1)
        core.review(eid,'Aprovada')
    core.initialize()
    assert core.progress(sid)[0]['progresso']==1
    assert core.progress(sid)[0]['projetos_completos']==12
    assert len(core.rows('SELECT * FROM history'))>27
    core.review(eid,'Rejeitada')
    assert core.progress(sid)[0]['aprovadas']==24
    core.unassign(eid)
    assert core.detail(sid)[-1]['estado']=='Pendente'

def test_assignment_constraints(local):
    sid=student(local)
    pid,_=core.import_photo(picture(),'foto.png')
    core.associate(pid,sid,'01-1')
    with pytest.raises(Exception): core.associate(pid,sid,'01-2')
    assert core.progress(sid)[0]['aprovadas']==0
    eid=core.rows('SELECT id FROM evidence')[0]['id']
    for state in ['Em revisão','Rejeitada','Pendente']:
        core.review(eid,state)
        assert core.progress(sid)[0]['aprovadas']==0

def test_folder_and_excel(local):
    student(local)
    folder=local/'inbox'; folder.mkdir()
    (folder/'a.png').write_bytes(picture())
    (folder/'b.png').write_bytes(b'bad')
    assert core.import_folder(folder)=={'novas':1,'duplicadas':0,'invalidas':1}
    assert core.import_folder(folder)['duplicadas']==1
    import openpyxl
    book=openpyxl.load_workbook(io.BytesIO(core.report()))
    assert book.sheetnames==['Alunos','Ausentes','Revisao','Projetos','Turma']
    assert book['Ausentes'].max_row==26

def test_empty_report(local):
    assert core.report().startswith(b'PK')
