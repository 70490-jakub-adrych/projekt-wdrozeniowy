from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden

def role_required(allowed_roles):
    """
    Decorator to check if user has the required role
    :param allowed_roles: List of role strings that are allowed (e.g. ['admin', 'moderator'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            try:
                user_role = request.user.profile.role
                if user_role in allowed_roles:
                    return view_func(request, *args, **kwargs)
            except:
                pass
                
            messages.error(request, "Nie masz uprawnień do tej operacji.")
            return HttpResponseForbidden("Brak uprawnień do wykonania tej operacji.")
        return _wrapped_view
    return decorator
