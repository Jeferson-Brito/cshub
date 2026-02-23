"""
Cria um superusuário inicial a partir de variáveis de ambiente.
Seguro para rodar no buildCommand — não faz nada se o usuário já existir.

Variáveis necessárias:
  ADMIN_EMAIL    - email do superusuário
  ADMIN_PASSWORD - senha do superusuário
  ADMIN_USERNAME - username (opcional, padrão: admin)
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Cria superusuário inicial via variáveis de ambiente (ADMIN_EMAIL, ADMIN_PASSWORD)"

    def handle(self, *args, **options):
        User = get_user_model()

        email = os.environ.get("ADMIN_EMAIL")
        password = os.environ.get("ADMIN_PASSWORD")
        username = os.environ.get("ADMIN_USERNAME", "admin")

        if not email or not password:
            self.stdout.write("ADMIN_EMAIL ou ADMIN_PASSWORD não definidos — pulando criação do superusuário.")
            return

        if User.objects.filter(email=email).exists():
            self.stdout.write(f"Superusuário '{email}' já existe — nenhuma ação.")
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        self.stdout.write(self.style.SUCCESS(f"✅ Superusuário '{email}' criado com sucesso!"))
