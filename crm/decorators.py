from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

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

def two_factor_required(view_func):
    """
    Decorator that ensures a user has completed 2FA verification if it's enabled
    on their account. Use this for particularly sensitive views.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Musisz być zalogowany, aby uzyskać dostęp do tej strony.')
            return redirect('login')
        
        # Check if user has 2FA enabled
        if hasattr(request.user, 'profile') and request.user.profile.ga_enabled:
            # Get the client IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            
            # Get device fingerprint
            device_fingerprint = request.META.get('HTTP_USER_AGENT', '')
            
            # If verification is needed (with both IP and fingerprint)
            if request.user.profile.needs_2fa_verification(request_ip=ip, device_fingerprint=device_fingerprint):
                # Store the original URL
                request.session['2fa_next'] = request.get_full_path()
                messages.warning(request, 'Ta strona wymaga weryfikacji dwuskładnikowej.')
                return redirect('verify_2fa')
        
        # User has 2FA disabled or has already verified
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view

def sensitive_view(view_func):
    """
    Decorator for highly sensitive views that always require 2FA verification,
    regardless of trusted device status (like account settings, security features).
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Musisz być zalogowany, aby uzyskać dostęp do tej strony.')
            return redirect('login')
        
        # Check if user has 2FA enabled
        if hasattr(request.user, 'profile') and request.user.profile.ga_enabled:
            # Check if 2FA was recently verified (within the last 5 minutes)
            now = timezone.now()
            last_auth = request.user.profile.ga_last_authenticated
            
            if not last_auth or (now - last_auth) > timedelta(minutes=5):
                # Require fresh 2FA verification
                request.session['2fa_next'] = request.get_full_path()
                request.session['require_fresh_2fa'] = True
                messages.warning(
                    request, 
                    'Ta strona wymaga dodatkowej weryfikacji ze względów bezpieczeństwa.'
                )
                return redirect('verify_2fa')
        
        # If 2FA is not enabled, remind user to set it up
        elif hasattr(request.user, 'profile') and not request.user.profile.ga_enabled:
            messages.warning(
                request, 
                'Zalecamy włączenie uwierzytelniania dwuskładnikowego, aby chronić Twoje konto.'
            )
        
        # User has 2FA disabled or has already verified recently
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view