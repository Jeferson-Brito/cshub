"""
Django management command to create the admin user.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Cria o usuário administrador Jeferson Brito'

    def handle(self, *args, **options):
        username = 'jefersonbrito'
        email = 'jeffersonbrito245@gmail.com'
        password = '@Lionnees14'
        
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            user.email = email
            user.set_password(password)
            user.role = 'gestor'
            user.ativo = True
            user.first_name = 'Jeferson'
            user.last_name = 'Brito'
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Usuário {username} atualizado com sucesso!')
            )
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role='gestor',
                ativo=True,
                first_name='Jeferson',
                last_name='Brito'
            )
            self.stdout.write(
                self.style.SUCCESS(f'Usuário {username} criado com sucesso!')
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nCredenciais de acesso:\n'
                f'Usuário: {username}\n'
                f'E-mail: {email}\n'
                f'Senha: {password}\n'
                f'Perfil: Gestor\n'
            )
        )

