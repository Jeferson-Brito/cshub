"""
APIs para o Sistema de Verificação de Lojas - Notificações e Timers
"""

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
import json

from .models import (
    Store, StoreAudit, StoreAuditIssue, StoreAuditItem,
    AnalystAssignment, User
)


@login_required
@require_http_methods(["POST"])
def api_notify_franchisee(request, issue_id):
    """
    API para notificar franqueado sobre irregularidade
    Abre o modal de escolha de canal (WhatsApp ou Ticket)
    """
    if request.user.role not in ['gestor', 'administrador']:
        return JsonResponse({'success': False, 'error': 'Permissão negada'}, status=403)
    
    issue = get_object_or_404(StoreAuditIssue, id=issue_id)
    
    # Retorna dados da irregularidade para o frontend
    irregular_items = []
    for item in issue.items.all():
        irregular_items.append({
            'name': item.get_item_name_display(),
            'description': item.description
        })
    
    return JsonResponse({
        'success': True,
        'issue': {
            'id': issue.id,
            'store_code': issue.store.code if issue.store else 'Desconhecida',
            'created_at': issue.created_at.strftime('%d/%m/%Y %H:%M'),
            'irregular_items': irregular_items
        }
    })


@login_required
@require_http_methods(["POST"])
def api_start_whatsapp_notification(request, issue_id):
    """
    Inicia o fluxo de notificação via WhatsApp com timer
    """
    if request.user.role not in ['gestor', 'administrador']:
        return JsonResponse({'success': False, 'error': 'Permissão negada'}, status=403)
    
    issue = get_object_or_404(StoreAuditIssue, id=issue_id)
    
    try:
        data = json.loads(request.body)
        deadline_hours = int(data.get('deadline_hours', 24))
        
        # Validar prazo (24-48 horas)
        if deadline_hours < 24 or deadline_hours > 48:
            return JsonResponse({
                'success': False,
                'error': 'Prazo deve ser entre 24 e 48 horas'
            }, status=400)
        
        # Atualizar issue
        issue.status = 'notificado_whatsapp'
        issue.notification_channel = 'whatsapp'
        issue.deadline_hours = deadline_hours
        issue.timer_started_at = timezone.now()
        issue.deadline_datetime = timezone.now() + timedelta(hours=deadline_hours)
        issue.notified = True
        
        # Adicionar ao histórico
        history_entry = {
            'timestamp': timezone.now().isoformat(),
            'user': request.user.get_full_name() or request.user.username,
            'action': 'whatsapp_notification_started',
            'deadline_hours': deadline_hours,
            'deadline_datetime': issue.deadline_datetime.isoformat()
        }
        
        if not isinstance(issue.resolution_history, list):
            issue.resolution_history = []
        issue.resolution_history.append(history_entry)
        
        issue.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Notificação via WhatsApp iniciada. Prazo: {deadline_hours}h',
            'issue': {
                'id': issue.id,
                'status': issue.status,
                'deadline_datetime': issue.deadline_datetime.isoformat(),
                'time_remaining_seconds': issue.get_time_remaining()
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def api_create_ticket_from_issue(request, issue_id):
    """
    Cria um ticket a partir de uma irregularidade
    """
    if request.user.role not in ['gestor', 'administrador']:
        return JsonResponse({'success': False, 'error': 'Permissão negada'}, status=403)
    
    issue = get_object_or_404(StoreAuditIssue, id=issue_id)
    
    try:
        data = json.loads(request.body)
        
        # Atualizar issue para status ticket
        issue.status = 'notificado_ticket'
        issue.notification_channel = 'ticket'
        issue.ticket_priority = data.get('priority', 'media')
        issue.ticket_notes = data.get('notes', '')
        issue.deadline_hours = int(data.get('deadline_hours', 72))
        issue.deadline_datetime = timezone.now() + timedelta(hours=issue.deadline_hours)
        issue.notified = True
        
        # Gerar ID do ticket (pode ser integrado com sistema externo)
        issue.ticket_id = f"TK-{issue.id}-{timezone.now().strftime('%Y%m%d')}"
        
        # Se há responsável, vincular
        responsible_id = data.get('responsible_id')
        if responsible_id:
            try:
                responsible = User.objects.get(id=responsible_id)
                issue.ticket_responsible = responsible
            except User.DoesNotExist:
                pass
        
        # Adicionar ao histórico
        history_entry = {
            'timestamp': timezone.now().isoformat(),
            'user': request.user.get_full_name() or request.user.username,
            'action': 'ticket_created',
            'ticket_id': issue.ticket_id,
            'priority': issue.ticket_priority,
            'deadline_hours': issue.deadline_hours
        }
        
        if not isinstance(issue.resolution_history, list):
            issue.resolution_history = []
        issue.resolution_history.append(history_entry)
        
        issue.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Ticket {issue.ticket_id} criado com sucesso',
            'ticket': {
                'id': issue.ticket_id,
                'priority': issue.ticket_priority,
                'deadline_datetime': issue.deadline_datetime.isoformat()
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def api_mark_issue_resolved(request, issue_id):
    """
    Marca uma irregularidade como resolvida
    """
    if request.user.role not in ['gestor', 'administrador']:
        return JsonResponse({'success': False, 'error': 'Permissão negada'}, status=403)
    
    issue = get_object_or_404(StoreAuditIssue, id=issue_id)
    
    try:
        data = json.loads(request.body)
        notes = data.get('notes', '')
        
        issue.status = 'resolvida'
        issue.resolved_at = timezone.now()
        issue.resolved_by = request.user
        issue.gestor_notes = notes
        
        # Se tinha timer, marca quando terminou
        if issue.timer_started_at and not issue.timer_ended_at:
            issue.timer_ended_at = timezone.now()
        
        # Adicionar ao histórico
        history_entry = {
            'timestamp': timezone.now().isoformat(),
            'user': request.user.get_full_name() or request.user.username,
            'action': 'marked_resolved',
            'notes': notes
        }
        
        if not isinstance(issue.resolution_history, list):
            issue.resolution_history = []
        issue.resolution_history.append(history_entry)
        
        issue.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Irregularidade marcada como resolvida'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def api_get_timer_status(request, issue_id):
    """
    Retorna o status atual do timer de uma irregularidade
    """
    issue = get_object_or_404(StoreAuditIssue, id=issue_id)
    
    time_remaining = issue.get_time_remaining()
    progress_percentage = issue.get_progress_percentage()
    
    # Determina cor do timer
    if progress_percentage < 50:
        timer_color = 'green'
    elif progress_percentage < 75:
        timer_color = 'yellow'
    else:
        timer_color = 'red'
    
    return JsonResponse({
        'success': True,
        'issue_id': issue.id,
        'status': issue.status,
        'time_remaining_seconds': time_remaining,
        'progress_percentage': progress_percentage,
        'timer_color': timer_color,
        'deadline_datetime': issue.deadline_datetime.isoformat() if issue.deadline_datetime else None,
        'is_overdue': issue.is_deadline_passed()
    })


@login_required
@require_http_methods(["POST"])
def api_escalate_to_ticket(request, issue_id):
    """
    Escalona automaticamente uma irregularidade WhatsApp para Ticket
    (Quando o prazo vence e não foi resolvido)
    """
    if request.user.role not in ['gestor', 'administrador']:
        return JsonResponse({'success': False, 'error': 'Permissão negada'}, status=403)
    
    issue = get_object_or_404(StoreAuditIssue, id=issue_id)
    
    try:
        data = json.loads(request.body)
        auto_escalate = data.get('auto_escalate', False)
        
        # Marca que a pergunta de escalonamento foi exibida
        issue.escalation_question_shown = True
        
        if auto_escalate:
            # Muda para ticket automaticamente
            issue.status = 'notificado_ticket'
            issue.auto_escalated = True
            issue.ticket_priority = 'alta'  # Escalonamento automático = prioridade alta
            issue.ticket_id = f"TK-ESC-{issue.id}-{timezone.now().strftime('%Y%m%d')}"
            issue.deadline_hours = 72  # 3 dias para ticket escalonado
            issue.deadline_datetime = timezone.now() + timedelta(hours=72)
            issue.notification_channel = 'ticket'
            
            # Timer do WhatsApp encerrou
            if issue.timer_started_at and not issue.timer_ended_at:
                issue.timer_ended_at = timezone.now()
            
            # Adicionar ao histórico
            history_entry = {
                'timestamp': timezone.now().isoformat(),
                'user': request.user.get_full_name() or request.user.username,
                'action': 'auto_escalated_to_ticket',
                'ticket_id': issue.ticket_id,
                'reason': 'whatsapp_deadline_expired'
            }
            
            if not isinstance(issue.resolution_history, list):
                issue.resolution_history = []
            issue.resolution_history.append(history_entry)
            
            issue.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Irregularidade escalonada para Ticket {issue.ticket_id}',
                'escalated': True,
                'ticket_id': issue.ticket_id
            })
        else:
            # Usuário disse que foi resolvido, não escalona
            issue.status = 'resolvida'
            issue.resolved_at = timezone.now()
            issue.resolved_by = request.user
            
            if issue.timer_started_at and not issue.timer_ended_at:
                issue.timer_ended_at = timezone.now()
            
            history_entry = {
                'timestamp': timezone.now().isoformat(),
                'user': request.user.get_full_name() or request.user.username,
                'action': 'resolved_after_deadline',
                'resolved_via': 'whatsapp'
            }
            
            if not isinstance(issue.resolution_history, list):
                issue.resolution_history = []
            issue.resolution_history.append(history_entry)
            
            issue.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Irregularidade marcada como resolvida',
                'escalated': False
            })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ==================================================
# APIs para Gest�o de Analistas
# ==================================================

@login_required
@require_http_methods(["GET"])
def api_get_analyst_assignments(request):
    """
    Retorna as lojas atribuídas a um analista específico
    """
    analyst_id = request.GET.get('analyst_id')
    
    if not analyst_id:
        # Se não especificado, retorna do próprio usuário
        analyst_id = request.user.id
    
    # Apenas gestores podem ver atribuições de outros analistas
    if int(analyst_id) != request.user.id and request.user.role not in ['gestor', 'administrador']:
        return JsonResponse({'success': False, 'error': 'Permissão negada'}, status=403)
    
    assignments = AnalystAssignment.objects.filter(
        analyst_id=analyst_id,
        active=True
    ).select_related('store')
    
    result = []
    for assignment in assignments:
        progress = assignment.get_weekly_progress()
        result.append({
            'store_id': assignment.store.id,
            'store_code': assignment.store.code,
            'store_city': assignment.store.city,
            'weekly_target': assignment.weekly_target,
            'progress': progress
        })
    
    return JsonResponse({'success': True, 'assignments': result})


@login_required
@require_http_methods(["GET"])
def api_get_all_assignments(request):
    """
    Retorna TODAS as atribuições ativas (apenas gestor/admin)
    """
    if request.user.role not in ['gestor', 'administrador']:
        return JsonResponse({'success': False, 'error': 'Permissão negada'}, status=403)
    
    assignments = AnalystAssignment.objects.filter(active=True).select_related('analyst', 'store').order_by('analyst__first_name', 'store__code')
    
    result = []
    for assignment in assignments:
        progress = assignment.get_weekly_progress()
        result.append({
            'id': assignment.id,
            'analyst_name': assignment.analyst.get_full_name() or assignment.analyst.username,
            'store_code': assignment.store.code,
            'store_city': assignment.store.city,
            'weekly_target': assignment.weekly_target,
            'progress': progress
        })
    
    return JsonResponse({'success': True, 'assignments': result})


@login_required
@require_http_methods(["POST"])
def api_assign_store_to_analyst(request):
    """
    Atribui uma loja a um analista (apenas gestor/admin)
    """
    if request.user.role not in ['gestor', 'administrador']:
        return JsonResponse({'success': False, 'error': 'Permissão negada'}, status=403)
    
    try:
        data = json.loads(request.body)
        analyst_id = data.get('analyst_id')
        store_id = data.get('store_id')
        weekly_target = data.get('weekly_target', 1)
        
        analyst = get_object_or_404(User, id=analyst_id)
        store = get_object_or_404(Store, id=store_id)
        
        assignment, created = AnalystAssignment.objects.get_or_create(
            analyst=analyst,
            store=store,
            defaults={'weekly_target': weekly_target, 'active': True}
        )
        
        if not created:
            assignment.weekly_target = weekly_target
            assignment.active = True
            assignment.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Loja {store.code} atribuída a {analyst.get_full_name() or analyst.username}',
            'created': created
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def api_get_available_stores(request):
    """
    Retorna lojas disponíveis (não atribuídas a nenhum analista)
    E opcionalmente seleciona N lojas aleatórias
    """
    if request.user.role not in ['gestor', 'administrador']:
        return JsonResponse({'success': False, 'error': 'Permissão negada'}, status=403)
    
    try:
        quantity = request.GET.get('quantity', None)
        
        # Buscar IDs de lojas já atribuídas (ativas)
        assigned_store_ids = AnalystAssignment.objects.filter(
            active=True
        ).values_list('store_id', flat=True).distinct()
        
        # Buscar lojas disponíveis (não atribuídas)
        available_stores = Store.objects.filter(
            active=True
        ).exclude(
            id__in=assigned_store_ids
        ).order_by('code')
        
        total_available = available_stores.count()
        
        # Se quantidade foi especificada, selecionar aleatoriamente
        selected_stores = []
        if quantity:
            try:
                qty = int(quantity)
                if qty > total_available:
                    return JsonResponse({
                        'success': False,
                        'error': f'Apenas {total_available} lojas disponíveis. Solicitado: {qty}'
                    }, status=400)
                
                # Seleção aleatória
                import random
                available_list = list(available_stores.values('id', 'code', 'city'))
                selected_stores = random.sample(available_list, qty)
                
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'error': 'Quantidade inválida'
                }, status=400)
        else:
            # Retornar todas as disponíveis
            selected_stores = list(available_stores.values('id', 'code', 'city'))
        
        return JsonResponse({
            'success': True,
            'total_available': total_available,
            'selected_count': len(selected_stores),
            'stores': selected_stores
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def api_bulk_assign_stores(request):
    """
    Atribui múltiplas lojas a um analista de uma vez
    """
    if request.user.role not in ['gestor', 'administrador']:
        return JsonResponse({'success': False, 'error': 'Permissão negada'}, status=403)
    
    try:
        data = json.loads(request.body)
        analyst_id = data.get('analyst_id')
        store_ids = data.get('store_ids', [])  # Lista de IDs
        weekly_target = data.get('weekly_target', 1)
        
        if not analyst_id or not store_ids:
            return JsonResponse({
                'success': False,
                'error': 'Analista e lojas são obrigatórios'
            }, status=400)
        
        analyst = get_object_or_404(User, id=analyst_id)
        
        # Verificar se alguma loja já está atribuída a outro analista
        already_assigned = AnalystAssignment.objects.filter(
            store_id__in=store_ids,
            active=True
        ).exclude(analyst=analyst).select_related('analyst', 'store')
        
        if already_assigned.exists():
            conflicts = []
            for assignment in already_assigned:
                conflicts.append({
                    'store': assignment.store.code,
                    'analyst': assignment.analyst.get_full_name() or assignment.analyst.username
                })
            
            return JsonResponse({
                'success': False,
                'error': 'Algumas lojas já estão atribuídas a outros analistas',
                'conflicts': conflicts
            }, status=400)
        
        # Criar/atualizar atribuições
        created_count = 0
        updated_count = 0
        
        for store_id in store_ids:
            try:
                store = Store.objects.get(id=store_id, active=True)
                
                assignment, created = AnalystAssignment.objects.get_or_create(
                    analyst=analyst,
                    store=store,
                    defaults={'weekly_target': weekly_target, 'active': True}
                )
                
                if created:
                    created_count += 1
                else:
                    assignment.weekly_target = weekly_target
                    assignment.active = True
                    assignment.save()
                    updated_count += 1
                    
            except Store.DoesNotExist:
                continue
        
        analyst_name = analyst.get_full_name() or analyst.username
        
        return JsonResponse({
            'success': True,
            'message': f'{created_count + updated_count} lojas atribuídas a {analyst_name}',
            'created': created_count,
            'updated': updated_count,
            'total': created_count + updated_count
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)



@login_required
@require_http_methods(["GET"])
def api_get_analyst_dashboard(request):
    """
    Retorna métricas e progresso do analista para dashboard
    """
    analyst_id = request.GET.get('analyst_id', request.user.id)
    
    # Verificar permissão
    if int(analyst_id) != request.user.id and request.user.role not in ['gestor', 'administrador']:
        return JsonResponse({'success': False, 'error': 'Permissão negada'}, status=403)
    
    analyst = get_object_or_404(User, id=analyst_id)
    
    # Buscar atribuições
    assignments = AnalystAssignment.objects.filter(
        analyst=analyst,
        active=True
    ).select_related('store')
    
    total_stores = assignments.count()
    
    # Calcular progresso semanal
    total_audited = 0
    total_target = 0
    
    for assignment in assignments:
        progress = assignment.get_weekly_progress()
        total_audited += progress['completed']
        total_target += progress['target']
    
    percentage = (total_audited / total_target * 100) if total_target > 0 else 0
    
    # Auditorias de hoje
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_audits = StoreAudit.objects.filter(
        analyst=analyst,
        created_at__gte=today_start
    ).count()
    
    # Dias restantes na semana
    today = timezone.now().date()
    days_until_sunday = (6 - today.weekday()) % 7  # Dias até domingo
    days_remaining = days_until_sunday if days_until_sunday > 0 else 0
    
    # Meta Diária (Total / 6 dias úteis)
    daily_target = max(1, round(total_stores / 6)) if total_stores > 0 else 0
    
    return JsonResponse({
        'success': True,
        'analyst': {
            'id': analyst.id,
            'name': analyst.get_full_name() or analyst.username
        },
        'metrics': {
            'total_stores': total_stores,
            'total_audited': total_audited,
            'total_target': total_target,
            'progress_percentage': round(percentage, 1),
            'pending': total_target - total_audited,
            'today_audits': today_audits,
            'daily_target': daily_target,
            'days_remaining': days_remaining
        }
    })
