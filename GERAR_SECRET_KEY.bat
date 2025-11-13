@echo off
echo ========================================
echo Gerando SECRET_KEY para Django
echo ========================================
echo.

venv\Scripts\python.exe -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

echo.
echo ========================================
echo Copie a chave acima e use nas variaveis de ambiente
echo ========================================
pause

