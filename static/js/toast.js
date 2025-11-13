/**
 * Sistema de Toast Notifications
 * Exibe mensagens animadas no canto inferior direito
 */

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    // Mapear tipos do Django para tipos de toast
    const typeMap = {
        'success': 'success',
        'error': 'error',
        'danger': 'error',
        'warning': 'warning',
        'info': 'info',
        'debug': 'info'
    };

    const toastType = typeMap[type] || 'info';

    // Criar elemento do toast
    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${toastType}`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');

    // Ícones por tipo
    const icons = {
        'success': 'bi-check-circle-fill',
        'error': 'bi-exclamation-triangle-fill',
        'warning': 'bi-exclamation-circle-fill',
        'info': 'bi-info-circle-fill'
    };

    // Títulos por tipo
    const titles = {
        'success': 'Sucesso!',
        'error': 'Erro!',
        'warning': 'Atenção!',
        'info': 'Informação'
    };

    // Cores de fundo
    const bgColors = {
        'success': 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
        'error': 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
        'warning': 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
        'info': 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)'
    };

    toast.innerHTML = `
        <div class="toast-content">
            <div class="toast-icon" style="background: ${bgColors[toastType]}">
                <i class="bi ${icons[toastType]}"></i>
            </div>
            <div class="toast-body">
                <div class="toast-title">${titles[toastType]}</div>
                <div class="toast-message">${message}</div>
            </div>
            <button type="button" class="toast-close" onclick="closeToast(this)">
                <i class="bi bi-x"></i>
            </button>
        </div>
        <div class="toast-progress">
            <div class="toast-progress-bar"></div>
        </div>
    `;

    // Adicionar ao container
    container.appendChild(toast);

    // Trigger animação de entrada
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);

    // Auto-remover após 5 segundos
    const progressBar = toast.querySelector('.toast-progress-bar');
    if (progressBar) {
        progressBar.style.animation = 'toastProgress 5s linear forwards';
    }

    setTimeout(() => {
        closeToast(toast.querySelector('.toast-close'));
    }, 5000);
}

function closeToast(button) {
    const toast = button.closest('.toast-notification');
    if (toast) {
        toast.classList.remove('show');
        toast.classList.add('hide');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }
}

// Função global para usar em outros lugares
window.showToast = showToast;

