from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Cria usuários analistas de exemplo para teste'

    def handle(self, *args, **options):
        # Criar analistas de exemplo
        analistas_data = [
            {
                'username': 'analista1',
                'email': 'analista1@example.com',
                'first_name': 'Analista',
                'last_name': 'Um',
                'role': 'analista',
                'ativo': True
            },
            {
                'username': 'analista2',
                'email': 'analista2@example.com',
                'first_name': 'Analista',
                'last_name': 'Dois',
                'role': 'analista',
                'ativo': True
            },
            {
                'username': 'analista3',
                'email': 'analista3@example.com',
                'first_name': 'Analista',
                'last_name': 'Tres',
                'role': 'analista',
                'ativo': True
            },
        ]

        for data in analistas_data:
            user, created = User.objects.update_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'role': data['role'],
                    'ativo': data['ativo']
                }
            )
            user.set_password('123456')
            user.save()

            if created:
                self.stdout.write(self.style.SUCCESS(f'Analista {data["username"]} criado com sucesso!'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Analista {data["username"]} atualizado com sucesso!'))

        self.stdout.write(self.style.SUCCESS('\nAnalistas criados:'))
        self.stdout.write(self.style.SUCCESS('  - analista1 / 123456'))
        self.stdout.write(self.style.SUCCESS('  - analista2 / 123456'))
        self.stdout.write(self.style.SUCCESS('  - analista3 / 123456'))

