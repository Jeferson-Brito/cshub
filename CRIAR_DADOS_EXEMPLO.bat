@echo off
cd /d "%~dp0"

echo ========================================
echo Criando Dados de Exemplo
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

echo Criando dados de exemplo...
echo Isso pode levar alguns segundos...
echo.

venv\Scripts\python.exe manage.py create_sample_data

if %errorlevel% neq 0 (
    echo ERRO ao criar dados de exemplo!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Dados de exemplo criados com sucesso!
echo ========================================
echo.
echo Usuarios criados:
echo - gestor (senha: 123456)
echo - analista1 (senha: 123456)
echo - analista2 (senha: 123456)
echo.
echo 50 reclamações de exemplo foram criadas.
echo.
pause

