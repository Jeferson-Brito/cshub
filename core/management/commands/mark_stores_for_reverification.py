"""
Management command para marcar lojas que precisam de reverificação diária.

Este comando deve ser executado diariamente (via cron/scheduler) para:
- Identificar lojas que foram auditadas há mais de 24 horas
- Marcar essas lojas com needs_reverification = True
- Enviar relatório de quantas lojas precisam de reverificação
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import Store


class Command(BaseCommand):
    help = 'Marca lojas que foram auditadas há mais de 24 horas para reverificação'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Número de horas desde a última auditoria para marcar para reverificação (padrão: 24)',
        )

    def handle(self, *args, **options):
        hours = options['hours']
        cutoff_time = timezone.now() - timedelta(hours=hours)

        # Encontrar lojas que foram auditadas mas ainda não foram reverificadas
        stores_to_reverify = Store.objects.filter(
            last_audit_date__isnull=False,  # Tem auditoria
            last_audit_date__lt=cutoff_time,  # Auditoria foi há mais de X horas
            needs_reverification=False,  # Ainda não foi marcada para reverificação
            active=True  # Loja está ativa
        )

        count = stores_to_reverify.count()

        if count == 0:
            self.stdout.write(
                self.style.SUCCESS(f'Nenhuma loja precisa ser marcada para reverificação.')
            )
            return

        # Marcar lojas para reverificação
        stores_to_reverify.update(needs_reverification=True)

        self.stdout.write(
            self.style.SUCCESS(
                f'✓ {count} loja(s) marcada(s) para reverificação.\n'
                f'Cutoff: {cutoff_time.strftime("%d/%m/%Y %H:%M")}'
            )
        )

        # Relatório detalhado (opcional)
        if self.verbosity >= 2:
            self.stdout.write('\nLojas marcadas:')
            for store in stores_to_reverify[:20]:  # Mostrar até 20
                last_audit = store.last_audit_date.strftime("%d/%m/%Y %H:%M") if store.last_audit_date else "N/A"
                result = store.get_last_audit_result_display()
                self.stdout.write(f'  - {store.code} ({store.city}) - Última auditoria: {last_audit} - Resultado: {result}')
            
            if count > 20:
                self.stdout.write(f'  ... e mais {count - 20} loja(s)')
