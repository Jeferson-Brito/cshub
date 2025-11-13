@echo off
cd /d "%~dp0"

echo ========================================
echo Instalando dependencias Python
echo ========================================
echo.

echo [1/4] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado!
    echo Instale Python de: https://www.python.org/downloads/
    echo E marque "Add Python to PATH" durante a instalacao
    pause
    exit /b 1
)
python --version
echo OK!
echo.

echo [2/4] Criando/Atualizando ambiente virtual...
if exist venv (
    echo Ambiente virtual ja existe, atualizando...
) else (
    echo Criando novo ambiente virtual...
)
python -m venv venv
if %errorlevel% neq 0 (
    echo ERRO: Falha ao criar ambiente virtual!
    pause
    exit /b 1
)
echo OK!
echo.

echo [3/4] Verificando pip do ambiente virtual...
if not exist venv\Scripts\python.exe (
    echo ERRO: Python do ambiente virtual nao encontrado!
    pause
    exit /b 1
)
venv\Scripts\python.exe -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: pip nao encontrado no ambiente virtual!
    pause
    exit /b 1
)
echo OK!
echo.

echo [4/4] Instalando dependencias...
echo Isso pode levar alguns minutos...
echo.
venv\Scripts\python.exe -m pip install --upgrade pip --quiet
if %errorlevel% neq 0 (
    echo ERRO ao atualizar pip!
    pause
    exit /b 1
)
echo pip atualizado!
echo.
venv\Scripts\python.exe -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERRO ao instalar dependencias!
    echo Verifique se o arquivo requirements.txt existe.
    pause
    exit /b 1
)
echo.
echo Verificando instalacao do Django...
venv\Scripts\python.exe -c "import django; print('Django', django.get_version(), 'instalado com sucesso!')" 2>nul
if %errorlevel% neq 0 (
    echo AVISO: Django pode nao ter sido instalado corretamente!
) else (
    echo OK!
)
echo.

echo ========================================
echo Instalacao concluida!
echo ========================================
echo.
echo Proximos passos:
echo 1. Configure o arquivo .env com suas credenciais PostgreSQL
echo 2. Execute: CONFIGURAR_BANCO_PYTHON.bat
echo 3. Execute: python manage.py createsuperuser
echo 4. Execute: python manage.py create_sample_data
echo 5. Execute: INICIAR_PYTHON.bat
echo.
pause
