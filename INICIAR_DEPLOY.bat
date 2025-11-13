@echo off
chcp 65001 >nul
cls
echo ========================================
echo 🚀 ASSISTENTE DE DEPLOY - CSHub
echo ========================================
echo.
echo Este script vai te guiar passo a passo!
echo.
pause

:menu
cls
echo ========================================
echo 🚀 ASSISTENTE DE DEPLOY - CSHub
echo ========================================
echo.
echo Escolha uma opção:
echo.
echo [1] Preparar código para GitHub
echo [2] Gerar SECRET_KEY
echo [3] Ver comandos Git
echo [4] Ver instruções do Render
echo [5] Verificar se tudo está pronto
echo [0] Sair
echo.
set /p opcao="Digite o número da opção: "

if "%opcao%"=="1" goto preparar
if "%opcao%"=="2" goto secretkey
if "%opcao%"=="3" goto comandos
if "%opcao%"=="4" goto render
if "%opcao%"=="5" goto verificar
if "%opcao%"=="0" goto fim
goto menu

:preparar
cls
echo ========================================
echo PREPARANDO CÓDIGO PARA GITHUB
echo ========================================
echo.

echo [1/4] Inicializando Git...
if not exist ".git" (
    git init
    echo ✓ Git inicializado
) else (
    echo ✓ Git já está configurado
)
echo.

echo [2/4] Verificando arquivos...
if exist "Procfile" (echo ✓ Procfile) else (echo ✗ Procfile não encontrado!)
if exist "runtime.txt" (echo ✓ runtime.txt) else (echo ✗ runtime.txt não encontrado!)
if exist "requirements.txt" (echo ✓ requirements.txt) else (echo ✗ requirements.txt não encontrado!)
if exist ".gitignore" (echo ✓ .gitignore) else (echo ✗ .gitignore não encontrado!)
echo.

echo [3/4] Adicionando arquivos ao Git...
git add .
echo ✓ Arquivos adicionados
echo.

echo [4/4] Criando commit...
git commit -m "CSHub - Sistema de Gestão de Reclamações" 2>nul
if %errorlevel%==0 (
    echo ✓ Commit criado com sucesso!
) else (
    echo ⚠ Configure seu Git primeiro:
    echo    git config --global user.name "Seu Nome"
    echo    git config --global user.email "seu@email.com"
    echo.
    echo    Depois execute novamente esta opção.
)
echo.
pause
goto menu

:secretkey
cls
echo ========================================
echo GERANDO SECRET_KEY
echo ========================================
echo.
echo Sua SECRET_KEY para usar no Render:
echo.
venv\Scripts\python.exe -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
echo.
echo ⚠️ COPIE ESTA CHAVE! Você precisará dela no Render.
echo.
pause
goto menu

:comandos
cls
echo ========================================
echo COMANDOS GIT
echo ========================================
echo.
echo Execute estes comandos no terminal:
echo.
echo 1. git branch -M main
echo.
echo 2. git remote add origin https://github.com/SEU_USUARIO/cshub.git
echo    (Substitua SEU_USUARIO pelo seu usuário do GitHub)
echo.
echo 3. git push -u origin main
echo.
echo ⚠️ Se pedir credenciais, use um Personal Access Token
echo    (não sua senha do GitHub)
echo.
type COMANDOS_GIT.txt
pause
goto menu

:render
cls
echo ========================================
echo INSTRUÇÕES DO RENDER
echo ========================================
echo.
type CONFIGURAR_RENDER.txt
pause
goto menu

:verificar
cls
echo ========================================
echo VERIFICAÇÃO FINAL
echo ========================================
echo.

set tudo_ok=1

echo Verificando arquivos necessários...
if exist "Procfile" (echo ✓ Procfile) else (echo ✗ Procfile - FALTANDO! & set tudo_ok=0)
if exist "runtime.txt" (echo ✓ runtime.txt) else (echo ✗ runtime.txt - FALTANDO! & set tudo_ok=0)
if exist "requirements.txt" (echo ✓ requirements.txt) else (echo ✗ requirements.txt - FALTANDO! & set tudo_ok=0)
if exist ".gitignore" (echo ✓ .gitignore) else (echo ✗ .gitignore - FALTANDO! & set tudo_ok=0)
if exist "manage.py" (echo ✓ manage.py) else (echo ✗ manage.py - FALTANDO! & set tudo_ok=0)
if exist "gestao_reclame_aqui\settings.py" (echo ✓ settings.py) else (echo ✗ settings.py - FALTANDO! & set tudo_ok=0)
echo.

echo Verificando Git...
if exist ".git" (
    echo ✓ Git inicializado
    git status >nul 2>&1
    if %errorlevel%==0 (
        echo ✓ Git configurado corretamente
    ) else (
        echo ⚠ Configure Git: git config --global user.name e user.email
    )
) else (
    echo ✗ Git não inicializado - Execute opção [1]
    set tudo_ok=0
)
echo.

if %tudo_ok%==1 (
    echo ========================================
    echo ✅ TUDO PRONTO PARA DEPLOY!
    echo ========================================
    echo.
    echo Próximos passos:
    echo 1. Crie conta no GitHub (se não tiver)
    echo 2. Crie repositório no GitHub
    echo 3. Execute os comandos Git (opção [3])
    echo 4. Configure no Render (opção [4])
    echo.
) else (
    echo ========================================
    echo ⚠️ ALGUNS ARQUIVOS ESTÃO FALTANDO
    echo ========================================
    echo.
    echo Execute a opção [1] para preparar o código.
    echo.
)
pause
goto menu

:fim
echo.
echo Até logo! 👋
timeout /t 2 >nul
exit

