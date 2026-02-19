from django.contrib import admin
from .models import User, Complaint, Activity, AuditLog, SystemNotification


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'ativo']
    list_filter = ['role', 'ativo']
    search_fields = ['username', 'email']


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['id_ra', 'nome_cliente', 'loja_cod', 'status', 'analista', 'created_at']
    list_filter = ['status', 'origem_contato', 'loja_cod']
    search_fields = ['id_ra', 'cpf_cliente', 'nome_cliente', 'email_cliente']


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['complaint', 'usuario', 'tipo_interacao', 'created_at']
    list_filter = ['tipo_interacao']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'action', 'target_type', 'created_at']
    list_filter = ['action']
    readonly_fields = ['created_at']


@admin.register(SystemNotification)
class SystemNotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'created_at', 'is_active']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['title', 'message']


