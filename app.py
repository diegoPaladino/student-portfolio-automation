import sqlite3
import streamlit as st
import pandas as pd
from src import core, settings, observability as obs
import logging
import sys

st.set_page_config(page_title='Portfólios da turma · 2026',page_icon='🌱',layout='wide')
try:
    obs.startup()
    core.initialize()
except (sqlite3.Error, OSError, ValueError):
    st.error('Não foi possível iniciar os dados ou os registros locais. Consulte o diagnóstico técnico.')
    st.stop()
st.title('🌱 Portfólios da turma · 2026')
st.caption('Organize as memórias de cada criança. Somente fotos aprovadas contam para a conclusão.')
page=st.sidebar.radio('Navegação',['Visão geral','Alunos','Aluno em detalhe','Importar e classificar','Revisar evidências','Relatório de pendências','Editor de Templates'])
try:
    students=core.rows('SELECT * FROM students ORDER BY name')
except (sqlite3.Error,OSError):
    st.error('Não foi possível consultar o banco local. Tente novamente ou consulte o diagnóstico.')
    st.stop()
by_id={s['id']:s for s in students}
def choose_student(key):
    return st.selectbox('Criança',list(by_id),format_func=lambda i:by_id[i]['name'],key=key) if students else None

def show_table(data):
    st.dataframe(pd.DataFrame(data),hide_index=True,use_container_width=True)

try:
    if page=='Visão geral':
        data=core.progress()
        a,b,c=st.columns(3)
        a.metric('Crianças',len(data))
        b.metric('Turma concluída',f"{sum(x['aprovadas'] for x in data)/(25*len(data)):.0%}" if data else '0%')
        c.metric('Portfólios completos',sum(x['aprovadas']==25 for x in data))
        show_table([{k:v for k,v in r.items() if k!='student_id'} for r in data])
        if not students: st.info('Abra Alunos e importe a lista para começar.')
    elif page=='Alunos':
        if st.button('Importar lista original de alunos'):
            st.success(f"{core.import_students(settings.ROOT / 'Lista_Alunos.txt')} novos cadastros.")
            st.rerun()
        query=st.text_input('Localizar pelo nome')
        show_table([{'Nome':s['name']} for s in students if query.casefold() in s['name'].casefold()])
        selected=st.selectbox('Cadastrar ou editar',[None]+list(by_id),format_func=lambda i:'Novo cadastro' if i is None else by_id[i]['name'])
        current=by_id.get(selected,{})
        with st.form('student'):
            name=st.text_input('Nome original',value=current.get('name',''))
            registration=st.text_input('Matrícula (uso administrativo)',value=current.get('registration',''),type='password')
            if st.form_submit_button('Salvar cadastro'):
                core.save_student(registration,name,selected)
                st.rerun()
    elif page=='Aluno em detalhe':
        sid=choose_student('detail')
        if sid:
            p=core.progress(sid)[0]
            st.progress(p['progresso'],text=f"{p['aprovadas']} de 25 fotos obrigatórias aprovadas")
            for project in core.rows('SELECT * FROM projects ORDER BY id'):
                subset=[r for r in core.detail(sid) if r['project_id']==project['id']]
                approved=sum(r['estado']=='Aprovada' for r in subset)
                with st.expander(f"{project['title']} · {approved}/{project['minimum']} aprovadas"):
                    show_table([{'Campo':r['requisito'],'O que fotografar':r['descricao'],'Estado':r['estado'],'Obrigatória':bool(r['obrigatoria'])} for r in subset])
                    for r in subset:
                        if r['photo_id']:
                            photo=core.rows('SELECT * FROM photos WHERE id=?',(r['photo_id'],))[0]
                            st.image(core.preview(photo['path']),caption=f"{r['requisito']} · {r['estado']}",width=250)
    elif page=='Importar e classificar':
        st.subheader('1. Trazer fotografias')
        uploads=st.file_uploader('Selecione fotos JPEG, PNG ou WEBP (até 30 MB cada)',type=['jpg','jpeg','png','webp'],accept_multiple_files=True)
        if st.button('Importar arquivos selecionados'):
            new=duplicate=failed=0
            for f in uploads:
                try:
                    _,created=core.import_photo(f.getvalue(),f.name)
                    new+=created; duplicate+=not created
                except ValueError: failed+=1
            st.success(f'{new} novas · {duplicate} duplicadas · {failed} inválidas')
        folder=st.text_input('Ou informe o caminho de uma pasta neste computador')
        if st.button('Importar pasta e subpastas'):
            st.write(core.import_folder(folder))
        st.subheader('2. Classificar manualmente')
        st.caption('Nenhuma identidade é deduzida pelo nome do arquivo ou pelo rosto. Confira a criança e a atividade.')
        photos=core.rows('SELECT p.*,COUNT(e.id) associations FROM photos p LEFT JOIN evidence e ON e.photo_id=p.id GROUP BY p.id ORDER BY p.id DESC')
        only=st.checkbox('Mostrar apenas fotos sem associação',value=True)
        photos=[p for p in photos if not only or p['associations']==0]
        photo_map={p['id']:p for p in photos}
        pid=st.selectbox('Fotografia',list(photo_map),format_func=lambda i:f"Foto {i} · {photo_map[i]['original_name']}") if photos else None
        sid=choose_student('assign')
        if pid:
            st.image(core.preview(photo_map[pid]['path']),width=450)
        if sid and pid:
            req=core.rows('SELECT r.*,p.title FROM requirements r JOIN projects p ON p.id=r.project_id ORDER BY p.id,r.id')
            rid=st.selectbox('Projeto e campo de evidência',[r['id'] for r in req],format_func=lambda i:next(f"{r['title']} · {r['id']} · {r['description']}" for r in req if r['id']==i))
            if st.button('Associar foto à criança e ao campo'):
                core.associate(pid,sid,rid)
                st.success('Foto recebida. Abra Revisar evidências para aprovar.')
    elif page=='Revisar evidências':
        sid=choose_student('review')
        if sid:
            evidence=[r for r in core.detail(sid) if r['evidence_id']]
            mapping={r['evidence_id']:r for r in evidence}
            eid=st.selectbox('Evidência',list(mapping),format_func=lambda i:f"{mapping[i]['projeto']} · {mapping[i]['requisito']} · {mapping[i]['estado']}") if evidence else None
            if eid:
                r=mapping[eid]
                st.write(r['descricao'])
                photo=core.rows('SELECT * FROM photos WHERE id=?',(r['photo_id'],))[0]
                st.image(core.preview(photo['path']),width=500)
                state=st.selectbox('Situação',core.STATES,index=core.STATES.index(r['estado']))
                if st.button('Salvar revisão'):
                    core.review(eid,state); st.rerun()
                if st.button('Desvincular para corrigir a classificação'):
                    core.unassign(eid); st.rerun()
    elif page=='Editor de Templates':
        from src.template_editor.ui import show
        show()
    else:
        data=core.detail()
        show_table([{'Criança':r['aluno'],'Projeto':r['projeto'],'Campo':r['requisito'],'Requisito':r['descricao'],'Situação':r['estado']} for r in data if r['obrigatoria'] and r['estado']!='Aprovada'])
        if st.button('Gerar relatório Excel atualizado'):
            st.session_state['report_bytes']=core.report()
        if 'report_bytes' in st.session_state:
            st.download_button('Baixar relatório Excel (dados pessoais: mantenha em local protegido)',st.session_state['report_bytes'],file_name='pendencias_portfolios.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
except sqlite3.IntegrityError:
    obs.emit('operation_failed','ui',logging.ERROR,sys.exc_info())
    st.error('Cadastro ou associação duplicada ou inválida. Desvincule a foto anterior para substituí-la; matrículas devem ser únicas.')
except sqlite3.Error:
    obs.emit('database_failed','ui',logging.ERROR,sys.exc_info())
    st.error('Não foi possível acessar o banco local. Tente novamente ou consulte o diagnóstico.')
except (ValueError,OSError):
    obs.emit('operation_failed','ui',logging.ERROR,sys.exc_info())
    st.error('Não foi possível concluir. Confira os dados, o formato da imagem e as permissões da pasta.')
except Exception:
    # Fronteira final: registra exceções inesperadas e interrompe a ação com mensagem segura.
    # Sinais de controle do Streamlit derivam de BaseException e não são capturados.
    obs.emit('operation_failed','ui',logging.ERROR,sys.exc_info())
    st.error('Ocorreu uma falha inesperada. Consulte o diagnóstico técnico antes de tentar novamente.')
