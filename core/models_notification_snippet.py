
class SystemNotification(models.Model):
    CATEGORY_CHOICES = [
        ('system', 'Melhoria do Sistema'),
        ('news', 'Novidade'),
        ('event', 'Evento'),
        ('alert', 'Alerta'),
    ]
    
    title = models.CharField(max_length=200)
    message = models.TextField(verbose_name="Mensagem Resumida")
    details = models.TextField(verbose_name="Detalhes Completos (HTML)", blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='system')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Notificação do Sistema"
        verbose_name_plural = "Notificações do Sistema"

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title}"
