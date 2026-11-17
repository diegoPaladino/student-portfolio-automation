import json
import logging
import sqlite3
from pathlib import Path
import pytest
from test_core import local, student, picture
from src import core, observability as obs, settings, diagnostics

@pytest.fixture
def logs(local,monkeypatch):
    monkeypatch.setenv('PORTFOLIO_LOG_DIR',str(local/'logs'))
    monkeypatch.setenv('PORTFOLIO_LOG_LEVEL','DEBUG')
    monkeypatch.setenv('PORTFOLIO_LOG_MAX_BYTES','2048')
    monkeypatch.setenv('PORTFOLIO_LOG_BACKUPS','2')
    obs.configure()
    return local/'logs'


def audit_events(logs):
    result=[]
    for p in sorted(logs.glob('audit.jsonl*')):
        result.extend(json.loads(line) for line in p.read_text(encoding='utf-8').splitlines())
    return result


def test_logging_idempotent_and_exception_privacy(logs):
    logger=obs.configure()
    handlers=list(logger.handlers)
    assert obs.configure().handlers==handlers
    try:
        raise ValueError('NOME SINTETICO PRIVADO 987654321 C:/privado/foto.png')
    except ValueError:
        import sys
        obs.emit('operation_failed','import_photo',logging.ERROR,sys.exc_info())
    logger.error('NOME SINTETICO PRIVADO 987654321',extra={'event':'texto privado','operation':'caminho privado'})
    text=(logs/'errors.log').read_text(encoding='utf-8')
    assert 'PRIVADO' not in text and '987654321' not in text and 'foto.png' not in text
    records=[json.loads(line) for line in text.splitlines()]
    assert records[0]['exception_type']=='ValueError'
    assert records[0]['stack']
    assert records[0]['timestamp'][-6] in '+-'
    assert records[1]['event']=='unknown'


def test_rotation_and_retention(logs):
    for _ in range(40):
        obs.emit('operation_failed','ui',logging.ERROR)
        obs.append_audit(obs.audit_payload('photo_received',1))
    for base in ['app.log','errors.log','audit.jsonl']:
        assert (logs/(base+'.1')).exists()
        assert len(list(logs.glob(base+'*')))<=3
        assert (logs/base).stat().st_size<=2048


def test_audit_success_persistence(logs,monkeypatch):
    monkeypatch.setenv('PORTFOLIO_LOG_MAX_BYTES','100000')
    sid=student(settings.DATA)
    pid,_=core.import_photo(picture(),'NOME PRIVADO.png')
    core.associate(pid,sid,'01-1')
    eid=core.rows('SELECT id FROM evidence')[0]['id']
    core.review(eid,'Aprovada')
    core.review(eid,'Rejeitada')
    core.unassign(eid)
    core.associate(pid,sid,'01-1')
    core.report()
    records=audit_events(logs)
    expected={'photo_received','photo_classified','photo_approved','photo_rejected','photo_unassigned','photo_replaced','report_exported'}
    assert expected <= {r['event'] for r in records}
    assert all(r['result']=='success' and isinstance(r['event_id'],int) for r in records)
    assert all(r['correlation_id'] and len(r['correlation_id'])==32 for r in records)
    assert 'NOME PRIVADO' not in (logs/'audit.jsonl').read_text(encoding='utf-8')
    assert core.rows('SELECT COUNT(*) n FROM audit_outbox WHERE delivered=0')[0]['n']==0


def test_rollback_never_audits_success(logs):
    with pytest.raises(RuntimeError):
        with core.connection() as db:
            core.audit(db,'report_exported',None)
            raise RuntimeError('falha sintetica')
    assert not [r for r in audit_events(logs) if r['event']=='report_exported']
    assert core.rows('SELECT COUNT(*) n FROM audit_outbox')[0]['n']==0


def test_outbox_retries_after_disk_failure(logs,monkeypatch):
    original=obs.append_audit
    def fail(payload):
        raise OSError('caminho privado')
    monkeypatch.setattr(obs,'append_audit',fail)
    pid,new=core.import_photo(picture(),'privado.png')
    assert new and core.rows('SELECT id FROM photos')[0]['id']==pid
    assert core.rows('SELECT COUNT(*) n FROM audit_outbox WHERE delivered=0')[0]['n']==1
    monkeypatch.setattr(obs,'append_audit',original)
    core.flush_audit()
    assert len(audit_events(logs))==1
    assert core.rows('SELECT COUNT(*) n FROM audit_outbox WHERE delivered=0')[0]['n']==0


def test_missing_student_and_export_failure(logs,monkeypatch):
    pid,_=core.import_photo(picture(),'x.png')
    with pytest.raises(ValueError): core.associate(pid,9999,'01-1')
    assert core.rows('SELECT COUNT(*) n FROM evidence')[0]['n']==0
    def fail(*args,**kwargs):
        raise OSError('caminho privado de exportacao')
    monkeypatch.setattr(core.pd,'ExcelWriter',fail)
    with pytest.raises(OSError): core.report()
    assert 'report_exported' not in {r['event'] for r in audit_events(logs)}
    text=(logs/'errors.log').read_text(encoding='utf-8')
    assert 'privado' not in text
    assert 'associate' in text and 'report' in text


def test_database_error_logged(logs,monkeypatch):
    monkeypatch.setattr(settings,'DB',settings.DATA/'absent'/'db.sqlite3')
    with pytest.raises(sqlite3.Error): core.rows('SELECT 1')
    assert 'database_failed' in (logs/'errors.log').read_text(encoding='utf-8')


def test_logging_off_and_invalid_configuration(logs,monkeypatch):
    monkeypatch.setenv('PORTFOLIO_LOG_LEVEL','OFF')
    assert obs.configure().disabled
    # Auditoria transacional é independente do nível dos logs técnicos.
    obs.append_audit(obs.audit_payload('photo_received',2))
    assert audit_events(logs)
    monkeypatch.setenv('PORTFOLIO_LOG_BACKUPS','0')
    with pytest.raises(ValueError): obs.configure()


def test_diagnostic_readonly_and_sanitized(logs,monkeypatch):
    student(settings.DATA)
    monkeypatch.setattr(diagnostics,'version',lambda:'a'*40)
    report=diagnostics.collect()
    assert report['database']['students']==1
    assert report['database']['requirements']==27
    assert 'CRIANCA TESTE' not in json.dumps(report)
    (logs/'errors.log').write_text(json.dumps({'timestamp':obs.timestamp(),'event':'operation_failed','operation':'ui','description':'NOME PRIVADO','stack':'caminho privado'})+'\n',encoding='utf-8')
    report=diagnostics.collect()
    assert report['recent_errors'] and 'PRIVADO' not in json.dumps(report)
    monkeypatch.setattr(settings,'DB',settings.DATA/'not-created.sqlite3')
    assert diagnostics.collect()['database']['status']=='BLOQUEADO'
    assert not settings.DB.exists()


def test_startup_not_repeated(logs,monkeypatch):
    monkeypatch.setenv('PORTFOLIO_LOG_MAX_BYTES','100000')
    logger=obs.configure()
    monkeypatch.setattr(logger,'_portfolio_started',False,raising=False)
    obs.startup(); obs.startup()
    records=[json.loads(line) for line in (logs/'app.log').read_text(encoding='utf-8').splitlines()]
    assert sum(r['event']=='startup' for r in records)==1


def test_additive_migration_preserves_legacy_data(logs):
    legacy=settings.DATA/'legacy.sqlite3'
    db=sqlite3.connect(legacy)
    db.execute('CREATE TABLE students(id INTEGER PRIMARY KEY, registration TEXT UNIQUE NOT NULL, name TEXT NOT NULL)')
    db.execute("INSERT INTO students VALUES (1,'123','SINTETICO LEGADO')")
    db.commit(); db.close()
    previous=settings.DB
    try:
        settings.DB=legacy
        core.initialize()
        assert core.rows('SELECT name FROM students')[0]['name']=='SINTETICO LEGADO'
        assert core.rows("SELECT COUNT(*) n FROM sqlite_master WHERE name='audit_outbox'")[0]['n']==1
    finally:
        settings.DB=previous


def test_normal_process_shutdown(logs):
    import os,subprocess,sys
    env=os.environ.copy()
    env['PORTFOLIO_LOG_DIR']=str(logs/'child')
    result=subprocess.run([sys.executable,'-c','from src.observability import startup; startup(); startup()'],capture_output=True,env=env,timeout=15)
    assert result.returncode==0
    records=[json.loads(line) for line in (logs/'child'/'app.log').read_text(encoding='utf-8').splitlines()]
    assert [r['event'] for r in records]==['startup','shutdown']
    assert (logs/'child'/'errors.log').exists()
    assert (logs/'child'/'audit.jsonl').exists()
