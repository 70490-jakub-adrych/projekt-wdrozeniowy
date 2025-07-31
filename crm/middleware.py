from django.shortcuts import redirect, render
from django.urls import reverse, resolve, Resolver404
from django.contrib import messages
from django.http import HttpResponse
import logging
from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone
import os
import sys
import traceback

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
        logger.debug(f"Initialized TwoFactorMiddleware with verify_2fa_url = {self.verify_2fa_url}")
        
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
            # Very detailed logging to help troubleshoot
            logger.debug(f"Processing request for {request.user.username} to path: {request.path}")
            
            # Add a session access check to identify potential session issues
            try:
                # Try to access and modify the session to verify it's working
                test_key = '2fa_session_test'
                request.session[test_key] = datetime.now().isoformat()
                del request.session[test_key]
            except Exception as e:
                logger.error(f"Session access error for {request.user.username}: {str(e)}")
                # Log the traceback
                logger.error(traceback.format_exc())
            
            # Check for the debug parameter
            if request.GET.get('2fa_debug') == '1':
                debug_url = reverse('debug_2fa')
                logger.info(f"Redirecting {request.user.username} to 2FA debug page")
                return redirect(debug_url)
            
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
                    
                    # Log detailed information about the user's 2FA status
                    logger.debug(f"User {request.user.username} 2FA status: enabled={profile.ga_enabled}, " +
                                f"has_secret={bool(profile.ga_secret_key)}, " +
                                f"last_auth={profile.ga_last_authenticated}")
                    
                    # Check URL path details to help diagnose routing issues
                    try:
                        from django.urls import get_resolver
                        resolver = get_resolver(None)
                        all_patterns = resolver.url_patterns
                        verify_patterns = [p for p in all_patterns if getattr(p, 'name', '') == 'verify_2fa']
                        logger.debug(f"URL resolver found verify_2fa patterns: {verify_patterns}")
                    except Exception as e:
                        logger.error(f"Error checking URL patterns: {str(e)}")
                    
                    # CRITICAL CHECK: Exact match for verify_2fa URL
                    logger.debug(f"Comparing paths: request.path={request.path}, verify_2fa_url={self.verify_2fa_url}")
                    
                    # If we're already on the verification page, proceed
                    if request.path == self.verify_2fa_url:
                        logger.debug(f"EXACT MATCH: Already on verify_2fa page - proceeding")
                        return self.get_response(request)
                    
                    # Try URL resolver to check if we're on the verify_2fa page
                    try:
                        current_url_name = resolve(request.path).url_name
                        logger.debug(f"Resolved URL name: {current_url_name}")
                        if current_url_name == 'verify_2fa':
                            logger.debug(f"RESOLVER MATCH: Already on verify_2fa page - proceeding")
                            return self.get_response(request)
                    except Resolver404:
                        logger.debug(f"URL resolver failed for path: {request.path}")
                    except Exception as e:
                        logger.debug(f"Exception in URL resolver: {str(e)}")
                    
                    # Normalize paths (remove trailing slashes) and compare
                    current_path = request.path.rstrip('/')
                    verify_path = self.verify_2fa_url.rstrip('/')
                    logger.debug(f"Normalized paths: current={current_path}, verify={verify_path}")
                    
                    if current_path == verify_path:
                        logger.debug(f"NORMALIZED MATCH: Already on verify_2fa page - proceeding")
                        return self.get_response(request)
                        
                    # Check if the path is exempt regardless
                    if self._is_exempt_path(request.path):
                        logger.debug(f"EXEMPT PATH: {request.path} is exempt from 2FA - proceeding")
                        return self.get_response(request)
                    
                    # Check redirect counter to prevent infinite loops
                    redirect_count = request.session.get('2fa_redirect_count', 0)
                    if redirect_count >= 3:  # Reduced from 5 to 3 for faster fallback
                        logger.warning(f"Too many 2FA redirects ({redirect_count}) for {request.user.username}, using emergency bypass")
                        request.session['2fa_redirect_count'] = 0  # Reset counter
                        
                        # EMERGENCY BYPASS - Add a link to the debug page
                        debug_url = reverse('debug_2fa')
                        messages.warning(
                            request, 
                            f"""
                            Wystąpił problem z uwierzytelnianiem dwuskładnikowym. 
                            <br><a href='{self.verify_2fa_url}'>Kliknij tutaj</a>, aby przejść bezpośrednio do weryfikacji.
                            <br><a href='{debug_url}'>Diagnozuj problem</a> (dla administratorów).
                            """
                        )
                        # Set a flag to indicate the bypass was used
                        request.session['2fa_bypass_used'] = True
                        # Also log system information to help diagnose the issue
                        logger.error(f"2FA bypass activated for {request.user.username}. " +
                                    f"Python: {sys.version}, OS: {os.name}, " +
                                    f"Platform: {sys.platform}")
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
                        # Store the original destination if it's not already in session
                        if '2fa_next' not in request.session:
                            request.session['2fa_next'] = request.path
                        
                        # Increment the redirect counter
                        request.session['2fa_redirect_count'] = redirect_count + 1
                        
                        logger.info(f"Redirecting user {request.user.username} to 2FA verification (count: {redirect_count + 1})")
                        return redirect(self.verify_2fa_url)
                
                # Second case: Approved user doesn't have 2FA enabled yet - redirect to setup
                elif not request.user.profile.ga_enabled:
                    # Check if we're already on the setup page
                    try:
                        current_url_name = resolve(request.path).url_name
                        if current_url_name == 'setup_2fa':
                            return self.get_response(request)
                    except:
                        pass
                        
                    # Direct path comparison
                    if request.path.rstrip('/') == self.setup_2fa_url.rstrip('/'):
                        return self.get_response(request)
                        
                    # Check if current path is already an exempt path
                    if self._is_exempt_path(request.path):
                        return self.get_response(request)
                        
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
        # First check against cached URL paths (exact matches)
        path_no_slash = path.rstrip('/')
        
        # Check exact matches with and without trailing slashes
        exempt_urls = [
            self.verify_2fa_url,
            self.setup_2fa_url,
            self.setup_2fa_success_url,
            self.recovery_code_url,
            self.logout_url
        ]
        
        for exempt_url in exempt_urls:
            exempt_no_slash = exempt_url.rstrip('/')
            if path == exempt_url or path_no_slash == exempt_no_slash:
                return True
        
        # Then check against static paths (prefix matches)
        for exempt_path in self.static_exempt_paths:
            if path.startswith(exempt_path):
                return True
        
        return False