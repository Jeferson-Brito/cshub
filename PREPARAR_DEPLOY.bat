@echo off
chcp 65001 >nul
echo ========================================
echo 🚀 PREPARANDO CÓDIGO PARA DEPLOY
echo ========================================
echo.

echo [1/5] Verificando Git...
if not exist ".git" (
    echo Inicializando repositório Git...
    git init
    echo ✓ Repositório Git inicializado
) else (
    echo ✓ Git já está configurado
)
echo.

echo [2/5] Verificando arquivos necessários...
if exist "Procfile" (
    echo ✓ Procfile encontrado
) else (
    echo ✗ Procfile não encontrado!
)

if exist "runtime.txt" (
    echo ✓ runtime.txt encontrado
) else (
    echo ✗ runtime.txt não encontrado!
)

if exist "requirements.txt" (
    echo ✓ requirements.txt encontrado
) else (
    echo ✗ requirements.txt não encontrado!
)
echo.

echo [3/5] Verificando .gitignore...
if exist ".gitignore" (
    echo ✓ .gitignore encontrado
) else (
    echo ✗ .gitignore não encontrado!
)
echo.

echo [4/5] Gerando SECRET_KEY...
echo.
venv\Scripts\python.exe -c "from django.core.management.utils import get_random_secret_key; print('SECRET_KEY=' + get_random_secret_key())" > SECRET_KEY_TEMP.txt
set /p SECRET_KEY=<SECRET_KEY_TEMP.txt
echo %SECRET_KEY%
del SECRET_KEY_TEMP.txt
echo.
echo ✓ SECRET_KEY gerado (copie acima)
echo.

echo [5/5] Verificando estrutura do projeto...
if exist "manage.py" (
    echo ✓ manage.py encontrado
) else (
    echo ✗ manage.py não encontrado!
)

if exist "gestao_reclame_aqui\settings.py" (
    echo ✓ settings.py encontrado
) else (
    echo ✗ settings.py não encontrado!
)

if exist "core\models.py" (
    echo ✓ core app encontrado
) else (
    echo ✗ core app não encontrado!
)
echo.

echo ========================================
echo ✅ PREPARAÇÃO CONCLUÍDA!
echo ========================================
echo.
echo PRÓXIMOS PASSOS:
echo.
echo 1. Crie uma conta no GitHub (se não tiver)
echo    https://github.com
echo.
echo 2. Crie um novo repositório no GitHub
echo    - Nome: cshub (ou outro nome)
echo    - Pode ser privado
echo.
echo 3. Execute os comandos Git abaixo:
echo.
echo    git add .
echo    git commit -m "CSHub - Sistema de Gestão de Reclamações"
echo    git branch -M main
echo    git remote add origin https://github.com/SEU_USUARIO/cshub.git
echo    git push -u origin main
echo.
echo 4. Siga as instruções em DEPLOY_RAPIDO.txt
echo    para configurar no Render.com
echo.
echo ========================================
pause

