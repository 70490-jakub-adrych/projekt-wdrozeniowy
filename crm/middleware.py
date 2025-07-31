from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
import re
import logging
from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone

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
        if request.user.is_authenticated:
            # Check if user needs email verification
            if hasattr(request.user, 'profile') and not request.user.profile.email_verified:
                # User needs to verify email
                if not self._is_exempt_path(request.path):
                    messages.info(request, 'Musisz zweryfikować swój adres email przed kontynuowaniem.')
                    return redirect('verify_email')
            
            # Check if verified but not approved user is trying to access non-exempt pages
            elif hasattr(request.user, 'profile') and request.user.profile.email_verified and not request.user.profile.is_approved:
                # User is verified but waiting for admin approval
                if not self._is_approval_exempt_path(request.path):
                    return redirect('register_pending')
                    
        return self.get_response(request)
    
    def _is_exempt_path(self, path):
        """Check if path is exempt from email verification"""
        exempt_paths = [
            '/verify-email/',
            '/logout/',
            '/static/',
            '/media/',
            '/admin/',
        ]
        return any(path.startswith(exempt) for exempt in exempt_paths)
    
    def _is_approval_exempt_path(self, path):
        """Check if path is exempt for users awaiting approval"""
        exempt_paths = [
            '/register/pending/',
            '/logout/',
            '/static/',
            '/media/',
            '/admin/',
        ]
        return any(path.startswith(exempt) for exempt in exempt_paths)

class TwoFactorMiddleware:
    """Middleware to enforce 2FA verification when needed"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Cache verify_2fa URL to avoid repeated calls to reverse()
        self.verify_2fa_url = reverse('verify_2fa')
        # Get other exempt URLs once on initialization
        self.setup_2fa_url = reverse('setup_2fa')
        self.setup_2fa_success_url = reverse('setup_2fa_success')
        self.recovery_code_url = reverse('recovery_code')
        self.logout_url = reverse('logout')
        
        # Store exempt paths as a set for faster lookups
        self.static_exempt_paths = {
            '/static/',
            '/media/',
            '/admin/',
            '/verify-email/',
            '/register/',
            '/password_reset/',
            '/reset/',
        }
        
    def __call__(self, request):
        if request.user.is_authenticated:
            # Check if user is exempt from 2FA enforcement (like superuser during initial setup)
            is_exempt = request.user.is_superuser and getattr(settings, 'EXEMPT_SUPERUSER_FROM_2FA', False)
            
            # Also check if user's group is exempt from 2FA
            group_exempt = False
            if hasattr(request.user, 'profile') and request.user.groups.exists():
                group = request.user.groups.first()
                if hasattr(group, 'settings'):
                    group_exempt = group.settings.exempt_from_2fa
                    
                    # Save navbar visibility setting in request for use in templates
                    request.show_navbar = group.settings.show_navbar
                else:
                    # Default show navbar if no settings
                    request.show_navbar = True
            else:
                # Default show navbar if no groups
                request.show_navbar = True
            
            # Check if user has profile and is already approved
            if hasattr(request.user, 'profile') and request.user.profile.is_approved and not is_exempt and not group_exempt:
                # First case: User has 2FA enabled
                if request.user.profile.ga_enabled:
                    profile = request.user.profile
                    
                    # First, check if we're already on the verification page to prevent infinite loops
                    current_path = request.path.rstrip('/')
                    verify_path = self.verify_2fa_url.rstrip('/')
                    
                    # Direct equality check for verification page
                    if current_path == verify_path:
                        # Already on verification page, don't redirect
                        return self.get_response(request)
                        
                    # Check if the path is exempt regardless
                    if self._is_exempt_path(request.path):
                        # Path is exempt from 2FA, proceed normally
                        return self.get_response(request)
                    
                    # Get the IP address
                    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                    if x_forwarded_for:
                        ip = x_forwarded_for.split(',')[0]
                    else:
                        ip = request.META.get('REMOTE_ADDR')
                    
                    # Check for successful 2FA verification in this session
                    verified = request.session.get('2fa_verified', False)
                    verified_time_str = request.session.get('2fa_verified_time', None)
                    
                    # Check if verification is still valid (not expired)
                    verification_valid = False
                    if verified and verified_time_str:
                        try:
                            verified_time = datetime.fromisoformat(verified_time_str)
                            verification_expiry = getattr(settings, '2FA_VERIFICATION_EXPIRY_HOURS', 24)
                            if timezone.now() < verified_time + timedelta(hours=verification_expiry):
                                verification_valid = True
                        except (ValueError, TypeError):
                            verification_valid = False
                    
                    # Check for trusted session marker (for superusers/admins)
                    trusted_session = False
                    if request.user.is_superuser or profile.role == 'admin':
                        trusted_ips = request.session.get('trusted_admin_ips', [])
                        if ip in trusted_ips:
                            trusted_session = True
                            logger.debug(f"Admin/superuser {request.user.username} has already verified from IP {ip} this session")
                    
                    # Force verification if:
                    # 1. Not verified in this session OR
                    # 2. Not from a trusted device/IP OR
                    # 3. Session verification has expired
                    needs_verification = (
                        not verification_valid or 
                        (not trusted_session and profile.needs_2fa_verification(request_ip=ip))
                    )
                    
                    if needs_verification:
                        # If we're not already on the verification page
                        if current_path != verify_path:
                            # Store the original destination if it's not already in session
                            if '2fa_next' not in request.session:
                                request.session['2fa_next'] = request.path
                                
                            logger.info(f"Redirecting user {request.user.username} to 2FA verification")
                            return redirect(self.verify_2fa_url)
                
                # Second case: Approved user doesn't have 2FA enabled yet - redirect to setup
                elif not request.user.profile.ga_enabled:
                    # Check if current path is already an exempt path (like 2FA setup itself)
                    if not self._is_exempt_path(request.path) and request.path != self.setup_2fa_url:
                        # If not in a grace period (first login)
                        setup_exempt_until = request.session.get('2fa_setup_exempt_until')
                        if not setup_exempt_until or timezone.now() > datetime.fromisoformat(setup_exempt_until):
                            messages.warning(request, 'Dla bezpieczeństwa Twojego konta, musisz skonfigurować uwierzytelnianie dwuskładnikowe.')
                            
                            # Store the original destination
                            request.session['2fa_next'] = request.path
                            
                            logger.info(f"Redirecting user {request.user.username} to 2FA setup (required)")
                            return redirect(self.setup_2fa_url)
        
        return self.get_response(request)
    
    def _is_exempt_path(self, path):
        """Check if path is exempt from 2FA verification"""
        # First check against cached URL paths (exact matches)
        if path.rstrip('/') == self.verify_2fa_url.rstrip('/'):
            return True
        if path.rstrip('/') == self.setup_2fa_url.rstrip('/'):
            return True
        if path.rstrip('/') == self.setup_2fa_success_url.rstrip('/'):
            return True
        if path.rstrip('/') == self.recovery_code_url.rstrip('/'):
            return True
        if path.rstrip('/') == self.logout_url.rstrip('/'):
            return True
        
        # Then check against static paths (prefix matches)
        for exempt_path in self.static_exempt_paths:
            if path.startswith(exempt_path):
                return True
        
        return False