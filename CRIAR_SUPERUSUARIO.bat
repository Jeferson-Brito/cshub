@echo off
cd /d "%~dp0"

echo ========================================
echo Criando Superusuario
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

echo.
echo Siga as instrucoes para criar o superusuario:
echo - Usuario: (digite um nome de usuario, ex: admin)
echo - Email: (opcional, pode deixar em branco)
echo - Senha: (digite uma senha forte)
echo.
echo ========================================
echo.

venv\Scripts\python.exe manage.py createsuperuser

if %errorlevel% neq 0 (
    echo ERRO ao criar superusuario!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Superusuario criado com sucesso!
echo ========================================
echo.
pause

