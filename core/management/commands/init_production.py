"""
Comando para inicializar o sistema em produção.
Executa migrações e cria usuário admin automaticamente.
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
import os

User = get_user_model()


class Command(BaseCommand):
    help = 'Inicializa o sistema em produção: executa migrações e cria usuário admin'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando configuração do sistema...'))
        
        # Executar migrações
        self.stdout.write(self.style.WARNING('Executando migrações...'))
        try:
            call_command('migrate', verbosity=0)
            self.stdout.write(self.style.SUCCESS('✓ Migrações executadas com sucesso!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Erro ao executar migrações: {e}'))
            return
        
        # Criar usuário admin
        self.stdout.write(self.style.WARNING('Criando usuário administrador...'))
        try:
            username = 'jefersonbrito'
            email = 'jeffersonbrito245@gmail.com'
            password = '@Lionnees14'
            first_name = 'Jeferson'
            last_name = 'Brito'
            role = 'gestor'
            ativo = True

            user, created = User.objects.update_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': role,
                    'ativo': ativo
                }
            )
            user.set_password(password)
            user.save()

            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Usuário {username} criado com sucesso!'))
            else:
                self.stdout.write(self.style.SUCCESS(f'✓ Usuário {username} atualizado com sucesso!'))

            self.stdout.write(self.style.SUCCESS('\nCredenciais de acesso:'))
            self.stdout.write(self.style.SUCCESS(f'Usuário: {username}'))
            self.stdout.write(self.style.SUCCESS(f'E-mail: {email}'))
            self.stdout.write(self.style.SUCCESS(f'Senha: {password}'))
            self.stdout.write(self.style.SUCCESS(f'Perfil: {role.capitalize()}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Erro ao criar usuário: {e}'))
            return
        
        self.stdout.write(self.style.SUCCESS('\n✅ Sistema inicializado com sucesso!'))

