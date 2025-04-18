from django.contrib.auth.decorators import login_required
from ..models import ActivityLog

def get_client_ip(request):
    """Funkcja pomocnicza do pobrania adresu IP klienta"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_activity(request, action_type, ticket=None, description=""):
    """Funkcja pomocnicza do logowania aktywności"""
    if request.user.is_authenticated:
        ActivityLog.objects.create(
            user=request.user,
            action_type=action_type,
            ticket=ticket,
            description=description,
            ip_address=get_client_ip(request)
        )
