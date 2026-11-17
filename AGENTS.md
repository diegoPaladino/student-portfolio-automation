# Rotina do projeto

Antes de implementar novas funcionalidades ou corrigir problemas:

1. Ler README.md, docs/ARQUITETURA.md e docs/VALIDACAO.md, preservando o histórico.
2. Consultar registros recentes de logs/app.log, logs/errors.log e logs/audit.jsonl (ou PORTFOLIO_LOG_DIR). Não copiar dados externos ou privados para documentos públicos.
3. Identificar erros abertos e possíveis regressões. Não exigir que o usuário descreva novamente erros suficientemente documentados.
4. Verificar estado do Git, versão, configuração e acesso ao banco com `python -m src.diagnostics`. Diagnóstico é somente leitura do banco.
5. Realizar alterações incrementais, preservando dados locais e documentos originais. Não alterar a estrutura pedagógica nem antecipar outros MVPs sem solicitação.
6. Executar testes pertinentes; para resumo persistente, usar `python -m src.validate`. Dados de teste devem ser sintéticos.
7. Acrescentar a docs/VALIDACAO.md os resultados efetivamente observados, horário com fuso, commit/base e condição de árvore modificada. Usar APROVADO, REPROVADO, NÃO TESTADO ou BLOQUEADO. Distinguir teste automatizado, verificação HTTP e revisão manual em navegador.

Nunca versionar logs, diagnósticos, fotografias, bancos, lista real de alunos ou documentos com nomes pessoais. Conferir também arquivos rastreados. Eventos de auditoria são inseridos na mesma transação do negócio e exportados somente após commit. Não remover histórico nem declarar sucesso antes do commit. Stack técnico deve continuar sem mensagens/argumentos externos e sem caminhos locais.
