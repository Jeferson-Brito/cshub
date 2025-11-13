from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    ROLE_CHOICES = [
        ('analista', 'Analista'),
        ('gestor', 'Gestor'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='analista')
    ativo = models.BooleanField(default=True)
    
    def is_gestor(self):
        return self.role == 'gestor'
    
    def is_analista(self):
        return self.role == 'analista'


class Complaint(models.Model):
    ORIGEM_CHOICES = [
        ('RA', 'Reclame Aqui'),
        ('Telefone', 'Telefone'),
        ('Email', 'Email'),
        ('WhatsApp', 'WhatsApp'),
        ('Outro', 'Outro'),
    ]
    
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_andamento', 'Em Andamento'),
        ('em_replica', 'Em Réplica'),
        ('aguardando_avaliacao', 'Aguardando Avaliação'),
        ('resolvido', 'Resolvido'),
    ]
    
    id_ra = models.CharField(max_length=100, unique=True)
    cpf_cliente = models.CharField(max_length=14)  # Aceita formato 000.000.000-00
    nome_cliente = models.CharField(max_length=200)
    sobrenome = models.CharField(max_length=200, blank=True)
    email_cliente = models.EmailField()
    telefone = models.CharField(max_length=20, blank=True)
    loja_cod = models.CharField(max_length=50)
    origem_contato = models.CharField(max_length=20, choices=ORIGEM_CHOICES)
    descricao = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    analista = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='complaints')
    data_reclamacao = models.DateField()
    data_resposta = models.DateField(null=True, blank=True)
    nota_satisfacao = models.IntegerField(null=True, blank=True)
    feedback_text = models.TextField(blank=True)
    repeticoes_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['cpf_cliente']),
            models.Index(fields=['id_ra']),
            models.Index(fields=['email_cliente']),
            models.Index(fields=['loja_cod']),
            models.Index(fields=['analista']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.id_ra} - {self.nome_cliente}"


class Activity(models.Model):
    TIPO_CHOICES = [
        ('criacao', 'Criação'),
        ('atualizacao', 'Atualização'),
        ('resposta_cliente', 'Resposta ao Cliente'),
        ('mudanca_status', 'Mudança de Status'),
        ('avaliacao', 'Avaliação'),
        ('comentario_interno', 'Comentário Interno'),
        ('anexo_adicionado', 'Anexo Adicionado'),
    ]
    
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='activities')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    comentario = models.TextField()
    tipo_interacao = models.CharField(max_length=20, choices=TIPO_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.complaint.id_ra} - {self.tipo_interacao}"


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Criar'),
        ('update', 'Atualizar'),
        ('delete', 'Excluir'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('password_reset', 'Reset de Senha'),
        ('status_change', 'Mudança de Status'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    target_type = models.CharField(max_length=100, blank=True)
    target_id = models.IntegerField(null=True, blank=True)
    detalhes_json = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.usuario} - {self.action}"


