"""Logging local: somente eventos conhecidos; textos externos nunca são persistidos."""
import atexit
import contextvars
import functools
import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import os
import threading
import traceback
import uuid
from datetime import datetime, timezone
from src import settings

_lock = threading.RLock()
_correlation = contextvars.ContextVar('portfolio_correlation', default=None)
EVENTS = {
    'startup': 'Aplicação inicializada.', 'shutdown': 'Encerramento do processo detectado.',
    'operation_failed': 'Operação não concluída.', 'database_failed': 'Acesso ou transação do banco falhou.',
    'audit_failed': 'Auditoria pendente; nova tentativa ocorrerá na próxima operação.',
    'photo_received': 'Fotografia recebida.', 'photo_classified': 'Fotografia classificada.',
    'photo_approved': 'Fotografia aprovada.', 'photo_rejected': 'Fotografia rejeitada.',
    'photo_unassigned': 'Fotografia desvinculada para possível substituição.',
    'photo_replaced': 'Fotografia substituída.', 'report_exported': 'Relatório Excel gerado.',
    'state_changed': 'Situação da evidência alterada.', 'import_students': 'Importação de cadastros confirmada.',
    'save_student': 'Cadastro confirmado.', 'invalid_file': 'Arquivo inválido ou incompatível.',
    'unknown_student': 'Associação a aluno inexistente recusada.', 'unknown': 'Evento não reconhecido.'
}
OPERATIONS = {'initialize','connection','import_students','save_student','import_photo','import_folder',
              'associate','review','unassign','preview','photo_path','report','ui','startup','shutdown','audit','unknown'}
RESULTS = {'success','failure','pending'}


def timestamp():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')


def log_dir():
    default = settings.ROOT / 'logs' if settings.DATA == settings.ROOT / 'data' else settings.DATA / 'logs'
    return Path(os.environ.get('PORTFOLIO_LOG_DIR', default)).resolve()


def configuration():
    level = os.environ.get('PORTFOLIO_LOG_LEVEL','INFO').upper()
    if level not in {'DEBUG','INFO','WARNING','ERROR','CRITICAL','OFF'}:
        raise ValueError('Nível de logging inválido.')
    size = int(os.environ.get('PORTFOLIO_LOG_MAX_BYTES','2097152'))
    retention = int(os.environ.get('PORTFOLIO_LOG_BACKUPS','5'))
    if size < 256 or not 1 <= retention <= 100:
        raise ValueError('Limites de logging inválidos.')
    return level,size,retention


class SafeFormatter(logging.Formatter):
    def format(self, record):
        event = getattr(record,'event','unknown')
        event = event if event in EVENTS else 'unknown'
        operation = getattr(record,'operation','unknown')
        operation = operation if operation in OPERATIONS else 'unknown'
        cid = getattr(record,'correlation_id',None)
        cid = cid if isinstance(cid,str) and len(cid)==32 and all(c in '0123456789abcdef' for c in cid) else None
        source = 'app' if operation=='ui' else 'observability' if operation in {'startup','shutdown','audit','unknown'} else 'core'
        payload = dict(timestamp=timestamp(),level=record.levelname,module=source,operation=operation,
                       correlation_id=cid,event=event,description=EVENTS[event])
        if record.exc_info:
            # Stack técnico sem mensagem de exceção, código-fonte, argumentos, nomes externos ou caminhos.
            frames = traceback.extract_tb(record.exc_info[2])
            payload['exception_type'] = record.exc_info[0].__name__ if record.exc_info[0].__module__ in ('builtins','sqlite3','PIL') else 'Exception'
            payload['stack'] = [{'module':Path(f.filename).stem if Path(f.filename).stem in {'core','app','observability','diagnostics'} else 'external',
                                 'line':f.lineno} for f in frames]
        return json.dumps(payload,ensure_ascii=False)


def configure():
    level,size,retention=configuration()
    directory=log_dir()
    signature=(str(directory),level,size,retention)
    logger=logging.getLogger('portfolio')
    with _lock:
        if getattr(logger,'_portfolio_signature',None)==signature:
            return logger
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
            handler.close()
        logger.propagate=False
        logger.setLevel(logging.DEBUG)
        logger.disabled=level=='OFF'
        if level!='OFF':
            directory.mkdir(parents=True,exist_ok=True)
            (directory/'audit.jsonl').touch(exist_ok=True)
            for filename,threshold in [('app.log',getattr(logging,level)),('errors.log',max(logging.ERROR,getattr(logging,level)))]:
                handler=RotatingFileHandler(directory/filename,maxBytes=size,backupCount=retention,encoding='utf-8')
                handler.setLevel(threshold)
                handler.setFormatter(SafeFormatter())
                logger.addHandler(handler)
        logger._portfolio_signature=signature
    return logger


def emit(event,operation,level=logging.INFO,exc_info=None):
    configure().log(level,'',extra={'event':event,'operation':operation,'correlation_id':_correlation.get()},exc_info=exc_info)


def operation(function):
    @functools.wraps(function)
    def wrapper(*args,**kwargs):
        token=_correlation.set(_correlation.get() or uuid.uuid4().hex)
        try:
            return function(*args,**kwargs)
        except Exception:
            # Fronteira de serviço: registra e relança, nunca transforma falha em sucesso.
            import sys
            emit('operation_failed',function.__name__,logging.ERROR,sys.exc_info())
            raise
        finally:
            _correlation.reset(token)
    return wrapper


def audit_payload(event,entity):
    if event not in EVENTS:
        event='unknown'
    # Entidade interna: apenas ID numérico; nunca texto arbitrário.
    internal_id = entity if isinstance(entity,int) else None
    return dict(timestamp=timestamp(),level='INFO',module='core',operation=event,event=event,
                correlation_id=_correlation.get(),entity_id=internal_id,result='success',description=EVENTS[event])


def append_audit(payload):
    _,size,retention=configuration()
    directory=log_dir()
    directory.mkdir(parents=True,exist_ok=True)
    with _lock:
        handler=RotatingFileHandler(directory/'audit.jsonl',maxBytes=size,backupCount=retention,encoding='utf-8')
        handler.setFormatter(logging.Formatter('%(message)s'))
        try:
            record=logging.LogRecord('portfolio.audit',logging.INFO,'',0,json.dumps(payload,ensure_ascii=False),(),None)
            # Escreve diretamente para que erro de disco seja propagado ao outbox.
            if handler.shouldRollover(record):
                handler.doRollover()
            handler.stream.write(handler.format(record)+'\n')
            handler.stream.flush()
            os.fsync(handler.stream.fileno())
        finally:
            handler.close()


def startup():
    logger=configure()
    with _lock:
        if not getattr(logger,'_portfolio_started',False):
            emit('startup','startup')
            logger._portfolio_started=True
            atexit.register(lambda: logger.log(logging.INFO,'',extra={'event':'shutdown','operation':'shutdown','correlation_id':None}))
