/**
 * Floating Chat Widget JavaScript
 * Reuses existing /api/chat/ endpoints and WebSocket logic
 */

class FloatingChat {
    constructor() {
        this.container = null;
        this.bubble = null;
        this.convList = null;
        this.msgList = null;
        this.msgContainer = null;
        this.input = null;
        this.sendBtn = null;

        this.currentConversationId = null;
        this.chatSocket = null;
        this.notificationSocket = null;
        this.usersCache = null;

        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.renderWidget();
            this.setupElements();
            this.setupEventListeners();
            this.loadConversations();
            this.connectNotificationSocket();
            this.updateTotalUnread();
        });
    }

    renderWidget() {
        const html = `
            <div class="chat-widget-bubble" id="chatWidgetBubble">
                <i class="bi bi-chat-dots-fill"></i>
                <span class="chat-widget-badge" id="chatWidgetBadge">0</span>
            </div>
            <div class="chat-widget-container" id="chatWidgetContainer">
                <div class="chat-widget-header">
                    <h5><i class="bi bi-chat-dots me-2"></i>Mensagens</h5>
                    <div class="chat-widget-header-actions">
                        <button class="btn-new-chat" id="btnNewChat" title="Nova Conversa">
                            <i class="bi bi-plus-lg"></i>
                        </button>
                        <button class="chat-widget-close" id="chatWidgetClose">
                            <i class="bi bi-dash-lg"></i>
                        </button>
                    </div>
                </div>
                <div class="chat-widget-body">
                    <div class="widget-conversations" id="widgetConversations">
                        <!-- Conversas carregadas via JS -->
                    </div>
                    
                    <div class="widget-search-view" id="widgetSearchView">
                        <div class="widget-search-header">
                            <div class="widget-search-input-wrapper">
                                <i class="bi bi-search"></i>
                                <input type="text" class="widget-search-input" id="widgetSearchInput" placeholder="Buscar contatos...">
                            </div>
                        </div>
                        <div class="widget-user-list" id="widgetUserList">
                            <!-- Usuários carregados via JS -->
                        </div>
                    </div>

                    <div class="widget-messages-container" id="widgetMessagesContainer">
                        <div class="widget-messages-header">
                            <button class="btn-back-to-convs" id="btnBackToConvs">
                                <i class="bi bi-arrow-left"></i>
                            </button>
                            <div class="widget-messages-header-info">
                                <span id="widgetChatName" class="fw-bold fs-6">Selecione um chat</span>
                                <span id="widgetChatStatus" class="widget-chat-status"></span>
                            </div>
                        </div>
                        <div class="widget-messages-list" id="widgetMessagesList">
                            <!-- Mensagens carregadas via JS -->
                        </div>
                        <div class="widget-input-area">
                            <input type="file" id="widgetFile" style="display: none;">
                            <button class="btn-widget-attach" id="btnWidgetAttach" title="Anexar arquivo">
                                <i class="bi bi-paperclip"></i>
                            </button>
                            <input type="text" class="widget-input" id="widgetInput" placeholder="Mensagem...">
                            <button class="btn-widget-send" id="btnWidgetSend" disabled>
                                <i class="bi bi-send-fill"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', html);
    }

    setupElements() {
        this.container = document.getElementById('chatWidgetContainer');
        this.bubble = document.getElementById('chatWidgetBubble');
        this.convList = document.getElementById('widgetConversations');
        this.msgList = document.getElementById('widgetMessagesList');
        this.msgContainer = document.getElementById('widgetMessagesContainer');
        this.searchView = document.getElementById('widgetSearchView');
        this.userList = document.getElementById('widgetUserList');
        this.searchInput = document.getElementById('widgetSearchInput');
        this.input = document.getElementById('widgetInput');
        this.sendBtn = document.getElementById('btnWidgetSend');
        this.badge = document.getElementById('chatWidgetBadge');
        this.backBtn = document.getElementById('btnBackToConvs');
        this.closeBtn = document.getElementById('chatWidgetClose');
        this.newChatBtn = document.getElementById('btnNewChat');
        this.attachBtn = document.getElementById('btnWidgetAttach');
        this.fileInput = document.getElementById('widgetFile');
        this.chatStatus = document.getElementById('widgetChatStatus');
    }

    setupEventListeners() {
        this.bubble.addEventListener('click', () => {
            const isVisible = this.container.style.display === 'flex';
            this.container.style.display = isVisible ? 'none' : 'flex';
            if (!isVisible) {
                this.showView('convs');
                this.loadConversations();
            }
        });

        this.closeBtn.addEventListener('click', () => {
            this.container.style.display = 'none';
        });

        this.newChatBtn.addEventListener('click', () => {
            this.showView('search');
            this.loadUsers();
        });

        this.backBtn.addEventListener('click', () => {
            this.showView('convs');
            this.currentConversationId = null;
            if (this.chatSocket) this.chatSocket.close();
            this.loadConversations();
        });

        this.searchInput.addEventListener('input', (e) => {
            clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(() => this.loadUsers(e.target.value), 300);
        });

        this.input.addEventListener('input', () => {
            this.sendBtn.disabled = !this.input.value.trim();
        });

        this.input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        this.sendBtn.addEventListener('click', () => this.sendMessage());

        this.attachBtn.addEventListener('click', () => this.fileInput.click());
        this.fileInput.addEventListener('change', () => this.handleFileSelect());
    }

    showView(view) {
        this.convList.style.display = view === 'convs' ? 'block' : 'none';
        this.searchView.style.display = view === 'search' ? 'flex' : 'none';
        this.msgContainer.style.display = view === 'msgs' ? 'flex' : 'none';

        // Altera o ícone do botão back conforme a vista
        if (view === 'search' || view === 'msgs') {
            this.backBtn.style.display = 'block';
        } else {
            this.backBtn.style.display = 'none';
        }
    }

    async loadConversations() {
        try {
            const res = await fetch('/api/chat/conversations/');
            const data = await res.json();
            this.renderConversations(data.conversations);
        } catch (e) {
            console.error('Erro ao carregar conversas widget:', e);
        }
    }

    async loadUsers(search = '') {
        const searchTerm = search.toLowerCase().trim();

        // Se a busca estiver vazia e já temos o cache, usa o cache local
        if (!searchTerm && this.usersCache) {
            this.renderUsers(this.usersCache);
            return;
        }

        this.userList.innerHTML = '<div class="p-4 text-center text-muted"><small>Buscando...</small></div>';
        try {
            const res = await fetch(`/api/chat/users/?search=${encodeURIComponent(search)}`);
            const data = await res.json();

            // Se a busca estava vazia, guarda no cache principal
            if (!searchTerm) {
                this.usersCache = data.users;
            }

            this.renderUsers(data.users);
        } catch (e) {
            console.error('Erro ao carregar usuários widget:', e);
        }
    }

    renderUsers(users) {
        if (!users.length) {
            this.userList.innerHTML = '<div class="p-4 text-center text-muted"><p>Nenhum usuário encontrado.</p></div>';
            return;
        }

        this.userList.innerHTML = users.map(u => `
            <div class="widget-user-item" data-id="${u.id}" data-name="${u.name}" data-role="${u.role || ''}" data-dept="${u.department || 'Sem setor'}">
                <div class="widget-user-avatar">${u.initials}</div>
                <div class="widget-user-info">
                    <div class="widget-user-name">${u.name}</div>
                    <div class="widget-user-dept">${u.role || ''} ${u.department ? 'do ' + u.department : ''}</div>
                </div>
            </div>
        `).join('');

        this.userList.querySelectorAll('.widget-user-item').forEach(item => {
            item.addEventListener('click', () => {
                this.startConversation(item.dataset.id, item.dataset.name);
            });
        });
    }

    async startConversation(userId, userName) {
        try {
            const res = await fetch('/api/chat/conversations/start/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify({ user_id: userId })
            });
            const data = await res.json();
            const roleInfo = data.other_user.role ? `${data.other_user.role} ${data.other_user.department ? 'do ' + data.other_user.department : ''}` : (data.other_user.department || '');
            this.openChat(data.conversation_id, userName, roleInfo);
        } catch (e) {
            console.error('Erro ao iniciar conversa widget:', e);
        }
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

    renderConversations(conversations) {
        if (!conversations.length) {
            this.convList.innerHTML = '<div class="p-4 text-center text-muted"><p>Nenhuma conversa ativa.</p></div>';
            return;
        }

        this.convList.innerHTML = conversations.map(c => {
            const roleInfo = c.other_user.role ? `${c.other_user.role} ${c.other_user.department ? 'do ' + c.other_user.department : ''}` : (c.other_user.department || '');
            return `
                <div class="widget-conv-item" data-id="${c.id}" data-name="${c.other_user.name}" data-status="${roleInfo}">
                    <div class="widget-conv-avatar">${c.other_user.initials}</div>
                    <div class="widget-conv-info">
                        <div class="widget-conv-name">${c.other_user.name}</div>
                        <div class="widget-conv-last">${c.last_message ? c.last_message.content : 'Nova conversa'}</div>
                    </div>
                    ${c.unread_count > 0 ? `<span class="badge rounded-pill bg-primary">${c.unread_count}</span>` : ''}
                </div>
            `;
        }).join('');

        this.convList.querySelectorAll('.widget-conv-item').forEach(item => {
            item.addEventListener('click', () => {
                const id = item.dataset.id;
                const name = item.dataset.name;
                const status = item.dataset.status;
                this.openChat(id, name, status);
            });
        });

        this.updateTotalUnread();
    }

    async openChat(id, name, statusValue = '') {
        this.currentConversationId = id;
        document.getElementById('widgetChatName').textContent = name;
        this.chatStatus.textContent = statusValue;
        this.showView('msgs');
        this.msgList.innerHTML = '<div class="p-4 text-center text-muted"><small>Carregando...</small></div>';

        try {
            const res = await fetch(`/api/chat/conversations/${id}/messages/`);
            if (!res.ok) {
                const errData = await res.json().catch(() => ({ error: 'Erro de servidor' }));
                this.msgList.innerHTML = `<div class="p-4 text-center text-danger"><small>Erro: ${errData.error || 'Falha ao carregar'}</small></div>`;
                return;
            }
            const data = await res.json();

            // Atualiza o status caso não tenha vindo no clique inicial (ex: refresh)
            if (!this.chatStatus.textContent && data.other_user) {
                const roleInfo = data.other_user.role ? `${data.other_user.role} ${data.other_user.department ? 'do ' + data.other_user.department : ''}` : (data.other_user.department || '');
                this.chatStatus.textContent = roleInfo;
            }

            this.renderMessages(data.messages);
            this.connectChatSocket(id);
        } catch (e) {
            console.error('Erro ao abrir chat widget:', e);
            this.msgList.innerHTML = '<div class="p-4 text-center text-danger"><small>Erro de conexão</small></div>';
        }
    }

    renderMessages(messages) {
        if (!messages.length) {
            this.msgList.innerHTML = '<div class="p-4 text-center text-muted"><small>Diga olá! 👋</small></div>';
            return;
        }

        this.msgList.innerHTML = messages.map(m => this.getMessageHtml(m)).join('');
        this.scrollToBottom();
    }

    getMessageHtml(m) {
        const isMine = m.is_mine || m.sender_id === (typeof currentUserId !== 'undefined' ? currentUserId : null);
        let attachmentHtml = '';
        if (m.file_url) {
            attachmentHtml = `
                <a href="${m.file_url}" target="_blank" class="message-attachment">
                    <i class="bi bi-file-earmark-arrow-down"></i>
                    <div class="message-attachment-info">
                        <span class="message-attachment-name" title="${m.file_name}">${this.escape(m.file_name)}</span>
                        <span class="message-attachment-label">Download</span>
                    </div>
                </a>
            `;
        }

        // Só mostra botões de ação para mensagens com ID real (não temporário)
        const hasRealId = typeof m.id === 'number';
        const actionsHtml = isMine && !m.is_deleted && hasRealId ? `
            <div class="message-actions">
                <button class="message-action-btn edit" onclick="chatWidget.showEditModal(${m.id}, this)" title="Editar">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="message-action-btn delete" onclick="chatWidget.confirmDelete(${m.id})" title="Excluir">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        ` : '';

        return `
            <div class="message ${isMine ? 'message-sent' : 'message-received'}" data-msg-id="${m.id}"
                 style="align-self: ${isMine ? 'flex-end' : 'flex-start'}; 
                        background: ${isMine ? '#dcf8c6' : 'white'};
                        max-width: 80%; padding: 8px 12px; border-radius: 8px; font-size: 0.9rem;
                        box-shadow: 0 1px 1px rgba(0,0,0,0.1); margin-bottom: 5px;">
                ${actionsHtml}
                <div class="message-content">${this.escape(m.content)}${m.edited_at ? ' <span style="font-size: 0.65rem; color: #94a3b8;">(editada)</span>' : ''}</div>
                ${attachmentHtml}
                <div class="message-time" style="font-size: 0.7rem; color: #94a3b8; text-align: right; margin-top: 4px;">
                    ${m.created_at || ''}
                </div>
            </div>
        `;
    }

    connectChatSocket(id) {
        if (this.chatSocket) this.chatSocket.close();

        const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
        this.chatSocket = new WebSocket(`${wsScheme}://${window.location.host}/ws/chat/${id}/`);

        this.chatSocket.onopen = () => {
            // Mark messages as read when chat opens
            this.chatSocket.send(JSON.stringify({ type: 'read' }));
            this.updateTotalUnread();
        };

        this.chatSocket.onmessage = (e) => {
            const data = JSON.parse(e.data);
            if (data.type === 'message') {
                // Ignora mensagens próprias (já exibidas via optimistic UI)
                const isMine = data.message.sender_id === (typeof currentUserId !== 'undefined' ? currentUserId : null);
                if (isMine) return;

                const empty = this.msgList.querySelector('.text-muted');
                if (empty) this.msgList.innerHTML = '';
                this.msgList.insertAdjacentHTML('beforeend', this.getMessageHtml(data.message));
                this.scrollToBottom();
                // Mark as read immediately
                this.chatSocket.send(JSON.stringify({ type: 'read' }));
                this.updateTotalUnread();
            } else if (data.type === 'edited') {
                const msgEl = this.msgList.querySelector(`[data-msg-id="${data.message_id}"] .message-content`);
                if (msgEl) {
                    msgEl.innerHTML = `${this.escape(data.content)} <span style="font-size: 0.65rem; color: #94a3b8;">(editada)</span>`;
                }
            } else if (data.type === 'deleted') {
                const msgEl = this.msgList.querySelector(`[data-msg-id="${data.message_id}"]`);
                if (msgEl) {
                    msgEl.style.opacity = '0.5';
                    const contentEl = msgEl.querySelector('.message-content');
                    if (contentEl) contentEl.innerHTML = '<em>Mensagem excluída</em>';
                }
            }
        };
    }

    connectNotificationSocket() {
        const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
        this.notificationSocket = new WebSocket(`${wsScheme}://${window.location.host}/ws/chat/`);

        this.notificationSocket.onmessage = (e) => {
            const data = JSON.parse(e.data);
            if (data.type === 'new_message' || data.type === 'unread_count') {
                if (this.container.style.display === 'flex' && !this.currentConversationId) {
                    this.loadConversations();
                } else {
                    this.updateTotalUnread();
                }
            }
        };
    }

    async updateTotalUnread() {
        try {
            const res = await fetch('/api/chat/unread-count/');
            if (res.ok) {
                const data = await res.json();
                if (data.count > 0) {
                    this.badge.textContent = data.count > 99 ? '99+' : data.count;
                    this.badge.style.display = 'block';
                } else {
                    this.badge.style.display = 'none';
                }
            }
        } catch (e) { }
    }

    sendMessage() {
        const content = this.input.value.trim();
        if (!content || !this.currentConversationId) return;

        // Optimistic UI - mostra mensagem imediatamente
        const tempId = `temp-${Date.now()}`;
        const now = new Date();
        const timeStr = now.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });

        const tempMessage = {
            id: tempId,
            content: content,
            sender_id: typeof currentUserId !== 'undefined' ? currentUserId : null,
            is_mine: true,
            created_at: timeStr,
            file_url: null,
            file_name: null,
            edited_at: null,
            is_deleted: false
        };

        // Remove o placeholder "Diga olá"
        const empty = this.msgList.querySelector('.text-muted');
        if (empty) this.msgList.innerHTML = '';

        // Adiciona mensagem instantaneamente
        this.msgList.insertAdjacentHTML('beforeend', this.getMessageHtml(tempMessage));
        this.scrollToBottom();

        // Limpa input
        this.input.value = '';
        this.sendBtn.disabled = true;

        // IMPORTANTE: Salvar via API HTTP (garante persistência no banco de dados)
        fetch(`/api/chat/conversations/${this.currentConversationId}/send/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCookie('csrftoken')
            },
            body: JSON.stringify({ content: content })
        })
            .then(res => {
                if (res.ok) {
                    return res.json();
                } else {
                    throw new Error('Falha ao salvar mensagem');
                }
            })
            .then(data => {
                // Atualiza o tempId para o ID real na mensagem exibida
                const tempEl = this.msgList.querySelector(`[data-msg-id="${tempId}"]`);
                if (tempEl) {
                    tempEl.dataset.msgId = data.id;
                }
            })
            .catch(e => {
                console.error('Erro ao enviar mensagem:', e);
                // Marca mensagem como erro visual
                const tempEl = this.msgList.querySelector(`[data-msg-id="${tempId}"]`);
                if (tempEl) {
                    tempEl.style.opacity = '0.5';
                    tempEl.title = 'Erro ao enviar - tente novamente';
                }
            });
    }

    async handleFileSelect() {
        const file = this.fileInput.files[0];
        if (!file || !this.currentConversationId) return;

        const formData = new FormData();
        formData.append('file', file);
        formData.append('conversation_id', this.currentConversationId);
        formData.append('csrfmiddlewaretoken', this.getCookie('csrftoken'));

        this.input.placeholder = "Enviando arquivo...";
        this.input.disabled = true;
        this.attachBtn.disabled = true;

        try {
            const res = await fetch('/api/chat/upload/', {
                method: 'POST',
                body: formData
            });
            if (res.ok) {
                const data = await res.json();
                // O WebSocket cuidará de mostrar a mensagem se estiver conectado, 
                // mas vamos limpar o input
                this.input.value = '';
                this.fileInput.value = '';
            } else {
                const errData = await res.json();
                alert(`Erro ao enviar arquivo: ${errData.error || res.statusText}`);
            }
        } catch (e) {
            console.error('Erro no upload widget:', e);
        } finally {
            this.input.placeholder = "Mensagem...";
            this.input.disabled = false;
            this.attachBtn.disabled = false;
            this.sendBtn.disabled = !this.input.value.trim();
        }
    }

    scrollToBottom() {
        this.msgList.scrollTop = this.msgList.scrollHeight;
    }

    escape(html) {
        const div = document.createElement('div');
        div.textContent = html;
        return div.innerHTML;
    }

    showEditModal(msgId, btn) {
        const msgEl = this.msgList.querySelector(`[data-msg-id="${msgId}"]`);
        if (!msgEl) return;

        const contentEl = msgEl.querySelector('.message-content');
        const currentText = contentEl.textContent.replace('(editada)', '').trim();

        const overlay = document.createElement('div');
        overlay.className = 'chat-edit-overlay';
        overlay.innerHTML = `
            <div class="chat-edit-modal">
                <h6>Editar mensagem</h6>
                <input type="text" class="chat-edit-input" value="${this.escape(currentText)}" id="editMsgInput">
                <div class="chat-edit-actions">
                    <button class="chat-edit-btn cancel" onclick="chatWidget.closeEditModal()">Cancelar</button>
                    <button class="chat-edit-btn save" onclick="chatWidget.editMessage(${msgId})">Salvar</button>
                </div>
            </div>
        `;

        this.msgContainer.appendChild(overlay);
        document.getElementById('editMsgInput').focus();
        document.getElementById('editMsgInput').select();
    }

    closeEditModal() {
        const overlay = this.msgContainer.querySelector('.chat-edit-overlay');
        if (overlay) overlay.remove();
    }

    async editMessage(msgId) {
        const input = document.getElementById('editMsgInput');
        const newContent = input.value.trim();

        if (!newContent) {
            alert('O conteúdo não pode estar vazio');
            return;
        }

        try {
            const res = await fetch(`/api/chat/messages/${msgId}/edit/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify({ content: newContent })
            });

            if (res.ok) {
                this.closeEditModal();
            } else {
                const data = await res.json();
                alert(data.error || 'Erro ao editar mensagem');
            }
        } catch (e) {
            console.error('Erro ao editar:', e);
        }
    }

    confirmDelete(msgId) {
        if (confirm('Deseja excluir esta mensagem?')) {
            this.deleteMessage(msgId);
        }
    }

    async deleteMessage(msgId) {
        try {
            const res = await fetch(`/api/chat/messages/${msgId}/delete/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                }
            });

            if (!res.ok) {
                const data = await res.json();
                alert(data.error || 'Erro ao excluir mensagem');
            }
        } catch (e) {
            console.error('Erro ao excluir:', e);
        }
    }
}

// Inicia o widget e expõe globalmente para os botões onclick
const floatingChat = new FloatingChat();
const chatWidget = floatingChat;
