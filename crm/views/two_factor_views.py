import pyotp
import qrcode
import io
import base64
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.urls import reverse, NoReverseMatch

from ..forms import TOTPVerificationForm
from ..models import UserProfile
from ..decorators import admin_required

logger = logging.getLogger(__name__)

def get_client_ip(request):
    """Helper function to get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def safe_redirect(request, url_name, fallback_url_name='dashboard'):
    """Helper function to safely handle URL redirects with fallback"""
    try:
        return redirect(url_name)
    except NoReverseMatch:
        logger.warning(f"Failed to redirect to {url_name}, falling back to {fallback_url_name}")
        try:
            return redirect(fallback_url_name)
        except NoReverseMatch:
            logger.error(f"Fallback redirect to {fallback_url_name} also failed")
            # Emergency fallback to an absolute URL
            return redirect('/')

@login_required
def setup_2fa(request):
    """View for setting up 2FA for approved users"""
    user = request.user
    profile = getattr(user, 'profile', None)
    
    # Check if the user is already using 2FA
    if profile and profile.ga_enabled:
        messages.info(request, 'Uwierzytelnianie dwuskładnikowe jest już włączone dla Twojego konta.')
        return redirect('dashboard')  # Changed from 'profile' to 'dashboard'
    
    # Check if the user is approved (only approved users can set up 2FA)
    if not profile or not profile.is_approved:
        messages.error(request, 'Twoje konto musi być zatwierdzone przed włączeniem uwierzytelniania dwuskładnikowego.')
        return redirect('dashboard')
    
    # Check if setup is required (vs optional)
    setup_required = not request.session.get('2fa_setup_exempt_until', False)
    
    # Check if we're in the verification step
    if 'ga_secret_key' in request.session and request.method == 'POST':
        form = TOTPVerificationForm(request.POST)
        if form.is_valid():
            # Get the secret key from session
            secret_key = request.session['ga_secret_key']
            verification_code = form.cleaned_data['verification_code']
            
            # Create TOTP object with the secret
            totp = pyotp.TOTP(secret_key)
            
            # Verify the TOTP code
            if totp.verify(verification_code):
                # Code is valid, save the secret key and enable 2FA
                profile.ga_secret_key = secret_key
                profile.ga_enabled = True
                profile.ga_enabled_on = timezone.now()
                
                # Generate a recovery code if not already generated
                if not profile.ga_recovery_hash:
                    success, recovery_code = profile.generate_recovery_code()
                    if success:
                        # Store recovery code in session for display on success page
                        request.session['recovery_code'] = recovery_code
                    else:
                        messages.error(request, 'Nie udało się wygenerować kodu odzyskiwania.')
                        return redirect('setup_2fa')
                
                # Save the profile
                profile.save()
                
                # Clean up session
                if 'ga_secret_key' in request.session:
                    del request.session['ga_secret_key']
                if 'last_2fa_key_generation' in request.session:
                    del request.session['last_2fa_key_generation']
                
                messages.success(request, 'Uwierzytelnianie dwuskładnikowe zostało pomyślnie włączone!')
                return redirect('setup_2fa_success')
            else:
                messages.error(request, 'Niepoprawny kod weryfikacyjny. Spróbuj ponownie.')
        
        # If form is invalid or code doesn't match, re-generate QR code
        secret_key = request.session['ga_secret_key']
        qr_uri = pyotp.totp.TOTP(secret_key).provisioning_uri(
            name=user.email,
            issuer_name='System Helpdesk'
        )
        qr_code_img = generate_qr_code(qr_uri)
        
        context = {
            'form': form,
            'qr_code': qr_code_img,
            'secret_key': secret_key,
            'verification_step': True
        }
        return render(request, 'crm/2fa/setup.html', context)
    
    # Initial setup - check if we should generate a new secret key or reuse existing one
    current_time = timezone.now().timestamp()
    last_generation_time = request.session.get('last_2fa_key_generation', 0)
    time_elapsed = current_time - last_generation_time
    rate_limit_seconds = 60  # Limit to one generation per minute
    
    if 'ga_secret_key' in request.session and time_elapsed < rate_limit_seconds:
        # Reuse existing secret key if we're within the rate limit period
        secret_key = request.session['ga_secret_key']
        logger.info(f"Rate limiting 2FA setup for user {user.username}: reusing existing key")
        
        # Optionally add a message to inform the user
        time_remaining = int(rate_limit_seconds - time_elapsed)
        messages.info(
            request, 
            f'Ze względów bezpieczeństwa nowy kod może być wygenerowany po upływie {time_remaining} sekund. ' 
            'Prosimy korzystać z obecnie wyświetlonego kodu.'
        )
    else:
        # Generate new secret key if we're outside the rate limit period
        secret_key = pyotp.random_base32()
        request.session['ga_secret_key'] = secret_key
        request.session['last_2fa_key_generation'] = current_time
        logger.debug(f"Generated new 2FA setup code for user {user.username}")
    
    # Generate QR code
    qr_uri = pyotp.totp.TOTP(secret_key).provisioning_uri(
        name=user.email,
        issuer_name='System Helpdesk'
    )
    qr_code_img = generate_qr_code(qr_uri)
    
    context = {
        'qr_code': qr_code_img,
        'secret_key': secret_key,
        'form': TOTPVerificationForm(),
        'verification_step': False,
        'setup_required': setup_required,  # Add this to the context
        'rate_limited': time_elapsed < rate_limit_seconds,
        'time_remaining': int(rate_limit_seconds - time_elapsed) if time_elapsed < rate_limit_seconds else 0
    }
    
    return render(request, 'crm/2fa/setup.html', context)

@login_required
def setup_2fa_success(request):
    """Success page after setting up 2FA"""
    if 'recovery_code' not in request.session:
        return redirect('dashboard')  # Changed from 'profile' to 'dashboard'
    
    recovery_code = request.session['recovery_code']
    # Clear from session after displaying to user
    del request.session['recovery_code']
    
    return render(request, 'crm/2fa/success.html', {
        'recovery_code': recovery_code
    })

@login_required
@require_POST
def disable_2fa(request):
    """View for disabling 2FA"""
    user = request.user
    profile = getattr(user, 'profile', None)
    
    if not profile or not profile.ga_enabled:
        messages.info(request, 'Uwierzytelnianie dwuskładnikowe nie jest włączone dla Twojego konta.')
        return redirect('dashboard')  # Changed from 'profile' to 'dashboard'
    
    # Disable 2FA
    profile.ga_enabled = False
    profile.ga_secret_key = None
    profile.ga_recovery_hash = None
    profile.trusted_ip = None
    profile.trusted_until = None
    profile.device_fingerprint = None
    profile.save()
    
    messages.success(request, 'Uwierzytelnianie dwuskładnikowe zostało wyłączone.')
    return redirect('dashboard')  # Changed from 'profile' to 'dashboard'

@login_required
def verify_2fa(request):
    """View for verifying 2FA during login"""
    user = request.user
    profile = getattr(user, 'profile', None)
    
    # Debug info
    logger.debug(f"verify_2fa view accessed by {user.username} with path: {request.path}")
    logger.debug(f"Session contains 2fa_next: {request.session.get('2fa_next', 'None')}")
    
    # If user doesn't have 2FA enabled, they shouldn't be here
    if not profile or not profile.ga_enabled:
        logger.debug(f"User {user.username} doesn't have 2FA enabled, redirecting to setup")
        messages.warning(request, 'Uwierzytelnianie dwuskładnikowe nie jest włączone dla Twojego konta.')
        return redirect('setup_2fa')
    
    # NEVER redirect to any other page unless it's an intentional action (like form submission)
    # This prevents redirect loops
    
    # Handle verification code submission
    if request.method == 'POST':
        form = TOTPVerificationForm(request.POST)
        if form.is_valid():
            verification_code = form.cleaned_data['verification_code']
            
            # Create TOTP object with the user's secret
            totp = pyotp.TOTP(profile.ga_secret_key)
            
            # Verify the TOTP code
            if totp.verify(verification_code):
                # Code is valid, mark device as trusted if checkbox is checked
                trust_device = request.POST.get('trust_device') == 'on'
                
                # Update last authentication time
                profile.ga_last_authenticated = timezone.now()
                profile.save(update_fields=['ga_last_authenticated'])
                
                # IMPORTANT: Reset the redirect counter to prevent loop detection false positives
                if '2fa_redirect_count' in request.session:
                    del request.session['2fa_redirect_count']
                    
                # Add a marker in the session that 2FA verification is completed
                request.session['2fa_verified'] = True
                request.session['2fa_verified_time'] = timezone.now().isoformat()
                
                # Redirect to original destination
                next_url = request.session.pop('2fa_next', reverse('dashboard'))
                messages.success(request, 'Weryfikacja dwuskładnikowa pomyślna. Ważna przez następne 30 dni.')
                return redirect(next_url)
            else:
                messages.error(request, 'Niepoprawny kod weryfikacyjny. Spróbuj ponownie.')
                # Log failed verification attempt
                logger.warning(f"Failed 2FA verification attempt for user {user.username} from IP {get_client_ip(request)}")
    else:
        # For GET requests, always show the verification form
        # Check if user is in grace period
        if request.session.get('2fa_setup_exempt_until'):
            try:
                exempt_until = datetime.fromisoformat(request.session.get('2fa_setup_exempt_until'))
                if timezone.now() < exempt_until:
                    logger.debug(f"User {user.username} is in grace period, redirecting to dashboard")
                    return redirect('dashboard')
            except (ValueError, TypeError):
                pass
        
        form = TOTPVerificationForm()
    
    # Create the context with debug info
    context = {
        'form': form,
        'debug_info': {
            'path': request.path,
            'next': request.session.get('2fa_next', None),
            'redirect_count': request.session.get('2fa_redirect_count', 0),
        }
    }
    
    # Always render the template - never redirect!
    return render(request, 'crm/2fa/verify.html', context)

@login_required
def verify_2fa_status(request):
    """View to display 2FA status and provide access to recovery options"""
    user = request.user
    profile = getattr(user, 'profile', None)
    
    if not profile or not profile.ga_enabled:
        messages.warning(request, 'Uwierzytelnianie dwuskładnikowe nie jest włączone dla Twojego konta.')
        return redirect('setup_2fa')
    
    # Calculate days remaining for current authentication
    days_remaining = 0
    auth_valid = False
    
    if profile.ga_last_authenticated:
        time_since_auth = timezone.now() - profile.ga_last_authenticated
        auth_valid = time_since_auth.days < 30
        days_remaining = max(0, 30 - time_since_auth.days)
    
    context = {
        'auth_valid': auth_valid,
        'days_remaining': days_remaining,
        'last_auth': profile.ga_last_authenticated,
        'setup_date': profile.ga_enabled_on
    }
    
    return render(request, 'crm/2fa/status.html', context)

@login_required
def recovery_code(request):
    """View for using recovery code when 2FA device is lost"""
    user = request.user
    profile = getattr(user, 'profile', None)
    
    # If user doesn't have 2FA enabled, redirect to profile
    if not profile or not profile.ga_enabled:
        messages.info(request, 'Uwierzytelnianie dwuskładnikowe nie jest włączone dla Twojego konta.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        recovery_code = request.POST.get('recovery_code', '')
        
        if recovery_code:
            # Check if profile has the verify_recovery_code method
            if hasattr(profile, 'verify_recovery_code'):
                if profile.verify_recovery_code(recovery_code):
                    # Success - recovery code matches
                    messages.success(request, 'Kod odzyskiwania poprawny. Twoje konto zostało zabezpieczone, a uwierzytelnianie dwuskładnikowe zostało wyłączone.')
                    # The verify_recovery_code method should handle disabling 2FA
                    return redirect('dashboard')
                else:
                    messages.error(request, 'Niepoprawny kod odzyskiwania. Spróbuj ponownie lub skontaktuj się z administratorem.')
            else:
                # Fallback if method doesn't exist
                # Simple string comparison (less secure but functional)
                if profile.ga_recovery_hash and profile.ga_recovery_hash == recovery_code:
                    # Disable 2FA
                    profile.ga_enabled = False
                    profile.ga_secret_key = None
                    profile.ga_recovery_hash = None
                    profile.save()
                    messages.success(request, 'Kod odzyskiwania poprawny. Twoje konto zostało zabezpieczone, a uwierzytelnianie dwuskładnikowe zostało wyłączone.')
                    return redirect('dashboard')
                else:
                    messages.error(request, 'Niepoprawny kod odzyskiwania. Spróbuj ponownie lub skontaktuj się z administratorem.')
    
    return render(request, 'crm/2fa/recovery.html')

def generate_qr_code(data):
    """Generate QR code image"""
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Create an image from the QR Code instance
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for embedding in HTML
    buffer = io.BytesIO()
    img.save(buffer)
    image_data = buffer.getvalue()
    base64_encoded = base64.b64encode(image_data).decode('utf-8')
    
    return f"data:image/png;base64,{base64_encoded}"

@login_required
@admin_required
def debug_2fa(request):
    """Debug view for troubleshooting 2FA issues"""
    user = request.user
    
    # Get client IP
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    client_ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
    
    # Get user agent
    user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
    
    # Prepare profile data
    profile_data = {}
    if hasattr(user, 'profile'):
        profile = user.profile
        profile_data = {
            'ga_enabled': profile.ga_enabled,
            'ga_enabled_on': profile.ga_enabled_on,
            'ga_last_authenticated': profile.ga_last_authenticated,
            'ga_recovery_last_generated': profile.ga_recovery_last_generated,
            'trusted_ip': profile.trusted_ip,
            'trusted_until': profile.trusted_until,
        }
    
    # Collect relevant session data
    session_data = {}
    for key, value in request.session.items():
        if '2fa' in key:
            session_data[key] = value
    
    # Important URLs for debugging
    urls = {
        'verify_2fa': reverse('verify_2fa'),
        'setup_2fa': reverse('setup_2fa'),
        'recovery_code': reverse('recovery_code'),
        'dashboard': reverse('dashboard')
    }
    
    # Handle actions
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'reset_redirect_count':
            if '2fa_redirect_count' in request.session:
                del request.session['2fa_redirect_count']
            messages.success(request, 'Licznik przekierowań zresetowany.')
            
        elif action == 'mark_verified':
            from django.utils import timezone
            request.session['2fa_verified'] = True
            request.session['2fa_verified_time'] = timezone.now().isoformat()
            messages.success(request, '2FA oznaczone jako zweryfikowane w sesji.')
            
        elif action == 'add_trusted_ip':
            trusted_ips = request.session.get('trusted_admin_ips', [])
            if client_ip not in trusted_ips:
                trusted_ips.append(client_ip)
                request.session['trusted_admin_ips'] = trusted_ips
                messages.success(request, f'Adres IP {client_ip} dodany do zaufanych.')
            else:
                messages.info(request, f'Adres IP {client_ip} jest już w zaufanych.')
                
        elif action == 'disable_2fa':
            if hasattr(user, 'profile') and user.profile.ga_enabled:
                user.profile.ga_enabled = False
                user.profile.ga_secret_key = None
                user.profile.save(update_fields=['ga_enabled', 'ga_secret_key'])
                messages.success(request, '2FA zostało wyłączone dla Twojego konta.')
            else:
                messages.info(request, '2FA jest już wyłączone.')
    
    context = {
        'profile_data': profile_data,
        'session_data': session_data,
        'client_ip': client_ip,
        'user_agent': user_agent,
        'urls': urls,
    }
    
    return render(request, 'crm/2fa/debug.html', context)
