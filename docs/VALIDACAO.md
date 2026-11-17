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
