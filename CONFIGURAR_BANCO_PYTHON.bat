@echo off
cd /d "%~dp0"

echo ========================================
echo Configurando Banco de Dados
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
echo OK!
echo.

echo Criando banco de dados (se nao existir)...
venv\Scripts\python.exe manage.py create_database
if %errorlevel% neq 0 (
    echo ERRO ao criar banco de dados!
    echo Verifique se o PostgreSQL esta rodando e se o .env esta correto.
    pause
    exit /b 1
)
echo OK!
echo.

echo Criando migracoes...
venv\Scripts\python.exe manage.py makemigrations
if %errorlevel% neq 0 (
    echo ERRO ao criar migracoes!
    pause
    exit /b 1
)
echo OK!
echo.

echo Aplicando migracoes...
venv\Scripts\python.exe manage.py migrate
if %errorlevel% neq 0 (
    echo ERRO ao aplicar migracoes!
    echo Verifique se o PostgreSQL esta rodando e se o .env esta correto.
    pause
    exit /b 1
)
echo OK!
echo.

echo ========================================
echo Configuracao concluida!
echo ========================================
echo.
echo Proximos passos:
echo 1. Execute: python manage.py createsuperuser
echo 2. Execute: python manage.py runserver
echo 3. Abra: http://localhost:8000
echo.
pause

