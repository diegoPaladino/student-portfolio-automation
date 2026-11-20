# Portfólios pedagógicos 2026 — MVP 1

Aplicação local para cadastro, organização e aprovação de fotografias. Os documentos originais permanecem intactos. Não gera PDFs nem publica informações.

## Instalar e executar no Windows

Na primeira execucao, abra `INSTALAR_AMBIENTE.bat`. Depois use
`INICIAR_PORTFOLIOS.bat` para abrir o dashboard automaticamente no navegador.
Mantenha a janela aberta. Para encerrar, salve rascunhos e pressione **Ctrl+C
nessa janela**. Fechar somente a aba do navegador nao encerra o servidor.

O preparo procura o ambiente ativo (`VIRTUAL_ENV`) e ambientes na raiz com
`pyvenv.cfg`, independentemente do nome. Sem ambiente, cria `.venv` com Python
3.11 ou superior disponivel no PATH, aproveitando pacotes do Python de origem
via `--system-site-packages`. Mantenha esse Python instalado. Se faltarem
requisitos, o instalador usa pip e exige rede. O uso cotidiano nunca instala
pacotes. Pytest e ferramenta de desenvolvimento: sua versao nao bloqueia o uso
cotidiano; instale requirements.txt para adequar o ambiente de testes.

O inicializador executa `app.py` em 127.0.0.1, escolhendo porta entre 8501 e 8600.
Aguarda HTTP 200/ok antes de solicitar abertura do navegador. Se ele nao abrir,
use o endereco exibido. Outra execucao reutiliza a instancia do inicializador.
Servidores iniciados manualmente nao possuem essa identidade: encerre-os antes
de migrar para o novo inicializador, pois podem usar o mesmo banco. Outros
aplicativos nao sao encerrados. Nao apague outputs/launcher.lock ou
outputs/launcher.port durante o uso. A porta e removida no encerramento normal.
Evite fechar a janela a forca; use Ctrl+C para finalizar tambem o processo filho.

Falhas ficam em logs/errors.log (ou PORTFOLIO_LOG_DIR), sem saida bruta do
Streamlit. `iniciar.ps1` usa o mesmo fluxo. E necessario acesso de escrita ao
projeto. Python continua necessario: nao se trata de executavel independente.

Alternativa tecnica apos o preparo:

```powershell
.\.venv\Scripts\python.exe -m src.launcher
.\.venv\Scripts\python.exe -m src.launcher --check
```

1. Abra **Alunos** e clique em **Importar lista original de alunos**. Importações repetidas não duplicam matrículas; nomes existentes só mudam pela edição explícita.
2. Em **Importar e classificar**, selecione fotografias ou informe uma pasta local. A importação por pastas percorre subpastas. JPEG, PNG e WEBP são aceitos, até 30 MB cada.
3. Confira a prévia, escolha a criança e o campo pedagógico e associe. Toda classificação é manual; não existe reconhecimento facial nem inferência de identidade pelo arquivo.
4. Em **Revisar evidências**, escolha a situação e salve. Só **Aprovada** conta. Para substituir uma foto, desvincule a anterior e classifique outra.
5. Consulte o aluno, a turma e baixe o Excel em **Relatório de pendências**.

Cada aluno precisa de 20 fotos nos projetos, quatro na síntese e uma no encerramento. A síntese aceita seis fotos, mas as duas adicionais não aumentam o denominador de 25. Uma foto não pode preencher dois campos do mesmo aluno. Pode ser associada a alunos diferentes, mediante conferência manual.

## Dados locais e cópia de segurança

SQLite: `data/portfolio.sqlite3`. Originais importados: `data/images/`, com nomes internos por hash e caminhos relativos. As origens não são alteradas. Pré-visualizações são reduzidas em memória, corrigindo a orientação EXIF. A importação não remove metadados dos originais.

Feche o aplicativo antes de copiar **toda a pasta data**, preservando banco e imagens juntos. Para restaurar, feche o aplicativo e restaure essa pasta. `PORTFOLIO_DATA_DIR` permite escolher outro diretório persistente antes de iniciar. Não compartilhe banco, fotos, lista de alunos ou relatórios; use conta Windows protegida e proteção de disco. O banco não é criptografado pela aplicação. Excel contém nomes, sem matrículas.

## Verificar

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Testes usam apenas dados sintéticos e diretórios temporários. A aplicação é local e não usa serviços externos. Instalar dependências exige acesso ao repositório de pacotes, mas não envia dados pedagógicos.

Consulte `docs/PRD_PORTFOLIO_2026.md`, `docs/ARQUITETURA.md` e `docs/PLANO_MVPS.md`. Pasta `outputs` fica reservada às saídas futuras; relatórios atuais são baixados pelo navegador. Pasta `images` fica reservada a recursos visuais futuros, sem fotografias reais.

## Logs, diagnóstico e validação contínua

Os logs locais ficam em `logs/app.log` (eventos e erros), `logs/errors.log` (ERROR/CRITICAL) e `logs/audit.jsonl` (operações confirmadas). Cada linha é JSON, com data/hora e fuso. Consulte os erros recentes no PowerShell:

```powershell
Get-Content .\logs\errors.log -Tail 30
Get-Content .\logs\audit.jsonl -Tail 30
python -m src.diagnostics
python -m src.validate
```

Use o Python do ambiente virtual, se criado (`.\.venv\Scripts\python.exe -m src.diagnostics`, por exemplo). O diagnóstico grava `outputs/diagnostico.json`: versão-base Git, Python, sistema operacional, acesso de leitura ao banco, contagens, auditorias pendentes, resumo de testes disponível e erros recentes sanitizados. Não inicializa banco ausente. A versão Git identifica o último commit; alterações locais ainda não commitadas devem ser consideradas ao comparar resultados. O relatório não contém nomes, matrículas, fotos, conteúdo de arquivos, stack ou caminhos pessoais. Pode ser gerado em outro destino com `--output`.

`python -m src.validate` executa toda a suíte, retorna o código de saída do pytest e preserva resultados em `outputs/test-summary-<execução>.json`, o resumo mais recente em `outputs/test-summary.json` e JUnit XML local por execução. O XML pode conter detalhes técnicos de testes; não o publique automaticamente. `python -m pytest -q` continua disponível, mas não atualiza o resumo persistente. Nenhum desses comandos marca uma validação manual como concluída.

`docs/VALIDACAO.md` mantém entradas históricas com comandos e resultados observados. **APROVADO** significa verificação realizada com sucesso; **REPROVADO**, falha observada; **NÃO TESTADO**, sem execução; **BLOQUEADO**, execução impedida. Consulte a entrada mais recente e suas pendências antes de mudar o código. Registros anteriores não são substituídos.

Configuração por variáveis de ambiente, definida antes de iniciar o processo:

```powershell
$env:PORTFOLIO_LOG_LEVEL = 'WARNING'
$env:PORTFOLIO_LOG_MAX_BYTES = '2097152'
$env:PORTFOLIO_LOG_BACKUPS = '5'
python -m streamlit run app.py --server.address 127.0.0.1 --browser.gatherUsageStats false
```

Níveis: DEBUG, INFO (padrão), WARNING, ERROR, CRITICAL ou OFF. OFF desativa os logs técnicos; a auditoria transacional continua ativa. Cada arquivo tem limite padrão de 2 MiB e cinco cópias rotacionadas; uma linha individual pode ultrapassar o limite. Retenção é por número de arquivos, não por dias. `PORTFOLIO_LOG_DIR` altera o destino. Quando `PORTFOLIO_DATA_DIR` aponta para outra pasta, o padrão de logs passa a ser `<pasta de dados>/logs`. Reinicie o aplicativo após alterar as variáveis.

Logs usam mensagens de um catálogo fechado e nunca interpolam dados recebidos. Exceções técnicas guardam tipo e sequência de módulos/linhas, sem mensagem original, argumentos, código-fonte ou caminhos. `correlation_id` conecta falhas de uma chamada de serviço. O shutdown só é detectado quando o processo Python encerra normalmente; fechar a aba ou encerrar à força não garante evento.

Auditoria distingue recebimento, classificação, aprovação, rejeição, desvinculação, substituição confirmada e geração de Excel. “Relatório exportado” confirma bytes Excel gerados; não confirma que o navegador salvou o download. Clique em **Gerar relatório Excel atualizado** para preparar o arquivo; navegar ou reexecutar a tela não gera exportações repetidas. O download conserva a versão preparada até nova geração.

Eventos pendentes ficam no SQLite se houver falha na escrita do JSONL e são tentados novamente no próximo acesso bem-sucedido ao banco. O banco é a fonte de verdade. Uma interrupção entre escrita do JSONL e confirmação da entrega pode repetir uma linha com o mesmo `event_id`; consumidores devem deduplicar pelo identificador dentro do mesmo banco. Rotação limita o JSONL; o histórico e o outbox permanecem no SQLite. Uso suportado: um processo local do aplicativo. Não abrir vários servidores escrevendo nos mesmos logs.

## Editor de Templates — MVP 2, etapa 1

O editor agora oferece vínculos pedagógicos, edição global/individual com histórico e controles tipográficos. Consulte o [guia do editor semântico](docs/EDITOR_SEMANTICO.md) para o fluxo completo, restauração e limites.

Abra **Editor de Templates** no menu. A arte deve estar pronta: esta aplicação não gera fundos Low Poly 3D.

1. Expanda **Criar template a partir de uma arte**, selecione PNG/JPEG/WebP (até 30 MB e 40 megapixels), informe o nome e o projeto e clique em **Importar arte e criar rascunho**. A proporção e a altura da arte são preservadas; não há formato 9:16 obrigatório.
2. Clique em **Desenhar região** e arraste o mouse sobre o fundo. Depois use **Selecionar / mover**: arraste a região para deslocá-la ou o quadrado inferior direito para redimensioná-la. Use zoom, barras de rolagem e **Ver arte inteira** para navegar.
3. Escolha **Tipo antes de desenhar** e **Campo da nova região** antes de arrastar. Tipos: `title`, `subtitle`, `body_text`, `photo`, `caption`, `highlight`, `student_name`. A lista identifica tipo e vínculo. Fotos usam um requisito do projeto, exibido como `P04_F01`, correspondente a `04-1` no catálogo existente. `contain` mostra a foto inteira; `cover` recorta para preencher e permite ajustar o foco horizontal/vertical. A ordem das regiões controla a sobreposição.
4. Clique em **Atualizar prévia**. O modo sintético exibe marcadores explicitamente demonstrativos, sem gerar evidências. O modo aluno real é somente local, usa o primeiro nome como nome de uso e exclusivamente suas fotos aprovadas. Campos sem aprovação são marcados como ausentes. Textos não são inventados: preencha os conteúdos literais quando necessários. Textos maiores que a região são cortados com aviso.
5. Clique em **Salvar template**. Abra **Abrir um template salvo**, selecione o identificador e clique em **Abrir template** para editar novamente. Salve antes de criar ou abrir outro template. Trocar a seleção de aluno exige clicar em **Atualizar prévia**; nenhuma prévia é salva em arquivo pelo aplicativo.

Fundos originais ficam em `assets/backgrounds/`, com nomes por hash e bytes preservados; o editor usa uma cópia visual corrigida por EXIF. Configurações ficam em `data/templates/<id>.json` e revisões imutáveis em `data/templates/versions/`. Com `PORTFOLIO_DATA_DIR` alternativo, os fundos ficam em `<dados>/assets/backgrounds/`. Faça backup dos templates junto com os fundos, além do banco. Artes, templates e capturas locais estão excluídos do Git. Não publique templates que contenham textos pessoais.

O componente JavaScript/SVG local usa a API v2 do Streamlit 1.53 ou superior, sem CDN, npm, serviço externo ou biblioteca adicional de execução. A suíte principal testa modelo, composição e regressões. Para também executar o teste opcional de mouse em Chromium:

```powershell
python -m pip install playwright
python -m playwright install chromium
python -m src.validate
```

Sem Playwright/Chromium, o teste de navegador é marcado como ignorado; isso não valida interação visual. Uma captura sintética da última execução local fica em `outputs/editor-template-sintetico.png`. Não é arte-matriz nem evidência. A validação em navegador foi feita com dados sintéticos e uma imagem branca de teste.

Limites desta etapa: sem PDF, lote, transições automáticas ou prévia contínua de vários módulos; sem rich text ou corte arrastável da própria foto. O enquadramento usa controles de foco em porcentagem. A interface abre a revisão atual; versões anteriores são preservadas para recuperação técnica, sem seletor de histórico. Use armazenamento local com suporte a hard links (como NTFS); pastas de rede/FAT não foram validadas. Em falha de gravação, arquivos temporários e snapshots são preservados, e nova tentativa pode pular um número de versão. Fechar o navegador perde rascunhos não salvos.
