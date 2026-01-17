"""
WSGI config for gestao_reclame_aqui project.
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestao_reclame_aqui.settings')

# Executar migrações e criar usuário automaticamente em produção
# (apenas na primeira vez, se a variável INIT_DB estiver definida)
if os.getenv('INIT_DB') == 'true':
    try:
        application = get_wsgi_application()
        from django.core.management import call_command
        from django.db import connection
        
        # Verificar se as tabelas existem
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'core_user'
                );
            """)
            tables_exist = cursor.fetchone()[0]
        
        if not tables_exist:
            # Executar migrações
            call_command('migrate', verbosity=0)
            # Criar usuário admin
            call_command('create_admin_user', verbosity=0)
    except Exception:
        # Se der erro, continua normalmente
        pass
else:
    application = get_wsgi_application()


