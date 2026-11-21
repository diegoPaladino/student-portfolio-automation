# Rotina do projeto

Antes de implementar novas funcionalidades ou corrigir problemas:

1. Ler README.md, docs/ARQUITETURA.md e docs/VALIDACAO.md, preservando o histórico.
2. Consultar registros recentes de logs/app.log, logs/errors.log e logs/audit.jsonl (ou PORTFOLIO_LOG_DIR). Não copiar dados externos ou privados para documentos públicos.
3. Identificar erros abertos e possíveis regressões. Não exigir que o usuário descreva novamente erros suficientemente documentados.
4. Verificar estado do Git, versão, configuração e acesso ao banco com `python -m src.diagnostics`. Diagnóstico é somente leitura do banco.
5. Realizar alterações incrementais, preservando dados locais e documentos originais. Não alterar a estrutura pedagógica nem antecipar outros MVPs sem solicitação.
6. Executar testes pertinentes; para resumo persistente, usar `python -m src.validate`. Dados de teste devem ser sintéticos.
7. Acrescentar a docs/VALIDACAO.md os resultados efetivamente observados, horário com fuso, commit/base e condição de árvore modificada. Usar APROVADO, REPROVADO, NÃO TESTADO ou BLOQUEADO. Distinguir teste automatizado, verificação HTTP e revisão manual em navegador.

Nunca versionar logs, diagnósticos, fotografias, bancos, lista real de alunos ou documentos com nomes pessoais. Conferir também arquivos rastreados. Eventos de auditoria são inseridos na mesma transação do negócio e exportados somente após commit. Não remover histórico. Distinguir conclusão local, commit Git e envio remoto; nunca declarar commit ou envio antes de verificá-los. Stack técnico deve continuar sem mensagens/argumentos externos e sem caminhos locais.

## Rastreabilidade permanente de desenvolvimento

Em toda solicitação futura de desenvolvimento, ler também [o histórico de prompts](docs/HISTORICO_PROMPTS.md) e a seção [Rastreabilidade de solicitações e implementações](docs/VALIDACAO.md#rastreabilidade-de-solicitações-e-implementações). Estas instruções orientam a atuação do agente quando o repositório for aberto; não há captura automática de outras conversas nem serviço em segundo plano.

1. Identificar a solicitação e reservar o próximo ID `DEV-AAAA-NNN`, consultando todos os IDs existentes; nunca reutilizar ou renumerar um ID. Os IDs `RETRO-AAAA-NNN` identificam retrospectivas, não solicitações formais antigas. A primeira solicitação formal é `DEV-2026-001`.
2. Abrir o registro no histórico antes das alterações significativas. Registrar o prompt completo disponível no contexto, após sanitização, sua origem, objetivo, requisitos e critérios de aceitação. Remover nomes pessoais, textos de documentos privados, credenciais, caminhos sensíveis e imagens; marcar cada omissão. Se o original não estiver disponível, usar exatamente: `Origem: reconstrução técnica; prompt original indisponível.` Nunca inventar texto literal ou horário de recebimento. Distinguir data de registro, data de teste e data de commit.
3. Vincular o registro a uma entrada de mesmo ID na seção de rastreabilidade de VALIDACAO.md, com links relativos recíprocos. Executar somente o escopo autorizado, preservando dados e alterações existentes.
4. Executar as verificações pertinentes e registrar comandos, resultados observados e limitações. Mudanças apenas documentais podem usar verificação estrutural dos documentos; não declarar a suíte da aplicação como executada com base em resultado anterior. Distinguir teste automatizado, HTTP, inspeção estática e revisão manual em navegador.
5. Ao concluir cada intervenção significativa, atualizar ambos os documentos com implementação efetiva, arquivos criados/modificados, problemas/correções, base Git, commit final quando existir, árvore modificada, arquivos não rastreados e pendências. Classificar separadamente IMPLEMENTADO, TESTADO, VALIDADO MANUALMENTE, PENDENTE e BLOQUEADO, indicando sim/não/parcial/não aplicável e evidência; manter APROVADO, REPROVADO, NÃO TESTADO e BLOQUEADO para as verificações.
6. Se houver falha ou interrupção, registrar o estado parcial quando possível; nunca marcar a tarefa como concluída por falta de tempo. Acrescentar evidências históricas sem apagar as anteriores. Se um commit posterior consolidar a entrega, referenciá-lo por ID em adendo, sem tentar inserir no próprio commit um hash autorreferente.
7. Antes da entrega, conferir unicidade de IDs, referências e âncoras, links relativos, privacidade, preservação do histórico e situação Git. Informar ao usuário os arquivos alterados e o que permanece pendente.
8. Criar commit ou enviar ao GitHub somente quando autorizado pelo usuário; não inferir autorização permanente deste protocolo. Uma entrega local sem commit deve ser relatada como tal. A intervenção inicial DEV-2026-001 foi entregue sem autorização de commit/envio; a autorização posterior para consolidá-la está registrada em DEV-2026-002.
