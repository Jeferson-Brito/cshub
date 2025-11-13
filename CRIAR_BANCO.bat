@echo off
cd /d "%~dp0"

echo ========================================
echo Criando Banco de Dados PostgreSQL
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
echo Criando banco de dados...
echo.

REM Carrega variaveis do .env
if exist .env (
    for /f "tokens=1,2 delims==" %%a in (.env) do (
        if "%%a"=="DB_NAME" set DB_NAME=%%b
        if "%%a"=="DB_USER" set DB_USER=%%b
        if "%%a"=="DB_PASSWORD" set DB_PASSWORD=%%b
        if "%%a"=="DB_HOST" set DB_HOST=%%b
        if "%%a"=="DB_PORT" set DB_PORT=%%b
    )
) else (
    echo AVISO: Arquivo .env nao encontrado, usando valores padrao
    set DB_NAME=gestao_reclame_aqui
    set DB_USER=postgres
    set DB_PASSWORD=
    set DB_HOST=localhost
    set DB_PORT=5433
)

echo Usando:
echo - Banco: %DB_NAME%
echo - Usuario: %DB_USER%
echo - Host: %DB_HOST%
echo - Porta: %DB_PORT%
echo.

REM Cria script Python temporario para criar o banco
echo import psycopg^
from psycopg import sql^
import os^
from dotenv import load_dotenv^
load_dotenv()^
^
DB_NAME = os.getenv('DB_NAME', 'gestao_reclame_aqui')^
DB_USER = os.getenv('DB_USER', 'postgres')^
DB_PASSWORD = os.getenv('DB_PASSWORD', '')^
DB_HOST = os.getenv('DB_HOST', 'localhost')^
DB_PORT = os.getenv('DB_PORT', '5433')^
^
try:^
    conn = psycopg.connect(^
        host=DB_HOST,^
        port=DB_PORT,^
        user=DB_USER,^
        password=DB_PASSWORD,^
        dbname='postgres'^
    )^
    conn.autocommit = True^
    cur = conn.cursor()^
    cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")^
    exists = cur.fetchone()^
    if not exists:^
        cur.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(DB_NAME)))^
        print(f'Banco de dados {DB_NAME} criado com sucesso!')^
    else:^
        print(f'Banco de dados {DB_NAME} ja existe.')^
    cur.close()^
    conn.close()^
except Exception as e:^
    print(f'ERRO: {e}')^
    exit(1)
> temp_create_db.py

venv\Scripts\python.exe temp_create_db.py

if %errorlevel% neq 0 (
    echo.
    echo ERRO ao criar banco de dados!
    echo Verifique se:
    echo - PostgreSQL esta rodando
    echo - Usuario e senha estao corretos no arquivo .env
    echo - Porta esta correta (padrao: 5433)
    del temp_create_db.py
    pause
    exit /b 1
)

del temp_create_db.py

echo.
echo ========================================
echo Banco de dados criado com sucesso!
echo ========================================
echo.
pause

