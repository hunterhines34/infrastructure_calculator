from django.db.models import Q
from .models import Project, Notification

def notifications(request):
    if request.user.is_authenticated and request.user.is_staff:
        # Get unread notifications
        unread_notifications = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        )
        
        return {
            'unread_notifications': unread_notifications,
            'unread_notifications_count': unread_notifications.count(),  # Changed variable name to match template
        }
    return {
        'unread_notifications': [],
        'unread_notifications_count': 0,  # Changed variable name to match template
    } 