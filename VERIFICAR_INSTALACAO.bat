@echo off
cd /d "%~dp0"

echo ========================================
echo Verificando Instalacao
echo ========================================
echo.

echo [1/4] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado!
    echo Instale Python de: https://www.python.org/downloads/
    echo E marque "Add Python to PATH" durante a instalacao
) else (
    python --version
    echo OK!
)
echo.

echo [2/4] Verificando ambiente virtual...
if not exist venv (
    echo ERRO: Ambiente virtual nao encontrado!
    echo Execute: INSTALAR_PYTHON.bat
) else (
    echo Ambiente virtual existe
    if exist venv\Scripts\python.exe (
        echo Python do venv: OK!
    ) else (
        echo ERRO: Python do venv nao encontrado!
    )
)
echo.

echo [3/4] Verificando Django...
if exist venv\Scripts\python.exe (
    venv\Scripts\python.exe -c "import django; print('Django', django.get_version())" 2>nul
    if %errorlevel% neq 0 (
        echo ERRO: Django nao esta instalado!
        echo Execute: INSTALAR_PYTHON.bat
    ) else (
        echo OK!
    )
) else (
    echo ERRO: Ambiente virtual nao configurado!
)
echo.

echo [4/4] Verificando arquivo .env...
if exist .env (
    echo Arquivo .env existe
) else (
    echo AVISO: Arquivo .env nao encontrado!
    echo Crie o arquivo .env com suas credenciais PostgreSQL
)
echo.

echo ========================================
echo Verificacao concluida!
echo ========================================
echo.
pause


