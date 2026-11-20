param([ValidateSet('iniciar','instalar')][string]$Acao = 'iniciar')
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
try {
    $candidatos = @()
    if ($env:VIRTUAL_ENV) { $candidatos += Join-Path $env:VIRTUAL_ENV 'Scripts\python.exe' }
    $candidatos += Get-ChildItem -Directory -Force | Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'pyvenv.cfg') } | ForEach-Object { Join-Path $_.FullName 'Scripts\python.exe' }
    $python = $candidatos | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
    if (-not $python) {
        $comando = Get-Command python.exe -ErrorAction SilentlyContinue
        if ($comando) { $python = $comando.Source }
    }
    if (-not $python) {
        Write-Host 'Python ausente. Instale Python 3.11 ou superior com venv e execute INSTALAR_AMBIENTE.bat.'
        exit 1
    }
    if ($Acao -eq 'instalar') {
        if (-not $candidatos) {
            Write-Host 'Preparando ambiente local .venv; pacotes compativeis existentes serao aproveitados.'
            & $python -m venv --system-site-packages .venv
            if ($LASTEXITCODE -ne 0) { exit 1 }
            $python = Join-Path (Get-Location) '.venv\Scripts\python.exe'
        }
        & $python -m src.launcher --check
        if ($LASTEXITCODE -ne 0) {
            Write-Host 'Instalando requisitos. Esta etapa requer acesso ao repositorio de pacotes.'
            & $python -m pip install -r requirements.txt
            if ($LASTEXITCODE -ne 0) { exit 1 }
        }
        & $python -m src.launcher --check
        exit $LASTEXITCODE
    }
    & $python -m src.launcher
    exit $LASTEXITCODE
} catch {
    Write-Host 'Nao foi possivel preparar ou iniciar. Confira Python, permissoes e execute INSTALAR_AMBIENTE.bat.'
    exit 1
}
