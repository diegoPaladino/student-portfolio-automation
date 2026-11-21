# Histórico de prompts e solicitações

Este arquivo deve ser lido com [VALIDACAO.md](VALIDACAO.md#rastreabilidade-de-solicitações-e-implementações). O procedimento permanente está em [AGENTS.md](../AGENTS.md#rastreabilidade-permanente-de-desenvolvimento).

## Convenções e limites

- `DEV-AAAA-NNN`: solicitação formal, sequência estável por ano. `DEV-2026-001` inaugura o protocolo; próximo ID livre: `DEV-2026-003`, sujeito à conferência do arquivo no início da tarefa.
- `RETRO-AAAA-NNN`: índice retrospectivo criado nesta intervenção. Sua numeração não significa ordem exata dos pedidos originais.
- Prompt disponível é transcrito após sanitização explícita; imagens e documentos privados não são incorporados. Prompt indisponível recebe apenas resumo verificável. Nunca inferir acesso a outras conversas.
- Horário de commit, teste ou registro não é horário de recebimento do pedido. Critérios retrospectivos abaixo foram derivados das evidências técnicas e não são apresentados como texto original do usuário.
- IMPLEMENTADO, TESTADO, VALIDADO MANUALMENTE, PENDENTE e BLOQUEADO são dimensões independentes. APROVADO/REPROVADO/NÃO TESTADO/BLOQUEADO qualificam cada verificação em VALIDACAO.md. Resultado histórico não é reexecução atual.
- Commit de consolidação pode conter várias intervenções; não atribuir a ele testes executados após o commit nem supor um commit exclusivo de cada subentrega.

## Índice

| ID | Solicitação | Origem | Commit associado |
|---|---|---|---|
| [DEV-2026-001](#dev-2026-001) | Protocolo permanente de rastreabilidade | Anexo disponível, sanitizado | Sem commit; não autorizado |
| [DEV-2026-002](#dev-2026-002) | Salvar protocolo no GitHub | Mensagem atual; autorização posterior | Consolidação de DEV-2026-001 |
| [RETRO-2026-001](#retro-2026-001) | MVP 1 | Reconstrução técnica | `97fd03c` |
| [RETRO-2026-002](#retro-2026-002) | Observabilidade e diagnóstico | Reconstrução técnica | `426db95` |
| [RETRO-2026-003](#retro-2026-003) | Editor visual de templates | Reconstrução técnica | `e90aeee` |
| [RETRO-2026-004](#retro-2026-004) | Inicializador Windows | Reconstrução técnica | `e90aeee` |
| [RETRO-2026-005](#retro-2026-005) | Editor semântico | Reconstrução técnica | `e90aeee` |
| [RETRO-2026-006](#retro-2026-006) | Integração de textos pedagógicos | Reconstrução técnica | `e90aeee` |
| [RETRO-2026-007](#retro-2026-007) | Preenchimento automático de textos | Contexto atual, sanitizado | `745eb02` |
| [RETRO-2026-008](#retro-2026-008) | Seleção e troca de projetos | Contexto atual, sanitizado | `08210f9` |
| [RETRO-2026-009](#retro-2026-009) | Consolidação no GitHub | Contexto atual, sanitizado | `e90aeee` |

<a id="dev-2026-001"></a>

## DEV-2026-001 — Protocolo permanente de rastreabilidade

- Data de registro: 2026-11-21T10:17:03-03:00 (America/Sao_Paulo). Pedido recebido no contexto de 2026-11-21; horário exato de recebimento não disponível.
- Origem: anexo textual fornecido pelo usuário nesta conversa; corpo integral abaixo, com o caminho absoluto do projeto substituído por `[RAIZ_DO_PROJETO]`. A localização privada do anexo não é persistida.
- Objetivo: relacionar solicitações, requisitos, implementações, arquivos, testes, problemas, versões e pendências, permitindo continuidade por outro agente.
- Critérios de aceitação: histórico com IDs únicos; retrospectiva baseada em evidências; seção recíproca de validação; instruções permanentes em AGENTS.md; links válidos; histórico anterior intacto; ausência de dados privados novos; nenhuma mudança funcional; nenhum commit ou push nesta intervenção.
- Status: IMPLEMENTADO localmente; TESTADO por verificação documental; VALIDADO MANUALMENTE em navegador: NÃO TESTADO (não aplicável à mudança documental); PENDENTE de decisão do usuário sobre commit; BLOQUEADO: não. Commit não solicitado não é falha técnica.
- Base: `08210f9438652a11acb0568016318063f3c4d1b1`; commit final: inexistente, não autorizado.
- Validação e arquivos: [DEV-2026-001 em VALIDACAO.md](VALIDACAO.md#dev-2026-001).

### Prompt original completo, sanitizado

```text
# MELHORIA INCREMENTAL — RASTREABILIDADE DE PROMPTS, IMPLEMENTAÇÕES E VALIDAÇÕES

Atue como engenheiro de software sênior especializado em documentação técnica, rastreabilidade de requisitos, Git e desenvolvimento assistido por IA.

Projeto:
`[RAIZ_DO_PROJETO]`

## OBJETIVO

Implementar um protocolo permanente de rastreabilidade entre:

1. Solicitações e prompts enviados pelo usuário ao Codex.
2. Funcionalidades solicitadas.
3. Alterações efetivamente realizadas no código.
4. Arquivos criados e modificados.
5. Testes e validações executados.
6. Problemas identificados e correções.
7. Commits e versões do Git.
8. Pendências e próximos passos.

O objetivo é permitir que outra instância de IA, recebendo `docs/VALIDACAO.md` e `docs/HISTORICO_PROMPTS.md`, compreenda precisamente o histórico e o estado atual do desenvolvimento.

## 1. INSPEÇÃO INICIAL

Antes de modificar os documentos:

- Ler `AGENTS.md`.
- Ler integralmente `docs/VALIDACAO.md`.
- Consultar `README.md` e documentação relacionada.
- Examinar o histórico recente do Git.
- Identificar o estado atual da árvore de trabalho.
- Consultar os testes e registros de diagnóstico disponíveis.

Preservar integralmente o histórico de validação existente.

Não modificar funcionalidades do software nesta tarefa.

## 2. HISTÓRICO DE PROMPTS

Criar:

`docs/HISTORICO_PROMPTS.md`

Cada solicitação deverá possuir um identificador único e estável, por exemplo:

`DEV-2026-001`

Registrar:

- Data e horário, quando verificáveis.
- Identificador da solicitação.
- Título resumido.
- Prompt original completo, quando disponível.
- Objetivo e critérios de aceitação.
- Origem do registro.
- Status da implementação.
- Referência à validação correspondente.
- Commit associado, quando existir.

Não reconstruir prompts literalmente a partir de suposições.

Para solicitações anteriores sem prompt original disponível, registrar apenas o resumo verificável e marcar:

`Origem: reconstrução técnica; prompt original indisponível.`

Não presumir acesso automático a conversas anteriores do Codex.

## 3. INCREMENTAR O VALIDACAO.MD

Preservar todas as seções existentes.

Adicionar uma seção denominada:

`## Rastreabilidade de solicitações e implementações`

Para cada nova intervenção, registrar:

### Identificação
- ID da solicitação.
- Data.
- Título.
- Referência ao histórico de prompts.

### Solicitação do usuário
- Objetivo solicitado.
- Requisitos específicos.
- Critérios de aceitação.

### Implementação realizada
- Funcionalidades efetivamente implementadas.
- Arquivos criados.
- Arquivos modificados.
- Decisões arquiteturais relevantes.

### Verificação
- Testes executados.
- Resultados obtidos.
- Testes não realizados.
- Erros encontrados e respectivas correções.

### Versionamento
- Commit inicial.
- Commit final, se existir.
- Arquivos ainda não versionados.
- Alterações locais pendentes.

### Estado final
Classificar separadamente:

- IMPLEMENTADO
- TESTADO
- VALIDADO MANUALMENTE
- PENDENTE
- BLOQUEADO

Não confundir testes automatizados com validação manual.

## 4. INTEGRAÇÃO COM O CODEX

Atualizar `AGENTS.md` para estabelecer que, em toda futura solicitação de desenvolvimento:

1. O Codex deve identificar a solicitação atual.
2. Registrar o prompt original, quando disponível no contexto.
3. Executar as alterações solicitadas.
4. Rodar os testes pertinentes.
5. Atualizar o histórico de prompts.
6. Atualizar a seção correspondente do `VALIDACAO.md`.
7. Registrar limitações e pendências.
8. Informar os arquivos modificados e a situação do Git.

Os documentos devem ser atualizados ao concluir cada intervenção significativa.

Caso uma tarefa falhe ou seja interrompida, registrar o estado parcial, quando possível, sem declarar conclusão.

## 5. PRIVACIDADE E SEGURANÇA

Não registrar:

- Fotografias de crianças.
- Dados pessoais de alunos.
- Senhas, tokens ou chaves de API.
- Conteúdo de arquivos privados.
- Caminhos absolutos contendo informações sensíveis.
- Dados internos do banco SQLite.

Sanitizar prompts antes de persistir informações sensíveis.

Não adicionar ao Git arquivos privados atualmente ignorados.

## 6. RETROSPECTIVA

Analisar o histórico já existente no `VALIDACAO.md` e no Git.

Criar um índice retrospectivo das intervenções verificáveis, incluindo:

- MVP 1.
- Observabilidade e diagnóstico.
- Editor visual de templates.
- Inicializador Windows.
- Editor semântico.
- Integração de textos pedagógicos.
- Preenchimento automático de textos.
- Seleção e troca de projetos.

Não duplicar integralmente relatórios anteriores.

Distinguir claramente o que foi reconstruído a partir de documentação daquilo cujo prompt original está disponível.

## 7. VALIDAÇÃO DA DOCUMENTAÇÃO

Verificar:

- Identificadores únicos.
- Referências consistentes entre os documentos.
- Links relativos válidos.
- Ausência de duplicação indevida.
- Preservação do histórico anterior.
- Ausência de dados privados.

Não executar modificações desnecessárias no código da aplicação.

## 8. ENTREGA

Ao finalizar:

1. Informar os documentos criados ou alterados.
2. Mostrar um exemplo real de registro.
3. Explicar como o procedimento será aplicado automaticamente nas próximas tarefas.
4. Informar eventuais limitações para recuperar prompts anteriores.
5. Apresentar o estado do Git.
6. Não criar commit nem enviar alterações ao GitHub sem minha autorização.

Esta intervenção deverá ser registrada como a primeira solicitação formal do novo protocolo de rastreabilidade.
```

## Retrospectiva verificável

Os oito primeiros registros cobrem as áreas solicitadas; o nono documenta a consolidação autorizada na conversa. Consultar o relatório legado indicado na validação correspondente para os detalhes e falhas intermediárias.

<a id="retro-2026-001"></a>

## RETRO-2026-001 — MVP 1

- Data/evidência: 2026-11-17 (data do primeiro commit; horário da solicitação não disponível). Retrospectiva registrada em 2026-11-21T10:17:03-03:00; recebimento original sem horário verificável.
- Origem: reconstrução técnica; prompt original indisponível.
- Objetivo verificável: Cadastro, importação/classificação manual, revisão, completude e Excel local.
- Critérios técnicos retrospectivos: comportamento descrito acima, preservação dos dados locais e verificações registradas no relatório legado; não há recuperação dos critérios originais quando o prompt está indisponível.
- Arquivos/áreas verificáveis: src/core.py; src/settings.py; app.py; config/catalog.json; tests/test_core.py; tests/test_ui.py.
- Status: IMPLEMENTADO no commit associado; TESTADO conforme evidência histórica a seguir; VALIDADO MANUALMENTE em navegador: não comprovado; PENDENTE: limites do relatório legado; BLOQUEADO: somente os itens explicitamente indicados nesse relatório, sem reavaliá-los nesta tarefa.
- Evidência: 8 testes e AppTest registrados; não reexecutados nesta tarefa. Revisão de usabilidade pendente.
- Commit associado: `97fd03c`. Confirmado no histórico Git local.
- Validação: [RETRO-2026-001 em VALIDACAO.md](VALIDACAO.md#retro-2026-001).

<a id="retro-2026-002"></a>

## RETRO-2026-002 — Observabilidade e diagnóstico

- Data/evidência: 2026-11-17T16:24:22-03:00 (registro da validação). Retrospectiva registrada em 2026-11-21T10:17:03-03:00; recebimento original sem horário verificável.
- Origem: reconstrução técnica; prompt original indisponível.
- Objetivo verificável: Logging sanitizado, auditoria transacional/outbox, diagnóstico somente leitura e validador persistente.
- Critérios técnicos retrospectivos: comportamento descrito acima, preservação dos dados locais e verificações registradas no relatório legado; não há recuperação dos critérios originais quando o prompt está indisponível.
- Arquivos/áreas verificáveis: src/observability.py; src/diagnostics.py; src/validate.py; src/core.py; app.py; tests/test_observability.py.
- Status: IMPLEMENTADO no commit associado; TESTADO conforme evidência histórica a seguir; VALIDADO MANUALMENTE em navegador: não comprovado; PENDENTE: limites do relatório legado; BLOQUEADO: somente os itens explicitamente indicados nesse relatório, sem reavaliá-los nesta tarefa.
- Evidência: 22 testes aprovados e HTTP 200 registrados. Recuperação física e revisão manual permanecem sem comprovação.
- Commit associado: `426db95`. Confirmado no histórico Git local.
- Validação: [RETRO-2026-002 em VALIDACAO.md](VALIDACAO.md#retro-2026-002).

<a id="retro-2026-003"></a>

## RETRO-2026-003 — Editor visual de templates

- Data/evidência: 2026-11-17T21:43:27-03:00 (registro da validação). Retrospectiva registrada em 2026-11-21T10:17:03-03:00; recebimento original sem horário verificável.
- Origem: reconstrução técnica; prompt original indisponível.
- Objetivo verificável: Regiões sobre arte local, movimento/zoom, composição e versões imutáveis de templates.
- Critérios técnicos retrospectivos: comportamento descrito acima, preservação dos dados locais e verificações registradas no relatório legado; não há recuperação dos critérios originais quando o prompt está indisponível.
- Arquivos/áreas verificáveis: src/template_editor/; src/rendering/preview.py; tests/test_templates.py; tests/test_template_browser.py.
- Status: IMPLEMENTADO no commit associado; TESTADO conforme evidência histórica a seguir; VALIDADO MANUALMENTE em navegador: não comprovado; PENDENTE: limites do relatório legado; BLOQUEADO: somente os itens explicitamente indicados nesse relatório, sem reavaliá-los nesta tarefa.
- Evidência: 39 testes aprovados e Chromium com dados sintéticos registrados. Toque e revisão interativa da professora não comprovados.
- Commit associado: `e90aeee`. Commit de consolidação compartilhado pelas entregas visual, Windows, semântica e integração textual; não é um commit exclusivo deste registro.
- Validação: [RETRO-2026-003 em VALIDACAO.md](VALIDACAO.md#retro-2026-003).

<a id="retro-2026-004"></a>

## RETRO-2026-004 — Inicializador Windows

- Data/evidência: 2026-11-19T20:48:32-03:00 (registro da validação). Retrospectiva registrada em 2026-11-21T10:17:03-03:00; recebimento original sem horário verificável.
- Origem: reconstrução técnica; prompt original indisponível.
- Objetivo verificável: Preparo separado, descoberta de ambiente, health HTTP, navegador e encerramento do processo filho.
- Critérios técnicos retrospectivos: comportamento descrito acima, preservação dos dados locais e verificações registradas no relatório legado; não há recuperação dos critérios originais quando o prompt está indisponível.
- Arquivos/áreas verificáveis: INICIAR_PORTFOLIOS.bat; INSTALAR_AMBIENTE.bat; iniciar.ps1; scripts/ambiente.ps1; src/launcher.py; tests/test_launcher.py.
- Status: IMPLEMENTADO no commit associado; TESTADO conforme evidência histórica a seguir; VALIDADO MANUALMENTE em navegador: não comprovado; PENDENTE: limites do relatório legado; BLOQUEADO: somente os itens explicitamente indicados nesse relatório, sem reavaliá-los nesta tarefa.
- Evidência: 42 testes aprovados e HTTP automatizado registrados. Pip check global reprovado; atualização de pytest bloqueada na ocasião. Duplo clique não validado.
- Commit associado: `e90aeee`. Commit de consolidação compartilhado pelas entregas visual, Windows, semântica e integração textual; não é um commit exclusivo deste registro.
- Validação: [RETRO-2026-004 em VALIDACAO.md](VALIDACAO.md#retro-2026-004).

<a id="retro-2026-005"></a>

## RETRO-2026-005 — Editor semântico

- Data/evidência: 2026-11-19T21:46:02-03:00 (registro da validação). Retrospectiva registrada em 2026-11-21T10:17:03-03:00; recebimento original sem horário verificável.
- Origem: reconstrução técnica; prompt original indisponível.
- Objetivo verificável: Vínculos semânticos, estilos tipográficos e composição com precedência individual/global/original.
- Critérios técnicos retrospectivos: comportamento descrito acima, preservação dos dados locais e verificações registradas no relatório legado; não há recuperação dos critérios originais quando o prompt está indisponível.
- Arquivos/áreas verificáveis: src/template_editor/model.py; src/template_editor/ui.py; src/template_editor/editor.js; src/rendering/typography.py; src/rendering/preview.py.
- Status: IMPLEMENTADO no commit associado; TESTADO conforme evidência histórica a seguir; VALIDADO MANUALMENTE em navegador: não comprovado; PENDENTE: limites do relatório legado; BLOQUEADO: somente os itens explicitamente indicados nesse relatório, sem reavaliá-los nesta tarefa.
- Evidência: 48 testes aprovados e 1 ignorado registrados na entrega conjunta. Revisão manual interativa pendente.
- Commit associado: `e90aeee`. Commit de consolidação compartilhado pelas entregas visual, Windows, semântica e integração textual; não é um commit exclusivo deste registro.
- Validação: [RETRO-2026-005 em VALIDACAO.md](VALIDACAO.md#retro-2026-005).

<a id="retro-2026-006"></a>

## RETRO-2026-006 — Integração de textos pedagógicos

- Data/evidência: 2026-11-19T21:46:02-03:00 (mesmo registro da entrega semântica). Retrospectiva registrada em 2026-11-21T10:17:03-03:00; recebimento original sem horário verificável.
- Origem: reconstrução técnica; prompt original indisponível.
- Objetivo verificável: Importação local com origem verificável, edições com histórico e personalização pelo prenome.
- Critérios técnicos retrospectivos: comportamento descrito acima, preservação dos dados locais e verificações registradas no relatório legado; não há recuperação dos critérios originais quando o prompt está indisponível.
- Arquivos/áreas verificáveis: src/pedagogy.py; src/template_editor/ui.py; src/rendering/preview.py; tests/test_pedagogy.py; tests/test_template_browser.py.
- Status: IMPLEMENTADO no commit associado; TESTADO conforme evidência histórica a seguir; VALIDADO MANUALMENTE em navegador: não comprovado; PENDENTE: limites do relatório legado; BLOQUEADO: somente os itens explicitamente indicados nesse relatório, sem reavaliá-los nesta tarefa.
- Evidência: Mesma suíte de 48 aprovados/1 ignorado; não é uma segunda execução independente. Arquivos privados ficam fora do Git.
- Commit associado: `e90aeee`. Commit de consolidação compartilhado pelas entregas visual, Windows, semântica e integração textual; não é um commit exclusivo deste registro.
- Validação: [RETRO-2026-006 em VALIDACAO.md](VALIDACAO.md#retro-2026-006).

<a id="retro-2026-007"></a>

## RETRO-2026-007 — Preenchimento automático de textos

- Data/evidência: 2026-11-20T16:08:12-03:00 (registro da validação). Retrospectiva registrada em 2026-11-21T10:17:03-03:00; recebimento original sem horário verificável.
- Origem: contexto atual desta conversa; prompt original disponível, sanitizado. Imagens anexas não persistidas.
- Objetivo verificável: Vincular introdução vazia e inserir legendas disponíveis, preservar conteúdo e avisar requisito repetido.
- Critérios técnicos retrospectivos: comportamento descrito acima, preservação dos dados locais e verificações registradas no relatório legado; não há recuperação dos critérios originais quando o prompt está indisponível.
- Arquivos/áreas verificáveis: src/template_editor/model.py; src/template_editor/ui.py; src/template_editor/editor.js; tests/test_pedagogy.py; tests/test_template_browser.py.
- Status: IMPLEMENTADO no commit associado; TESTADO conforme evidência histórica a seguir; VALIDADO MANUALMENTE em navegador: não comprovado; PENDENTE: limites do relatório legado; BLOQUEADO: somente os itens explicitamente indicados nesse relatório, sem reavaliá-los nesta tarefa.
- Evidência: 50 testes aprovados e 1 ignorado registrados. PNG local inspecionado estaticamente; não equivale a revisão manual em navegador.
- Commit associado: `745eb02`. Confirmado no histórico Git local.
- Validação: [RETRO-2026-007 em VALIDACAO.md](VALIDACAO.md#retro-2026-007).

### Prompt original disponível, sanitizado

```text
1) Veja na img1 que houve sucesso parcial. Esses testes iniciais, estou fazendo utilizando a "PROJETO 4", do arquivo que será referência para as páginas, que é o "PARTES-PORFOLIO-2026.txt", que está na pasta "[RAIZ_DO_PROJETO]"
1.1) O software conseguiu implementar de forma satisfatória os campos, mas o texto oriundo do documento não está vindo. Por exemplo, esse trecho é destinado ao ""PROJETO 4"", que é justamente o que está sendo trabalhado nesse caso:
[TRECHO DO DOCUMENTO PEDAGÓGICO PRIVADO OMITIDO]
Então ela já pode vir automaticamente. Ou seja, os textos referentes às partes, ou seja, aos "projetos" (PROJETO 1, PROJETO 2, PROJETO 3, etc.) já podem vir automaticamente.
Caso isso já ocorra e apenas não está aparecendo nessa visualização, favor desconsiderar.
1.2) os textos relativos às fotos também podem vir abaixo das imagens, ou nos locias que mais forem apropriados. Exemplo, para a imagem 1, dessa mesma parte / projeto 4:
[ORIENTAÇÃO FOTOGRÁFICA E LEGENDA DO DOCUMENTO PRIVADO OMITIDAS]
```

<a id="retro-2026-008"></a>

## RETRO-2026-008 — Seleção e troca de projetos

- Data/evidência: 2026-11-20T18:47:52-03:00 (registro da validação). Retrospectiva registrada em 2026-11-21T10:17:03-03:00; recebimento original sem horário verificável.
- Origem: contexto atual desta conversa; prompt original disponível, sanitizado. Imagens anexas não persistidas.
- Objetivo verificável: Catálogo por projeto agrupado, rótulos legíveis, aplicação da chamada e troca de vínculos equivalentes.
- Critérios técnicos retrospectivos: comportamento descrito acima, preservação dos dados locais e verificações registradas no relatório legado; não há recuperação dos critérios originais quando o prompt está indisponível.
- Arquivos/áreas verificáveis: src/pedagogy.py; src/template_editor/editor.js; src/template_editor/editor.css; src/template_editor/model.py; src/template_editor/ui.py; tests/test_pedagogy.py; tests/test_template_browser.py.
- Status: IMPLEMENTADO no commit associado; TESTADO conforme evidência histórica a seguir; VALIDADO MANUALMENTE em navegador: não comprovado; PENDENTE: limites do relatório legado; BLOQUEADO: somente os itens explicitamente indicados nesse relatório, sem reavaliá-los nesta tarefa.
- Evidência: 51 testes aprovados e 1 ignorado registrados; Chromium aplicou chamada a subtítulo e trocou projetos. Revisão manual não executada.
- Commit associado: `08210f9`. Confirmado no histórico Git local.
- Validação: [RETRO-2026-008 em VALIDACAO.md](VALIDACAO.md#retro-2026-008).

### Prompt original disponível, sanitizado

```text
1) Veja que na edição, há um campo que estou tentando preencher com o trecho dentro do "PROJETO 4", que é o "[CHAMADA DO DOCUMENTO PEDAGÓGICO PRIVADO OMITIDA]" Mas não consigo.
Como a lógica será trabalharmos por blocos, que são justamente esses "PROJETOS", o interessante seria ter sempre todas as opções de cada projeto. Na verdade já haver na própria interface a seleção de qual "PROJETO" se trata essa tela que está sendo configurada. Uma vez selecionado o projeto pelo usuário, as opçoes de texto d cada projeto estar disponível de maneira lógicamente separada, dividia, para que seja preenchida com elas, cada cmapo. Compreendeu?
```

<a id="retro-2026-009"></a>

## RETRO-2026-009 — Consolidação no GitHub

- Data/evidência: 2026-11-20 (datas de commits; horário da solicitação não disponível). Retrospectiva registrada em 2026-11-21T10:17:03-03:00; recebimento original sem horário verificável.
- Origem: contexto atual desta conversa; prompt original disponível.
- Objetivo verificável: Salvar as entregas locais no repositório remoto preservando dados privados.
- Critérios técnicos retrospectivos: comportamento descrito acima, preservação dos dados locais e verificações registradas no relatório legado; não há recuperação dos critérios originais quando o prompt está indisponível.
- Arquivos/áreas verificáveis: Arquivos consolidados no commit e90aeee; conjunto exato verificável por git show --stat e90aeee..
- Status: IMPLEMENTADO no commit associado; TESTADO conforme evidência histórica a seguir; VALIDADO MANUALMENTE em navegador: não comprovado; PENDENTE: limites do relatório legado; BLOQUEADO: somente os itens explicitamente indicados nesse relatório, sem reavaliá-los nesta tarefa.
- Evidência: Registro local: 48 aprovados/1 ignorado antes do envio; saída de push disponível nesta conversa. Não houve nova consulta remota nesta tarefa.
- Commit associado: `e90aeee`. Commit de consolidação compartilhado pelas entregas visual, Windows, semântica e integração textual; não é um commit exclusivo deste registro.
- Validação: [RETRO-2026-009 em VALIDACAO.md](VALIDACAO.md#retro-2026-009).

### Prompt original disponível

```text
consegue salvar no github? para que implementemos as próximas features?
```

## Estado conhecido e continuidade

A versão-base atual inclui as entregas até RETRO-2026-008. Limitações já relatadas: transbordamento de textos, símbolo não renderizado pela fonte e dúvidas de organização da interface; as imagens de feedback nesta conversa não comprovam correção nem revisão manual concluída. Não foram corrigidas nesta tarefa documental. A intenção do destaque na barra lateral ainda precisa de esclarecimento; não se infere novo requisito de layout.

Persistem as pendências de revisão humana, outros navegadores/dispositivos e limitações de ambiente descritas em VALIDACAO.md. As observações históricas sobre SQLite permanecem no documento original, preservado integralmente; este índice não reproduz dados internos do banco.

Para continuar, ler os dois documentos, conferir o Git e as evidências atuais, reservar o próximo ID formal e registrar o novo pedido antes de implementar. Anexar adendos ao obter novas evidências, sem reescrever os resultados anteriores.

<a id="dev-2026-002"></a>

## DEV-2026-002 — Salvar o protocolo no GitHub

- Registro: 2026-11-21T10:20:33-03:00 (America/Sao_Paulo); horário exato de recebimento não disponível.
- Origem: mensagem atual do usuário, integral abaixo. Autorização posterior à entrega local DEV-2026-001; a proibição inicial foi respeitada na intervenção anterior.
- Prompt original: “Vamos salvar no github? Para prosseguirmos seguros”.
- Objetivo e critérios: revisar e consolidar os cinco arquivos documentais da entrega anterior, registrar esta autorização, executar a checagem documental, criar commit e enviá-lo à main do origin configurado. Preservar dados privados e não alterar funcionalidades.
- Arquivos: AGENTS.md, README.md, .gitignore, docs/HISTORICO_PROMPTS.md e docs/VALIDACAO.md.
- Base: `08210f9438652a11acb0568016318063f3c4d1b1`; árvore inicialmente modificada pelos cinco arquivos de DEV-2026-001.
- Implementação: autorização registrada e instrução histórica esclarecida; entrega documental preparada para consolidação. Verificação e resultado Git em [DEV-2026-002](VALIDACAO.md#dev-2026-002).
- Versionamento: commit de consolidação identificado pela mensagem `DEV-2026-002: registra protocolo de rastreabilidade`; consultar seu hash no Git, evitando hash autorreferente no próprio documento. O resultado efetivo de commit e push será informado ao usuário após verificação.
- Estado: IMPLEMENTADO localmente; TESTADO por checagem documental; VALIDADO MANUALMENTE no navegador: NÃO TESTADO; PENDENTE de execução/verificação do commit e envio no momento deste registro; BLOQUEADO: não. Resultados da intervenção inicial permanecem históricos.
