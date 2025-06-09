from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
import re
import logging

logger = logging.getLogger(__name__)

class ViewerRestrictMiddleware:
    """
    Blokuje użytkownikom z rolą 'viewer' dostęp do wszystkich stron poza ticket_display, get_tickets_update i logout.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            if request.user.profile.role == 'viewer':
                allowed_urls = [
                    reverse('ticket_display'),
                    reverse('logout'),
                    reverse('get_tickets_update'),
                ]
                if request.path not in allowed_urls:
                    return redirect('ticket_display')
        return self.get_response(request)

class EmailVerificationMiddleware:
    """Middleware to restrict users who haven't verified their email"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Process the request
        if self._should_redirect_to_verification(request):
            # Store the originally requested URL in session for redirect after verification
            request.session['next_after_verification'] = request.get_full_path()
            messages.info(request, "Musisz zweryfikować swój adres email przed dostępem do systemu.")
            return redirect('verify_email')
            
        # Continue processing the request
        response = self.get_response(request)
        return response
    
    def _should_redirect_to_verification(self, request):
        """Check if the user should be redirected to email verification"""
        # Only apply to authenticated users
        if not request.user.is_authenticated:
            return False
            
        # Skip for admin users
        if request.user.is_superuser or request.user.is_staff:
            return False
            
        # Check if the user has verified their email
        if not hasattr(request.user, 'profile'):
            return False
            
        email_verified = request.user.profile.email_verified
        
        # Allow access to verification-related paths
        allowed_paths = [
            '/verify-email/',  # Make sure this matches the actual URL path
            '/logout/',
            '/static/',
            '/media/',
            '/admin/',
        ]
        
        # Check if current path is in allowed paths
        current_path = request.path
        for path in allowed_paths:
            if current_path.startswith(path):
                return False
                
        # If not verified and not an allowed path, redirect to verification
        return not email_verified