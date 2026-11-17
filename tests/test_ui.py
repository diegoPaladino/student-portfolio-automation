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


def test_ui_sanitizes_unexpected_and_database_errors(local,monkeypatch):
    import sqlite3
    from streamlit.testing.v1 import AppTest
    from src import core
    for exc in [ValueError('SEGREDO SINTETICO C:/privado'),sqlite3.OperationalError('SEGREDO SINTETICO'),RuntimeError('SEGREDO SINTETICO')]:
        def fail(exc=exc):
            raise exc
        monkeypatch.setattr(core,'progress',fail)
        app=AppTest.from_file('app.py').run(timeout=30)
        assert not app.exception
        assert app.error
        assert 'SEGREDO' not in app.error[0].value


def test_report_only_generated_on_explicit_action(local,monkeypatch):
    from streamlit.testing.v1 import AppTest
    from src import core
    calls=[]
    original=core.report
    def counted():
        calls.append(1)
        return original()
    monkeypatch.setattr(core,'report',counted)
    app=AppTest.from_file('app.py').run(timeout=30)
    app.sidebar.radio[0].set_value('Relatório de pendências').run()
    assert not calls
    app.button[0].click().run()
    assert len(calls)==1 and not app.exception
    app.run()
    assert len(calls)==1
