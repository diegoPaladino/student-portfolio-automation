"""Executa pytest e preserva apenas contagens e metadados no resumo local."""
import json
import os
import subprocess
import sys
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from src import settings
from src.diagnostics import version


def main():
    directory=settings.ROOT/'outputs'
    directory.mkdir(parents=True,exist_ok=True)
    run_id=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8]
    xml=directory/('tests-'+run_id+'.xml')
    result=subprocess.run([sys.executable,'-m','pytest','-q',f'--junitxml={xml}'],cwd=settings.ROOT)
    counts={'passed':0,'failed':0,'skipped':0,'errors':0}
    try:
        suites=ET.parse(xml).getroot()
        for suite in suites.iter('testsuite'):
            n=int(suite.get('tests',0)); failed=int(suite.get('failures',0)); skipped=int(suite.get('skipped',0)); errors=int(suite.get('errors',0))
            counts['passed']+=max(0,n-failed-skipped-errors)
            counts['failed']+=failed; counts['skipped']+=skipped; counts['errors']+=errors
    except (OSError,ET.ParseError,ValueError):
        counts['errors']+=1
    summary=dict(timestamp=datetime.now(timezone.utc).isoformat(),version=version(),python=sys.version.split()[0],exit_code=result.returncode,**counts)
    content=json.dumps(summary,indent=2)
    (directory/('test-summary-'+run_id+'.json')).write_text(content,encoding='utf-8')
    temporary=directory/('summary-'+run_id+'.tmp')
    temporary.write_text(content,encoding='utf-8')
    os.replace(temporary,directory/'test-summary.json')
    return result.returncode

if __name__=='__main__':
    raise SystemExit(main())
