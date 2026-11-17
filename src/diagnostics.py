"""Diagnóstico local sem conteúdo pessoal: python -m src.diagnostics."""
import argparse
import json
import platform
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from src import settings, observability as obs


def version():
    try:
        result=subprocess.run(['git','-c',f'safe.directory={settings.ROOT.as_posix()}','rev-parse','HEAD'],cwd=settings.ROOT,capture_output=True,text=True,timeout=5)
        commit=result.stdout.strip()
        return commit if result.returncode==0 and len(commit)==40 and all(c in '0123456789abcdef' for c in commit) else 'indisponivel'
    except (OSError,subprocess.TimeoutExpired):
        return 'indisponivel'


def collect():
    report={'generated_at':obs.timestamp(),'version':version(),'python':platform.python_version(),
            'os':platform.system()+' '+platform.release(),'database':{'status':'NÃO TESTADO'},
            'tests':None,'recent_errors':[],'configuration_problems':[]}
    try:
        obs.configuration()
    except (ValueError,OSError):
        report['configuration_problems'].append('Configuração de logging inválida.')
    if not settings.DB.is_file():
        report['database']['status']='BLOQUEADO'
        report['configuration_problems'].append('Banco local não encontrado; inicie o aplicativo.')
    else:
        db=None
        try:
            db=sqlite3.connect(settings.DB.resolve().as_uri()+'?mode=ro',uri=True,timeout=5)
            report['database']={'status':'APROVADO',
                'students':db.execute('SELECT COUNT(*) FROM students').fetchone()[0],
                'requirements':db.execute('SELECT COUNT(*) FROM requirements').fetchone()[0]}
            if db.execute("SELECT 1 FROM sqlite_master WHERE name='audit_outbox'").fetchone():
                report['database']['audit_pending']=db.execute('SELECT COUNT(*) FROM audit_outbox WHERE delivered=0').fetchone()[0]
        except (sqlite3.Error,OSError):
            report['database']={'status':'REPROVADO'}
            report['configuration_problems'].append('Banco indisponível ou esquema incompatível.')
        finally:
            if db is not None: db.close()
    summary=settings.ROOT/'outputs/test-summary.json'
    try:
        raw=json.loads(summary.read_text(encoding='utf-8'))
        report['tests']={k:raw[k] for k in ('passed','failed','skipped','errors','exit_code') if isinstance(raw.get(k),int)}
        when=datetime.fromisoformat(raw['timestamp'])
        report['tests']['timestamp']=when.isoformat()
    except (OSError,ValueError,KeyError,TypeError):
        report['configuration_problems'].append('Resumo automatizado de testes indisponível.')
    # Nunca copiar texto livre, stack, conteúdo ou caminhos do log para o diagnóstico.
    try:
        path=obs.log_dir()/'errors.log'
        with path.open('rb') as stream:
            stream.seek(max(0,path.stat().st_size-65536))
            lines=stream.read(65536).decode('utf-8',errors='replace').splitlines()
        for line in lines[-50:]:
            try:
                event=json.loads(line)
                if event.get('event') not in obs.EVENTS or event.get('operation') not in obs.OPERATIONS:
                    continue
                when=datetime.fromisoformat(event['timestamp'])
                report['recent_errors'].append({'timestamp':when.isoformat(),'event':event['event'],
                    'operation':event['operation'],'description':obs.EVENTS[event['event']]})
            except (ValueError,KeyError,TypeError):
                continue
    except OSError:
        pass
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=settings.ROOT/'outputs/diagnostico.json')
    args=parser.parse_args()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(collect(),ensure_ascii=False,indent=2),encoding='utf-8')
    print('Relatório técnico local gerado.')

if __name__=='__main__':
    main()
