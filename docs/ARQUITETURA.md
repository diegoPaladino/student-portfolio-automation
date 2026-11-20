# Arquitetura

`app.py` apresenta Streamlit; `src/core.py` implementa serviços, consultas e exportação; `src/settings.py` centraliza caminhos e limite de upload; `config/catalog.json` contém os requisitos verificáveis. SQLite armazena students, projects, requirements, photos, evidence e history. Chaves estrangeiras, matrícula/hash únicos e restrições de associação protegem integridade. Cada operação de escrita usa transação; conexões são fechadas após uso. Histórico registra entidade, evento e horário UTC, sem nomes/matrículas.

Fotografias são verificadas e decodificadas por Pillow. Somente JPEG/PNG/WEBP são aceitos. Limite de bytes e proteção de descompressão reduzem consumo indevido. Armazenamento usa SHA-256, não nomes externos. Caminhos lidos são restritos à pasta de imagens. Importação por pasta ignora links simbólicos e sua própria área de armazenamento. Conteúdo original é imutável. Falha entre escrita de arquivo e commit pode deixar um arquivo órfão: a reimportação verifica o hash e recupera o registro; não há limpeza destrutiva automática.

Uma associação por aluno/campo e uma por aluno/foto evitam duplicar evidências para a mesma criança. Desvincular conserva a foto e registra o evento. Aprovações são estado atual na associação e eventos históricos. Sem multiusuário ou controle de acesso por função neste MVP. Servidor deve ficar em 127.0.0.1; telemetria Streamlit é desativada no inicializador. Relatórios neutralizam fórmulas Excel em textos. Não publicar o servidor nem sincronizar dados sem avaliação de acesso.

## Distribuição Windows futura

Empacotar um inicializador com PyInstaller em modo onedir, incluindo Streamlit e catálogo como recursos de leitura. Resolver recursos por __file__; configurar PORTFOLIO_DATA_DIR em diretório gravável do usuário (por exemplo LocalAppData) antes de iniciar. Nunca colocar o SQLite na área temporária de extração do executável. Inicializador futuro deverá escolher porta local livre, abrir navegador, controlar encerramento e registrar erros sem dados pessoais. Validar em máquina Windows limpa sem Python, com backup/restauração e atualização preservando dados. Executável não é entregue no MVP 1.

## Limitações

### Extensão semântica do editor

`src/pedagogy.py` importa a referência local em catálogo JSON de esquema 1, com hash, linhas de origem e distinção entre texto, descrição de evidência e instrução editorial. O catálogo local e snapshots por hash ficam fora do Git; não devem ser publicados automaticamente. Reimportação é explícita e não modifica edições. PORTFOLIO_CONTENT_FILE permite indicar outra referência local, inclusive a sintética usada pelos testes.

`pedagogical_edits` é uma tabela SQLite aditiva, criada no primeiro uso do editor de textos, com revisões imutáveis por campo e aluno (NULL significa global). Texto NULL remove a edição, preservando a revisão. A precedência é individual, global, original. Revisão otimista evita sobrescrever uma alteração concorrente. Auditoria e revisão são inseridas na mesma transação por core.audit; o outbox só é exportado depois do commit. Nenhum conteúdo textual entra nos logs. Backup deve incluir o banco completo.

Templates aceitam esquemas 1 e 2; o próximo save publica esquema 2 sem excluir campos desconhecidos ou snapshots. Origem pedagogical referencia field_id, validado contra a seção do projeto; aliases fotográficos continuam resolvendo os requisitos existentes. Troca de tipo no componente conserva estilos e guarda origens inativas para recuperação. Abertura geral usa project_id 0 somente no JSON; não altera o catálogo de requisitos SQLite.

`src/rendering/typography.py` centraliza presets, fontes do sistema, medidas, quebra e espaçamento. A composição em memória resolve personalizações e substitui sublinhados apenas na prévia real. Sinaliza ausência e transbordamento, sem reduzir fonte automaticamente ou registrar evidências. Altura e coordenadas continuam vinculadas à arte original. Não há PDF/lote/portal. Detalhes em docs/EDITOR_SEMANTICO.md; descrições anteriores do editor permanecem como histórico arquitetural.

Sem criptografia própria, rotação de backups, importação HEIC, classificação automática ou edição de catálogo na interface. Dependências são delimitadas por versões principais, sem lock completo. Uso previsto é uma professora em computador local. Textos e identidade visual do PDF serão tratados na fase seguinte. Revisão humana continua indispensável.

## Observabilidade incremental

`src/observability.py` centraliza logging padrão com dois RotatingFileHandler técnicos e escrita rotativa de JSONL. Configuração idempotente e lock de processo evitam duplicar handlers em reruns. Mensagens seguem catálogo fechado; stack retém apenas módulos internos conhecidos e linhas. Não registrar str(exc), argumentos, SQL com valores, nome de foto, caminho de usuário ou dados de cadastro. Erros esperados são capturados especificamente na interface; uma fronteira final captura exceções inesperadas e informa falha sem expor detalhes. Serviços instrumentados registram e relançam exceções, preservando rollback.

Migração aditiva em initialize cria audit_outbox e replacement_pending sem alterar tabelas ou registros preexistentes. Cada alteração relevante insere histórico e payload de auditoria na mesma transação. Após commit, flush_audit exporta eventos e marca entrega. Falhas de exportação não desfazem uma operação já confirmada; pendências são recuperáveis. Garantia de entrega é pelo menos uma vez, não exatamente uma vez: deduplicar event_id em caso de interrupção. Lock cobre threads do mesmo processo, não múltiplos processos. Outbox/histórico não possuem limpeza automática; backup deve preservar todo o banco.

replacement_pending conserva apenas aluno/campo interno após desvincular. Ao associar novamente, a transação emite classificação e substituição e consome esse marcador. O histórico anterior não é removido. IDs e correlação aparecem em auditoria; dados pessoais não. logs e outputs são privados e ignorados pelo Git.

`src/diagnostics.py` consulta SQLite em mode=ro, não cria banco nem expõe resultados de SQL além de contagens. `src/validate.py` executa pytest e persiste contagens por execução, sem enviar dados. Nenhum novo pacote foi adicionado. Rotação não substitui backup e o encerramento abrupto não produz necessariamente log de shutdown.

## Editor de templates — MVP 2, etapa 1

`src/template_editor/model.py` valida e persiste JSON; `ui.py` faz a integração Streamlit; editor.html/js/css são um componente v2 local com SVG e Pointer Events. Não há compilação Node ou biblioteca de canvas externa. O zoom altera somente dimensões de exibição. A posição é calculada em coordenadas normalizadas a partir do SVG, incluindo deslocamento por rolagem. Arraste só é concluído no pointerup; seleção, movimento, alça de tamanho e campos numéricos coexistem.

O documento contém id UUID, schema_version=1, version crescente, name, project_id, background(file, width, height, raw_width, raw_height), regions, module_order, overlap e transition(mode=none). As dimensões width/height são as de exibição após EXIF; raw_width/raw_height registram dimensões armazenadas no original. Cada região tem id, type, x/y/width/height normalizados, source, fit, focus_x/y e text_style(font_size/color/align). Origem photo usa requirement_id; texto usa literal, project_title ou student_name. Códigos P04_F01 são aliases de 04-1; a associação é validada contra SQLite e deve pertencer ao projeto. Não há alteração do catálogo ou do esquema do banco do MVP 1.

Campos desconhecidos do JSON são preservados ao carregar e salvar. Coordenadas finitas, IDs únicos, tipos, projeto, requisitos, limites, estilos e dimensões do fundo são validados antes de salvar/renderizar. Templates usam versão otimista: salvar uma revisão desatualizada é recusado. Temporário completo com fsync é publicado em snapshot por hard link exclusivo e depois trocado atomicamente pelo arquivo atual. Snapshots anteriores não são sobrescritos; uma interrupção pode deixar revisão órfã e temporário, preservados para recuperação. Nova tentativa considera números já presentes para não bloquear edição. Essa estratégia exige NTFS ou sistema com hard links; não oferece transação entre JSON, eventos de log e sistema de arquivos. A interface usa a revisão atual, sem restaurador de histórico nesta etapa.

`src/rendering/preview.py` compõe Pillow em memória, mantendo a proporção variável e reduzindo o tamanho da prévia. contain usa margens transparentes; cover usa recorte e foco normalizado. Textos ficam restritos ao retângulo e avisam overflow. Aluno real é consulta local e somente evidence.state=Aprovada entra na composição; student_name usa o primeiro nome cadastrado. Ausências e marcadores sintéticos não inserem nem alteram evidências. Os textos literais vêm do usuário; nenhum texto individual é gerado automaticamente.

Artes originais são privadas em assets/backgrounds, templates em data/templates; ambos ficam fora do versionamento. O componente recebe apenas fundo e configuração, nunca as fotos ou o nome do aluno. Prévia real é servida pelo Streamlit local como imagem em memória, sem exportação explícita, e deixa de ser exibida quando o modo/aluno selecionado muda até nova geração. A futura distribuição precisa incluir HTML/JS/CSS como recursos de leitura e configurar diretórios persistentes graváveis para JSON e artes. Modelo já reserva ordem/sobreposição/transição; apenas sobreposição entre regiões é aplicada agora.

Logging existente inclui import_background, save_template, load_template, list_templates e render_preview, com stack sanitizado; template_saved só é emitido após publicação do arquivo atual. Os testes de navegador são opcionais e requerem Playwright/Chromium como ferramentas de desenvolvimento; execução do aplicativo continua sem dependências novas. Arte demonstrativa dos testes é somente fundo branco sintético, sem geração de arte Low Poly.


## Inicializador Windows local

INICIAR_PORTFOLIOS.bat delega a scripts/ambiente.ps1 a descoberta do Python e
a src/launcher.py o controle do servidor. INSTALAR_AMBIENTE.bat faz o preparo
separado; nao ha pip no uso cotidiano. O ambiente local pode aproveitar pacotes
do Python de origem. Launcher usa lock msvcrt por projeto, health HTTP sem proxy,
porta livre em loopback e processo filho identificado pelo proprio Popen.
Ctrl+C solicita CTRL_BREAK ao filho e aguarda; terminate e restrito a esse filho
se ele nao responder. O lock nao identifica servidores iniciados manualmente.
Estado local fica em outputs, excluido do Git. Eventos launcher_ready e
launcher_failed usam o catalogo sanitizado existente, sem saida bruta externa.
Nao ha alteracao de banco, dashboard, editor ou catalogo pedagogico.
