from django.core.management.base import BaseCommand
from core.models import Department

class Command(BaseCommand):
    help = 'Cria o departamento Concierge'

    def handle(self, *args, **options):
        dept, created = Department.objects.get_or_create(
            slug='concierge',
            defaults={
                'name': 'Concierge',
                'description': 'Departamento de Concierge'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Departamento "{dept.name}" criado com sucesso!'))
        else:
            self.stdout.write(self.style.WARNING(f'Departamento "{dept.name}" já existe.'))
