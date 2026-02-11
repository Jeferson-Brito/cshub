
@login_required
def api_get_system_notifications(request):
    """
    API para retornar as últimas notificações do sistema.
    Retorna JSON com lista de notificações ativas.
    """
    notifications = SystemNotification.objects.filter(is_active=True).order_by('-created_at')[:5]
    
    data = []
    for notification in notifications:
        data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'details': notification.details,
            'category': notification.get_category_display(),
            'category_code': notification.category,
            'created_at': notification.created_at.strftime('%d/%m/%Y %H:%M'),
            'timestamp': notification.created_at.timestamp()
        })
        
    return JsonResponse({'notifications': data})
