from django.shortcuts import redirect
from django.urls import reverse, resolve
from django.contrib import messages
import logging
from ..utils.two_factor import requires_2fa_setup, is_trusted_device, is_admin_from_known_ip

logger = logging.getLogger(__name__)

class TwoFactorMiddleware:
    """
    Middleware to enforce 2FA for protected views
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Skip middleware if user is not authenticated
        if not request.user.is_authenticated:
            return self.get_response(request)
            
        # Get the current path
        current_path = request.path
        
        # Paths that are always exempt from 2FA
        exempt_paths = [
            reverse('login'),
            reverse('logout'),
            '/two-factor/setup/',
            '/two-factor/verify/',
            '/two-factor/recovery/',
            '/admin/login/',
            '/static/',
            '/media/',
            '/verify-email/',
            '/register/pending/',
        ]
        
        # Check if path is exempt
        if any(current_path.startswith(path) for path in exempt_paths):
            return self.get_response(request)
        
        # Admin users from known IPs bypass 2FA
        if is_admin_from_known_ip(request):
            return self.get_response(request)
        
        # Check if user needs to set up 2FA
        if requires_2fa_setup(request.user):
            # Only redirect if not already going to setup page
            if current_path != '/two-factor/setup/':
                messages.info(request, "Wymagane skonfigurowanie uwierzytelniania dwuskładnikowego.")
                return redirect('two_factor_setup')  # Use named URL pattern
        
        # If 2FA is enabled, check if device is trusted
        try:
            if request.user.two_factor.ga_enabled and not is_trusted_device(request):
                # Store the intended URL in the session for redirection after 2FA verification
                request.session['next_url'] = current_path
                return redirect('two_factor_verify')  # Use named URL pattern
        except Exception as e:
            logger.error(f"Error checking 2FA status: {str(e)}")
        
        # Continue with the request
        return self.get_response(request)
