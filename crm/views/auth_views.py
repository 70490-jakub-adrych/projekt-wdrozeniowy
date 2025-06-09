from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone
from django.db import transaction, IntegrityError
from django.db.models import Q

from ..forms import UserRegisterForm, UserProfileForm, CustomAuthenticationForm
from ..models import UserProfile, User, EmailVerification, EmailNotificationSettings
from .helpers import log_activity
from .error_views import forbidden_access
from ..forms import EmailVerificationForm
from ..services.email_service import EmailNotificationService
import random
import logging

# Configure logger
logger = logging.getLogger(__name__)


def landing_page(request):
    """Widok strony głównej przed zalogowaniem"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'crm/landing_page.html')


def register(request):
    """Widok rejestracji użytkownika z weryfikacją email"""
    # If user is already logged in, redirect to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
        
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
                        
                        # Activate user profile for email verification but set is_approved=False
                        profile = user.profile
                        profile.email_verified = True
                        profile.is_approved = False  # Ensure this is explicitly set to False
                        profile.save()
                        
                        # Activate the user account now that email is verified
                        # This allows login but they'll see "pending approval" until an admin approves
                        user.is_active = True  # Activate the user after email verification
                        user.save()
                        
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
                try:
                    with transaction.atomic():
                        # First check if there's any data that would cause conflicts
                        email = form.cleaned_data.get('email')
                        username = form.cleaned_data.get('username')
                        
                        # Extra check for orphaned verification records
                        existing_verifications = EmailVerification.objects.filter(
                            user__email=email
                        )
                        if existing_verifications.exists():
                            # Clean up orphaned verification records
                            for verification in existing_verifications:
                                verification.delete()
                                logger.warning(f"Deleted orphaned verification record for email: {email}")
                        
                        # Check for existing users with this email or username
                        if User.objects.filter(email=email).exists():
                            form.add_error('email', 'Użytkownik z tym adresem email już istnieje.')
                            raise IntegrityError("User with this email already exists")
                            
                        if User.objects.filter(username=username).exists():
                            form.add_error('username', 'Użytkownik z tą nazwą użytkownika już istnieje.')
                            raise IntegrityError("User with this username already exists")
                        
                        # Check for orphaned profiles and clean them up
                        orphaned_profiles = UserProfile.objects.filter(user_id__isnull=False).exclude(
                            user_id__in=User.objects.values_list('id', flat=True)
                        )
                        if orphaned_profiles.exists():
                            logger.warning(f"Found {orphaned_profiles.count()} orphaned profiles, cleaning up")
                            orphaned_profiles.delete()
                        
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
                        if not EmailNotificationService.send_verification_email(user, verification_code):
                            # If email sending fails, roll back the transaction
                            raise Exception("Failed to send verification email")
                        
                        # Store user ID in session
                        request.session['pending_user_id'] = user.id
                        
                        messages.success(request, 'Konto zostało utworzone! Sprawdź swój email i wprowadź kod weryfikacyjny.')
                        return render(request, 'crm/verify_email.html', {
                            'verification_form': EmailVerificationForm(),
                            'user': user
                        })
                
                except IntegrityError as e:
                    # Handle integrity errors
                    logger.error(f"Registration integrity error: {str(e)}")
                    if "Duplicate entry" in str(e) and "user_id" in str(e):
                        messages.error(request, 'Błąd systemu: konflikt z istniejącym użytkownikiem. Proszę spróbować ponownie.')
                    elif not form.errors and not profile_form.errors:
                        messages.error(request, 'Błąd podczas tworzenia konta. Spróbuj ponownie.')
                
                except Exception as e:
                    # Handle other errors
                    logger.error(f"Registration error: {str(e)}")
                    if "Failed to send verification email" in str(e):
                        messages.error(request, 'Błąd podczas wysyłania emaila weryfikacyjnego. Spróbuj ponownie.')
                    else:
                        messages.error(request, f'Wystąpił nieoczekiwany błąd. Spróbuj ponownie później.')
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
    """Custom login view using our form and template"""
    form_class = CustomAuthenticationForm
    template_name = 'crm/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        """Check if user has verified email before proceeding"""
        user = form.get_user()
        
        # If login was successful but email verification pending, redirect to verification
        if user and hasattr(user, 'profile') and not user.profile.email_verified:
            try:
                verification = EmailVerification.objects.get(user=user, is_verified=False)
                
                # If verification exists and is not too old, redirect to verification page
                if not verification.is_expired():
                    # Store user ID in session for verification
                    self.request.session['pending_user_id'] = user.id
                    messages.info(self.request, 'Musisz zweryfikować swój adres email przed kontynuowaniem.')
                    
                    # Don't actually log the user in yet
                    return redirect('verify_email')
                else:
                    # If expired, generate new code
                    new_code = verification.generate_new_code()
                    EmailNotificationService.send_verification_email(user, new_code)
                    
                    # Store user ID in session for verification
                    self.request.session['pending_user_id'] = user.id
                    messages.info(self.request, 'Kod weryfikacyjny wygasł. Wysłaliśmy nowy kod na Twój adres email.')
                    
                    # Don't actually log the user in yet
                    return redirect('verify_email')
            except EmailVerification.DoesNotExist:
                # If for some reason verification doesn't exist, create one
                verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
                EmailVerification.objects.create(
                    user=user,
                    verification_code=verification_code
                )
                EmailNotificationService.send_verification_email(user, verification_code)
                
                # Store user ID in session for verification
                self.request.session['pending_user_id'] = user.id
                messages.info(self.request, 'Musisz zweryfikować swój adres email przed kontynuowaniem.')
                
                # Don't actually log the user in yet
                return redirect('verify_email')
        
        # Continue with normal login if email is verified
        return super().form_valid(form)

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
