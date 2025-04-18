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

def log_error(request, error_type, url=None, description=None):
    """Log error activities like 404 and 403 errors"""
    from ..models import ActivityLog
    
    # Get the URL that was attempted to be accessed
    if url is None:
        url = request.path
        
    # Create descriptive message if not provided
    if description is None:
        if error_type == '404_error':
            description = f"Attempted to access non-existent page: {url}"
        elif error_type == '403_error':
            description = f"Attempted to access restricted page: {url}"
    
    # Get IP address
    ip_address = get_client_ip(request)
    
    # Create log entry
    log_entry = ActivityLog(
        action_type=error_type,
        description=description,
        ip_address=ip_address
    )
    
    # Add user information if authenticated
    if request.user.is_authenticated:
        log_entry.user = request.user
        
    log_entry.save()
    return log_entry
