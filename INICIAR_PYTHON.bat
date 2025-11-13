@echo off
cd /d "%~dp0"

echo ========================================
echo Iniciando servidor Django
echo ========================================
echo.

if not exist venv (
    echo ERRO: Ambiente virtual nao encontrado!
    echo Execute primeiro: INSTALAR_PYTHON.bat
    pause
    exit /b 1
)

if not exist venv\Scripts\python.exe (
    echo ERRO: Python do ambiente virtual nao encontrado!
    echo Execute primeiro: INSTALAR_PYTHON.bat
    pause
    exit /b 1
)

echo Verificando se Django esta instalado...
venv\Scripts\python.exe -c "import django" 2>nul
if %errorlevel% neq 0 (
    echo ERRO: Django nao esta instalado!
    echo Execute primeiro: INSTALAR_PYTHON.bat
    pause
    exit /b 1
)

echo O servidor vai iniciar em: http://localhost:8000
echo.
echo Para parar o servidor, pressione Ctrl+C
echo.
echo ========================================
echo.

venv\Scripts\python.exe manage.py runserver

pause

