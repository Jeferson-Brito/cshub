from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Complaint, Activity, AuditLog
from datetime import datetime, timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Cria dados de exemplo para teste'

    def handle(self, *args, **options):
        # Criar usuários
        gestor, _ = User.objects.get_or_create(
            username='gestor',
            defaults={
                'email': 'gestor@example.com',
                'role': 'gestor',
                'ativo': True
            }
        )
        gestor.set_password('123456')
        gestor.save()

        analista1, _ = User.objects.get_or_create(
            username='analista1',
            defaults={
                'email': 'analista1@example.com',
                'role': 'analista',
                'ativo': True
            }
        )
        analista1.set_password('123456')
        analista1.save()

        analista2, _ = User.objects.get_or_create(
            username='analista2',
            defaults={
                'email': 'analista2@example.com',
                'role': 'analista',
                'ativo': True
            }
        )
        analista2.set_password('123456')
        analista2.save()

        # Criar reclamações
        statuses = ['pendente', 'em_andamento', 'aguardando_avaliacao', 'resolvido']
        origens = ['RA', 'Telefone', 'Email', 'WhatsApp', 'Outro']
        lojas = ['001', '002', '003', '004', '005', '010', '015', '020', '025', '030']
        nomes = ['João', 'Maria', 'Pedro', 'Ana', 'Carlos', 'Juliana', 'Roberto', 'Fernanda', 'Lucas', 'Patricia']
        sobrenomes = ['Silva', 'Santos', 'Oliveira', 'Souza', 'Costa', 'Ferreira', 'Rodrigues', 'Almeida', 'Nascimento', 'Lima']

        for i in range(50):
            nome = random.choice(nomes)
            sobrenome = random.choice(sobrenomes)
            loja = random.choice(lojas)
            status = random.choice(statuses)
            origem = random.choice(origens)
            analista = random.choice([analista1, analista2])

            complaint = Complaint.objects.create(
                id_ra=f"RA-{datetime.now().strftime('%Y%m%d')}-{i:04d}",
                cpf_cliente=f"{random.randint(10000000000, 99999999999)}",
                nome_cliente=nome,
                sobrenome=sobrenome,
                email_cliente=f"{nome.lower()}.{sobrenome.lower()}@example.com",
                telefone=f"(11) {random.randint(90000, 99999)}-{random.randint(1000, 9999)}",
                loja_cod=loja,
                origem_contato=origem,
                descricao=f"Reclamação sobre produto/serviço. Cliente relata problema com {random.choice(['atraso na entrega', 'qualidade do produto', 'atendimento', 'cobrança indevida', 'produto defeituoso'])}.",
                status=status,
                analista=analista,
                data_reclamacao=datetime.now().date() - timedelta(days=random.randint(0, 30)),
                data_resposta=datetime.now().date() - timedelta(days=random.randint(0, 5)) if status == 'resolvido' else None,
                nota_satisfacao=random.randint(6, 10) if status == 'resolvido' else None,
                feedback_text=random.choice(['Ótimo atendimento', 'Problema resolvido', 'Satisfeito', 'Poderia melhorar']) if status == 'resolvido' else '',
                repeticoes_count=random.randint(0, 3),
            )

            Activity.objects.create(
                complaint=complaint,
                usuario=analista,
                comentario="Reclamação criada",
                tipo_interacao='criacao'
            )

            if status == 'resolvido':
                Activity.objects.create(
                    complaint=complaint,
                    usuario=analista,
                    comentario=f"Reclamação resolvida. Nota: {complaint.nota_satisfacao}/10",
                    tipo_interacao='avaliacao'
                )

        self.stdout.write(self.style.SUCCESS('Dados de exemplo criados com sucesso!'))
        self.stdout.write(self.style.SUCCESS('Usuários criados:'))
        self.stdout.write(self.style.SUCCESS('  Gestor: gestor / 123456'))
        self.stdout.write(self.style.SUCCESS('  Analista 1: analista1 / 123456'))
        self.stdout.write(self.style.SUCCESS('  Analista 2: analista2 / 123456'))


