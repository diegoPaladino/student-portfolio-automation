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
