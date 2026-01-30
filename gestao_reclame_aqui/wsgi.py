"""
WSGI config for gestao_reclame_aqui project.
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestao_reclame_aqui.settings')

application = get_wsgi_application()


