from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from ..forms import UserRegisterForm, UserProfileForm, CustomAuthenticationForm
from ..models import UserProfile, User, EmailVerification, EmailNotificationSettings
from .helpers import log_activity
from .error_views import forbidden_access
from ..forms import EmailVerificationForm
from ..services.email_service import EmailNotificationService
import random


def landing_page(request):
    """Widok strony głównej przed zalogowaniem"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'crm/landing_page.html')


@login_required
def register(request):
    """Widok rejestracji użytkownika z weryfikacją email"""
    if request.method == 'POST':
        if 'verify_email' in request.POST:
            # Email verification step
            verification_form = EmailVerificationForm(request.POST)
            if verification_form.is_valid():
                code = verification_form.cleaned_data['verification_code']
                user_id = request.session.get('pending_user_id')
                
                if not user_id:
                    messages.error(request, 'Sesja wygasła. Rozpocznij rejestrację ponownie.')
                    return redirect('register')
                
                try:
                    user = User.objects.get(id=user_id)
                    verification = EmailVerification.objects.get(user=user)
                    
                    if verification.is_expired():
                        messages.error(request, 'Kod weryfikacyjny wygasł. Wygeneruj nowy kod.')
                        return render(request, 'crm/verify_email.html', {
                            'verification_form': verification_form,
                            'user': user,
                            'expired': True
                        })
                    
                    if verification.verification_code == code:
                        # Email verified successfully
                        verification.is_verified = True
                        verification.verified_at = timezone.now()
                        verification.save()
                        
                        # Activate user profile
                        profile = user.profile
                        profile.email_verified = True
                        profile.save()
                        
                        # Create default notification settings
                        EmailNotificationSettings.objects.get_or_create(user=user)
                        
                        # Clear session
                        del request.session['pending_user_id']
                        
                        messages.success(request, 'Email został zweryfikowany pomyślnie! Twoje konto oczekuje na zatwierdzenie przez administratora.')
                        return redirect('register_pending')
                    else:
                        messages.error(request, 'Nieprawidłowy kod weryfikacyjny.')
                        
                except (User.DoesNotExist, EmailVerification.DoesNotExist):
                    messages.error(request, 'Błąd weryfikacji. Rozpocznij rejestrację ponownie.')
                    return redirect('register')
            
            return render(request, 'crm/verify_email.html', {
                'verification_form': verification_form,
                'user': User.objects.get(id=request.session.get('pending_user_id'))
            })
        
        elif 'resend_code' in request.POST:
            # Resend verification code
            user_id = request.session.get('pending_user_id')
            if user_id:
                try:
                    user = User.objects.get(id=user_id)
                    verification = EmailVerification.objects.get(user=user)
                    new_code = verification.generate_new_code()
                    
                    if EmailNotificationService.send_verification_email(user, new_code):
                        messages.success(request, 'Nowy kod weryfikacyjny został wysłany na Twój email.')
                    else:
                        messages.error(request, 'Błąd podczas wysyłania emaila. Spróbuj ponownie.')
                except:
                    messages.error(request, 'Błąd podczas generowania nowego kodu.')
            
            return render(request, 'crm/verify_email.html', {
                'verification_form': EmailVerificationForm(),
                'user': User.objects.get(id=request.session.get('pending_user_id'))
            })
        
        else:
            # Initial registration step
            form = UserRegisterForm(request.POST)
            profile_form = UserProfileForm(request.POST)
            
            if form.is_valid() and profile_form.is_valid():
                # Create user (inactive until email verification)
                user = form.save(commit=False)
                user.is_active = False  # Deactivate until email verification
                user.save()
                
                # Create profile
                profile = profile_form.save(commit=False)
                profile.user = user
                profile.is_approved = False
                profile.email_verified = False
                profile.save()
                
                # Handle organizations
                if profile_form.cleaned_data.get('organizations'):
                    profile.organizations.set(profile_form.cleaned_data['organizations'])
                
                # Generate verification code
                verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
                EmailVerification.objects.create(
                    user=user,
                    verification_code=verification_code
                )
                
                # Send verification email
                if EmailNotificationService.send_verification_email(user, verification_code):
                    request.session['pending_user_id'] = user.id
                    messages.success(request, 'Konto zostało utworzone! Sprawdź swój email i wprowadź kod weryfikacyjny.')
                    return render(request, 'crm/verify_email.html', {
                        'verification_form': EmailVerificationForm(),
                        'user': user
                    })
                else:
                    # If email sending fails, delete the user and show error
                    user.delete()
                    messages.error(request, 'Błąd podczas wysyłania emaila weryfikacyjnego. Spróbuj ponownie.')
    else:
        form = UserRegisterForm()
        profile_form = UserProfileForm()
    
    return render(request, 'crm/register.html', {
        'form': form,
        'profile_form': profile_form
    })


def register_pending(request):
    """Widok informujący o oczekiwaniu na zatwierdzenie konta"""
    return render(request, 'crm/register_pending.html')


class CustomLoginView(LoginView):
    """Custom login view that uses our authentication form which logs failed attempts"""
    form_class = CustomAuthenticationForm
    template_name = 'crm/login.html'
    
    def form_valid(self, form):
        """When form is valid (login successful), redirect to custom_login_view"""
        login(self.request, form.get_user())
        return redirect('custom_login_success')

def custom_login_success(request):
    """Przekierowanie po zalogowaniu w zależności od roli użytkownika"""
    if request.user.profile.role == 'viewer':
        return redirect('ticket_display')
    return redirect('dashboard')

def custom_logout_view(request):
    """Niestandardowy widok wylogowania z zapisywaniem logów"""
    if request.user.is_authenticated:
        log_activity(request, 'logout')
    logout(request)
    return redirect('landing_page')


@login_required
def pending_approvals(request):
    """Widok dla adminów, superagentów i agentów do zarządzania oczekującymi zatwierdzeniami"""
    user_role = request.user.profile.role
    
    if user_role not in ['admin', 'superagent', 'agent']:
        return forbidden_access(request, "strony zatwierdzeń")
    
    # Get pending users based on role
    if user_role in ['admin', 'superagent']:
        # Admins and superagents see all pending users and locked accounts
        pending_users = UserProfile.objects.filter(is_approved=False)
        locked_users = UserProfile.objects.filter(is_locked=True)
    else:
        # Agents see only users trying to join their organizations and locked users from their orgs
        agent_orgs = request.user.profile.organizations.all()
        if not agent_orgs.exists():
            messages.warning(request, "Nie masz przypisanej organizacji.")
            return redirect('dashboard')
        pending_users = UserProfile.objects.filter(
            is_approved=False,
            organizations__in=agent_orgs
        ).distinct()
        locked_users = UserProfile.objects.filter(
            is_locked=True,
            organizations__in=agent_orgs
        ).distinct()
    
    return render(request, 'crm/approvals/pending_approvals.html', {
        'pending_users': pending_users,
        'locked_users': locked_users
    })


@login_required
def approve_user(request, user_id):
    """Zatwierdzanie użytkownika przez administratora, superagenta lub agenta"""
    user_role = request.user.profile.role
    
    if user_role not in ['admin', 'superagent', 'agent']:
        return forbidden_access(request, "funkcji zatwierdzania")
    
    profile = get_object_or_404(UserProfile, user_id=user_id, is_approved=False)
    
    # Check if agent has permission to approve this user (admins and superagents can approve anyone)
    if user_role == 'agent':
        agent_orgs = set(request.user.profile.organizations.values_list('id', flat=True))
        user_orgs = set(profile.organizations.values_list('id', flat=True))
        if not agent_orgs.intersection(user_orgs):
            return forbidden_access(request, "zatwierdzania tego użytkownika", user_id)
    
    if request.method == 'POST':
        profile.is_approved = True
        profile.save()
        
        # Log the approval
        log_activity(
            request,
            'preferences_updated',
            description=f"Zatwierdzono konto użytkownika {profile.user.username}"
        )
        
        messages.success(request, f"Użytkownik {profile.user.username} został zatwierdzony.")
        return redirect('pending_approvals')
    
    return render(request, 'crm/approvals/approve_user.html', {'profile': profile})


@login_required
def reject_user(request, user_id):
    """Odrzucenie użytkownika przez administratora, superagenta lub agenta"""
    user_role = request.user.profile.role
    
    if user_role not in ['admin', 'superagent', 'agent']:
        return forbidden_access(request, "funkcji odrzucania")
    
    profile = get_object_or_404(UserProfile, user_id=user_id, is_approved=False)
    
    # Check if agent has permission to reject this user (admins and superagents can reject anyone)
    if user_role == 'agent':
        agent_orgs = set(request.user.profile.organizations.values_list('id', flat=True))
        user_orgs = set(profile.organizations.values_list('id', flat=True))
        if not agent_orgs.intersection(user_orgs):
            return forbidden_access(request, "odrzucania tego użytkownika", user_id)
    
    if request.method == 'POST':
        username = profile.user.username
        
        # Log the rejection before deleting
        log_activity(
            request,
            'preferences_updated',
            description=f"Odrzucono konto użytkownika {username}"
        )
        
        # Delete the user (this will cascade delete the profile)
        profile.user.delete()
        
        messages.success(request, f"Użytkownik {username} został odrzucony i usunięty.")
        return redirect('pending_approvals')
    
    return render(request, 'crm/approvals/reject_user.html', {'profile': profile})


@login_required
def unlock_user(request, user_id):
    """Odblokowanie konta użytkownika"""
    if request.user.profile.role not in ['admin', 'superagent', 'agent']:
        return forbidden_access(request, "funkcji odblokowywania")
    
    profile = get_object_or_404(UserProfile, user_id=user_id, is_locked=True)
    
    # Check if agent has permission to unlock this user (admins and superagents can unlock anyone)
    if request.user.profile.role == 'agent':
        agent_orgs = set(request.user.profile.organizations.values_list('id', flat=True))
        user_orgs = set(profile.organizations.values_list('id', flat=True))
        if not agent_orgs.intersection(user_orgs):
            return forbidden_access(request, "odblokowywania tego użytkownika", user_id)
    
    # Unlock the user
    if request.method == 'POST':
        profile.unlock_account()
        
        # Log the unlock action
        log_activity(
            request,
            'account_unlocked',
            description=f"Odblokowano konto użytkownika {profile.user.username}"
        )
        
        messages.success(request, f"Konto użytkownika {profile.user.username} zostało odblokowane.")
        return redirect('pending_approvals')
    
    return render(request, 'crm/approvals/unlock_user.html', {'profile': profile})


@login_required
def custom_password_change_view(request):
    """Custom password change view with activity logging"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to keep user logged in
            
            # Log the password change
            log_activity(request, 'password_changed', description="Użytkownik zmienił hasło")
            
            messages.success(request, 'Twoje hasło zostało pomyślnie zmienione!')
            return redirect('dashboard')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'registration/password_change_form.html', {
        'form': form
    })
