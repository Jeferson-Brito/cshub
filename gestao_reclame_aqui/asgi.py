"""
ASGI config for gestao_reclame_aqui project.
"""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestao_reclame_aqui.settings')

application = get_asgi_application()


