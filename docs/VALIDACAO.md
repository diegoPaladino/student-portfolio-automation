# Validação do MVP 1

Execução local em Python 3.11.3: `python -m pytest -q` — **8 testes aprovados**, última execução em 7,44 segundos.

Cobertura exercitada com dados sintéticos: lista de alunos repetida e edição, matrícula única, catálogo idempotente de 12 seções/27 campos/25 obrigatórios, preservação binária e hash de imagens, rejeição de conteúdo inválido, proteção de caminhos, associações únicas, estados não aprovados sem progresso, aprovação e reabertura do banco, conclusão total incluindo síntese opcional, rejeição e desvinculação, pastas com arquivo inválido/duplicado e Excel vazio/preenchido com cinco abas.

Streamlit AppTest abriu as seis telas com aluno e fotografia sintéticos, selecionou Aprovada na revisão, salvou pela interface e confirmou incremento da completude no banco. Não substitui avaliação de usabilidade pela professora nem valida correspondência pedagógica de fotos reais.

Inicialização real local concluída: 26 alunos importados da lista original; 27 campos de evidência; nenhuma fotografia real importada ou enviada. Documentos de referência preservados. Relatórios não contêm matrículas. Não foram implementados PDF, geração em lote ou publicação.


---

## Validação incremental — logs, diagnóstico e continuidade

- Data/hora do registro: 2026-11-17T16:24:22-03:00 (America/Sao_Paulo).
- Base Git: `97fd03c2eeccc20faba426d8435af78382791975`; árvore local modificada, melhorias ainda sem commit. Esse hash identifica a base, não um commit das melhorias.
- Ambiente: Windows 10; Python 3.11.3; bibliotecas instaladas no ambiente local, sem dependências novas.
- **APROVADO — suíte automatizada**: `python -m src.validate`; última execução concluída em 2026-11-17T19:23:10.070893+00:00; **22 aprovados, 0 reprovados, 0 ignorados, 0 erros**, exit code 0; pytest informou 12,44 segundos. Comandos anteriores de regressão: `python -m pytest -q` (8 e depois 18 aprovados); execuções intermediárias do validador (20 e 21 aprovados). Cada execução do validador preserva JUnit e resumo em outputs, sem substituir artefatos históricos.
- **APROVADO — funcionalidades existentes**: cadastro/importação idempotente, catálogo preservado, imagens sintéticas, associação, persistência de aprovação, completude e cinco abas Excel; navegação pelas seis telas e aprovação via Streamlit AppTest.
- **APROVADO — observabilidade**: configuração idempotente, handlers sem duplicação, rotação e retenção de três arquivos, stack sanitizado, mensagens externas e nomes/caminhos sintéticos omitidos, auditoria estruturada persistente e correlacionada, rollback sem sucesso falso, recuperação de falha de disco simulada, associação a aluno inexistente recusada e registrada, falha de banco e exportação registradas, OFF e configuração inválida, startup único e shutdown normal em subprocesso.
- **APROVADO — interface sob falha**: AppTest simulou ValueError, erro SQLite e RuntimeError; mensagens técnicas sintéticas não apareceram na interface. A tela de relatórios só gera bytes mediante ação explícita e não repete auditoria ao reexecutar.
- **APROVADO — migração**: teste automatizado de banco legado e verificação local conservaram cadastros. Antes de inicializar as tabelas adicionais, foi criado backup SQLite privado em outputs/baseline-before-observability.sqlite3. Banco local continuou com 26 alunos e 27 requisitos; nenhuma foto real usada nos testes.
- **APROVADO — inicialização real do servidor**: processo Streamlit local iniciado com `python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true --browser.gatherUsageStats false`; consulta a `http://127.0.0.1:8501/_stcore/health` retornou HTTP 200 e `ok`. O processo criado exclusivamente para essa verificação foi encerrado depois. Esse teste HTTP verifica o servidor; a execução das telas foi verificada separadamente por AppTest.
- **APROVADO — diagnóstico**: `python -m src.diagnostics` gerou outputs/diagnostico.json, com acesso somente leitura, contagens esperadas, zero auditorias pendentes, resumo de testes disponível e nenhuma configuração inválida. Testes também cobriram banco ausente sem criação e remoção de texto externo no resumo de erros.
- **APROVADO — higiene Git**: `git diff --check` sem erros de whitespace; `git check-ignore` confirmou exclusão de logs/app.log, logs/errors.log, logs/audit.jsonl, outputs/diagnostico.json e data/portfolio.sqlite3.

### Problemas encontrados e correções aplicadas

1. O histórico SQLite anterior não tinha logs persistentes nem diagnóstico. Acrescentados logging centralizado, outbox transacional, exportação JSONL, comandos de diagnóstico e validação.
2. A interface anterior podia exibir o texto bruto de ValueError e não tratava erros SQLite gerais. Mensagens agora são seguras, com detalhes técnicos sanitizados nos logs; exceções de serviço são relançadas, preservando rollback.
3. A exportação era executada em toda reexecução da tela. Agora é explícita, com download dos bytes preparados e evento somente após geração bem-sucedida.
4. Desvincular não significa que uma substituição foi concluída. Eventos separados e marcador transacional distinguem desvinculação e associação posterior ao mesmo campo, mantendo histórico anterior.
5. Durante a implementação, foram detectados caracteres acentuados corrompidos pela passagem de scripts via shell e reconfiguração de logging no callback de saída de testes. Corrigidos UTF-8 e callback de shutdown vinculado ao logger já configurado; suíte final passou após as correções. Registros de teste anteriores foram preservados localmente.

### Pendências e próximas verificações

- **NÃO TESTADO**: revisão visual manual em navegador e avaliação de usabilidade pela professora; não confundir AppTest com essa revisão.
- **NÃO TESTADO**: interrupção real durante commit/escrita, disco fisicamente cheio e execução concorrente de vários processos. Foram testados rollback e falha simulada de escrita; a entrega JSONL continua pelo menos uma vez e pode repetir event_id após interrupção.
- **NÃO TESTADO**: fluxo pedagógico com fotografias reais, intencionalmente fora da suíte sintética; conferir localmente sem publicar dados.
- Limitações conhecidas: auditoria anterior à migração permanece apenas no histórico SQLite; não há reconstrução retroativa do JSONL. Rotação não limpa histórico/outbox do banco. OFF desativa logs técnicos, preservando auditoria. Shutdown abrupto pode não gerar evento. Uso suportado é um processo local.
- Próximas verificações: revisão da professora, simulação controlada de recuperação de backup e observação dos primeiros eventos reais de importação/revisão; nenhuma dessas verificações foi marcada como concluída.
- Nenhum teste final **REPROVADO** ou **BLOQUEADO**. MVPs 2, 3 e 4 não implementados; catálogo pedagógico sem alterações.


---

## MVP 2 — etapa 1: editor visual de templates

- Registro: 2026-11-17T21:43:27-03:00 (fuso local America/Sao_Paulo). Base Git `426db950e0ed6dff4ece018b1a7d11a71616dfce`; árvore local modificada, sem commit desta etapa.
- Ambiente: Windows 10, Python 3.11.3, Streamlit 1.53.0, Pillow. Playwright/Chromium disponíveis para teste; nenhuma dependência nova na execução do aplicativo.
- **APROVADO — suíte completa**: `python -m src.validate`; conclusão 2026-11-18T00:42:40.537704+00:00; **39 aprovados, 0 reprovados, 0 ignorados, 0 erros**, exit code 0; pytest informou 44,89 s. Artefatos JUnit e resumos por execução preservados em outputs.
- **APROVADO — regressões do MVP 1**: testes anteriores mantidos, incluindo cadastro, fotos sintéticas, revisão, completude, Excel, observabilidade e navegação. AppTest agora abre também Editor de Templates. `git diff --exit-code -- src/core.py config/catalog.json src/settings.py` confirmou esses arquivos inalterados.
- **APROVADO — modelo/persistência**: JSON com leitura/serialização, versões, campos desconhecidos preservados, revisão desatualizada recusada, coordenadas normalizadas e limites/NaN, requisitos reais do catálogo com alias P04_F01/04-1 e rejeição de associação a projeto incorreto, fundo original preservado por hash, proteção de caminhos, leitura de JSON corrompido com erro registrado.
- **APROVADO — composição**: fundos verticais 400x1200, horizontais 1000x300 e quadrados 600x600; fotos horizontais, verticais e quadradas em contain/cover; originais inalterados; quatro tipos de texto; aviso de overflow; marcador sintético sem inserir evidência. Prévia de aluno sintético com foto Recebida/Aprovada/Rejeitada confirmou uso exclusivo das aprovadas e indicação de ausência nos outros estados.
- **APROVADO — gravação sob falha**: os.replace foi simulado com erro; template anterior permaneceu legível, snapshot completo foi preservado e nova tentativa salvou revisão seguinte sem sobrescrever versões. Lock serializa saves entre threads do mesmo processo; múltiplos processos continuam fora do uso suportado.
- **APROVADO — navegador real, dados sintéticos**: Chromium iniciou servidor Streamlit em porta local livre, verificou health HTTP, abriu Editor de Templates, importou PNG branco 400x1200, desenhou retângulo com mouse, moveu, redimensionou pela alça, ajustou X numericamente, selecionou cover, mudou zoom e voltou sem distorção, alterou nome, salvou versão 1, verificou JSON, reabriu e excluiu outra região. Captura sintética em outputs/editor-template-sintetico.png; também inspecionada visualmente nesta sessão. Não é teste com arte-matriz real nem foto de criança.
- **APROVADO — diagnóstico do ambiente real**: `python -m src.diagnostics` confirmou 26 alunos, 27 requisitos, zero auditorias pendentes e nenhum problema de configuração. Não houve migração de esquema SQLite nesta etapa.
- **APROVADO — privacidade/versionamento**: git check-ignore confirmou assets/backgrounds, data/templates e a captura em outputs fora do Git. Nenhum original pedagógico foi modificado. Não foram gerados PDFs, artes Low Poly ou fotografias demonstrativas realistas.

### Problemas encontrados e corrigidos

1. Após o primeiro save, a lista de arquivos só aparecia no próximo rerun. O save agora atualiza a sessão e refaz a tela, preservando aviso e prévia.
2. O primeiro teste de upload apontava ao dropzone em vez do input file. Corrigido o seletor do teste.
3. Uma execução intermediária teve 38 aprovados e uma falha de timing: o teste contava a alça de seleção enquanto a reabertura ainda estava em andamento. Corrigida a espera pelo estado renderizado; execução final com 39 aprovados, sem ignorados.
4. Revisão da persistência identificou risco de snapshot parcial e bloqueio de revisão após falha de publicação. Snapshot passou a ser publicado por hard link do temporário completo; tentativas futuras usam números ainda livres. O teste de falha confirma preservação e recuperação.

### Pendências e limites

- **NÃO TESTADO**: artes Low Poly 3D externas reais, fotografia de criança real, avaliação de usabilidade pela professora, dispositivos de toque, navegadores além do Chromium, empacotamento Windows sem Python, disco cheio/interrupção física e armazenamento FAT/rede.
- **NÃO TESTADO**: recuperação de histórico via procedimento manual. Revisões são preservadas, mas a interface só abre a versão atual.
- Não há restauração de rascunho após fechar navegador, editor avançado de fonte, ajuste de recorte arrastando a foto, PDF definitivo, lote, portal, transição automática ou composição contínua entre módulos. Foco fotográfico é ajustado por porcentagens; ordem/sobreposição/transição ficam preparados no JSON. Textos longos são cortados com aviso.
- Próxima verificação recomendada: importar uma arte-matriz real fornecida pela professora e conferir legibilidade, enquadramento e campos antes de planejar PDF. Não ampliar escopo automaticamente.
- Estado final desta etapa: testes executados **APROVADOS**; nenhuma falha final **REPROVADA** ou **BLOQUEADA**. As verificações acima marcadas como NÃO TESTADO permanecem pendentes.


---

## Inicializador Windows - verificacoes locais

- Registro: 2026-11-19T20:48:32-03:00 (America/Sao_Paulo). Base Git `426db950e0ed6dff4ece018b1a7d11a71616dfce`; arvore modificada antes e depois desta tarefa, sem commit do inicializador. Resultados abaixo sao verificacoes locais, nao uma entrega commitada. Alteracoes anteriores preservadas.
- Causa observada: `.venv/Scripts/python.exe` nao existia. Nenhum ambiente virtual identificado na raiz; Python 3.11.3 e Streamlit 1.53.0 estavam instalados no Python do usuario. Entrada confirmada: app.py. Criada .venv por venv --system-site-packages, aproveitando bibliotecas existentes, sem reinstalacao cotidiana.
- **APROVADO - preparacao por PowerShell**: scripts/ambiente.ps1 instalar criou ambiente; repeticao verificou requisitos compativeis sem executar pip. Check de runtime exclui pytest, ferramenta de desenvolvimento.
- **APROVADO - testes automatizados**: .venv/Scripts/python.exe -m src.validate; 42 aprovados, zero falhas/erros/ignorados; 55,87 s, exit 0; resumo persistente em outputs, conclusao 2026-11-19T23:47:26.209322+00:00. Inclui dashboard/AppTest, Editor de Templates, teste Chromium sintetico existente e tres testes novos do inicializador.
- **APROVADO - HTTP em teste automatizado Windows**: servidor real respondeu HTTP 200/ok; socket sintetico ocupou 8501 e servidor escolheu outra porta; segunda chamada reutilizou instancia; CTRL_BREAK encerrou processo filho, removeu estado da porta e deixou o socket de outro aplicativo intacto. Dados e logs do teste foram temporarios/sinteticos.
- **APROVADO - teste unitario de navegador**: mock confirmou uma abertura somente depois de health falhar e depois responder. Nao equivale a revisao manual do navegador padrao.
- **APROVADO - diagnostico somente leitura**: banco acessivel, sem pendencias de auditoria ou problemas de configuracao. Dados reais nao foram usados nos testes.
- **APROVADO - higiene**: git diff --check sem erros; git check-ignore confirmou ambiente, lock, logs e banco excluidos; lista de arquivos rastreados inspecionada, sem fotografias, bancos, logs ou documentos pessoais. Nenhum commit criado.
- **REPROVADO - compatibilidade global de pacotes**: pip check encontrou conflitos preexistentes em pacotes de outros aplicativos (incluindo Pillow, numpy e cachetools); nao foram alterados para evitar afetar outros softwares. Requisitos de execucao deste aplicativo conferidos pelo launcher e suite passaram. Ambiente criado compartilha pacotes do Python de origem e nao e distribuicao isolada.
- **BLOQUEADO - atualizacao de ferramenta de desenvolvimento**: pytest instalado 7.3.1, abaixo de >=8,<10 em requirements.txt. Tentativa inicial de pip nao conseguiu acessar a rede. Suite executada com versao existente, explicitamente fora da faixa declarada. Uso cotidiano nao depende de pytest.
- Corrigido durante desenvolvimento: leitor de requirements passou a aceitar BOM UTF-8. Primeira rodada teve 2 falhas e 1 aprovado; apos correcao, 3/3 novos testes e suite completa 42/42 passaram. Logs sanitizados dessa tentativa preservados localmente.
- **NAO TESTADO**: duplo clique no Windows Explorer, revisao manual do navegador padrao, maquina Windows limpa, ausencia total de Python, perda fisica de energia e encerramento forcado da janela. Fechar a aba nao encerra servidor; usar Ctrl+C na janela original. Servidores iniciados manualmente nao sao identificados pelo lock: devem ser encerrados antes da adocao do inicializador.
- Nenhuma alteracao pedagogica, de layout, de esquema do banco ou de servicos do editor nesta tarefa.

- **APROVADO - arquivo de preparo BAT**: cmd.exe /c INSTALAR_AMBIENTE.bat retornou 0 e confirmou requisitos compativeis duas vezes; nao acionou pip. Esta verificacao por terminal nao valida duplo clique no Explorer.

---

## MVP 2 — editor semântico e textos pedagógicos

- Registro: 2026-11-19T21:46:02-03:00 (America/Sao_Paulo). Base Git `426db950e0ed6dff4ece018b1a7d11a71616dfce`. Árvore já modificada antes desta tarefa e continua modificada, com arquivos novos; sem commit desta melhoria. Alterações anteriores preservadas. Os resultados abaixo são verificações locais, não uma entrega commitada.
- **APROVADO — suíte automatizada final**: `.venv/Scripts/python.exe -m src.validate`; 48 aprovados, 0 reprovados, 0 erros, 1 ignorado, exit code 0, 72,40 s. Conclusão em 2026-11-20T00:45:41.111763+00:00. Resumo e JUnit por execução preservados em outputs. Python 3.11.3, Streamlit 1.53.0; pytest 7.3.1 compartilhado permanece abaixo da faixa declarada, conforme limitação já registrada. Nenhuma instalação adicional nesta tarefa.
- **NÃO TESTADO nesta execução — teste ignorado**: teste Windows do inicializador que precisa reservar 8501; a porta já estava ocupada. Nenhum processo existente foi encerrado. Os outros testes do inicializador passaram; a validação anterior de porta/reutilização continua registrada acima.
- **APROVADO — catálogo, testes sintéticos**: importação de 13 seções, redação e pontuação preservadas, parágrafos, sublinhados vinculados ao nome, linhas de origem, campos ausentes, exclusão de comentário editorial dos textos de composição, descrições fotográficas distintas de legendas, reimportação sem substituir edições e snapshots locais por hash.
- **APROVADO — persistência e precedência, testes sintéticos**: original/global/individual, atualização global preservando individual, remoção/restauração com histórico preservado, revisão otimista, reabertura SQLite, recusa de campo não textual e aluno inexistente, rollback da edição e da auditoria quando a transação falha. Auditoria usa outbox após commit do banco e não inclui conteúdo textual.
- **APROVADO — templates e composição, testes sintéticos**: sete tipos, campos validados contra a seção, associação aos requisitos existentes, serialização/reabertura, aceitação do esquema 1 e publicação aditiva no esquema 2, fontes instaladas com caracteres portugueses, configurações inválidas recusadas, transbordamento vertical e horizontal, composição alterada pela personalização e ausência de evidências artificiais. Regressões do MVP 1 e do Editor de Templates anterior passaram.
- **APROVADO — HTTP e navegador automatizado Chromium**: o teste anterior de mouse continuou passando. Novo fluxo selecionou Projeto 4, importou fundo branco sintético 400x1200, criou título, abertura, duas fotos com 04-1/04-2 e duas legendas; verificou carregamento automático do texto sintético, preservação do vínculo ao trocar tipo, tamanho 48, cor e alinhamento, salvou seis regiões, editou título global pela interface e confirmou o texto no SQLite. Encerrou somente o servidor do teste, iniciou outro processo e reabriu o template com os mesmos vínculos/estilos e a edição global. Captura local em outputs/editor-semantico-sintetico.png, também inspecionada visualmente nesta sessão. Não é revisão manual interativa pela professora.
- **APROVADO — conferência local da referência real, separada da suíte**: catálogo privado gerado em config/conteudo_pedagogico_2026.json com 91 campos em 13 seções; conferida a correspondência de cada texto com suas linhas no TXT. Campos ausentes permaneceram ausentes. A arte da horta, de 887x1774, foi composta com título, subtítulo, abertura e legendas originais, usando apenas placeholders fotográficos, sem aluno real. PNG local em outputs/editor-p04-revisao-local.png foi inspecionado visualmente. Hashes do TXT e da arte antes/depois permaneceram iguais. O rascunho de conferência usa armazenamento separado em outputs, não altera templates da usuária e não é portfólio definitivo.
- **APROVADO — diagnóstico de leitura do banco local**: acesso aprovado, contagens anteriores preservadas, zero auditorias pendentes e nenhum problema de configuração. A tabela de revisões é aditiva; cadastro, catálogo de requisitos, evidências e serviços do MVP 1 não foram reestruturados.
- **APROVADO — higiene**: git diff --check sem erros; lista rastreada inspecionada. Catálogo pedagógico local, snapshots, TXT original, arte, capturas, banco e logs permanecem fora do Git. O catálogo contém textos privados e não foi adicionado à lista permitida de configuração pública. Código e documentação de uso não copiam assinaturas, nomes de alunos nem caminhos pessoais nos logs.

### Ajustes e falhas intermediárias observadas

- Rodada dirigida de modelo/interface: 25 testes aprovados. A primeira rodada de navegador teve um teste aprovado e uma falha no seletor do combobox Streamlit; o seletor foi corrigido. Execuções seguintes revelaram reexecução/recolhimento do painel e sincronização da edição textual. O painel passou a abrir expandido e o texto editável passou a usar formulário com envio explícito, preservando o conteúdo até salvar. O teste passou a aguardar o formulário completo antes de interagir.
- Uma execução intermediária do validador teve 47 aprovados, 1 reprovado e 1 ignorado enquanto esses ajustes eram concluídos. A execução final acima substitui o resultado corrente sem remover os artefatos históricos. O teste dirigido de reinício/reabertura também passou separadamente em 34,50 s.
- Medidas de caracteres e fontes foram armazenadas em cache para evitar repetir consultas tipográficas na quebra de textos longos. As métricas usadas para quebra e desenho permanecem as mesmas.

### Limitações e pendências

- **NÃO TESTADO**: avaliação interativa pela professora, legibilidade em smartphone físico, fotos reais, navegadores além de Chromium, toque, interrupção física, disco cheio e migração em outra máquina. A inspeção estática de PNG e a automação Chromium não equivalem a essas revisões.
- Sem ampliação automática da altura da arte, redução automática de fonte, rich text, fontes enviadas pelo usuário, PDF, lote ou portal. Transbordamento recebe borda e aviso; o texto completo permanece salvo. A professora pode aumentar a região dentro da arte ou ajustar a fonte.
- Seminegrito em Arial/Georgia utiliza a variante negrito disponível; Segoe UI utiliza a variante própria. As fontes são lidas do sistema, sem redistribuição. O parser espera a estrutura atual do TXT; mudanças de formato exigem revisão. Catálogo e originais privados precisam acompanhar o backup local.
- Rascunhos de regiões precisam do botão Salvar template; edições de texto precisam do botão Salvar edição de texto. A prévia deve ser atualizada após mudar textos. Encerrar o navegador sem salvar pode perder rascunhos.
- Uso e restauração documentados em docs/EDITOR_SEMANTICO.md. Nenhuma funcionalidade de MVP futuro foi antecipada.

---

## Preparacao para versionamento no GitHub

- Registro: 2026-11-20T15:23:00-03:00 (America/Sao_Paulo). Base Git `426db950e0ed6dff4ece018b1a7d11a71616dfce`; arvore modificada com as entregas locais do inicializador e editor, antes do commit. Historico anterior preservado.
- **APROVADO - testes automatizados**: `.venv/Scripts/python.exe -m src.validate`; 48 aprovados, 1 ignorado, nenhuma falha, em 113,59 s. Resumo persistente e JUnit permanecem locais em outputs. Permanece a limitacao anterior da versao instalada de pytest.
- **NAO TESTADO - caso ignorado**: teste do inicializador com reserva da porta 8501, ocupada no ambiente; nenhum servidor existente foi encerrado.
- **APROVADO - diagnostico somente leitura**: banco acessivel, zero auditorias pendentes e nenhum problema de configuracao. Erro historico do inicializador permanece nos logs; nao foi observado novo erro neste diagnostico.
- **APROVADO - higiene de publicacao**: arquivos rastreados e novos conferidos; apenas codigo, configuracao publica, testes e documentacao. Banco, logs, diagnostico, catalogo pedagogico privado, fotos, artes e documentos originais permanecem excluidos. `git diff --check` sem erros.
- **APROVADO - acesso remoto de leitura**: GitHub respondeu com a mesma base Git. Commit e envio serao verificados separadamente apos este registro.
- **NAO TESTADO - revisao manual em navegador**: nao realizada nesta tarefa; testes automatizados de navegador nao equivalem a revisao manual. Nenhuma verificacao HTTP manual separada foi realizada.

---

## Textos automaticos no rascunho do template

- Registro: 2026-11-20T16:08:12-03:00 (America/Sao_Paulo). Base Git `e90aeee3aca284398bb81a9361ab05c3e3469187`; arvore limpa ao iniciar e modificada durante esta tarefa, antes do commit. Historico preservado.
- Causa observada: template local do Projeto 4 tinha texto literal vazio e nenhuma regiao de legenda; as duas fotos apontavam ao mesmo requisito. A referencia original e o catalogo local contem os textos correspondentes. Nenhum conteudo privado foi copiado para esta documentacao.
- Implementado comando Preencher textos do projeto, trabalhando no rascunho atual; vincula texto vazio, acrescenta campos ausentes, mede altura das legendas e procura espaco livre. Preserva conteudo preenchido e fotos. Repeticao nao duplica vinculos. Requisitos fotograficos repetidos recebem aviso, sem alteracao automatica da associacao. Persistencia continua explicita em Salvar template.
- **APROVADO - diagnostico somente leitura**: banco acessivel, nenhuma auditoria pendente e nenhum problema de configuracao. Logs recentes consultados; erro historico de inicializacao permanece registrado, sem nova ocorrencia identificada nesta verificacao.
- **APROVADO - suite automatizada intermediaria**: `.venv/Scripts/python.exe -m src.validate`; 50 aprovados, 1 ignorado, nenhuma falha, em 92,59 s. O ajuste final de altura e busca horizontal foi posterior a essa rodada. Resumos anteriores preservados localmente.
- **APROVADO - testes dirigidos apos ajuste de layout**: `.venv/Scripts/python.exe -m pytest -q tests/test_pedagogy.py`; 8 aprovados, em 8,49 s. Cobertos preenchimento, preservacao de fotos e texto personalizado, falta de espaco, IDs fotograficos canonicos/aliases, duplicidade de requisito, repeticao, persistencia e composicao sintetica.
- **APROVADO - conferencia local separada da suite**: correspondencia entre referencia e catalogo dos campos de introducao e legendas do Projeto 4; hash do original preservado. Previa em memoria do template existente mostrou introducao e legenda vinculadas, com aviso de requisito repetido. Outra copia apenas em memoria recebeu requisitos distintos e mostrou introducao e duas legendas sem transbordamento; PNG inspecionado visualmente, sem salvar ou alterar o template original. Capturas e scripts de conferencia continuam privados em outputs.
- **NAO TESTADO - revisao manual interativa em navegador**: nao realizada. Inspecao estatica de PNG e automacao Chromium nao equivalem a essa revisao. Nenhuma verificacao HTTP manual separada foi realizada.
- **APROVADO - higiene Git**: arquivos rastreados conferidos; original, banco, logs e capturas continuam excluidos. Sem nova dependencia ou alteracao pedagogica. Permanece a limitacao da versao instalada de pytest documentada anteriormente.
- **APROVADO - suite automatizada final apos todos os ajustes**: `.venv/Scripts/python.exe -m src.validate`; 50 aprovados, 1 ignorado, zero falhas, exit 0, em 78,22 s. Resumo persistente atualizado em outputs. Inclui regressao Chromium do comando de preenchimento, preservacao do arquivo salvo e ausencia de duplicacao de regioes, alem dos testes existentes de mouse, reabertura e edicao.
- **NAO TESTADO - caso ignorado**: teste do inicializador que reserva 8501, ocupada no ambiente. Nenhum servidor existente foi encerrado. A verificacao HTTP automatizada esta integrada aos testes de navegador; nao foi feita revisao HTTP manual independente.
