from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from django.core.exceptions import PermissionDenied

def role_required(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Musisz być zalogowany, aby uzyskać dostęp do tej strony.')
                return redirect('login')
            
            if not hasattr(request.user, 'profile'):
                messages.error(request, 'Twój profil użytkownika nie jest poprawnie skonfigurowany.')
                return redirect('login')
            
            # Specjalna obsługa dla roli viewer
            if request.user.profile.role == 'viewer' and request.resolver_match.url_name != 'ticket_display':
                return redirect('ticket_display')
            
            if request.user.profile.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'Nie masz uprawnień do dostępu do tej strony.')
                raise PermissionDenied
        return _wrapped_view
    return decorator

def admin_required(view_func):
    return role_required(['admin'])(view_func)

def admin_or_superagent_required(view_func):
    return role_required(['admin', 'superagent'])(view_func)

def superagent_required(view_func):
    return role_required(['admin', 'superagent'])(view_func)

def agent_required(view_func):
    return role_required(['admin', 'superagent', 'agent'])(view_func)

def viewer_required(view_func):
    return role_required(['admin', 'superagent', 'agent', 'viewer'])(view_func)

def client_required(view_func):
    return role_required(['admin', 'superagent', 'agent', 'client'])(view_func)
