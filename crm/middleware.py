from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
import re
import logging
from django.conf import settings
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


class ImpersonationMiddleware:
    """
    Middleware that adds effective user and organizations to request for impersonation functionality
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Add effective_user attribute to request
        if hasattr(request, 'user') and request.user.is_authenticated:
            if request.user.profile.role == 'admin':
                impersonated_user_id = request.session.get('impersonated_user_id')
                if impersonated_user_id:
                    try:
                        request.effective_user = User.objects.get(id=impersonated_user_id)
                        
                        # Also add effective organizations
                        impersonated_org_ids = request.session.get('impersonated_organizations')
                        if impersonated_org_ids is not None:  # Could be empty list
                            from .models import Organization
                            request.effective_organizations = Organization.objects.filter(id__in=impersonated_org_ids)
                        else:
                            # Use the impersonated user's real organizations
                            request.effective_organizations = request.effective_user.profile.organizations.all()
                            
                    except User.DoesNotExist:
                        # Clean up invalid session
                        keys_to_delete = ['impersonated_user_id', 'original_user_id', 'impersonated_organizations']
                        for key in keys_to_delete:
                            if key in request.session:
                                del request.session[key]
                        request.effective_user = request.user
                        request.effective_organizations = request.user.profile.organizations.all()
                else:
                    request.effective_user = request.user
                    request.effective_organizations = request.user.profile.organizations.all()
            else:
                request.effective_user = request.user
                request.effective_organizations = request.user.profile.organizations.all()
        else:
            request.effective_user = None
            request.effective_organizations = None
            
        return self.get_response(request)


class ViewerRestrictMiddleware:
    """
    Blokuje użytkownikom z rolą 'viewer' dostęp do wszystkich stron poza ticket_display, get_tickets_update i logout.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Use effective_user if available (for impersonation), otherwise use regular user
        effective_user = getattr(request, 'effective_user', request.user) if hasattr(request, 'user') else None
        
        if effective_user and effective_user.is_authenticated and hasattr(effective_user, 'profile'):
            if effective_user.profile.role == 'viewer':
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
            '/2fa/recovery/',  # Add exemption for recovery code path
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
        
    def __call__(self, request):
        if request.user.is_authenticated:
            # Check if user's group is exempt from 2FA
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
            if hasattr(request.user, 'profile') and request.user.profile.is_approved and not group_exempt:
                # First case: User has 2FA enabled and needs verification
                if request.user.profile.ga_enabled:
                    profile = request.user.profile
                    
                    # Get the IP address
                    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                    if x_forwarded_for:
                        ip = x_forwarded_for.split(',')[0]
                    else:
                        ip = request.META.get('REMOTE_ADDR')
                    
                    # Check if verification is needed
                    if profile.needs_2fa_verification(request_ip=ip):
                        # Check if current path is already the 2FA verification path or other exempt path
                        if not self._is_exempt_path(request.path):
                            # Store the original destination if it's not already in session
                            if '2fa_next' not in request.session:
                                request.session['2fa_next'] = request.path
                                
                            logger.info(f"Redirecting user {request.user.username} to 2FA verification")
                            return redirect('verify_2fa')
                
                # Second case: Approved user doesn't have 2FA enabled yet - redirect to setup
                elif not request.user.profile.ga_enabled:
                    # Check if current path is already an exempt path (like 2FA setup itself)
                    if not self._is_exempt_path(request.path) and request.path != reverse('setup_2fa'):
                        # If not in a grace period (first login)
                        setup_exempt_until = request.session.get('2fa_setup_exempt_until')
                        if not setup_exempt_until or timezone.now() > datetime.fromisoformat(setup_exempt_until):
                            messages.warning(request, 'Dla bezpieczeństwa Twojego konta, musisz skonfigurować uwierzytelnianie dwuskładnikowe.')
                            
                            # Store the original destination
                            request.session['2fa_next'] = request.path
                            
                            logger.info(f"Redirecting user {request.user.username} to 2FA setup (required)")
                            return redirect('setup_2fa')
        
        return self.get_response(request)
    
    def _is_exempt_path(self, path):
        """Check if path is exempt from 2FA verification"""
        exempt_paths = [
            reverse('verify_2fa'),
            reverse('setup_2fa'),
            reverse('setup_2fa_success'),
            reverse('recovery_code'),
            reverse('logout'),
            '/static/',
            '/media/',
            '/admin/',
            '/verify-email/',  # Don't interfere with email verification
            '/register/',       # Don't interfere with registration flow
            '/password_reset/', # Don't interfere with password resets
            '/reset/',          # Don't interfere with password reset confirmations
        ]
        return any(path.startswith(exempt) for exempt in exempt_paths)