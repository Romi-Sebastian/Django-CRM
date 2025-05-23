from .models import Notification

def unread_notifications_context(request):
    count = 0
    notifications = []
    if request.user.is_authenticated:
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:5]
    
    return {
        'unread_notifications_count': count,
        'recent_unread_notifications': notifications,
    }
