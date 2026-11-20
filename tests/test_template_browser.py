"""Verificação opcional de navegador, sem dados reais nem arte externa."""
import io
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.request
import pytest
from PIL import Image


@pytest.fixture
def semantic_server(tmp_path):
    from test_pedagogy import synthetic_source
    root=Path(__file__).resolve().parents[1]
    source=tmp_path/'source.txt';source.write_text(synthetic_source(),encoding='utf-8')
    env=dict(os.environ,PORTFOLIO_DATA_DIR=str(tmp_path/'data'),PORTFOLIO_LOG_DIR=str(tmp_path/'logs'),PORTFOLIO_CONTENT_FILE=str(source))
    with socket.socket() as sock:
        sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
    def start():
        process=subprocess.Popen([sys.executable,'-m','streamlit','run','app.py','--server.address','127.0.0.1','--server.port',str(port),'--server.headless','true','--browser.gatherUsageStats','false'],cwd=root,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        for _ in range(100):
            try:
                with urllib.request.urlopen(f'http://127.0.0.1:{port}/_stcore/health',timeout=1): return process
            except OSError: time.sleep(.2)
        process.terminate();process.wait(timeout=15)
        raise RuntimeError('Servidor sintetico indisponivel')
    processes=[]
    def boot():
        process=start();processes.append(process);return process
    try:
        yield f'http://127.0.0.1:{port}',boot
    finally:
        for process in processes:
            if process.poll() is None:process.terminate();process.wait(timeout=15)


def test_semantic_p04_create_style_save_restart_reopen(tmp_path,semantic_server):
    import json
    playwright=pytest.importorskip('playwright.sync_api')
    url,boot=semantic_server;process=boot()
    with playwright.sync_playwright() as p:
        try: browser=p.chromium.launch(headless=True)
        except playwright.Error:pytest.skip('Chromium nao instalado')
        page=browser.new_page(viewport={'width':1500,'height':1100})
        page.goto(url)
        page.get_by_text('Editor de Templates',exact=True).click()
        page.get_by_text('Criar template a partir de uma arte',exact=True).click()
        content=io.BytesIO();Image.new('RGB',(400,1200),'white').save(content,format='PNG')
        page.locator('input[type=file]').set_input_files({'name':'synthetic.png','mimeType':'image/png','buffer':content.getvalue()})
        page.get_by_label('Nome do novo template',exact=True).fill('SEMANTICO SINTETICO P04')
        page.locator('[data-testid="stSelectbox"]').filter(has=page.get_by_text('Projeto associado',exact=True)).get_by_role('combobox').click()
        page.get_by_role('option',name='MÃOS NA TERRA, CORAÇÃO NA NATUREZA',exact=True).click()
        page.get_by_role('button',name='Importar arte e criar rascunho',exact=True).click()
        page.get_by_label('Tipo antes de desenhar',exact=True).wait_for(timeout=20000)
        svg=page.locator('svg[aria-label="Imagem e regiões"]')
        def draw(kind,field,y):
            page.get_by_label('Tipo antes de desenhar',exact=True).select_option(kind)
            page.get_by_label('Campo da nova região',exact=True).select_option(field)
            page.get_by_role('button',name='Desenhar região',exact=True).click()
            svg.scroll_into_view_if_needed();box=svg.bounding_box()
            page.mouse.move(box['x']+20,box['y']+y);page.mouse.down()
            page.mouse.move(box['x']+360,box['y']+y+55,steps=5);page.mouse.up()
            page.get_by_label('Tipo',exact=True).wait_for()
        draw('title','P04.title',20)
        assert page.get_by_label('Conteúdo associado',exact=True).input_value()=='TÍTULO SINTÉTICO 4'
        page.get_by_label('Fonte (referência 1080 px)',exact=True).fill('48')
        page.get_by_label('Fonte (referência 1080 px)',exact=True).press('Tab')
        page.get_by_label('Alinhamento',exact=True).select_option('center')
        page.get_by_label('Cor do texto',exact=True).evaluate("e=>{e.value='#145632';e.dispatchEvent(new Event('input',{bubbles:true}))}")
        # Trocar ida/volta entre foto e texto deve recuperar o vinculo textual.
        page.get_by_label('Tipo',exact=True).select_option('photo')
        page.get_by_label('Tipo',exact=True).select_option('title')
        assert page.get_by_label('Campo pedagógico',exact=True).input_value()=='P04.title'
        draw('body_text','P04.introduction',100)
        draw('photo','04-1',180)
        draw('caption','P04.caption_1',260)
        draw('photo','04-2',340)
        draw('caption','P04.caption_2',420)
        assert 'P04.caption_2' in page.get_by_label('Região selecionada',exact=True).inner_text()
        page.get_by_role('button',name='Salvar template',exact=True).click()
        page.get_by_text('Template salvo — versão 1.',exact=True).wait_for(timeout=25000)
        saved=list((tmp_path/'data/templates').glob('*.json'))
        assert len(saved)==1
        original=json.loads(saved[0].read_text(encoding='utf-8'))
        assert len(original['regions'])==6 and original['project_id']==4
        assert original['regions'][0]['text_style']['font_size']==48
        assert original['regions'][0]['text_style']['color']=='#145632'
        assert original['regions'][0]['text_style']['align']=='center'
        # Edicao global pela interface; evidencia fotografica continua ausente.
        page.get_by_role('button',name='Salvar edição de texto',exact=True).wait_for(timeout=20000)
        playwright.expect(page.get_by_label('Texto editável',exact=True)).to_have_value('TÍTULO SINTÉTICO 4')
        page.get_by_label('Texto editável',exact=True).fill('TÍTULO GLOBAL SINTÉTICO')
        page.get_by_label('Texto editável',exact=True).press('Tab')
        page.get_by_role('button',name='Salvar edição de texto',exact=True).click(timeout=15000)
        page.get_by_text('Texto salvo. Atualize a prévia para conferir.',exact=True).wait_for(timeout=20000)
        import sqlite3
        with sqlite3.connect(tmp_path/'data/portfolio.sqlite3') as db:
            assert db.execute('SELECT text FROM pedagogical_edits ORDER BY id DESC LIMIT 1').fetchone()[0]=='TÍTULO GLOBAL SINTÉTICO'
        process.terminate();process.wait(timeout=15)
        boot()
        page.goto(url)
        page.get_by_text('Editor de Templates',exact=True).click()
        page.get_by_role('button',name='Abrir template',exact=True).click()
        page.get_by_label('Região selecionada',exact=True).wait_for(timeout=20000)
        page.get_by_label('Região selecionada',exact=True).select_option(original['regions'][0]['id'])
        assert page.get_by_label('Conteúdo associado',exact=True).input_value()=='TÍTULO GLOBAL SINTÉTICO'
        assert page.get_by_label('Fonte (referência 1080 px)',exact=True).input_value()=='48'
        assert json.loads(saved[0].read_text(encoding='utf-8'))==original
        page.screenshot(path=str(tmp_path/'semantic-reopened.png'))
        import shutil
        shutil.copy2(tmp_path/'semantic-reopened.png',Path(__file__).resolve().parents[1]/'outputs/editor-semantico-sintetico.png')
        browser.close()


def test_visual_editor_mouse_save_reopen(tmp_path):
    playwright=pytest.importorskip('playwright.sync_api')
    root=Path(__file__).resolve().parents[1]
    env=os.environ.copy();env['PORTFOLIO_DATA_DIR']=str(tmp_path/'data');env['PORTFOLIO_LOG_DIR']=str(tmp_path/'logs')
    from test_pedagogy import synthetic_source
    content=tmp_path/'synthetic-content.txt';content.write_text(synthetic_source(),encoding='utf-8')
    env['PORTFOLIO_CONTENT_FILE']=str(content)
    with socket.socket() as listener:
        listener.bind(('127.0.0.1',0));port=listener.getsockname()[1]
    process=subprocess.Popen([sys.executable,'-m','streamlit','run','app.py','--server.address','127.0.0.1','--server.port',str(port),'--server.headless','true','--browser.gatherUsageStats','false'],cwd=root,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    try:
        url=f'http://127.0.0.1:{port}'
        for _ in range(60):
            try:
                urllib.request.urlopen(url+'/_stcore/health',timeout=1).close();break
            except OSError:time.sleep(.25)
        with playwright.sync_playwright() as p:
            try: browser=p.chromium.launch(headless=True)
            except playwright.Error: pytest.skip('Chromium de teste não instalado.')
            page=browser.new_page(viewport={'width':1450,'height':1000})
            page.goto(url)
            page.get_by_text('Editor de Templates',exact=True).click()
            page.get_by_text('Criar template a partir de uma arte',exact=True).click()
            output=io.BytesIO();Image.new('RGB',(400,1200),'white').save(output,format='PNG')
            page.locator('input[type=file]').set_input_files({'name':'synthetic.png','mimeType':'image/png','buffer':output.getvalue()})
            page.get_by_label('Nome do novo template',exact=True).fill('SINTETICO NAVEGADOR')
            page.get_by_role('button',name='Importar arte e criar rascunho',exact=True).click()
            page.get_by_role('button',name='Desenhar região',exact=True).wait_for(timeout=20000)
            page.get_by_role('button',name='Desenhar região',exact=True).click()
            svg=page.locator('svg[aria-label="Imagem e regiões"]')
            box=svg.bounding_box()
            page.mouse.move(box['x']+40,box['y']+80);page.mouse.down();page.mouse.move(box['x']+240,box['y']+260,steps=10);page.mouse.up()
            page.get_by_label('Largura (%)',exact=True).wait_for()
            assert float(page.get_by_label('Largura (%)',exact=True).input_value())==pytest.approx(50,abs=.1)
            # Movimento com o mouse e redimensionamento pela alça.
            page.mouse.move(box['x']+100,box['y']+160);page.mouse.down();page.mouse.move(box['x']+120,box['y']+180,steps=5);page.mouse.up()
            assert float(page.get_by_label('X (%)',exact=True).input_value())==pytest.approx(15,abs=.2)
            handle=svg.locator('[data-handle="resize"]').bounding_box()
            page.mouse.move(handle['x']+handle['width']/2,handle['y']+handle['height']/2);page.mouse.down();page.mouse.move(handle['x']+handle['width']/2+30,handle['y']+handle['height']/2+30,steps=5);page.mouse.up()
            assert float(page.get_by_label('Largura (%)',exact=True).input_value())>55
            page.get_by_label('X (%)',exact=True).fill('20')
            page.get_by_label('X (%)',exact=True).press('Tab')
            assert float(page.get_by_label('X (%)',exact=True).input_value())==20
            page.get_by_label('Enquadramento',exact=True).select_option('cover')
            page.get_by_label('Zoom',exact=True).evaluate("e=>{e.value='1.5';e.dispatchEvent(new Event('input',{bubbles:true}))}")
            assert svg.bounding_box()['width']==pytest.approx(600,abs=1)
            page.get_by_label('Zoom',exact=True).evaluate("e=>{e.value='1';e.dispatchEvent(new Event('input',{bubbles:true}))}")
            page.get_by_label('Nome do template em edição',exact=True).fill('SINTETICO EDITADO')
            page.get_by_label('Nome do template em edição',exact=True).press('Enter')
            page.get_by_role('button',name='Salvar template',exact=True).click()
            page.get_by_text('Template salvo — versão 1.',exact=True).wait_for(timeout=20000)
            import json
            saved=list((tmp_path/'data/templates').glob('*.json'))
            assert len(saved)==1
            template=json.loads(saved[0].read_text(encoding='utf-8'))
            assert len(template['regions'])==1 and template['background']['height']==1200 and template['name']=='SINTETICO EDITADO'
            assert template['regions'][0]['x']==pytest.approx(.2) and template['regions'][0]['fit']=='cover'
            if not page.get_by_role('button',name='Abrir template',exact=True).is_visible():
                page.get_by_text('Abrir um template salvo',exact=True).click()
            page.get_by_role('button',name='Abrir template',exact=True).click()
            page.get_by_role('button',name='Selecionar / mover',exact=True).wait_for(timeout=20000)
            playwright.expect(svg.locator('rect[data-id]')).to_have_count(1,timeout=15000)
            # Segunda região pode ser desenhada e excluída visualmente.
            page.get_by_role('button',name='Desenhar região',exact=True).click()
            box=svg.bounding_box();page.mouse.move(box['x']+280,box['y']+100);page.mouse.down();page.mouse.move(box['x']+360,box['y']+160,steps=5);page.mouse.up()
            page.get_by_role('button',name='Excluir região',exact=True).click()
            playwright.expect(svg.locator('rect[data-id]')).to_have_count(1,timeout=15000)
            page.screenshot(path=str(tmp_path/'editor-synthetic.png'))
            import shutil
            (root/'outputs').mkdir(exist_ok=True)
            shutil.copy2(tmp_path/'editor-synthetic.png',root/'outputs/editor-template-sintetico.png')
            browser.close()
    finally:
        process.terminate();process.wait(timeout=15)
