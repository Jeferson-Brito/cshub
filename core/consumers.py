"""
WebSocket Consumers para o sistema de chat.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    """Consumer para mensagens em uma conversa específica"""
    
    async def connect(self):
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'
        
        # Verifica se o usuário faz parte da conversa
        is_participant = await self.check_participant()
        if not is_participant:
            await self.close()
            return
        
        # Entra no grupo da conversa
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Atualiza status online
        await self.update_online_status(True)
        
        await self.accept()
        
        # Notifica outros participantes que o usuário está online
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'user_id': self.user.id,
                'username': self.user.get_full_name() or self.user.username,
                'is_online': True
            }
        )
    
    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            # Notifica que o usuário saiu
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_status',
                    'user_id': self.user.id,
                    'username': self.user.get_full_name() or self.user.username,
                    'is_online': False
                }
            )
            
            # Sai do grupo
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        
        # Atualiza status offline
        await self.update_online_status(False)
    
    async def receive(self, text_data):
        """Recebe mensagem do WebSocket"""
        data = json.loads(text_data)
        message_type = data.get('type', 'message')
        
        if message_type == 'message':
            content = data.get('content', '').strip()
            if not content:
                return
            
            # Salva a mensagem no banco
            message_data = await self.save_message(content)
            
            # Envia para todos no grupo
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message_data
                }
            )
        
        elif message_type == 'typing':
            # Notifica que o usuário está digitando
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_typing',
                    'user_id': self.user.id,
                    'username': self.user.get_full_name() or self.user.username,
                    'is_typing': data.get('is_typing', False)
                }
            )
        
        elif message_type == 'read':
            # Marca mensagens como lidas
            await self.mark_messages_read()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'messages_read',
                    'user_id': self.user.id
                }
            )
    
    async def chat_message(self, event):
        """Envia mensagem para o WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message']
        }))
    
    async def user_status(self, event):
        """Envia status do usuário para o WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'status',
            'user_id': event['user_id'],
            'username': event['username'],
            'is_online': event['is_online']
        }))
    
    async def user_typing(self, event):
        """Envia indicador de digitação"""
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user_id': event['user_id'],
                'username': event['username'],
                'is_typing': event['is_typing']
            }))
    
    async def messages_read(self, event):
        """Notifica que mensagens foram lidas"""
        await self.send(text_data=json.dumps({
            'type': 'read',
            'user_id': event['user_id']
        }))
    
    async def message_edited(self, event):
        """Notifica que uma mensagem foi editada"""
        await self.send(text_data=json.dumps({
            'type': 'edited',
            'message_id': event['message_id'],
            'content': event['content'],
            'edited_at': event['edited_at']
        }))
    
    async def message_deleted(self, event):
        """Notifica que uma mensagem foi excluída"""
        await self.send(text_data=json.dumps({
            'type': 'deleted',
            'message_id': event['message_id']
        }))
    
    @database_sync_to_async
    def check_participant(self):
        """Verifica se o usuário é participante da conversa"""
        from .models import Conversation
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            return conversation.participants.filter(id=self.user.id).exists()
        except Conversation.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, content):
        """Salva mensagem no banco de dados"""
        from .models import Conversation, Message
        
        conversation = Conversation.objects.get(id=self.conversation_id)
        message = Message.objects.create(
            conversation=conversation,
            sender=self.user,
            content=content
        )
        
        # Atualiza timestamp da conversa
        conversation.updated_at = timezone.now()
        conversation.save(update_fields=['updated_at'])
        
        return {
            'id': message.id,
            'content': message.content,
            'sender_id': message.sender.id,
            'sender_name': message.sender.get_full_name() or message.sender.username,
            'sender_photo_url': message.sender.profile_photo.url if message.sender.profile_photo else None,
            'created_at': message.created_at.strftime('%H:%M'),
            'is_read': message.is_read
        }
    
    def get_initials(self, user):
        """Retorna as iniciais do usuário"""
        name = user.get_full_name() or user.username
        parts = name.split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        return name[:2].upper()
    
    @database_sync_to_async
    def mark_messages_read(self):
        """Marca todas as mensagens não lidas como lidas"""
        from .models import Message
        Message.objects.filter(
            conversation_id=self.conversation_id,
            is_read=False
        ).exclude(sender=self.user).update(is_read=True)
    
    @database_sync_to_async
    def update_online_status(self, is_online):
        """Atualiza status online do usuário"""
        from .models import UserOnlineStatus
        status, created = UserOnlineStatus.objects.get_or_create(user=self.user)
        status.is_online = is_online
        status.save()


class ChatNotificationConsumer(AsyncWebsocketConsumer):
    """Consumer para notificações gerais do chat (badge de não lidas, etc)"""
    
    async def connect(self):
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Cada usuário tem seu próprio grupo de notificações
        self.notification_group = f'chat_notifications_{self.user.id}'
        
        await self.channel_layer.group_add(
            self.notification_group,
            self.channel_name
        )
        
        await self.accept()
        
        # Envia contagem inicial de não lidas
        unread_count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'type': 'unread_count',
            'count': unread_count
        }))
    
    async def disconnect(self, close_code):
        if hasattr(self, 'notification_group'):
            await self.channel_layer.group_discard(
                self.notification_group,
                self.channel_name
            )
    
    async def new_message_notification(self, event):
        """Notifica sobre nova mensagem"""
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'conversation_id': event['conversation_id'],
            'sender_name': event['sender_name'],
            'preview': event['preview'],
            'unread_count': event['unread_count']
        }))
    
    @database_sync_to_async
    def get_unread_count(self):
        """Conta total de mensagens não lidas"""
        from .models import Message
        return Message.objects.filter(
            conversation__participants=self.user,
            is_read=False
        ).exclude(sender=self.user).count()
