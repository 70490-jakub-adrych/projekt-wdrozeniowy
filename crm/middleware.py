from django.shortcuts import redirect, render
from django.urls import reverse, resolve, Resolver404, NoReverseMatch
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
        try:
            self.verify_2fa_url = reverse('verify_2fa')
            # Get other exempt URLs once on initialization
            self.setup_2fa_url = reverse('setup_2fa')
            self.setup_2fa_success_url = reverse('setup_2fa_success')
            self.recovery_code_url = reverse('recovery_code')
            self.logout_url = reverse('logout')
            self.debug_2fa_url = reverse('debug_2fa')
            
            logger.debug(f"Initialized TwoFactorMiddleware with URLs: verify={self.verify_2fa_url}, "
                          f"setup={self.setup_2fa_url}, debug={self.debug_2fa_url}")
        except NoReverseMatch as e:
            logger.error(f"Failed to initialize TwoFactorMiddleware URLs: {str(e)}")
            # Default fallback URLs
            self.verify_2fa_url = '/2fa/verify/'
            self.setup_2fa_url = '/2fa/setup/'
            self.setup_2fa_success_url = '/2fa/setup/success/'
            self.recovery_code_url = '/2fa/recovery/'
            self.logout_url = '/logout/'
            self.debug_2fa_url = '/2fa/debug/'
        
        # Store exempt paths as a set for faster lookups
        self.static_exempt_paths = {
            '/static/',
            '/media/',
            '/admin/',
            '/verify-email/',
            '/register/',
            '/password_reset/',
            '/reset/',
            '/2fa/',  # Important: exempting all 2FA paths
        }
        
    def __call__(self, request):
        if request.user.is_authenticated:
            # DEBUG: Add detailed logging about the request path
            logger.debug(f"2FA Middleware processing path: {request.path}")
            
            # CRITICAL FIX: Check exact paths first before anything else
            if (request.path == self.verify_2fa_url or
                request.path.rstrip('/') == self.verify_2fa_url.rstrip('/') or
                request.path.startswith('/2fa/')):
                logger.debug(f"Exempt 2FA path detected: {request.path} - skipping middleware checks")
                return self.get_response(request)

            # Skip the entire middleware if bypass was already used in this session
            if request.session.get('2fa_bypass_used', False):
                logger.debug(f"2FA bypass active for {request.user.username}, skipping middleware")
                return self.get_response(request)
            
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
                logger.info(f"Redirecting {request.user.username} to 2FA debug page")
                return redirect(self.debug_2fa_url)
            
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
                # Store debug info in session
                request.session['debug_last_path'] = request.path
                request.session['debug_verify_2fa_url'] = self.verify_2fa_url
                
                # Force verification if auth is expired
                # Important: first check if we should completely skip verification
                if self._should_skip_verification(request):
                    logger.debug(f"Skipping verification for user {request.user.username} based on session state")
                    return self.get_response(request)
                
                # First case: User has 2FA enabled
                if request.user.profile.ga_enabled:
                    profile = request.user.profile
                    
                    # Log detailed information about the user's 2FA status
                    logger.debug(f"User {request.user.username} 2FA status: enabled={profile.ga_enabled}, " +
                                f"has_secret={bool(profile.ga_secret_key)}, " +
                                f"last_auth={profile.ga_last_authenticated}")
                    
                    # Skip verification check if we're on these specific pages
                    if request.path == reverse('verify_2fa_status') or self._is_exempt_path_improved(request.path):
                        logger.debug(f"Skipping 2FA check for exempt path: {request.path}")
                        return self.get_response(request)
                    
                    # Check if we're within the 30-day verification window
                    auth_valid = False
                    if profile.ga_last_authenticated:
                        time_since_auth = timezone.now() - profile.ga_last_authenticated
                        auth_valid = time_since_auth.days < 30  # Valid for 30 days
                        
                        logger.debug(f"2FA auth valid: {auth_valid}, days since auth: {time_since_auth.days}")
                        
                        # Store if auth is valid in session for views to use
                        request.session['2fa_auth_valid'] = auth_valid
                        request.session['2fa_days_remaining'] = max(0, 30 - time_since_auth.days)
                    
                    # If authentication is still valid, let the user through
                    if auth_valid:
                        return self.get_response(request)
                    
                    # Check redirect counter to prevent infinite loops
                    redirect_count = request.session.get('2fa_redirect_count', 0)
                    if redirect_count >= 3:  # Reduced from 5 to 3 for faster fallback
                        logger.warning(f"Too many 2FA redirects ({redirect_count}) for {request.user.username}, using emergency bypass")
                        request.session['2fa_redirect_count'] = 0  # Reset counter
                        
                        # EMERGENCY BYPASS - Set permanent bypass flag
                        request.session['2fa_bypass_used'] = True
                        
                        # Add a link to the debug page
                        debug_url = self.debug_2fa_url
                        messages.warning(
                            request, 
                            f"""
                            Wystąpił problem z uwierzytelnianiem dwuskładnikowym. 
                            <br><a href='{self.verify_2fa_url}'>Kliknij tutaj</a>, aby przejść bezpośrednio do weryfikacji.
                            <br><a href='{debug_url}'>Diagnozuj problem</a> (dla administratorów).
                            """
                        )
                        
                        # Also log system information to help diagnose the issue
                        logger.error(f"2FA bypass activated for {request.user.username}. " +
                                    f"Python: {sys.version}, OS: {os.name}, " +
                                    f"Platform: {sys.platform}")
                        
                        # Mark as verified temporarily to break out of loops
                        request.session['2fa_verified'] = True
                        request.session['2fa_verified_time'] = timezone.now().isoformat()
                        
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
                
                # Second case: Approved user doesn't have 2FA enabled yet - redirect to setup (UNSKIPPABLE)
                elif not request.user.profile.ga_enabled:
                    # Always check non-exempt paths first to prevent loops
                    if self._is_exempt_path_improved(request.path):
                        return self.get_response(request)
                    
                    # For approved users without 2FA, force setup (no grace period)
                    if request.path != reverse('setup_2fa'):
                        # Store the original destination for later redirect
                        request.session['2fa_next'] = request.path
                        
                        # Force redirect to 2FA setup
                        messages.warning(request, 'Musisz skonfigurować uwierzytelnianie dwuskładnikowe przed kontynuowaniem.')
                        logger.info(f"Redirecting user {request.user.username} to mandatory 2FA setup")
                        return redirect('setup_2fa')
        
        return self.get_response(request)
    
    def _should_skip_verification(self, request):
        """Determine if verification should be skipped completely"""
        user = request.user
        
        # Skip for grace period (first login)
        if request.session.get('2fa_setup_exempt_until'):
            try:
                exempt_until = datetime.fromisoformat(request.session.get('2fa_setup_exempt_until'))
                if timezone.now() < exempt_until:
                    logger.debug(f"User {user.username} is in 2FA setup grace period until {exempt_until}")
                    return True
            except (ValueError, TypeError):
                pass
        
        # Skip if already verified in this session
        if request.session.get('2fa_verified'):
            logger.debug(f"User {user.username} already verified 2FA in this session")
            return True
            
        return False

    def _is_exempt_path_improved(self, path):
        """Improved version of is_exempt_path with more robust checks"""
        # First check direct prefix matches - critical for 2FA paths
        if path.startswith('/2fa/'):
            logger.debug(f"Path {path} is exempt as it starts with /2fa/")
            return True
            
        # First check direct matches
        if path == self.verify_2fa_url or path == self.setup_2fa_url or path == self.setup_2fa_success_url or \
           path == self.recovery_code_url or path == self.logout_url or path == self.debug_2fa_url:
            return True
            
        # Check with trailing slashes normalized
        path_no_slash = path.rstrip('/')
        if path_no_slash == self.verify_2fa_url.rstrip('/') or \
           path_no_slash == self.setup_2fa_url.rstrip('/') or \
           path_no_slash == self.setup_2fa_success_url.rstrip('/') or \
           path_no_slash == self.recovery_code_url.rstrip('/') or \
           path_no_slash == self.logout_url.rstrip('/') or \
           path_no_slash == self.debug_2fa_url.rstrip('/'):
            return True
            
        # Then check static paths
        for exempt_path in self.static_exempt_paths:
            if path.startswith(exempt_path):
                return True
                
        # Fallback to URL resolver (but put this last as it's the slowest method)
        try:
            current_url_name = resolve(path).url_name
            exempt_names = ['verify_2fa', 'setup_2fa', 'setup_2fa_success', 'recovery_code', 'logout', 'debug_2fa']
            if current_url_name in exempt_names:
                return True
        except Resolver404:
            pass
        except Exception as e:
            logger.debug(f"Exception in URL resolver: {str(e)}")
            
        return False
    
    def _is_exempt_path(self, path):
        """Original is_exempt_path method - preserved for backward compatibility"""
        # First check against cached URL paths (exact matches)
        path_no_slash = path.rstrip('/')
        
        # Check exact matches with and without trailing slashes
        exempt_urls = [
            self.verify_2fa_url,
            self.setup_2fa_url,
            self.setup_2fa_success_url,
            self.recovery_code_url,
            self.logout_url,
            self.debug_2fa_url  # Add debug URL
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
    
    def _get_url_safely(self, url_name, default_path='/dashboard/'):
        """Get URL by name with fallback to prevent crashes"""
        try:
            return reverse(url_name)
        except NoReverseMatch:
            logger.error(f"Failed to reverse URL name: {url_name}, using fallback")
            return default_path