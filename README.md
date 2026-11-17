# Portfólios pedagógicos 2026 — MVP 1

Aplicação local para cadastro, organização e aprovação de fotografias. Os documentos originais permanecem intactos. Não gera PDFs nem publica informações.

## Instalar e executar no Windows

Abra o PowerShell neste diretório, com Python 3.11 ou compatível:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.maxUploadSize 30 --browser.gatherUsageStats false
```

Abra http://127.0.0.1:8501. Para usar `iniciar.ps1`, ative o ambiente antes ou execute o mesmo comando acima. Encerre com Ctrl+C.

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
