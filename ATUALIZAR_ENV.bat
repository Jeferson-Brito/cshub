@echo off
cd /d "%~dp0"

echo ========================================
echo Atualizando arquivo .env
echo ========================================
echo.

if exist .env (
    echo Arquivo .env ja existe, atualizando...
) else (
    echo Criando arquivo .env...
)

(
echo DB_NAME=gestao_reclame_aqui
echo DB_USER=postgres
echo DB_PASSWORD=@Lionnees14
echo DB_HOST=localhost
echo DB_PORT=5433
echo SECRET_KEY=django-insecure-change-me-in-production-12345
) > .env

echo.
echo Arquivo .env atualizado com sucesso!
echo.
echo IMPORTANTE: Se sua senha do PostgreSQL for diferente,
echo edite o arquivo .env manualmente e altere DB_PASSWORD
echo.
pause

