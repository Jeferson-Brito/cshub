/**
 * Redesigned Floating Chat (Bitrix Style)
 * - Side menu with recent contacts
 * - Multiple independent chat popups
 */

class SideChatMenu {
    constructor() {
        this.menu = document.getElementById('sideChatMenu');
        this.list = document.getElementById('sideChatList');
        this.newBtn = document.getElementById('sideChatNew');
        this.popupsContainer = document.getElementById('chatPopupsContainer');
        
        this.activePopups = new Map(); // conversationId -> ChatPopup instance
        this.notificationSocket = null;
        
        this.init();
    }

    init() {
        if (!this.menu) return;
        
        this.loadRecentChats();
        this.connectNotificationSocket();
        this.setupEventListeners();
    }

    setupEventListeners() {
        this.newBtn.addEventListener('click', () => {
            // Re-use current implementation for starting a new chat if possible
            // For now, let's keep it simple and load all users in a specific way if needed
            window.location.href = '/chat/'; // Fallback to full chat page for now or implement search
        });
    }

    async loadRecentChats() {
        try {
            const res = await fetch('/api/chat/conversations/');
            const data = await res.json();
            this.renderRecentChats(data.conversations);
        } catch (e) {
            console.error('Error loading side chat:', e);
        }
    }

    renderRecentChats(conversations) {
        if (!conversations.length) {
            this.list.innerHTML = '<div class="text-muted small px-2">Vazio</div>';
            return;
        }

        this.list.innerHTML = conversations.map(c => {
            const initials = c.other_user.initials || '??';
            return `
                <div class="side-chat-item" data-id="${c.id}" data-name="${c.other_user.name}" title="${c.other_user.name}">
                    <div class="side-chat-avatar">${initials}</div>
                    ${c.unread_count > 0 ? `<span class="side-chat-badge">${c.unread_count > 9 ? '9+' : c.unread_count}</span>` : ''}
                </div>
            `;
        }).join('');

        this.list.querySelectorAll('.side-chat-item').forEach(item => {
            item.addEventListener('click', () => {
                this.openPopup(item.dataset.id, item.dataset.name);
            });
        });
    }

    openPopup(conversationId, name) {
        if (this.activePopups.has(conversationId)) {
            const popup = this.activePopups.get(conversationId);
            popup.maximize();
            popup.focus();
            return;
        }

        const popup = new ChatPopup(conversationId, name, this);
        this.activePopups.set(conversationId, popup);
    }

    connectNotificationSocket() {
        const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
        this.notificationSocket = new WebSocket(`${wsScheme}://${window.location.host}/ws/chat/`);

        this.notificationSocket.onmessage = (e) => {
            const data = JSON.parse(e.data);
            if (data.type === 'new_message' || data.type === 'unread_count') {
                this.loadRecentChats();
                
                // If message is for an open popup, it will be handled by the popup's own socket
            }
        };

        this.notificationSocket.onclose = () => {
            setTimeout(() => this.connectNotificationSocket(), 5000);
        };
    }

    removePopup(conversationId) {
        this.activePopups.delete(conversationId);
    }
}

class ChatPopup {
    constructor(conversationId, name, parentManager) {
        this.conversationId = conversationId;
        this.name = name;
        this.manager = parentManager;
        this.socket = null;
        this.element = null;
        
        this.render();
        this.init();
    }

    render() {
        const initials = this.name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
        const html = `
            <div class="chat-popup" id="popup-${this.conversationId}">
                <div class="chat-popup-header">
                    <div class="chat-popup-info">
                        <div class="chat-popup-avatar">${initials}</div>
                        <span class="chat-popup-name">${this.name}</span>
                    </div>
                    <div class="chat-popup-actions">
                        <button class="chat-popup-btn minimize-btn" title="Minimizar">
                            <i class="bi bi-dash-lg"></i>
                        </button>
                        <button class="chat-popup-btn close-btn" title="Fechar">
                            <i class="bi bi-x-lg"></i>
                        </button>
                    </div>
                </div>
                <div class="chat-popup-body">
                    <div class="chat-popup-messages" id="messages-${this.conversationId}">
                        <div class="text-center py-4"><small class="text-muted">Carregando...</small></div>
                    </div>
                    <div class="chat-popup-input-area">
                        <input type="text" class="chat-popup-input" placeholder="Mensagem..." id="input-${this.conversationId}">
                        <button class="chat-popup-send" id="send-${this.conversationId}">
                            <i class="bi bi-send-fill"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
        this.manager.popupsContainer.insertAdjacentHTML('afterbegin', html);
        this.element = document.getElementById(`popup-${this.conversationId}`);
        this.messagesList = document.getElementById(`messages-${this.conversationId}`);
        this.input = document.getElementById(`input-${this.conversationId}`);
        this.sendBtn = document.getElementById(`send-${this.conversationId}`);
    }

    init() {
        this.loadMessages();
        this.connectSocket();
        this.setupEventListeners();
    }

    setupEventListeners() {
        this.element.querySelector('.minimize-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleMinimize();
        });

        this.element.querySelector('.close-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            this.close();
        });

        this.element.querySelector('.chat-popup-header').addEventListener('click', () => {
            if (this.element.classList.contains('minimized')) {
                this.maximize();
            }
        });

        this.input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        this.sendBtn.addEventListener('click', () => this.sendMessage());
    }

    async loadMessages() {
        try {
            const res = await fetch(`/api/chat/conversations/${this.conversationId}/messages/`);
            const data = await res.json();
            this.renderMessages(data.messages);
        } catch (e) {
            this.messagesList.innerHTML = '<div class="text-danger small p-2">Erro ao carregar</div>';
        }
    }

    renderMessages(messages) {
        if (!messages.length) {
            this.messagesList.innerHTML = '<div class="text-muted small text-center py-4">Diga olá! 👋</div>';
            return;
        }

        this.messagesList.innerHTML = messages.map(m => this.getMessageHtml(m)).join('');
        this.scrollToBottom();
    }

    getMessageHtml(m) {
        const isMine = m.is_mine || m.sender_id == currentUserId;
        return `
            <div class="message ${isMine ? 'message-sent' : 'message-received'}" 
                 style="align-self: ${isMine ? 'flex-end' : 'flex-start'}; 
                        background: ${isMine ? '#dcf8c6' : 'white'};
                        max-width: 85%; padding: 6px 10px; border-radius: 8px; font-size: 0.85rem;
                        box-shadow: 0 1px 1px rgba(0,0,0,0.1); margin-bottom: 2px;">
                <div class="message-content">${this.escape(m.content)}</div>
                <div class="message-time" style="font-size: 0.65rem; color: #94a3b8; text-align: right; margin-top: 2px;">
                    ${m.created_at || ''}
                </div>
            </div>
        `;
    }

    sendMessage() {
        const content = this.input.value.trim();
        if (!content) return;

        // Optimistic UI
        const tempMsg = {
            id: Date.now(),
            content: content,
            is_mine: true,
            created_at: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
        };

        const empty = this.messagesList.querySelector('.text-muted');
        if (empty) this.messagesList.innerHTML = '';

        this.messagesList.insertAdjacentHTML('beforeend', this.getMessageHtml(tempMsg));
        this.scrollToBottom();
        this.input.value = '';

        fetch(`/api/chat/conversations/${this.conversationId}/send/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCookie('csrftoken')
            },
            body: JSON.stringify({ content: content })
        }).catch(e => console.error('Error sending message:', e));
    }

    connectSocket() {
        const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
        this.socket = new WebSocket(`${wsScheme}://${window.location.host}/ws/chat/${this.conversationId}/`);

        this.socket.onopen = () => {
            this.socket.send(JSON.stringify({ type: 'read' }));
        };

        this.socket.onmessage = (e) => {
            const data = JSON.parse(e.data);
            if (data.type === 'message') {
                if (data.message.sender_id != currentUserId) {
                    const empty = this.messagesList.querySelector('.text-muted');
                    if (empty) this.messagesList.innerHTML = '';
                    this.messagesList.insertAdjacentHTML('beforeend', this.getMessageHtml(data.message));
                    this.scrollToBottom();
                    this.socket.send(JSON.stringify({ type: 'read' }));
                }
            }
        };

        this.socket.onclose = () => {
            // Socket handle closing if needed
        };
    }

    toggleMinimize() {
        this.element.classList.toggle('minimized');
    }

    maximize() {
        this.element.classList.remove('minimized');
    }

    focus() {
        this.input.focus();
    }

    close() {
        if (this.socket) this.socket.close();
        this.element.remove();
        this.manager.removePopup(this.conversationId);
    }

    scrollToBottom() {
        this.messagesList.scrollTop = this.messagesList.scrollHeight;
    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    escape(html) {
        const div = document.createElement('div');
        div.textContent = html;
        return div.innerHTML;
    }
}

// Global initialization
let nexusChat;
document.addEventListener('DOMContentLoaded', () => {
    nexusChat = new SideChatMenu();
});
