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
from django.urls import reverse

from ..forms import TOTPVerificationForm
from ..models import UserProfile

logger = logging.getLogger(__name__)

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
    
    # Initial setup - generate new secret key
    secret_key = pyotp.random_base32()
    request.session['ga_secret_key'] = secret_key
    
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
        'setup_required': setup_required  # Add this to the context
    }
    
    return render(request, 'crm/2fa/setup.html', context)

@login_required
def setup_2fa_success(request):
    """Success page after setting up 2FA"""
    if 'recovery_code' not in request.session:
        return redirect('profile')
    
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
    
    # Check if requires fresh verification even for trusted devices
    require_fresh = request.session.get('require_fresh_2fa', False)
    
    # If user doesn't need 2FA verification, redirect to dashboard
    if not profile or not profile.ga_enabled or (not require_fresh and not profile.needs_2fa_verification(get_client_ip(request))):
        return redirect('dashboard')
    
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
                
                if trust_device:
                    # Mark device as trusted
                    profile.set_device_trusted(
                        request_ip=get_client_ip(request),
                        fingerprint=request.META.get('HTTP_USER_AGENT', '')
                    )
                else:
                    # Just update the last authentication time
                    profile.ga_last_authenticated = timezone.now()
                    profile.save(update_fields=['ga_last_authenticated'])
                
                # If user is admin/superuser, add IP to trusted session IPs
                if user.is_superuser or profile.role == 'admin':
                    # Get current list of trusted IPs for this session
                    trusted_ips = request.session.get('trusted_admin_ips', [])
                    ip = get_client_ip(request)
                    if ip not in trusted_ips:
                        trusted_ips.append(ip)
                        request.session['trusted_admin_ips'] = trusted_ips
                        logger.debug(f"Added IP {ip} to trusted admin IPs for this session")
                
                # Clear require_fresh flag if set
                if 'require_fresh_2fa' in request.session:
                    del request.session['require_fresh_2fa']
                
                # Redirect to original destination
                next_url = request.session.pop('2fa_next', reverse('dashboard'))
                messages.success(request, 'Weryfikacja dwuskładnikowa pomyślna.')
                return redirect(next_url)
            else:
                messages.error(request, 'Niepoprawny kod weryfikacyjny. Spróbuj ponownie.')
                # Log failed verification attempt
                logger.warning(f"Failed 2FA verification attempt for user {user.username} from IP {get_client_ip(request)}")
    else:
        form = TOTPVerificationForm()
    
    # Get the require_fresh flag from session to inform the template
    require_fresh = request.session.get('require_fresh_2fa', False)
    
    return render(request, 'crm/2fa/verify.html', {
        'form': form,
        'require_fresh': require_fresh
    })

@login_required
def recovery_code(request):
    """View for using recovery code when 2FA device is lost"""
    user = request.user
    profile = getattr(user, 'profile', None)
    
    # If user doesn't have 2FA enabled, redirect to profile
    if not profile or not profile.ga_enabled:
        messages.info(request, 'Uwierzytelnianie dwuskładnikowe nie jest włączone dla Twojego konta.')
        return redirect('profile')
    
    if request.method == 'POST':
        recovery_code = request.POST.get('recovery_code', '')
        
        if recovery_code:
            # Verify recovery code
            if profile.verify_recovery_code(recovery_code):
                messages.success(request, 'Kod odzyskiwania poprawny. Twoje konto zostało zabezpieczone, a uwierzytelnianie dwuskładnikowe zostało wyłączone.')
                return redirect('profile')
            else:
                messages.error(request, 'Niepoprawny kod odzyskiwania. Spróbuj ponownie lub skontaktuj się z administratorem.')
    
    return render(request, 'crm/2fa/recovery.html')

def generate_qr_code(data):
    """Generate QR code image as base64 data URL"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save image to bytes buffer
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Convert to base64
    img_str = base64.b64encode(buffer.getvalue()).decode('ascii')
    return f"data:image/png;base64,{img_str}"

def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
