"""
API endpoints para o sistema de chat.
"""
import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max, Count
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import User, Department, Conversation, Message, UserOnlineStatus


@login_required
@require_http_methods(["GET"])
def api_conversations_list(request):
    """Lista todas as conversas do usuário com otimização de queries"""
    user = request.user
    
    # Busca conversas com prefetch dos participantes e anotação de não lidas
    conversations = Conversation.objects.filter(
        participants=user
    ).prefetch_related(
        'participants',
        'participants__chat_online_status'
    ).annotate(
        last_message_time=Max('messages__created_at'),
    ).order_by('-last_message_time')
    
    data = []
    # Busca todas as últimas mensagens de uma vez para evitar N+1
    # Como são apenas 2 participantes, prefetching participants é suficiente
    for conv in conversations:
        # Pega o outro participante (já em memória pelo prefetch)
        other_user = None
        for p in conv.participants.all():
            if p.id != user.id:
                other_user = p
                break
        
        if not other_user:
            continue
        
        # Pega última mensagem (ainda causa uma query por conversa, mas as outras estão otimizadas)
        last_message = conv.get_last_message()
        
        # Status online (já em memória pelo prefetch)
        try:
            online_status = other_user.chat_online_status
            is_online = online_status.is_online
            last_seen = online_status.last_seen
        except UserOnlineStatus.DoesNotExist:
            is_online = False
            last_seen = None
        
        data.append({
            'id': conv.id,
            'other_user': {
                'id': other_user.id,
                'name': other_user.get_full_name() or other_user.username,
                'role': other_user.get_role_display(),
                'department': other_user.department.name if other_user.department else None,
                'initials': get_initials(other_user),
                'profile_photo_url': getattr(other_user.profile_photo, 'url', None) if other_user.profile_photo else None,
                'is_online': is_online,
                'last_seen': last_seen.strftime('%d/%m/%Y %H:%M') if last_seen else None
            },
            'last_message': {
                'content': last_message.content[:50] + '...' if last_message and len(last_message.content) > 50 else (last_message.content if last_message else ''),
                'time': last_message.created_at.strftime('%H:%M') if last_message else '',
                'is_mine': last_message.sender_id == user.id if last_message else False
            } if last_message else None,
            'unread_count': conv.get_unread_count(user)
        })
    
    return JsonResponse({'conversations': data})


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def api_conversation_start(request):
    """Inicia uma nova conversa ou retorna existente"""
    try:
        data = json.loads(request.body)
        other_user_id = data.get('user_id')
        
        if not other_user_id:
            return JsonResponse({'error': 'user_id é obrigatório'}, status=400)
        
        try:
            other_user = User.objects.get(id=other_user_id, is_active=True)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Usuário não encontrado'}, status=404)
        
        if other_user == request.user:
            return JsonResponse({'error': 'Não é possível criar conversa consigo mesmo'}, status=400)
        
        # Procura conversa existente
        existing = Conversation.objects.filter(
            participants=request.user
        ).filter(
            participants=other_user
        ).first()
        
        if existing:
            conversation = existing
            created = False
        else:
            # Cria nova conversa
            conversation = Conversation.objects.create()
            conversation.participants.add(request.user, other_user)
            created = True
        
        # Info do outro participante para atualizar o header do chat
        return JsonResponse({
            'conversation_id': conversation.id,
            'created': created,
            'other_user': {
                'id': other_user.id,
                'name': other_user.get_full_name() or other_user.username,
                'role': other_user.get_role_display(),
                'department': other_user.department.name if other_user.department else None,
                'profile_photo_url': getattr(other_user.profile_photo, 'url', None) if other_user.profile_photo else None,
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)


@login_required
@require_http_methods(["GET"])
def api_messages_list(request, conv_id):
    """Lista mensagens de uma conversa - otimizado para velocidade"""
    try:
        # Query simples primeiro para validar
        conversation = Conversation.objects.get(
            id=conv_id,
            participants=request.user
        )
        
        limit = int(request.GET.get('limit', 30))  # Reduzido para carregar mais rápido
        
        # Mensagens com sender em uma única query
        messages = Message.objects.filter(
            conversation_id=conv_id
        ).select_related('sender', 'sender__department').order_by('-created_at')[:limit]
        
        # Converte para lista e inverte
        messages_list = list(messages)
        messages_list.reverse()
        
        data = []
        for msg in messages_list:
            # Safe URL generation
            sender_photo_url = None
            if msg.sender.profile_photo:
                try:
                    sender_photo_url = msg.sender.profile_photo.url
                except Exception:
                    pass

            file_url = None
            if msg.attachment:
                try:
                    file_url = msg.attachment.url
                except Exception:
                    pass

            data.append({
                'id': msg.id,
                'content': msg.content,
                'sender_id': msg.sender_id,
                'sender_name': msg.sender.get_full_name() or msg.sender.username,
                'sender_initials': get_initials(msg.sender),
                'sender_profile_photo_url': sender_photo_url,
                'is_mine': msg.sender_id == request.user.id,
                'created_at': msg.created_at.strftime('%H:%M'),
                'created_at_full': msg.created_at.strftime('%d/%m/%Y %H:%M'),
                'file_url': file_url,
                'file_name': msg.file_name,
                'is_read': msg.is_read,
                'edited_at': msg.edited_at.strftime('%H:%M') if msg.edited_at else None,
                'is_deleted': msg.is_deleted
            })
        
        # Info do outro participante - query simples pelos participantes da conversa
        other_user = conversation.participants.exclude(id=request.user.id).select_related('department').first()
        
        is_online = False
        if other_user:
            try:
                is_online = other_user.chat_online_status.is_online
            except:
                pass
        
        # Marca como lidas em background (não bloqueia a resposta)
        Message.objects.filter(
            conversation_id=conv_id,
            is_read=False
        ).exclude(sender_id=request.user.id).update(is_read=True)
        
        return JsonResponse({
            'messages': data,
            'other_user': {
                'id': other_user.id if other_user else None,
                'name': (other_user.get_full_name() or other_user.username) if other_user else "Sistema",
                'role': other_user.get_role_display() if other_user else None,
                'department': other_user.department.name if other_user and other_user.department else None,
                'initials': get_initials(other_user) if other_user else "S",
                'profile_photo_url': getattr(other_user.profile_photo, 'url', None) if other_user and other_user.profile_photo else None,
                'is_online': is_online
            }
        })
    except Conversation.DoesNotExist:
        return JsonResponse({'error': 'Conversa não encontrada'}, status=404)
    except Exception as e:
        print(f"Erro ao listar mensagens: {str(e)}")
        return JsonResponse({'error': f'Erro ao carregar mensagens: {str(e)}'}, status=500)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def api_message_send(request, conv_id):
    """Envia uma mensagem (fallback para quando WebSocket não está disponível)"""
    try:
        conversation = Conversation.objects.get(
            id=conv_id,
            participants=request.user
        )
    except Conversation.DoesNotExist:
        return JsonResponse({'error': 'Conversa não encontrada'}, status=404)
    
    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        
        if not content:
            return JsonResponse({'error': 'Conteúdo é obrigatório'}, status=400)
        
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content
        )
        
        # Atualiza timestamp da conversa
        conversation.updated_at = timezone.now()
        conversation.save(update_fields=['updated_at'])
        
        return JsonResponse({
            'id': message.id,
            'content': message.content,
            'sender_id': message.sender.id,
            'sender_name': message.sender.get_full_name() or message.sender.username,
            'sender_initials': get_initials(message.sender),
            'sender_profile_photo_url': message.sender.profile_photo.url if message.sender.profile_photo else None,
            'created_at': message.created_at.strftime('%H:%M'),
            'is_read': message.is_read
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def api_messages_read(request, conv_id):
    """Marca todas as mensagens de uma conversa como lidas"""
    try:
        conversation = Conversation.objects.get(
            id=conv_id,
            participants=request.user
        )
    except Conversation.DoesNotExist:
        return JsonResponse({'error': 'Conversa não encontrada'}, status=404)
    
    updated = conversation.messages.filter(
        is_read=False
    ).exclude(sender=request.user).update(is_read=True)
    
    return JsonResponse({'marked_read': updated})


@login_required
@require_http_methods(["GET"])
def api_chat_users(request):
    """Lista usuários disponíveis para chat com otimização"""
    search = request.GET.get('search', '').strip()
    
    users = User.objects.filter(
        is_active=True
    ).exclude(id=request.user.id).select_related(
        'department', 
        'chat_online_status'
    )
    
    if search:
        users = users.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(username__icontains=search) |
            Q(email__icontains=search)
        )
    
    users = users[:30]  # Aumenta um pouco o limite se otimizado
    
    data = []
    for user in users:
        is_online = False
        try:
            is_online = user.chat_online_status.is_online
        except UserOnlineStatus.DoesNotExist:
            pass
        
        data.append({
            'id': user.id,
            'name': user.get_full_name() or user.username,
            'role': user.get_role_display(),
            'role_slug': user.role,
            'email': user.email,
            'initials': get_initials(user),
            'profile_photo_url': getattr(user.profile_photo, 'url', None) if user.profile_photo else None,
            'department': user.department.name if user.department else None,
            'is_online': is_online
        })
    
    return JsonResponse({'users': data})


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def api_chat_upload(request):
    """Realiza upload de arquivo e envia como mensagem"""
    conv_id = request.POST.get('conversation_id')
    content = request.POST.get('content', '').strip()
    file = request.FILES.get('file')
    
    try:
        if not conv_id:
            return JsonResponse({'error': 'conversation_id é obrigatório'}, status=400)
        
        try:
            conversation = Conversation.objects.get(
                id=conv_id,
                participants=request.user
            )
        except Conversation.DoesNotExist:
            return JsonResponse({'error': 'Conversa não encontrada'}, status=404)
            
        if not file:
            return JsonResponse({'error': 'Arquivo é obrigatório'}, status=400)
            
        # Garante que o diretório de mídia existe
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content or f"Arquivo enviado: {file.name}",
            attachment=file,
            file_name=file.name
        )
        
        conversation.updated_at = timezone.now()
        conversation.save(update_fields=['updated_at'])
        
        message_data = {
            'id': message.id,
            'content': message.content,
            'sender_id': message.sender.id,
            'sender_name': message.sender.get_full_name() or message.sender.username,
            'sender_initials': get_initials(message.sender),
            'sender_profile_photo_url': message.sender.profile_photo.url if message.sender.profile_photo else None,
            'created_at': message.created_at.strftime('%H:%M'),
            'file_url': message.attachment.url if message.attachment else None,
            'file_name': message.file_name,
            'is_read': message.is_read
        }
        
        # Notifica via WebSocket vinculando ao grupo da conversa
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_{conversation.id}',
            {
                'type': 'chat_message',
                'message': message_data
            }
        )
        
        return JsonResponse(message_data)
    except Exception as e:
        print(f"Erro no upload: {str(e)}")
        return JsonResponse({'error': f'Erro interno no servidor: {str(e)}'}, status=500)


@login_required
@require_http_methods(["GET"])
def api_unread_count(request):
    """Retorna contagem total de mensagens não lidas e mensagens recentes para notificações"""
    # Busca mensagens não lidas
    unread_messages = Message.objects.filter(
        conversation__participants=request.user,
        is_read=False
    ).exclude(sender=request.user).select_related('sender').order_by('-created_at')
    
    count = unread_messages.count()
    
    # Verifica se deve retornar detalhes das mensagens (para notificações)
    include_messages = request.GET.get('include_messages', 'false').lower() == 'true'
    last_check = request.GET.get('last_check')
    
    response_data = {'count': count}
    
    if include_messages and count > 0:
        # Filtra por mensagens após o último check (se fornecido)
        if last_check:
            try:
                from datetime import datetime
                last_check_dt = datetime.fromisoformat(last_check.replace('Z', '+00:00'))
                unread_messages = unread_messages.filter(created_at__gt=last_check_dt)
            except (ValueError, TypeError):
                pass
        
        # Retorna até 5 mensagens mais recentes para notificação
        recent_messages = []
        for msg in unread_messages[:5]:
            sender_name = msg.sender.get_full_name() or msg.sender.username
            # Preview da mensagem (primeiros 80 caracteres)
            preview = msg.content[:80] + '...' if len(msg.content) > 80 else msg.content
            recent_messages.append({
                'id': msg.id,
                'sender_name': sender_name,
                'preview': preview,
                'created_at': msg.created_at.isoformat()
            })
        
        response_data['messages'] = recent_messages
        response_data['has_new'] = len(recent_messages) > 0
    
    return JsonResponse(response_data)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def api_heartbeat(request):
    """Atualiza status online do usuário"""
    status, created = UserOnlineStatus.objects.get_or_create(user=request.user)
    status.is_online = True
    status.save()
    
    return JsonResponse({'status': 'ok'})


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def api_message_edit(request, msg_id):
    """Edita uma mensagem existente"""
    try:
        message = Message.objects.get(id=msg_id, sender=request.user)
    except Message.DoesNotExist:
        return JsonResponse({'error': 'Mensagem não encontrada'}, status=404)
    
    try:
        data = json.loads(request.body)
        new_content = data.get('content', '').strip()
        
        if not new_content:
            return JsonResponse({'error': 'Conteúdo é obrigatório'}, status=400)
        
        message.content = new_content
        message.edited_at = timezone.now()
        message.save(update_fields=['content', 'edited_at'])
        
        # Notify via WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_{message.conversation_id}',
            {
                'type': 'message_edited',
                'message_id': message.id,
                'content': message.content,
                'edited_at': message.edited_at.strftime('%H:%M')
            }
        )
        
        return JsonResponse({
            'id': message.id,
            'content': message.content,
            'edited_at': message.edited_at.strftime('%H:%M')
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def api_message_delete(request, msg_id):
    """Exclui logicamente uma mensagem"""
    try:
        message = Message.objects.get(id=msg_id, sender=request.user)
    except Message.DoesNotExist:
        return JsonResponse({'error': 'Mensagem não encontrada'}, status=404)
    
    message.is_deleted = True
    message.content = "Mensagem excluída"
    message.save(update_fields=['is_deleted', 'content'])
    
    # Notify via WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'chat_{message.conversation_id}',
        {
            'type': 'message_deleted',
            'message_id': message.id
        }
    )
    
    return JsonResponse({'deleted': True, 'id': message.id})


def get_initials(user):
    """Retorna as iniciais do usuário"""
    name = user.get_full_name() or user.username
    parts = name.split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return name[:2].upper()
