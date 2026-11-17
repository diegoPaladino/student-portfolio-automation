# Arquitetura

`app.py` apresenta Streamlit; `src/core.py` implementa serviços, consultas e exportação; `src/settings.py` centraliza caminhos e limite de upload; `config/catalog.json` contém os requisitos verificáveis. SQLite armazena students, projects, requirements, photos, evidence e history. Chaves estrangeiras, matrícula/hash únicos e restrições de associação protegem integridade. Cada operação de escrita usa transação; conexões são fechadas após uso. Histórico registra entidade, evento e horário UTC, sem nomes/matrículas.

Fotografias são verificadas e decodificadas por Pillow. Somente JPEG/PNG/WEBP são aceitos. Limite de bytes e proteção de descompressão reduzem consumo indevido. Armazenamento usa SHA-256, não nomes externos. Caminhos lidos são restritos à pasta de imagens. Importação por pasta ignora links simbólicos e sua própria área de armazenamento. Conteúdo original é imutável. Falha entre escrita de arquivo e commit pode deixar um arquivo órfão: a reimportação verifica o hash e recupera o registro; não há limpeza destrutiva automática.

Uma associação por aluno/campo e uma por aluno/foto evitam duplicar evidências para a mesma criança. Desvincular conserva a foto e registra o evento. Aprovações são estado atual na associação e eventos históricos. Sem multiusuário ou controle de acesso por função neste MVP. Servidor deve ficar em 127.0.0.1; telemetria Streamlit é desativada no inicializador. Relatórios neutralizam fórmulas Excel em textos. Não publicar o servidor nem sincronizar dados sem avaliação de acesso.

## Distribuição Windows futura

Empacotar um inicializador com PyInstaller em modo onedir, incluindo Streamlit e catálogo como recursos de leitura. Resolver recursos por __file__; configurar PORTFOLIO_DATA_DIR em diretório gravável do usuário (por exemplo LocalAppData) antes de iniciar. Nunca colocar o SQLite na área temporária de extração do executável. Inicializador futuro deverá escolher porta local livre, abrir navegador, controlar encerramento e registrar erros sem dados pessoais. Validar em máquina Windows limpa sem Python, com backup/restauração e atualização preservando dados. Executável não é entregue no MVP 1.

## Limitações

Sem criptografia própria, rotação de backups, importação HEIC, classificação automática ou edição de catálogo na interface. Dependências são delimitadas por versões principais, sem lock completo. Uso previsto é uma professora em computador local. Textos e identidade visual do PDF serão tratados na fase seguinte. Revisão humana continua indispensável.
