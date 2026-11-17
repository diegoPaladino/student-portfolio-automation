"""Serviços locais do MVP 1. Nenhum envio externo."""
import hashlib
import io
import json
import re
import sqlite3
import warnings
from contextlib import contextmanager
from pathlib import Path
from PIL import Image, ImageOps
import pandas as pd
from src import settings

STATES = ['Pendente', 'Recebida', 'Em revisão', 'Aprovada', 'Rejeitada']

@contextmanager
def connection():
    settings.DATA.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(settings.DB, timeout=20)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    try:
        with db:
            yield db
    finally:
        db.close()

def rows(sql, args=()):
    with connection() as db:
        return [dict(r) for r in db.execute(sql, args)]

def audit(db, kind, entity):
    db.execute('INSERT INTO history(kind,entity) VALUES (?,?)', (kind, str(entity)))

def initialize():
    with connection() as db:
        db.executescript('''
        CREATE TABLE IF NOT EXISTS students(id INTEGER PRIMARY KEY, registration TEXT UNIQUE NOT NULL, name TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS projects(id INTEGER PRIMARY KEY, title TEXT NOT NULL, minimum INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS requirements(id TEXT PRIMARY KEY, project_id INTEGER REFERENCES projects(id), description TEXT NOT NULL, required INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS photos(id INTEGER PRIMARY KEY, digest TEXT UNIQUE NOT NULL, path TEXT UNIQUE NOT NULL, original_name TEXT NOT NULL, width INTEGER, height INTEGER);
        CREATE TABLE IF NOT EXISTS evidence(id INTEGER PRIMARY KEY, photo_id INTEGER REFERENCES photos(id), student_id INTEGER REFERENCES students(id), requirement_id TEXT REFERENCES requirements(id), state TEXT NOT NULL CHECK(state IN ('Pendente','Recebida','Em revisão','Aprovada','Rejeitada')), UNIQUE(student_id,requirement_id), UNIQUE(student_id,photo_id));
        CREATE TABLE IF NOT EXISTS history(id INTEGER PRIMARY KEY, created TEXT DEFAULT CURRENT_TIMESTAMP, kind TEXT, entity TEXT);
        ''')
        catalog = json.loads((settings.ROOT / 'config/catalog.json').read_text(encoding='utf-8-sig'))
        for project in catalog:
            db.execute('INSERT OR IGNORE INTO projects VALUES (?,?,?)', (project['id'],project['title'],project['minimum']))
            for i, desc in enumerate(project['requirements'],1):
                db.execute('INSERT OR IGNORE INTO requirements VALUES (?,?,?,?)', (f"{project['id']:02d}-{i}",project['id'],desc,int(i<=project['minimum'])))

def import_students(path):
    lines = [s.strip() for s in Path(path).read_text(encoding='utf-8-sig').splitlines() if s.strip()]
    pairs=[]
    for i,line in enumerate(lines):
        if re.fullmatch(r'\d+',line):
            if i+1>=len(lines) or lines[i+1].isdigit() or lines[i+1].startswith('Quantidade'):
                raise ValueError('Lista de alunos incompleta.')
            pairs.append((line,lines[i+1]))
    if not pairs:
        raise ValueError('Nenhum aluno encontrado.')
    count=0
    with connection() as db:
        for registration,name in pairs:
            count += db.execute('INSERT OR IGNORE INTO students(registration,name) VALUES (?,?)',(registration,name)).rowcount
        audit(db,'import_students',count)
    return count

def save_student(registration,name,student_id=None):
    if not registration.strip() or not name.strip():
        raise ValueError('Informe matrícula e nome.')
    with connection() as db:
        if student_id:
            db.execute('UPDATE students SET registration=?,name=? WHERE id=?',(registration.strip(),name.strip(),student_id))
        else:
            db.execute('INSERT INTO students(registration,name) VALUES (?,?)',(registration.strip(),name.strip()))
        audit(db,'save_student',student_id or db.execute('SELECT last_insert_rowid()').fetchone()[0])

def import_photo(content,name):
    if not content or len(content)>settings.MAX_BYTES:
        raise ValueError('Arquivo vazio ou maior que 30 MB.')
    with warnings.catch_warnings():
        warnings.simplefilter('error',Image.DecompressionBombWarning)
        try:
            with Image.open(io.BytesIO(content)) as im:
                if im.format not in ('JPEG','PNG','WEBP'):
                    raise ValueError('Use JPEG, PNG ou WEBP.')
                width,height=im.size
                ext={'JPEG':'.jpg','PNG':'.png','WEBP':'.webp'}[im.format]
                im.verify()
            with Image.open(io.BytesIO(content)) as im:
                im.load()
        except Exception as exc:
            raise ValueError('Imagem inválida ou insegura.') from exc
    digest=hashlib.sha256(content).hexdigest()
    settings.IMAGES.mkdir(parents=True,exist_ok=True)
    target=settings.IMAGES / (digest+ext)
    with connection() as db:
        found=db.execute('SELECT id FROM photos WHERE digest=?',(digest,)).fetchone()
        if found:
            return found[0],False
        if target.exists():
            if hashlib.sha256(target.read_bytes()).hexdigest()!=digest:
                raise ValueError('Falha de integridade no armazenamento.')
        else:
            with target.open('xb') as f:
                f.write(content)
        cur=db.execute('INSERT INTO photos(digest,path,original_name,width,height) VALUES (?,?,?,?,?)',(digest,target.relative_to(settings.DATA).as_posix(),Path(name).name,width,height))
        audit(db,'import_photo',cur.lastrowid)
        return cur.lastrowid,True

def import_folder(folder):
    folder=Path(folder).expanduser().resolve(strict=True)
    if not folder.is_dir():
        raise ValueError('Selecione uma pasta local.')
    result={'novas':0,'duplicadas':0,'invalidas':0}
    for path in folder.rglob('*'):
        if path.is_symlink() or not path.is_file() or path.suffix.lower() not in ('.jpg','.jpeg','.png','.webp'):
            continue
        if not path.resolve().is_relative_to(folder) or path.resolve().is_relative_to(settings.IMAGES.resolve()):
            continue
        try:
            if path.stat().st_size>settings.MAX_BYTES:
                raise ValueError('Arquivo grande')
            _,new=import_photo(path.read_bytes(),path.name)
            result['novas' if new else 'duplicadas']+=1
        except (OSError,ValueError):
            result['invalidas']+=1
    return result

def photo_path(relative):
    path=(settings.DATA / relative).resolve()
    if not path.is_relative_to(settings.IMAGES.resolve()):
        raise ValueError('Caminho de imagem inválido.')
    return path

def preview(relative):
    with Image.open(photo_path(relative)) as im:
        im=ImageOps.exif_transpose(im).convert('RGB')
        im.thumbnail((1000,1000))
        return im.copy()

def associate(photo_id,student_id,requirement_id):
    with connection() as db:
        cur=db.execute("INSERT INTO evidence(photo_id,student_id,requirement_id,state) VALUES (?,?,?,'Recebida')",(photo_id,student_id,requirement_id))
        audit(db,'associate',cur.lastrowid)

def review(evidence_id,state):
    if state not in STATES:
        raise ValueError('Estado inválido.')
    with connection() as db:
        if db.execute('UPDATE evidence SET state=? WHERE id=?',(state,evidence_id)).rowcount!=1:
            raise ValueError('Evidência não encontrada.')
        audit(db,'state:'+state,evidence_id)

def unassign(evidence_id):
    with connection() as db:
        db.execute('DELETE FROM evidence WHERE id=?',(evidence_id,))
        audit(db,'unassign',evidence_id)

def detail(student_id=None):
    return rows('''SELECT s.id student_id,s.name aluno,p.id project_id,p.title projeto,r.id requisito,r.description descricao,r.required obrigatoria,COALESCE(e.state,'Pendente') estado,e.id evidence_id,e.photo_id FROM students s CROSS JOIN requirements r JOIN projects p ON p.id=r.project_id LEFT JOIN evidence e ON e.student_id=s.id AND e.requirement_id=r.id ''' + ('WHERE s.id=? ' if student_id else '') + 'ORDER BY s.name,p.id,r.id', (student_id,) if student_id else ())

def progress(student_id=None):
    data=detail(student_id)
    result=[]
    for s in rows('SELECT id,name FROM students ORDER BY name'):
        if student_id and s['id']!=student_id:
            continue
        own=[r for r in data if r['student_id']==s['id']]
        done=0
        complete=0
        for p in rows('SELECT * FROM projects'):
            approved=sum(r['estado']=='Aprovada' for r in own if r['project_id']==p['id'])
            done+=min(approved,p['minimum'])
            complete+=approved>=p['minimum']
        result.append({'student_id':s['id'],'aluno':s['name'],'aprovadas':done,'necessarias':25,'progresso':done/25,'projetos_completos':complete})
    return result

def report():
    data=pd.DataFrame(detail())
    summary=pd.DataFrame(progress()).drop(columns=['student_id'],errors='ignore')
    output=io.BytesIO()
    with pd.ExcelWriter(output,engine='openpyxl',engine_kwargs={'options':{}} if False else {}) as writer:
        sheets={'Alunos':summary,'Ausentes':data[data.estado.isin(['Pendente','Rejeitada']) & (data.obrigatoria==1)] if not data.empty else data,'Revisao':data[data.estado.isin(['Recebida','Em revisão'])] if not data.empty else data}
        projects=[]
        for s in rows('SELECT id,name FROM students'):
            for p in rows('SELECT * FROM projects'):
                n=sum(r['estado']=='Aprovada' for r in detail(s['id']) if r['project_id']==p['id'])
                projects.append({'aluno':s['name'],'projeto':p['title'],'aprovadas':n,'minimo':p['minimum'],'situacao':'Completo' if n>=p['minimum'] else 'Incompleto'})
        sheets['Projetos']=pd.DataFrame(projects)
        sheets['Turma']=pd.DataFrame([{'alunos':len(summary),'progresso_medio':float(summary.progresso.mean()) if len(summary) else 0}])
        for name,df in sheets.items():
            df=df.drop(columns=['student_id','evidence_id','photo_id'],errors='ignore').copy()
            for col in df.select_dtypes(include='object'):
                df[col]=df[col].map(lambda v: "'"+v if isinstance(v,str) and v.startswith(('=','+','-','@')) else v)
            df.to_excel(writer,sheet_name=name,index=False)
    return output.getvalue()
