/**
 * Sistema de Toast Notifications (Premium SweetAlert2)
 * Exibe mensagens animadas no canto inferior direito
 */

function showToast(message, type = 'info') {
    // Se o Swal estiver disponível, usa ele. Caso contrário, tenta showGlobalToast
    if (typeof Swal !== 'undefined') {
        const Toast = Swal.mixin({
            toast: true,
            position: 'bottom-end',
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true,
            didOpen: (toast) => {
                toast.addEventListener('mouseenter', Swal.stopTimer)
                toast.addEventListener('mouseleave', Swal.resumeTimer)
            }
        });

        const typeMap = {
            'success': 'success',
            'error': 'error',
            'danger': 'error',
            'warning': 'warning',
            'info': 'info',
            'debug': 'info'
        };

        Toast.fire({
            icon: typeMap[type] || 'info',
            title: message
        });
    } else {
        console.warn('SweetAlert2 não carregado. Toast:', message);
        // Fallback simples se necessário
        alert(message);
    }
}

// Alias global
window.showToast = showToast;

