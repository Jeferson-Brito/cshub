@echo off
cd /d "%~dp0"

echo ========================================
echo Conectando ao Banco de Dados PostgreSQL
echo ========================================
echo.
echo Conectando ao banco: gestao_reclame_aqui
echo Host: localhost
echo Porta: 5433
echo Usuario: postgres
echo.
echo Comandos uteis:
echo   \dt              - Lista todas as tabelas
echo   SELECT * FROM core_user;        - Ver usuarios
echo   SELECT * FROM core_complaint;   - Ver reclamacoes
echo   SELECT * FROM core_activity;     - Ver atividades
echo   SELECT * FROM core_auditlog;    - Ver logs
echo   \q              - Sair
echo.
echo ========================================
echo.

psql -h localhost -p 5433 -U postgres -d gestao_reclame_aqui

if %errorlevel% neq 0 (
    echo.
    echo ERRO ao conectar!
    echo Verifique se o PostgreSQL esta rodando.
    pause
)

