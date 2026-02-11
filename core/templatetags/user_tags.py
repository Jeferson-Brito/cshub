from django import template

register = template.Library()


@register.filter
def get_user_initials(user):
    """
    Retorna as iniciais do usuário para usar como fallback do avatar.
    Usa o método do modelo se disponível, caso contrário calcula aqui.
    """
    if hasattr(user, 'get_initials'):
        return user.get_initials()
    
    # Fallback se o método não existir
    if hasattr(user, 'first_name') and hasattr(user, 'last_name'):
        if user.first_name and user.last_name:
            return f"{user.first_name[0]}{user.last_name[0]}".upper()
        elif user.first_name:
            return user.first_name[0].upper()
    
    if hasattr(user, 'username') and user.username:
        return user.username[0].upper()
    
    return "?"


@register.filter
def has_profile_photo(user):
    """
    Verifica se o usuário tem uma foto de perfil válida.
    """
    return hasattr(user, 'profile_photo') and user.profile_photo and bool(user.profile_photo.name)


@register.simple_tag
def monthly_audit_count(store):
    """
    Retorna a contagem de auditorias do mês para a loja.
    """
    return getattr(store, 'audits_this_month_count', 0)
