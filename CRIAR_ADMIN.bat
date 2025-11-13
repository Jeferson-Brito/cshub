@echo off
cd /d "%~dp0"

echo ========================================
echo Criando Usuario Administrador
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
echo Criando usuario administrador Jeferson Brito...
echo.

venv\Scripts\python.exe manage.py create_admin_user

if %errorlevel% neq 0 (
    echo ERRO ao criar usuario administrador!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Usuario administrador criado/atualizado!
echo ========================================
echo.
echo Credenciais:
echo - Usuario: jefersonbrito
echo - Email: jeffersonbrito245@gmail.com
echo - Senha: @Lionnees14
echo - Perfil: Gestor
echo.
pause

