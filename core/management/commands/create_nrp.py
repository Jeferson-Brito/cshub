from django.core.management.base import BaseCommand
from core.models import Department

class Command(BaseCommand):
    help = 'Cria o departamento NRP'

    def handle(self, *args, **options):
        dept, created = Department.objects.get_or_create(
            slug='nrp',
            defaults={
                'name': 'NRP',
                'description': 'Departamento de NRP'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Departamento "{dept.name}" criado com sucesso!'))
        else:
            self.stdout.write(self.style.WARNING(f'Departamento "{dept.name}" já existe.'))
