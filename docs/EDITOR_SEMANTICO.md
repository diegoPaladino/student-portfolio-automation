# Editor semântico de templates

Inicie pelo INICIAR_PORTFOLIOS.bat e abra Editor de Templates. Se o programa já estava aberto durante uma atualização, salve os rascunhos, encerre com Ctrl+C e inicie novamente.

## Projeto 4

1. Em Criar template a partir de uma arte, escolha o Projeto 4 e envie a arte local `P04_HORTA_BG_V01.png`. Os bytes originais serão preservados.
2. Selecione `title` em Tipo antes de desenhar. Em Campo da nova região, escolha `P04.title` e arraste o retângulo sobre a arte.
3. O painel Conteúdo associado mostra o texto da professora automaticamente. A lista e o rótulo da região mostram `title — P04.title`.
4. Crie `body_text` com `P04.introduction`; duas regiões `photo`, uma para `P04_F01` e outra para `P04_F02`; e regiões `caption` com `P04.caption_1` e `P04.caption_2`.
5. Ajuste posição, tamanho, enquadramento, família, tamanho da fonte, peso, cor, alinhamento, altura de linha, espaçamento entre letras, margem interna e quebra automática. Os valores tipográficos usam referência de 1080 pixels de largura e acompanham a redução da prévia.
6. Clique Atualizar prévia para ver a composição real. Fotos sintéticas e evidências aprovadas ausentes têm marcadores explícitos e não geram evidências. Textos ausentes também são sinalizados. Regiões com texto excedente recebem borda vermelha e aviso: aumente a região ou ajuste a fonte. O texto persistido permanece completo; não há redução automática da fonte.
7. Salve o template. Depois de reiniciar, use Abrir um template salvo para recuperar regiões, vínculos e estilos.

`subtitle`, `highlight` e `student_name` seguem o mesmo fluxo. Abertura geral, síntese e encerramento também aparecem entre as seções disponíveis. A abertura geral não possui requisitos fotográficos. Trocar o tipo preserva o estilo e guarda a origem anterior para recuperá-la ao voltar ao tipo anterior. Confira o vínculo após a troca; Aplicar estilo sugerido é uma ação explícita.

## Conteúdo e personalizações

O TXT de referência é lido localmente e permanece intacto. O catálogo gerado fica em `config/conteudo_pedagogico_2026.json`, com esquema 1, hash e linhas de origem. Contém 13 seções, com instruções editoriais separadas dos campos destinados à composição. As descrições fotográficas não são oferecidas como legendas. Campos ausentes são informados, nunca completados automaticamente.

O catálogo e suas versões são privados e excluídos do Git, pois podem conter assinatura e outros textos pessoais. Com PORTFOLIO_DATA_DIR alternativo, ficam no subdiretório config dessa pasta. Preserve o TXT, o catálogo e `config/pedagogy_versions` na cópia de segurança local. O catálogo existente não é reimportado automaticamente: use Reimportar referência local preservando edições após revisar uma alteração no TXT. O importador espera a estrutura atual da referência; mudanças de formato exigem revisão técnica.

Em Textos pedagógicos — original, edição global e personalização:

- Confira o original e as linhas de origem. Escolha o campo e o alcance Global ou Individual. Para Individual, selecione antes o aluno em Aluno real na prévia.
- Salvar edição de texto mantém uma revisão no SQLite. A prioridade é **individual > global > original**. Mudanças globais preservam personalizações existentes.
- Restaurar texto original neste alcance remove a edição global; no alcance individual, grava uma cópia do original, que prevalece sobre futuras mudanças globais. Remover personalização e seguir texto global/original volta a seguir a precedência normal.
- Revisão para recuperar permite inspecionar e recuperar uma versão anterior. Recuperar também cria uma nova revisão, sem apagar histórico.

Sublinhados de seis ou mais caracteres são preservados no catálogo. Na prévia de aluno real, recebem o primeiro nome cadastrado; a prévia sintética mantém os sublinhados e avisa sobre o campo individual pendente. Isso não gera observações sobre a criança. Texto informado é um conteúdo local do próprio template; campos pedagógicos usam as edições persistidas com a precedência acima.

## Compatibilidade e limites

Templates de esquema 1 continuam legíveis; o próximo salvamento usa esquema 2, mantendo campos desconhecidos e revisões anteriores. A proporção e a altura da arte continuam livres; coordenadas permanecem normalizadas. Não há ampliação automática do fundo nem fixação em 1920 pixels: aumente as regiões nos limites da arte ou importe outra arte para um novo template.

As fontes oferecidas são as disponíveis no sistema: Arial, Segoe UI e Georgia no Windows verificado. São usadas da instalação local, sem redistribuição. Em Arial e Georgia, seminegrito usa a variante negrito disponível; Segoe UI tem variante seminegrito própria. Não há upload de fontes ou rich text. Alterar fontes do sistema pode afetar a composição. A revisão de legibilidade pela professora, especialmente na largura de um smartphone, continua necessária.

Fechar o navegador perde rascunhos não salvos. Salve o template e as edições de texto em seus respectivos botões. A prévia precisa ser atualizada após editar textos. Sem PDF definitivo, lote ou portal nesta etapa.
