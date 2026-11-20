"""Tela Streamlit e ponte para o componente SVG local."""
import base64
import copy
import io
import uuid
from pathlib import Path
import streamlit as st
from PIL import Image,ImageOps
from src import core, pedagogy
from src.rendering import typography
from src.template_editor import model
from src.rendering.preview import render_preview

HERE=Path(__file__).parent
_component=st.components.v2.component('portfolio_template_editor',
    html=(HERE/'editor.html').read_text(encoding='utf-8-sig'),
    css=(HERE/'editor.css').read_text(encoding='utf-8-sig'),
    js=(HERE/'editor.js').read_text(encoding='utf-8-sig'))


def _background_uri(template):
    with Image.open(model.background_path(template['background']['file'])) as im:
        image=ImageOps.exif_transpose(im).convert('RGB')
        image.thumbnail((1400,6000))
        output=io.BytesIO();image.save(output,format='JPEG',quality=88)
    return 'data:image/jpeg;base64,'+base64.b64encode(output.getvalue()).decode('ascii')


def show():
    st.subheader('Editor de Templates')
    st.caption('Importe sua arte pronta. Desenhe regiões sobre o fundo; nenhuma arte é gerada pelo sistema.')
    if 'editor_flash' in st.session_state:
        st.success(st.session_state.pop('editor_flash'))
    ids=model.list_templates()
    labels={}
    for identifier in ids:
        try:
            saved=model.load_template(identifier)
            labels[identifier]=f"{saved['name']} · v{saved['version']} · {identifier[:8]}"
        except (ValueError,OSError):
            labels[identifier]='Template indisponível · '+identifier[:8]
    with st.expander('Abrir um template salvo',expanded='editor_template' not in st.session_state):
        selected=st.selectbox('Template salvo',ids,format_func=labels.get) if ids else None
        if selected and st.button('Abrir template'):
            st.session_state.editor_template=model.load_template(selected)
            st.session_state.editor_token=uuid.uuid4().hex
            st.session_state.pop('editor_preview',None)
            st.rerun()
    catalog=pedagogy.load_catalog()
    projects=core.rows('SELECT * FROM projects ORDER BY id')
    project_map={0:'Abertura geral',**{p['id']:p['title'] for p in projects}}
    with st.expander('Criar template a partir de uma arte'):
        with st.form('new_template'):
            upload=st.file_uploader('Arte de fundo (PNG, JPEG ou WebP)',type=['png','jpg','jpeg','webp'])
            name=st.text_input('Nome do novo template',max_chars=120)
            project=st.selectbox('Projeto associado',list(project_map),index=1,format_func=project_map.get)
            if st.form_submit_button('Importar arte e criar rascunho'):
                if not upload or not name.strip():
                    st.warning('Selecione uma arte e informe o nome.')
                else:
                    background=model.import_background(upload.getvalue())
                    st.session_state.editor_template=model.new_template(background,project,name.strip())
                    st.session_state.editor_token=uuid.uuid4().hex
                    st.session_state.pop('editor_preview',None)
                    st.rerun()
    if 'editor_template' not in st.session_state:
        st.info('Importe uma arte ou abra um template para começar.')
        return
    template=st.session_state.editor_template
    st.write(f"{template['name']} · {project_map[template['project_id']]} · versão salva {template['version']}")
    st.caption('As coordenadas usam porcentagens da arte. Zoom e rolagem não alteram as posições. Salve antes de abrir ou criar outro template.')
    st.caption('Use Preencher textos do projeto para vincular textos vazios à referência e inserir introdução e legendas ausentes. As legendas usam o texto após a orientação FOTO, sem incluir essa orientação. Confira as posições e salve o template.')
    new_name=st.text_input('Nome do template em edição',template['name'],key='template_name_'+st.session_state.editor_token,max_chars=120)
    mode=st.radio('Dados da prévia',['Sintéticos (sem evidências reais)','Aluno real — somente local'])
    sid=None
    if mode.startswith('Aluno real'):
        students=core.rows('SELECT id,name FROM students ORDER BY name')
        mapping={s['id']:s['name'] for s in students}
        sid=st.selectbox('Aluno para prévia local',list(mapping),format_func=mapping.get) if mapping else None
        st.warning('Prévia local: somente fotos aprovadas. Não compartilhe capturas com dados da criança.')
        if sid is None: st.info('Cadastre um aluno para usar esta opção.');return
    requirements=core.rows('SELECT id,description FROM requirements WHERE project_id=? ORDER BY id',(template['project_id'],))
    for req in requirements:
        a,b=req['id'].split('-');req['alias']=f'P{int(a):02d}_F{int(b):02d}'
    fields=pedagogy.text_fields(template['project_id'],catalog)
    effective_fields=[]
    for key,field in fields.items():
        text,level=pedagogy.resolve_text(key,sid,catalog)
        effective_fields.append(dict(id=key,type=field['type'],text=text,level=level,
            label=pedagogy.field_label(key),group=pedagogy.field_group(key)))
    section=catalog['sections'][pedagogy.section_for(template['project_id'],catalog)]
    if section.get('missing'):
        st.info('Campos ausentes no original (não serão inventados): '+', '.join(section['missing']))
    result=_component(data=dict(token=st.session_state.editor_token,regions=template['regions'],
        project_id=template['project_id'],projects=[dict(id=k,label=f'Projeto {k} — {v}' if 1<=k<=10 else v) for k,v in project_map.items()],
        image=_background_uri(template),width=template['background']['width'],height=template['background']['height'],
        types=list(model.TYPES),requirements=requirements,fields=effective_fields,
        fonts=typography.families(),presets={kind:typography.preset(kind) for kind in model.TYPES}),key='visual_'+st.session_state.editor_token,
        on_save_change=lambda:None,on_preview_change=lambda:None,on_fill_change=lambda:None,on_project_change=lambda:None)
    project_change=result.get('project')
    if project_change:
        draft=copy.deepcopy(template)
        draft['regions']=project_change['regions']
        draft['name']=new_name.strip()
        try:
            draft=model.change_project(draft,project_change['project_id'])
        except ValueError:
            # Mensagens locais fixas do modelo; nunca texto de arquivo ou servico externo.
            st.warning('Não foi possível trocar o projeto. Ele precisa ter os mesmos campos de texto e requisitos fotográficos usados nas regiões atuais. Ajuste as regiões ou crie outro template.')
        else:
            st.session_state.editor_template=draft
            st.session_state.editor_token=uuid.uuid4().hex
            st.session_state.pop('editor_preview',None)
            st.session_state.editor_flash='Projeto alterado no rascunho. Confira os vínculos e salve o template.'
            st.rerun()
    fill=result.get('fill')
    if fill:
        draft=copy.deepcopy(template)
        draft['regions']=fill['regions']
        draft['name']=new_name.strip()
        draft,messages=model.fill_project_texts(draft)
        st.session_state.editor_template=draft
        st.session_state.editor_token=uuid.uuid4().hex
        image,warnings=render_preview(draft,sid)
        st.session_state.editor_preview=(image,messages+warnings)
        st.session_state.editor_preview_mode=(mode,sid)
        st.session_state.editor_flash='Textos vinculados no rascunho. Confira a prévia e clique em Salvar template.'
        st.rerun()
    save=result.get('save');preview=result.get('preview')
    if save or preview:
        draft=copy.deepcopy(template)
        draft['regions']=(save or preview)['regions']
        draft['name']=new_name.strip()
        model.validate_template(draft)
        if save:
            saved=model.save_template(draft)
            st.session_state.editor_template=saved
            st.session_state.editor_flash=f"Template salvo — versão {saved['version']}."
        else:
            st.session_state.editor_template=draft
        st.session_state.editor_preview=render_preview(draft,sid)
        st.session_state.editor_preview_mode=(mode,sid)
        if save:
            st.rerun()
    if 'editor_preview' in st.session_state:
        if st.session_state.get('editor_preview_mode')!=(mode,sid):
            st.info('Clique em Atualizar prévia para usar os dados selecionados.')
        else:
            image,messages=st.session_state.editor_preview
            st.image(image,caption='Pré-visualização local — não é um portfólio final',use_container_width=True)
            for message in messages: st.warning(message)
    with st.expander('Textos pedagógicos — original, edição global e personalização',expanded=True):
        st.caption('Prioridade: personalização individual > edição global > original. Alterações globais preservam as personalizações. Sublinhados são substituídos pelo primeiro nome apenas na prévia do aluno.')
        field_id=st.selectbox('Campo pedagógico para editar',list(fields),format_func=lambda key:pedagogy.field_label(key)+' · '+key,key='pedagogy_field_'+st.session_state.editor_token)
        if field_id:
            field=fields[field_id]
            st.text_area('Texto original da professora',field['text'],disabled=True,key='original_'+field_id)
            st.caption(f"Origem: referência local, linhas {field['origin']['start_line']}–{field['origin']['end_line']}. Revise a associação antes de usar.")
            scope=st.radio('Alcance da edição',['Global — todos os alunos','Individual — aluno da prévia'],key='text_scope')
            edit_sid=sid if scope.startswith('Individual') else None
            if scope.startswith('Individual') and sid is None:
                st.info('Selecione Aluno real e o aluno na área de prévia para personalizar.')
            else:
                current=pedagogy.current_edit(field_id,edit_sid)
                revision=current['id'] if current else 0
                text,level=pedagogy.resolve_text(field_id,edit_sid,catalog)
                st.caption('Conteúdo efetivo: '+level+'. Edições e restaurações preservam histórico.')
                if edit_sid is None:
                    st.info('Edições globais não substituem os campos já personalizados por aluno.')
                key=f'edit_{field_id}_{edit_sid}_{revision}'
                with st.form('form_'+key):
                    edited=st.text_area('Texto editável',text,key=key,max_chars=10000,height=180)
                    save_text=st.form_submit_button('Salvar edição de texto')
                if save_text:
                    pedagogy.save_text(field_id,edited,edit_sid,revision)
                    st.session_state.pop('editor_preview',None)
                    st.session_state.editor_flash='Texto salvo. Atualize a prévia para conferir.'
                    st.rerun()
                if st.button('Restaurar texto original neste alcance'):
                    # Individual recebe copia do original, independente da edicao global.
                    pedagogy.save_text(field_id,field['text'] if edit_sid else None,edit_sid,revision)
                    st.session_state.pop('editor_preview',None)
                    st.rerun()
                if edit_sid and st.button('Remover personalização e seguir texto global/original'):
                    pedagogy.save_text(field_id,None,edit_sid,revision)
                    st.session_state.pop('editor_preview',None)
                    st.rerun()
                revisions=pedagogy.history(field_id,edit_sid)
                if revisions:
                    selected_revision=st.selectbox('Revisão para recuperar',[row['id'] for row in revisions],format_func=lambda value:next(f"Revisão {r['id']} · {r['created']} UTC" for r in revisions if r['id']==value))
                    previous=next(row for row in revisions if row['id']==selected_revision)
                    st.text_area('Conteúdo da revisão',previous['text'] if previous['text'] is not None else '[Edição removida: seguir precedência]',disabled=True,key=f'history_{field_id}_{selected_revision}')
                    if st.button('Recuperar revisão selecionada'):
                        pedagogy.save_text(field_id,previous['text'],edit_sid,revision)
                        st.session_state.pop('editor_preview',None)
                        st.rerun()
        if st.button('Reimportar referência local preservando edições'):
            pedagogy.import_catalog()
            st.session_state.pop('editor_preview',None)
            st.rerun()
