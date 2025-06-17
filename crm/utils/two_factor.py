import pyotp
import qrcode
import io
import base64
from django.utils import timezone
from django.conf import settings
from crm.models import TwoFactorAuth, TrustedDevice

def generate_totp_secret():
    """Generate a new TOTP secret"""
    return pyotp.random_base32()

def generate_totp_uri(user, secret):
    """Generate the URI for the QR code"""
    site_name = getattr(settings, 'SITE_NAME', 'Helpdesk')
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(user.email, issuer_name=site_name)

def generate_qr_code(uri):
    """Generate a QR code image for the TOTP URI"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer)
    return base64.b64encode(buffer.getvalue()).decode()

def verify_totp_code(secret, code):
    """Verify a TOTP code against the secret"""
    if not secret or not code:
        return False
        
    totp = pyotp.TOTP(secret)
    return totp.verify(code.strip())

def get_or_create_2fa(user):
    """Get or create a 2FA record for a user"""
    two_factor, created = TwoFactorAuth.objects.get_or_create(user=user)
    return two_factor

def requires_2fa_setup(user):
    """Check if user needs to set up 2FA based on approval status"""
    # Check if user is approved
    if not getattr(user.profile, 'is_approved', False):
        return False
    
    # Check if user is a superagent
    is_superagent = getattr(user.profile, 'role', '') == 'superagent'
    
    # If user is approved or a superagent, check if 2FA is already enabled
    if is_superagent or user.profile.is_approved:
        try:
            return not user.two_factor.ga_enabled
        except TwoFactorAuth.DoesNotExist:
            return True
            
    return False

def is_trusted_device(request):
    """Check if the current device is trusted for 2FA"""
    if not request.user.is_authenticated:
        return False
    
    try:
        # Generate the current device ID
        device_id = TrustedDevice.generate_device_id(request)
        client_ip = TrustedDevice.get_client_ip(request)
        
        # Look for a matching trusted device
        device = TrustedDevice.objects.get(
            user=request.user,
            device_identifier=device_id
        )
        
        # Check if the device is still valid and from same IP
        if device.is_valid() and device.ip_address == client_ip:
            device.last_used = timezone.now()
            device.save(update_fields=['last_used'])
            return True
            
    except TrustedDevice.DoesNotExist:
        return False
    
    return False

def is_admin_from_known_ip(request):
    """Check if an admin user is accessing from a known IP"""
    if not request.user.is_authenticated:
        return False
    
    # Check if user is admin or superuser
    is_admin = request.user.is_staff or request.user.is_superuser
    if not is_admin:
        return False
    
    # Get client IP
    client_ip = TrustedDevice.get_client_ip(request)
    
    # Check if this IP has been used by this admin in this session
    admin_ips = request.session.get('admin_ips', [])
    if client_ip in admin_ips:
        return True
    
    # If not found, but user is admin, add this IP to the session
    admin_ips.append(client_ip)
    request.session['admin_ips'] = admin_ips
    request.session.modified = True
    
    # Still require 2FA for first login from this IP
    return False

def get_recovery_url(user_id):
    """Generate URL for recovery code regeneration"""
    return f"/two-factor/regenerate-recovery-code/?user_id={user_id}"
