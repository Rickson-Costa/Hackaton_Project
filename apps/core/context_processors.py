from .notifications import NotificationService

def notifications(request):
    """Context processor para adicionar notificações globalmente"""
    if request.user.is_authenticated:
        return {
            'notifications': NotificationService.get_all_notifications(request.user)
        }
    return {'notifications': []}