# Validação do MVP 1

Execução local em Python 3.11.3: `python -m pytest -q` — **8 testes aprovados**, última execução em 7,44 segundos.

Cobertura exercitada com dados sintéticos: lista de alunos repetida e edição, matrícula única, catálogo idempotente de 12 seções/27 campos/25 obrigatórios, preservação binária e hash de imagens, rejeição de conteúdo inválido, proteção de caminhos, associações únicas, estados não aprovados sem progresso, aprovação e reabertura do banco, conclusão total incluindo síntese opcional, rejeição e desvinculação, pastas com arquivo inválido/duplicado e Excel vazio/preenchido com cinco abas.

Streamlit AppTest abriu as seis telas com aluno e fotografia sintéticos, selecionou Aprovada na revisão, salvou pela interface e confirmou incremento da completude no banco. Não substitui avaliação de usabilidade pela professora nem valida correspondência pedagógica de fotos reais.

Inicialização real local concluída: 26 alunos importados da lista original; 27 campos de evidência; nenhuma fotografia real importada ou enviada. Documentos de referência preservados. Relatórios não contêm matrículas. Não foram implementados PDF, geração em lote ou publicação.
