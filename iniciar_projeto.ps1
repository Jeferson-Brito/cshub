# CSHub - Script de Inicialização do Projeto
# PowerShell Script para Windows

# Define encoding
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Define cores
$Host.UI.RawUI.WindowTitle = "CSHub - Sistema de Gestão de Reclamações"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  CSHub - Iniciando o Projeto" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Verifica se está no diretório correto
if (-not (Test-Path "manage.py")) {
    Write-Host "[ERRO] Arquivo manage.py não encontrado!" -ForegroundColor Red
    Write-Host "Por favor, execute este script a partir da pasta raiz do projeto." -ForegroundColor Yellow
    Read-Host -Prompt "Pressione Enter para sair"
    exit 1
}

# Ativa o ambiente virtual
Write-Host "[1/3] Ativando ambiente virtual..." -ForegroundColor Cyan
if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1"
    Write-Host "✓ Ambiente virtual ativado" -ForegroundColor Green
}
else {
    Write-Host "[AVISO] Ambiente virtual não encontrado!" -ForegroundColor Yellow
    Write-Host "Continuando sem ambiente virtual..." -ForegroundColor Yellow
}
Write-Host ""

# Verifica o Python
Write-Host "[2/4] Verificando dependências..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion encontrado" -ForegroundColor Green
}
catch {
    Write-Host "[ERRO] Python não encontrado!" -ForegroundColor Red
    Write-Host "Por favor, instale o Python 3.11+ e tente novamente." -ForegroundColor Yellow
    Read-Host -Prompt "Pressione Enter para sair"
    exit 1
}
Write-Host ""

# Instala dependências
Write-Host "[3/4] Instalando/Atualizando dependências..." -ForegroundColor Cyan
if (Test-Path "requirements.txt") {
    Write-Host "Instalando pacotes do requirements.txt..." -ForegroundColor Yellow
    python -m pip install --quiet --upgrade pip
    python -m pip install --quiet -r requirements.txt
    Write-Host "✓ Dependências instaladas" -ForegroundColor Green
}
else {
    Write-Host "[AVISO] Arquivo requirements.txt não encontrado!" -ForegroundColor Yellow
}
Write-Host ""

# Inicia o servidor
Write-Host "[4/4] Iniciando servidor Django..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Servidor rodando em: http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host "  Pressione Ctrl+C para parar o servidor" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Inicia o servidor Django
python manage.py runserver

# Pausa no final (caso o servidor seja encerrado)
Read-Host -Prompt "Pressione Enter para sair"
