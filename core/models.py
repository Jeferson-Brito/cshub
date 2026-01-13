from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class User(AbstractUser):
    ROLE_CHOICES = [
        ('analista', 'Analista'),
        ('gestor', 'Gestor'),
        ('administrador', 'Administrador'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='analista')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    ativo = models.BooleanField(default=True)
    
    def is_gestor(self):
        return self.role == 'gestor'
    
    def is_analista(self):
        return self.role == 'analista'
    
    def is_administrador(self):
        return self.role == 'administrador'


class Store(models.Model):
    code = models.CharField(max_length=10, unique=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    address = models.CharField(max_length=200, blank=True)
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.code} - {self.city}"

class Escala(models.Model):
    """Modelo legado ou simplificado para manter compatibilidade"""
    nome = models.CharField(max_length=100)
    ativo = models.BooleanField(default=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return self.nome
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
    
    TIPO_RECLAMACAO_CHOICES = [
        ('nota_fiscal', 'Nota fiscal'),
        ('pagamento_cartao', 'Pagamento não processado - Cartão'),
        ('pagamento_pix', 'Pagamento não processado - PIX'),
        ('pagamento_checkout', 'Pagamento não processado - Checkout Web'),
        ('assinatura_mensal', 'Assinatura mensal'),
        ('lavagem', 'Lavagem'),
        ('secagem', 'Secagem'),
        ('atendimento', 'Atendimento'),
        ('sistema_totem', 'Sistema/Totem'),
        ('cupons', 'Cupons'),
        ('outros', 'Outros'),
    ]
    
    VOLTA_FAZER_NEGOCIO_CHOICES = [
        ('sim', 'Sim'),
        ('nao', 'Não'),
        ('nao_informado', 'Não informado'),
    ]
    
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='complaints', null=True, blank=True)
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
    tipo_reclamacao = models.CharField(max_length=30, choices=TIPO_RECLAMACAO_CHOICES, blank=True, null=True)
    nota_satisfacao = models.IntegerField(null=True, blank=True)  # 0 a 10
    volta_fazer_negocio = models.CharField(max_length=20, choices=VOLTA_FAZER_NEGOCIO_CHOICES, blank=True, null=True)
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


# ========================================
# MODELOS PARA ESCALA NRS SUPORTE
# ========================================

class Turno(models.Model):
    """Turnos de trabalho para a escala"""
    nome = models.CharField(max_length=100)
    horario = models.CharField(max_length=50)  # Ex: "22:00 - 06:00"
    cor = models.CharField(max_length=20, default='#2563eb')  # Cor hexadecimal
    ordem = models.IntegerField(default=0)
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['ordem', 'nome']
    
    def __str__(self):
        return f"{self.nome} ({self.horario})"


class AnalistaEscala(models.Model):
    """Analistas específicos para a escala NRS (separado do User para flexibilidade)"""
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='escala_perfil')
    nome = models.CharField(max_length=200)
    turno = models.ForeignKey(Turno, on_delete=models.SET_NULL, null=True, blank=True, related_name='analistas')
    pausa = models.CharField(max_length=50, blank=True)  # Ex: "01:00 - 02:00"
    data_primeira_folga = models.DateField(null=True, blank=True)  # Data da primeira folga no ciclo 6x2
    ordem = models.IntegerField(default=0)
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['turno__ordem', 'ordem', 'nome']
    
    def __str__(self):
        return f"{self.nome} - {self.turno.nome if self.turno else 'Sem turno'}"

    @staticmethod
    def format_schedule_name(first_name, last_name):
        """Formata para 'PrimeiroNome S.'"""
        if not first_name:
            return ""
        
        initial = ""
        if last_name:
            initial = f" {last_name[0].upper()}."
        
        return f"{first_name}{initial}"


class FolgaManual(models.Model):
    """Folgas, férias, atestados manuais que sobrescrevem o cálculo automático"""
    TIPO_CHOICES = [
        ('folga', 'Folga'),
        ('ferias', 'Férias'),
        ('atestado', 'Atestado'),
        ('trabalho', 'Trabalho'),  # Para forçar trabalho quando era folga automática
    ]
    
    analista = models.ForeignKey(AnalistaEscala, on_delete=models.CASCADE, related_name='folgas_manuais')
    data = models.DateField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    motivo = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['data']
        unique_together = ['analista', 'data']
    
    def __str__(self):
        return f"{self.analista.nome} - {self.data} - {self.tipo}"


class Evento(models.Model):
    """Eventos para o calendário"""
    TIPO_CHOICES = [
        ('agendamento', 'Agendamento'),
        ('reuniao', 'Reunião'),
        ('visita', 'Visita'),
        ('outro', 'Outro'),
    ]
    
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    data_inicio = models.DateTimeField()
    horario = models.CharField(max_length=10, blank=True, null=True)  # Ex: "14:30"
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='agendamento')
    codigo_loja = models.CharField(max_length=50, blank=True, null=True)
    analista_nome = models.CharField(max_length=200, blank=True, null=True)
    observacao = models.TextField(blank=True, null=True)
    
    # Relações
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='eventos')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='eventos_criados')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['data_inicio', 'horario']
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
    
    def __str__(self):
        return f"{self.titulo} ({self.data_inicio.strftime('%d/%m/%Y')})"

class ArtigoBaseConhecimento(models.Model):
    """Artigos da Base de Conhecimento"""
    CATEGORIA_CHOICES = [
        ('tutorials', 'Tutoriais e Guias'),
        ('solutions', 'Soluções Comuns'),
        ('faq', 'Perguntas Frequentes'),
    ]
    
    titulo = models.CharField(max_length=200)
    conteudo = models.TextField()
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default='tutorials')
    tags = models.CharField(max_length=255, blank=True)
    views = models.PositiveIntegerField(default=0)
    
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='artigos_kb')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='artigos_kb_criados')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-views', '-created_at']
        verbose_name = 'Artigo da Base de Conhecimento'
        verbose_name_plural = 'Artigos da Base de Conhecimento'

    def __str__(self):
        return self.titulo

class FerramentaIA(models.Model):
    """Links para ferramentas de IA"""
    titulo = models.CharField(max_length=200)
    url = models.URLField(max_length=500)
    descricao = models.TextField()
    categoria = models.CharField(max_length=100, default='ia')
    
    class Meta:
        ordering = ['titulo']
        verbose_name = 'Ferramenta de IA'
        verbose_name_plural = 'Ferramentas de IA'

    def __str__(self):
        return self.titulo


# ========================================
# MODELOS PARA DESEMPENHO DO TIME
# ========================================

class IndicadorDesempenho(models.Model):
    """Métricas mensais de desempenho para analistas"""
    analista = models.ForeignKey(User, on_delete=models.CASCADE, related_name='indicadores_desempenho')
    mes = models.IntegerField()  # 1-12
    ano = models.IntegerField()  # Ex: 2026
    nps = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)  # 0.00 a 10.00
    tme = models.IntegerField(null=True, blank=True)  # Tempo Médio de Espera (segundos)
    chats = models.IntegerField(default=0)  # Volume de atendimentos
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='indicadores_desempenho')
    
    # Metas mensais
    meta_tme = models.IntegerField(null=True, blank=True, help_text="Meta de TME em segundos")
    meta_nps = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, help_text="Meta de NPS")
    meta_chats = models.IntegerField(null=True, blank=True, help_text="Meta de quantidade de chats")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-ano', '-mes']
        unique_together = ['analista', 'mes', 'ano']
        verbose_name = 'Indicador de Desempenho'
        verbose_name_plural = 'Indicadores de Desempenho'
        
    def __str__(self):
        return f"{self.analista.username} - {self.mes}/{self.ano} (NPS: {self.nps})"


class MetaMensalGlobal(models.Model):
    """Metas globais aplicáveis a todos os analistas em um determinado mês/ano"""
    mes = models.IntegerField()  # 1-12
    ano = models.IntegerField()  # Ex: 2026
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='metas_globais')
    
    meta_tme = models.IntegerField(null=True, blank=True, help_text="Meta global de TME em segundos")
    meta_nps = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, help_text="Meta global de NPS")
    meta_chats = models.IntegerField(null=True, blank=True, help_text="Meta global de quantidade de chats")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-ano', '-mes']
        unique_together = ['mes', 'ano', 'department']
        verbose_name = 'Meta Mensal Global'
        verbose_name_plural = 'Metas Mensais Globais'
        
    def __str__(self):
        return f"Meta Global - {self.mes}/{self.ano} ({self.department.name})"


class ObservacaoDesempenho(models.Model):
    """Feedbacks, eventos ou observações sobre o desempenho do analista"""
    TIPO_CHOICES = [
        ('feedback', 'Feedback'),
        ('evento', 'Evento'),
        ('treinamento', 'Treinamento'),
        ('elogio', 'Elogio'),
        ('alerta', 'Alerta'),
    ]
    
    analista = models.ForeignKey(User, on_delete=models.CASCADE, related_name='observacoes_desempenho')
    autor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='observacoes_criadas')
    data = models.DateField()
    texto = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='feedback')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='observacoes_desempenho')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-data', '-created_at']
        verbose_name = 'Observação de Desempenho'
        verbose_name_plural = 'Observações de Desempenho'
        
    def __str__(self):
        return f"{self.analista.username} - {self.tipo} - {self.data}"


# ========================================
# MODELOS PARA QUADRO DE TAREFAS (KANBAN)
# ========================================

class QuadroEtiqueta(models.Model):
    """Etiquetas coloridas para o quadro"""
    nome = models.CharField(max_length=50)
    cor = models.CharField(max_length=20) # Hex code
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='etiquetas_quadro')
    
    class Meta:
        verbose_name = 'Etiqueta do Quadro'
        verbose_name_plural = 'Etiquetas do Quadro'
    
    def __str__(self):
        return f"{self.nome} ({self.department.name})"

class Lista(models.Model):
    """Colunas do Quadro Kanban (ex: A Fazer, Em Andamento)"""
    titulo = models.CharField(max_length=100)
    ordem = models.IntegerField(default=0)
    archived = models.BooleanField(default=False)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='listas_quadro')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['ordem']
        verbose_name = 'Lista do Quadro'
        verbose_name_plural = 'Listas do Quadro'
        
    def __str__(self):
        return f"{self.titulo} - {self.department.name}"


class Cartao(models.Model):
    """Cartões/Tarefas do Quadro Kanban"""
    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    lista = models.ForeignKey(Lista, on_delete=models.CASCADE, related_name='cartoes')
    ordem = models.IntegerField(default=0)
    
    responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='cartoes_responsaveis')
    criado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cartoes_criados')
    
    data_limite = models.DateField(null=True, blank=True)
    prioridade = models.CharField(max_length=20, choices=PRIORIDADE_CHOICES, default='media')
    tags = models.CharField(max_length=200, blank=True) # Separadas por vírgula
    
    archived = models.BooleanField(default=False)
    
    membros = models.ManyToManyField(User, related_name='cartoes_membro', blank=True)
    etiquetas = models.ManyToManyField(QuadroEtiqueta, related_name='cartoes', blank=True)
    
    # Nexus Features
    cover_color = models.CharField(max_length=20, blank=True)
    checklists = models.JSONField(default=list, blank=True)
    
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='cartoes_quadro')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['ordem']
        verbose_name = 'Cartão'
        verbose_name_plural = 'Cartões'
        
    def __str__(self):
        return self.titulo


class CartaoComentario(models.Model):
    """Comentários nos cartões"""
    cartao = models.ForeignKey(Cartao, on_delete=models.CASCADE, related_name='comentarios')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comentarios_cartao')
    texto = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']

class CartaoAnexo(models.Model):
    """Anexos nos cartões"""
    cartao = models.ForeignKey(Cartao, on_delete=models.CASCADE, related_name='anexos')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='anexos_cartao')
    arquivo = models.FileField(upload_to='quadro_anexos/%Y/%m/')
    nome_original = models.CharField(max_length=255)
    tipo_arquivo = models.CharField(max_length=100, blank=True)
    tamanho = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']


# ========================================
# MODELOS PARA TAREFAS E ROTINAS
# ========================================

class Task(models.Model):
    """Tarefas avulsas criadas por gestores"""
    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('concluida', 'Concluída'),
        ('atrasada', 'Atrasada'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    due_date = models.DateTimeField(null=True, blank=True)
    priority = models.CharField(max_length=20, choices=PRIORIDADE_CHOICES, default='media')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    notified = models.BooleanField(default=False)
    warning_sent = models.BooleanField(default=False)
    
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.assigned_to.username})"
    
    class Meta:
        ordering = ['due_date', '-priority']


class Routine(models.Model):
    """Definição de rotinas (atribuições) recorrentes"""
    FREQUENCY_CHOICES = [
        ('diaria', 'Diária'),
        ('semanal', 'Semanal'),
        ('mensal', 'Mensal'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='routines')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_routines')
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='diaria')
    active = models.BooleanField(default=True)
    notified = models.BooleanField(default=False)
    time_limit = models.TimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rotina: {self.title} - {self.assigned_to.username}"


class RoutineLog(models.Model):
    """Registro de cumprimento de rotina"""
    routine = models.ForeignKey(Routine, on_delete=models.CASCADE, related_name='logs')
    date = models.DateField()
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    warning_sent = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['routine', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"Log {self.routine.title} - {self.date}"


class RefundRequest(models.Model):
    """Solicitações de estorno entre NRS Suporte e CS Clientes"""
    STATUS_CHOICES = [
        ('aberta', 'Aberta'),
        ('em_analise', 'Em Análise'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
    ]
    PURCHASE_LOCATION_CHOICES = [
        ('loja_fisica', 'Loja Física'),
        ('site', 'Site'),
    ]
    REFUND_TYPE_CHOICES = [
        ('pix', 'PIX'),
        ('cartao_credito', 'Cartão de Crédito'),
        ('cartao_debito', 'Cartão de Débito'),
        ('checkout_web', 'Checkout Web (Site)'),
        ('saldo_lavanderia', 'Estorno para Saldo da Lavanderia'),
    ]
    
    # Quem solicitou
    analyst = models.ForeignKey(User, on_delete=models.CASCADE, related_name='refund_requests_created')
    store_code = models.CharField(max_length=20)
    
    # Dados do cliente
    customer_name = models.CharField(max_length=200)
    customer_cpf = models.CharField(max_length=14)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    
    # Detalhes da solicitação
    incident_date = models.DateField()
    purchase_location = models.CharField(max_length=20, choices=PURCHASE_LOCATION_CHOICES)
    reason = models.TextField()
    checked_cameras = models.BooleanField(default=False)
    refund_value = models.DecimalField(max_digits=10, decimal_places=2)
    refund_type = models.CharField(max_length=30, choices=REFUND_TYPE_CHOICES)
    pix_key = models.CharField(max_length=100, blank=True)
    summary = models.TextField()
    
    # Status e rastreamento
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberta')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Rastreamento de visualização pelo CS Clientes
    viewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='viewed_refunds')
    viewed_at = models.DateTimeField(null=True, blank=True)
    
    # Cancelamento (solicitado pelo gestor NRS)
    cancellation_requested = models.BooleanField(default=False)
    cancellation_requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='cancelled_refunds')
    cancellation_requested_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True, null=True)

    
    # Controle de notificações
    notified_cs = models.BooleanField(default=False)
    notified_nrs_completion = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Estorno #{self.id} - {self.customer_name} ({self.status})"



class RefundRequestAttachment(models.Model):
    """Anexos das solicitações de estorno"""
    refund_request = models.ForeignKey(RefundRequest, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='refund_attachments/')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Anexo {self.id} - Solicitação #{self.refund_request.id}"


# ========================================
# MODELOS PARA VERIFICAÇÃO DE LOJAS (AUDITORIA)
# ========================================

class StoreAudit(models.Model):
    """Representa uma sessão de verificação/auditoria de uma loja"""
    analyst = models.ForeignKey(User, on_delete=models.CASCADE, related_name='store_audits')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='audits')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Auditoria de Loja"
        verbose_name_plural = "Auditorias de Lojas"

    def __str__(self):
        return f"Auditoria {self.store.code} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"

    def has_irregularities(self):
        return self.items.filter(is_compliant=False).exists()


class StoreAuditItem(models.Model):
    """Itens específicos verificados durante uma auditoria"""
    ITEM_CHOICES = [
        ('cameras', 'Câmeras'),
        ('estofados', 'Estofados'),
        ('cestos_medidas', 'Cestos de medidas'),
        ('layout', 'Layout'),
        ('tv', 'TV'),
        ('totem', 'Totem'),
        ('limpeza', 'Limpeza da loja'),
        ('marketing', 'Marketing'),
    ]
    
    audit = models.ForeignKey(StoreAudit, on_delete=models.CASCADE, related_name='items')
    issue = models.ForeignKey('StoreAuditIssue', on_delete=models.SET_NULL, null=True, blank=True, related_name='items')
    item_name = models.CharField(max_length=50, choices=ITEM_CHOICES)
    is_compliant = models.BooleanField(default=True)
    photo = models.ImageField(upload_to='audit_photos/', null=True, blank=True)
    description = models.TextField(blank=True, help_text="Observações sobre a irregularidade")
    
    def __str__(self):
        status = "OK" if self.is_compliant else "IRREGULAR"
        return f"{self.get_item_name_display()} - {status}"


class StoreAuditIssue(models.Model):
    """Solicitação de resolução para itens irregulares de uma loja"""
    STATUS_CHOICES = [
        ('aberta', 'Aberta'),
        ('resolvida', 'Resolvida'),
    ]
    
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='audit_issues', null=True, blank=True)
    gestor_notes = models.TextField(blank=True, verbose_name="Notas do Gestor")
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_audit_issues')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberta')
    notified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Pendência de Auditoria"
        verbose_name_plural = "Pendências de Auditoria"

    def __str__(self):
        return f"Pendência: {self.store.code} ({self.get_status_display()})"


class StoreViewerSession(models.Model):
    """Tracks which analysts are currently viewing/auditing a store"""
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='viewer_sessions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='store_viewer_sessions')
    last_heartbeat = models.DateTimeField(auto_now=True)
    is_auditing = models.BooleanField(default=False, help_text="True if user is actively auditing, not just viewing")
    
    class Meta:
        unique_together = ['store', 'user']
        verbose_name = "Sessão de Visualização de Loja"
        verbose_name_plural = "Sessões de Visualização de Lojas"
    
    def __str__(self):
        action = "auditando" if self.is_auditing else "visualizando"
        return f"{self.user.get_full_name() or self.user.username} {action} {self.store.code}"
    
    @classmethod
    def get_active_viewers(cls, store, exclude_user=None, timeout_seconds=15):
        """Get users who have sent a heartbeat within the timeout period"""
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff = timezone.now() - timedelta(seconds=timeout_seconds)
        viewers = cls.objects.filter(store=store, last_heartbeat__gte=cutoff)
        if exclude_user:
            viewers = viewers.exclude(user=exclude_user)
        return viewers


# ========================================
# MODELOS PARA CHAT INTERNO
# ========================================

class Conversation(models.Model):
    """Conversa entre dois usuários"""
    participants = models.ManyToManyField(User, related_name='chat_conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Conversa'
        verbose_name_plural = 'Conversas'
    
    def get_other_participant(self, user):
        """Retorna o outro participante da conversa"""
        return self.participants.exclude(id=user.id).first()
    
    def get_last_message(self):
        """Retorna a última mensagem da conversa"""
        return self.messages.order_by('-created_at').first()
    
    def get_unread_count(self, user):
        """Conta mensagens não lidas para um usuário"""
        return self.messages.filter(is_read=False).exclude(sender=user).count()
    
    def __str__(self):
        participants_names = ", ".join([p.get_full_name() or p.username for p in self.participants.all()[:2]])
        return f"Conversa: {participants_names}"


class Message(models.Model):
    """Mensagem em uma conversa"""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages_sent')
    content = models.TextField()
    attachment = models.FileField(upload_to='chat_attachments/', null=True, blank=True)
    file_name = models.CharField(max_length=255, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['sender', 'is_read']),
        ]
        verbose_name = 'Mensagem'
        verbose_name_plural = 'Mensagens'
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}..."


class UserOnlineStatus(models.Model):
    """Status online do usuário para o chat"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='chat_online_status')
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Status Online'
        verbose_name_plural = 'Status Online'
    
    def __str__(self):
        status = "Online" if self.is_online else "Offline"
        return f"{self.user.username}: {status}"


# ============================================
# KANBAN BOARD MODELS
# ============================================

class KanbanBoard(models.Model):
    """Quadro Kanban (equivalente a um Board do Trello)"""
    VISIBILITY_CHOICES = [
        ('private', 'Privado'),
        ('team', 'Equipe'),
        ('public', 'Público'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    background_color = models.CharField(max_length=7, default='#0079bf')
    background_image = models.URLField(blank=True)
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='private')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_boards')
    is_archived = models.BooleanField(default=False)
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Quadro Kanban'
        verbose_name_plural = 'Quadros Kanban'
    
    def __str__(self):
        return self.name


class BoardMembership(models.Model):
    """Membros de um quadro com permissões"""
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('member', 'Membro'),
        ('viewer', 'Visualizador'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='board_memberships')
    board = models.ForeignKey(KanbanBoard, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'board']
        verbose_name = 'Membro do Quadro'
        verbose_name_plural = 'Membros do Quadro'
    
    def __str__(self):
        return f"{self.user.username} - {self.board.name} ({self.role})"


class KanbanList(models.Model):
    """Lista/Coluna dentro de um quadro"""
    board = models.ForeignKey(KanbanBoard, on_delete=models.CASCADE, related_name='lists')
    name = models.CharField(max_length=200)
    position = models.PositiveIntegerField(default=0)
    card_limit = models.PositiveIntegerField(null=True, blank=True)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['position']
        verbose_name = 'Lista Kanban'
        verbose_name_plural = 'Listas Kanban'
    
    def __str__(self):
        return f"{self.name} ({self.board.name})"


class CardLabel(models.Model):
    """Etiquetas/Labels para cartões"""
    board = models.ForeignKey(KanbanBoard, on_delete=models.CASCADE, related_name='labels')
    name = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=7, default='#61bd4f')
    
    class Meta:
        verbose_name = 'Etiqueta'
        verbose_name_plural = 'Etiquetas'
    
    def __str__(self):
        return f"{self.name or 'Sem nome'} ({self.color})"


class KanbanCard(models.Model):
    """Cartão dentro de uma lista"""
    list = models.ForeignKey(KanbanList, on_delete=models.CASCADE, related_name='cards')
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    position = models.PositiveIntegerField(default=0)
    due_date = models.DateTimeField(null=True, blank=True)
    due_complete = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    cover_color = models.CharField(max_length=7, blank=True)
    cover_image = models.URLField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_cards')
    assigned_to = models.ManyToManyField(User, related_name='assigned_cards', blank=True)
    labels = models.ManyToManyField(CardLabel, related_name='cards', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['position']
        verbose_name = 'Cartão Kanban'
        verbose_name_plural = 'Cartões Kanban'
    
    def __str__(self):
        return self.title
    
    @property
    def checklist_progress(self):
        """Retorna progresso dos checklists (completed, total)"""
        items = ChecklistItem.objects.filter(checklist__card=self)
        total = items.count()
        completed = items.filter(is_completed=True).count()
        return {'completed': completed, 'total': total}


class Checklist(models.Model):
    """Checklist dentro de um cartão"""
    card = models.ForeignKey(KanbanCard, on_delete=models.CASCADE, related_name='checklists')
    title = models.CharField(max_length=200)
    position = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['position']
        verbose_name = 'Checklist'
        verbose_name_plural = 'Checklists'
    
    def __str__(self):
        return self.title


class ChecklistItem(models.Model):
    """Item de um checklist"""
    checklist = models.ForeignKey(Checklist, on_delete=models.CASCADE, related_name='items')
    text = models.CharField(max_length=500)
    is_completed = models.BooleanField(default=False)
    position = models.PositiveIntegerField(default=0)
    due_date = models.DateTimeField(null=True, blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['position']
        verbose_name = 'Item do Checklist'
        verbose_name_plural = 'Itens do Checklist'
    
    def __str__(self):
        status = "✓" if self.is_completed else "○"
        return f"{status} {self.text}"


class CardComment(models.Model):
    """Comentário em um cartão"""
    card = models.ForeignKey(KanbanCard, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='card_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Comentário'
        verbose_name_plural = 'Comentários'
    
    def __str__(self):
        return f"{self.author.username}: {self.content[:50]}..."


class CardAttachment(models.Model):
    """Anexo de um cartão"""
    card = models.ForeignKey(KanbanCard, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='kanban_attachments/')
    filename = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Anexo'
        verbose_name_plural = 'Anexos'
    
    def __str__(self):
        return self.filename


class CardActivity(models.Model):
    """Log de atividades de um cartão"""
    ACTION_CHOICES = [
        ('created', 'Criado'),
        ('moved', 'Movido'),
        ('updated', 'Atualizado'),
        ('commented', 'Comentado'),
        ('assigned', 'Atribuído'),
        ('due_date', 'Data alterada'),
        ('label_added', 'Etiqueta adicionada'),
        ('label_removed', 'Etiqueta removida'),
        ('checklist_added', 'Checklist adicionado'),
        ('checklist_completed', 'Checklist concluído'),
        ('attachment_added', 'Anexo adicionado'),
        ('archived', 'Arquivado'),
    ]
    
    card = models.ForeignKey(KanbanCard, on_delete=models.CASCADE, related_name='activities')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Atividade'
        verbose_name_plural = 'Atividades'
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.card.title}"
