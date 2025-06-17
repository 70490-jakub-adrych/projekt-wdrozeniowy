from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
import logging

from ..models import TwoFactorAuth, TrustedDevice
from ..utils.two_factor import (
    generate_totp_secret, generate_totp_uri, generate_qr_code,
    verify_totp_code, get_or_create_2fa, requires_2fa_setup
)

logger = logging.getLogger(__name__)

@login_required
def setup_2fa(request):
    """View for setting up 2FA"""
    # Check if user is already set up
    try:
        if request.user.two_factor.ga_enabled:
            messages.info(request, "Uwierzytelnianie dwuskładnikowe jest już skonfigurowane.")
            return redirect('dashboard')
    except TwoFactorAuth.DoesNotExist:
        pass
    
    # Check if user is approved
    if not getattr(request.user.profile, 'is_approved', False):
        messages.error(request, "Twoje konto musi zostać zatwierdzone przed konfiguracją 2FA.")
        return redirect('dashboard')
    
    # Get or create 2FA record
    two_factor = get_or_create_2fa(request.user)
    
    if request.method == 'POST':
        verification_code = request.POST.get('verification_code')
        
        # Verify the code
        if verify_totp_code(two_factor.ga_secret, verification_code):
            # Enable 2FA
            two_factor.ga_enabled = True
            two_factor.ga_enabled_on = timezone.now()
            two_factor.ga_last_authenticated = timezone.now()
            two_factor.save()
            
            # Generate recovery code
            recovery_code = two_factor.generate_recovery_code()
            
            # Create trusted device
            TrustedDevice.create(request.user, request)
            
            # Success message
            messages.success(request, "Uwierzytelnianie dwuskładnikowe zostało włączone!")
            
            # Show recovery code
            return render(request, 'crm/two_factor/setup_success.html', {
                'recovery_code': recovery_code
            })
        else:
            messages.error(request, "Nieprawidłowy kod weryfikacyjny. Spróbuj ponownie.")
    
    # Generate TOTP secret if not exists
    if not two_factor.ga_secret:
        two_factor.ga_secret = generate_totp_secret()
        two_factor.save()
    
    # Generate QR code
    totp_uri = generate_totp_uri(request.user, two_factor.ga_secret)
    qr_code = generate_qr_code(totp_uri)
    
    return render(request, 'crm/two_factor/setup.html', {
        'qr_code': qr_code,
        'secret': two_factor.ga_secret,
    })

@login_required
def verify_2fa(request):
    """View for verifying 2FA token"""
    # Get 2FA record
    try:
        two_factor = request.user.two_factor
        if not two_factor.ga_enabled:
            return redirect('/two-factor/setup/')
    except TwoFactorAuth.DoesNotExist:
        return redirect('/two-factor/setup/')
    
    if request.method == 'POST':
        verification_code = request.POST.get('verification_code')
        recovery_mode = request.POST.get('recovery_mode') == 'true'
        
        if recovery_mode:
            # Handle recovery code
            if two_factor.verify_recovery_code(verification_code):
                # Update last authenticated time
                two_factor.ga_last_authenticated = timezone.now()
                two_factor.save()
                
                # Create trusted device
                TrustedDevice.create(request.user, request)
                
                # Recovery code was valid, now they need to set up 2FA again
                two_factor.ga_enabled = False
                two_factor.ga_secret = None
                two_factor.save()
                
                # Redirect to next URL or dashboard
                next_url = request.session.pop('next_url', 'dashboard')
                messages.success(request, "Kod odzyskiwania został przyjęty. Ze względów bezpieczeństwa musisz ponownie skonfigurować 2FA.")
                return redirect('/two-factor/setup/')
            else:
                messages.error(request, "Nieprawidłowy kod odzyskiwania. Spróbuj ponownie.")
        else:
            # Handle TOTP code
            if verify_totp_code(two_factor.ga_secret, verification_code):
                # Update last authenticated time
                two_factor.ga_last_authenticated = timezone.now()
                two_factor.save()
                
                # Create trusted device
                TrustedDevice.create(request.user, request)
                
                # Success message
                messages.success(request, "Weryfikacja 2FA zakończona pomyślnie.")
                
                # Redirect to next URL or dashboard
                next_url = request.session.pop('next_url', 'dashboard')
                return redirect(next_url)
            else:
                messages.error(request, "Nieprawidłowy kod weryfikacyjny. Spróbuj ponownie.")
    
    return render(request, 'crm/two_factor/verify.html')

@login_required
def recovery_2fa(request):
    """View for using recovery code"""
    return render(request, 'crm/two_factor/recovery.html')

@login_required
def regenerate_recovery_code(request):
    """View for regenerating recovery code"""
    # Check if user is authenticated
    if not request.user.is_authenticated:
        messages.error(request, "Musisz być zalogowany, aby wygenerować kod odzyskiwania.")
        return redirect('login')
    
    # Check if admin requesting for another user
    user_id = request.GET.get('user_id')
    user = request.user
    
    if user_id and (request.user.is_staff or request.user.is_superuser):
        # Admin can regenerate codes for other users
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            messages.error(request, "Użytkownik nie istnieje.")
            return redirect('admin:index')
    
    # Get 2FA record
    try:
        two_factor = user.two_factor
        if not two_factor.ga_enabled:
            messages.error(request, "Uwierzytelnianie dwuskładnikowe nie jest włączone.")
            return redirect('dashboard')
    except TwoFactorAuth.DoesNotExist:
        messages.error(request, "Uwierzytelnianie dwuskładnikowe nie jest włączone.")
        return redirect('dashboard')
    
    if not two_factor.can_regenerate_recovery_code():
        messages.error(request, "Możesz wygenerować nowy kod odzyskiwania tylko raz na 24 godziny.")
        if user_id and (request.user.is_staff or request.user.is_superuser):
            return redirect('admin:auth_user_change', object_id=user_id)
        return redirect('dashboard')
    
    # Generate new recovery code
    recovery_code = two_factor.generate_recovery_code()
    
    # If admin regenerated for another user
    if user_id and user != request.user and (request.user.is_staff or request.user.is_superuser):
        messages.success(request, f"Wygenerowano nowy kod odzyskiwania dla {user.username}: {recovery_code}")
        return redirect('admin:auth_user_change', object_id=user_id)
        
    return render(request, 'crm/two_factor/recovery_code.html', {
        'recovery_code': recovery_code
    })

@login_required
def disable_2fa(request):
    """View for disabling 2FA"""
    # Check if admin is disabling for another user
    user_id = request.GET.get('user_id')
    user = request.user
    
    if user_id and (request.user.is_staff or request.user.is_superuser):
        # Admin can disable 2FA for other users
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            messages.error(request, "Użytkownik nie istnieje.")
            return redirect('admin:index')
            
        try:
            two_factor = user.two_factor
            two_factor.ga_enabled = False
            two_factor.ga_secret = None
            two_factor.save()
            
            # Delete trusted devices
            TrustedDevice.objects.filter(user=user).delete()
            
            messages.success(request, f"Wyłączono uwierzytelnianie dwuskładnikowe dla {user.username}.")
            return redirect('admin:auth_user_change', object_id=user_id)
        except TwoFactorAuth.DoesNotExist:
            messages.error(request, "Uwierzytelnianie dwuskładnikowe nie jest włączone.")
            return redirect('admin:auth_user_change', object_id=user_id)
    
    # Regular users disabling their own 2FA
    try:
        two_factor = request.user.two_factor
        
        if request.method == 'POST':
            verification_code = request.POST.get('verification_code')
            
            # Verify the code
            if verify_totp_code(two_factor.ga_secret, verification_code):
                two_factor.ga_enabled = False
                two_factor.ga_secret = None
                two_factor.save()
                
                # Delete trusted devices
                TrustedDevice.objects.filter(user=request.user).delete()
                
                messages.success(request, "Uwierzytelnianie dwuskładnikowe zostało wyłączone.")
                return redirect('dashboard')
            else:
                messages.error(request, "Nieprawidłowy kod weryfikacyjny.")
    except TwoFactorAuth.DoesNotExist:
        messages.error(request, "Uwierzytelnianie dwuskładnikowe nie jest włączone.")
        return redirect('dashboard')
    
    return render(request, 'crm/two_factor/disable.html')
