from test_core import local, student, picture
from src import core
from streamlit.testing.v1 import AppTest

def test_screens(local):
    sid=student(local)
    pid,_=core.import_photo(picture(),'sintetica.png')
    core.associate(pid,sid,'01-1')
    app=AppTest.from_file('app.py').run(timeout=30)
    assert not app.exception
    for page in ['Alunos','Aluno em detalhe','Importar e classificar','Revisar evidências','Relatório de pendências']:
        app.sidebar.radio[0].set_value(page).run(timeout=30)
        assert not app.exception
    app.sidebar.radio[0].set_value('Revisar evidências').run()
    app.selectbox[2].set_value('Aprovada').run()
    app.button[0].click().run()
    assert not app.exception
    assert core.progress(sid)[0]['aprovadas']==1
