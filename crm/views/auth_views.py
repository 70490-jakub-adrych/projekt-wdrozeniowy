from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone
from django.db import transaction, IntegrityError, connection
from django.db.models import Q
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.urls import reverse
from datetime import timedelta  # Add this import
from ..services.email_service import EmailNotificationService
import importlib

from ..forms import UserRegisterForm, UserProfileForm, CustomAuthenticationForm, GroupSelectionForm, PasswordChangeVerificationForm, EmailVerificationForm
from ..models import UserProfile, User, EmailVerification, EmailNotificationSettings, Organization
from .helpers import log_activity
from .error_views import forbidden_access
import random
import logging
from django.conf import settings

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
                        messages.success(request, 'Nowy kod weryfikacyjny został wysłany na Twój email. Poprzedni kod nie będzie już ważny.')
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
            registration_form = UserRegisterForm(request.POST)
            profile_form = UserProfileForm(request.POST)
            
            if registration_form.is_valid() and profile_form.is_valid():
                try:
                    with transaction.atomic():
                        # First check if there's any data that would cause conflicts
                        email = registration_form.cleaned_data.get('email')
                        username = registration_form.cleaned_data.get('username')
                        
                        # Log current state before any changes
                        logger.info(f"Registration attempt for username={username}, email={email}")
                        
                        # Check for existing users with this email or username
                        if User.objects.filter(email=email).exists():
                            logger.info(f"Email {email} already exists - rejecting")
                            registration_form.add_error('email', 'Użytkownik z tym adresem email już istnieje.')
                            raise IntegrityError("User with this email already exists")
                            
                        if User.objects.filter(username=username).exists():
                            logger.info(f"Username {username} already exists - rejecting")
                            registration_form.add_error('username', 'Użytkownik z tą nazwą użytkownika już istnieje.')
                            raise IntegrityError("User with this username already exists")
                        
                        # Create a savepoint before user creation
                        sid = transaction.savepoint()
                        
                        # Log highest user and profile ids before creation
                        with connection.cursor() as cursor:
                            cursor.execute("SELECT MAX(id) FROM auth_user")
                            max_user_id = cursor.fetchone()[0] or 0
                            cursor.execute("SELECT MAX(id) FROM crm_userprofile")
                            max_profile_id = cursor.fetchone()[0] or 0
                            logger.info(f"Before creation: max user_id={max_user_id}, max profile_id={max_profile_id}")
                        
                        # Create user (inactive until email verification)
                        user = registration_form.save(commit=False)
                        user.is_active = False  # Deactivate until email verification
                        user.save()
                        logger.info(f"Created user with ID={user.id}, username={user.username}, email={user.email}")
                        
                        # Get next ID that will be used for profile
                        with connection.cursor() as cursor:
                            cursor.execute("SELECT AUTO_INCREMENT FROM information_schema.TABLES WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'crm_userprofile'")
                            next_profile_id = cursor.fetchone()[0]
                            logger.info(f"Next profile ID will be: {next_profile_id}")
                            
                            # Check for orphaned profile with same user_id
                            cursor.execute(f"SELECT id FROM crm_userprofile WHERE user_id = {user.id}")
                            conflict_profiles = cursor.fetchall()
                            if conflict_profiles:
                                profile_ids = [row[0] for row in conflict_profiles]
                                logger.error(f"CONFLICT: Found profiles {profile_ids} with user_id={user.id}")
                                # Delete conflicting profiles
                                cursor.execute(f"DELETE FROM crm_userprofile WHERE user_id = {user.id}")
                                logger.info(f"Deleted {cursor.rowcount} conflicting profiles")
                        
                        try:
                            # Create profile with explicit user_id to avoid conflicts
                            profile = profile_form.save(commit=False)
                            profile.user = user
                            profile.is_approved = False
                            profile.email_verified = False
                            logger.info(f"Attempting to save profile for user_id={user.id}")
                            profile.save()
                            logger.info(f"Created profile with ID={profile.id} for user_id={user.id}")
                        except IntegrityError as e:
                            # If profile creation fails, roll back to savepoint
                            transaction.savepoint_rollback(sid)
                            logger.error(f"Profile creation failed: {str(e)}")
                            raise
                        
                        # Create a new savepoint before verification
                        sid2 = transaction.savepoint()
                        
                        # Generate verification code
                        verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
                        try:
                            verif = EmailVerification.objects.create(
                                user=user,
                                verification_code=verification_code
                            )
                            logger.info(f"Created verification record with ID={verif.id} for user_id={user.id}")
                        except IntegrityError as e:
                            # If verification creation fails, roll back to savepoint
                            transaction.savepoint_rollback(sid2)
                            logger.error(f"Verification creation failed: {str(e)}")
                            raise
                        
                        # Send verification email
                        if not EmailNotificationService.send_verification_email(user, verification_code):
                            # If email sending fails, roll back the transaction
                            logger.error(f"Failed to send verification email to {email}")
                            raise Exception("Failed to send verification email")
                        
                        # Store user ID in session
                        request.session['pending_user_id'] = user.id
                        logger.info(f"Registration successful for user_id={user.id}, stored in session")
                        
                        messages.success(request, 'Konto zostało utworzone! Sprawdź swój email i wprowadź kod weryfikacyjny.')
                        return render(request, 'crm/verify_email.html', {
                            'verification_form': EmailVerificationForm(),
                            'user': user
                        })
                
                except IntegrityError as e:
                    # Handle integrity errors
                    logger.error(f"Registration integrity error: {str(e)}")
                    
                    # Get detailed SQL information
                    with connection.cursor() as cursor:
                        # Check for any conflicting profiles
                        cursor.execute("SELECT id, user_id FROM crm_userprofile WHERE user_id IN (SELECT id FROM auth_user WHERE email=%s OR username=%s)", [email, username])
                        conflicts = cursor.fetchall()
                        if conflicts:
                            logger.error(f"Found conflicting profiles: {conflicts}")
                    
                    if "Duplicate entry" in str(e) and "user_id" in str(e):
                        # Extract the problematic ID
                        import re
                        match = re.search(r'Duplicate entry \'(\d+)\'', str(e))
                        conflict_id = match.group(1) if match else "unknown"
                        
                        # Check if user with this ID exists
                        user_exists = User.objects.filter(id=conflict_id).exists()
                        logger.critical(f"Conflict with user_id={conflict_id}, user exists: {user_exists}")
                        
                        messages.error(
                            request, 
                            f'Wystąpił problem z bazą danych podczas tworzenia konta (ID konfliktu: {conflict_id}). '
                            'Prosimy o kontakt z administratorem.'
                        )
                    elif not registration_form.errors and not profile_form.errors:
                        messages.error(request, 'Błąd podczas tworzenia konta. Spróbuj ponownie.')
                
                except Exception as e:
                    # Handle other errors
                    logger.error(f"Registration error: {str(e)}")
                    if "Failed to send verification email" in str(e):
                        messages.error(request, 'Błąd podczas wysyłania emaila weryfikacyjnego. Spróbuj ponownie.')
                    else:
                        messages.error(request, f'Wystąpił nieoczekiwany błąd. Spróbuj ponownie później.')
    else:
        registration_form = UserRegisterForm()
        profile_form = UserProfileForm()  # No organizations in registration form
    
    return render(request, 'crm/register.html', {
        'form': registration_form,
        'profile_form': profile_form
    })


def register_pending(request):
    """Widok informujący o oczekiwaniu na zatwierdzenie konta"""
    # Check if user is authenticated
    if request.user.is_authenticated:
        # If user is already approved, redirect to dashboard
        if hasattr(request.user, 'profile') and request.user.profile.is_approved:
            return redirect('dashboard')
    # User is either not authenticated or not approved, show the pending page    
    return render(request, 'crm/register_pending.html')


class CustomLoginView(LoginView):
    """Custom login view using our form and template"""
    form_class = CustomAuthenticationForm
    template_name = 'crm/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        """Check if user has verified email before proceeding"""
        user = form.get_user()
        logger.info(f"Login successful for user {user.username}, checking verification status")
        
        # If login was successful but email verification pending, redirect to verification
        if user and hasattr(user, 'profile'):
            # Check if profile has email_verified attribute (for backwards compatibility)
            email_verified = getattr(user.profile, 'email_verified', True)
            logger.debug(f"User {user.username} email_verified: {email_verified}")
            
            if not email_verified:
                # First we need to log the user in to allow access to verification page
                login(self.request, user)
                logger.info(f"User {user.username} logged in but redirected to verification")
                
                # Store user ID in session for verification (might be needed)
                self.request.session['pending_user_id'] = user.id
                
                # Try to find or create verification record
                try:
                    verification = EmailVerification.objects.get(user=user, is_verified=False)
                    
                    # If expired, generate new code
                    if verification.is_expired():
                        new_code = verification.generate_new_code()
                        EmailNotificationService.send_verification_email(user, new_code)
                        messages.info(self.request, 'Kod weryfikacyjny wygasł. Wysłaliśmy nowy kod na Twój adres email.')
                    else:
                        messages.info(self.request, 'Musisz zweryfikować swój adres email przed kontynuowaniem.')
                        
                except EmailVerification.DoesNotExist:
                    # Create new verification record
                    verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
                    verification = EmailVerification.objects.create(
                        user=user,
                        verification_code=verification_code
                    )
                    EmailNotificationService.send_verification_email(user, verification_code)
                    messages.info(self.request, 'Musisz zweryfikować swój adres email przed kontynuowaniem.')
                
                # Redirect to verification page
                return redirect('verify_email')
            elif not user.profile.is_approved:
                # User has verified email but is not approved yet
                # Log them in but redirect to pending approval page
                login(self.request, user)
                logger.info(f"User {user.username} logged in but redirected to pending approval")
                messages.info(self.request, 'Twoje konto oczekuje na zatwierdzenie przez administratora.')
                return redirect('register_pending')
            elif user.profile.ga_enabled:
                # User has 2FA enabled - log them in but check verification needs
                login(self.request, user)
                
                # Check if they need 2FA verification
                x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
                ip = x_forwarded_for.split(',')[0] if x_forwarded_for else self.request.META.get('REMOTE_ADDR')
                
                if user.profile.needs_2fa_verification(request_ip=ip):
                    logger.info(f"User {user.username} needs 2FA verification, redirecting")
                    # Store intended destination
                    next_param = self.request.GET.get('next', '')
                    if next_param:
                        self.request.session['2fa_next'] = next_param
                    # Redirect to 2FA verification
                    return redirect('verify_2fa')
            else:
                # User is verified and approved but doesn't have 2FA set up
                # Set a grace period (10 minutes) for first login after approval
                # This allows the user to see the interface briefly before being forced to set up 2FA
                login(self.request, user)
                
                exemption_end = timezone.now() + timedelta(minutes=10)
                self.request.session['2fa_setup_exempt_until'] = exemption_end.isoformat()
                logger.info(f"User {user.username} logged in with 2FA setup grace period until {exemption_end}")
                
                # Set a message informing the user about 2FA setup requirement
                messages.warning(
                    self.request,
                    'Dla bezpieczeństwa Twojego konta, skonfiguruj uwierzytelnianie dwuskładnikowe w ciągu 10 minut.'
                )
        
        # Continue with normal login
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
        pending_users = UserProfile.objects.filter(
            is_approved=False,
            email_verified=True  # Only show users who verified their email
        )
        pending_email_verification = UserProfile.objects.filter(
            is_approved=False,
            email_verified=False  # Users who haven't verified email yet
        )
        locked_users = UserProfile.objects.filter(is_locked=True)
    else:
        # Agents see only users trying to join their organizations
        agent_orgs = request.user.profile.organizations.all()
        if not agent_orgs.exists():
            messages.warning(request, "Nie masz przypisanej organizacji.")
            return redirect('dashboard')
        
        pending_users = UserProfile.objects.filter(
            is_approved=False,
            email_verified=True,  # Only show users who verified their email
            organizations__in=agent_orgs
        ).distinct()
        
        pending_email_verification = UserProfile.objects.filter(
            is_approved=False,
            email_verified=False,  # Users who haven't verified email yet
            organizations__in=agent_orgs
        ).distinct()
        
        locked_users = UserProfile.objects.filter(
            is_locked=True,
            organizations__in=agent_orgs
        ).distinct()
    
    return render(request, 'crm/approvals/pending_approvals.html', {
        'pending_users': pending_users,
        'pending_email_verification': pending_email_verification,
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
    
    # Determine which groups the approver can assign based on their role
    available_groups = []
    if user_role == 'admin':
        # Admin can assign any group
        available_groups = Group.objects.all()
    elif user_role == 'superagent':
        # Superagent can assign agent, client, viewer groups
        available_groups = Group.objects.filter(name__in=['Agent', 'Klient', 'Viewer'])
    elif user_role == 'agent':
        # Agent can only assign client and viewer groups
        available_groups = Group.objects.filter(name__in=['Klient', 'Viewer'])
    
    # Determine which organizations the approver can assign
    if user_role == 'admin' or user_role == 'superagent':
        available_organizations = Organization.objects.all()
    else:
        # Agents can only assign their own organizations
        available_organizations = request.user.profile.organizations.all()
    
    # Create form with available groups and organizations
    form = GroupSelectionForm(request.POST or None,
                              available_groups=available_groups,
                              available_organizations=available_organizations,
                              initial_organizations=profile.organizations.all())
    
    if request.method == 'POST' and form.is_valid():
        selected_group = form.cleaned_data['group']
        selected_organizations = form.cleaned_data['organizations']
        
        # Check if the selected group allows multiple organizations
        try:
            group_settings = selected_group.settings
            allow_multiple = group_settings.allow_multiple_organizations
        except GroupSettings.DoesNotExist:
            allow_multiple = selected_group.name in ['Admin', 'Superagent', 'Agent']
        
        # If the group doesn't allow multiple organizations, only keep the first one
        if not allow_multiple and len(selected_organizations) > 1:
            first_org = selected_organizations[0]
            selected_organizations = [first_org]
            messages.warning(request, f"Użytkownicy w grupie {selected_group.name} mogą być przypisani tylko do jednej organizacji. Przypisano tylko do {first_org.name}.")
        
        # Approve the user
        profile.is_approved = True
        profile.save()
        
        # Assign the selected group
        user = profile.user
        user.groups.clear()  # Remove any existing groups
        user.groups.add(selected_group)
        
        # Update the user's organizations
        profile.organizations.clear()
        for org in selected_organizations:
            profile.organizations.add(org)
        
        # Update the user's role based on the group
        if selected_group.name == 'Admin':
            profile.role = 'admin'
        elif selected_group.name == 'Superagent':
            profile.role = 'superagent'
        elif selected_group.name == 'Agent':
            profile.role = 'agent'
        elif selected_group.name == 'Viewer':
            profile.role = 'viewer'
        else:
            profile.role = 'client'
        profile.save()
        
        # Log the approval
        log_activity(
            request,
            'preferences_updated',
            description=f"Zatwierdzono konto użytkownika {profile.user.username} jako {profile.get_role_display()}"
        )
        
        messages.success(request, f"Użytkownik {profile.user.username} został zatwierdzony jako {profile.get_role_display()}.")
        return redirect('pending_approvals')
    
    return render(request, 'crm/approvals/approve_user.html', {
        'profile': profile,
        'form': form
    })


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
    """Custom password change view with verification and activity logging"""
    user = request.user
    verification_step = request.session.get('password_change_verification', False)
    verification_sent = request.session.get('verification_code_sent', False)
    
    # STEP 1: Show password change form and send verification code
    if not verification_step:
        if request.method == 'POST':
            form = PasswordChangeForm(user, request.POST)
            if form.is_valid():
                # Store form data in session for later use
                request.session['password_form_data'] = request.POST
                
                # Generate and store verification code
                verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
                request.session['password_verification_code'] = verification_code
                request.session['password_change_verification'] = True
                request.session['verification_code_sent'] = True
                
                # Send verification code via email
                success = EmailNotificationService.send_password_verification_email(user, verification_code)
                if not success:
                    messages.error(request, 'Błąd podczas wysyłania emaila z kodem weryfikacyjnym. Spróbuj ponownie.')
                    return redirect('password_change')
                
                messages.info(request, 'Wysłaliśmy kod weryfikacyjny na Twój adres email. Wprowadź go i kliknij zatwierdź, aby zmienić hasło.')
                return redirect('password_change')
        else:
            form = PasswordChangeForm(user)
        
        return render(request, 'emails/password_change_form.html', {
            'form': form,
            'verification_step': False
        })
    
    # STEP 2: Verify code and complete password change
    else:
        if request.method == 'POST':
            if 'verify_code' in request.POST:
                verification_form = PasswordChangeVerificationForm(request.POST)
                if verification_form.is_valid():
                    entered_code = verification_form.cleaned_data['verification_code']
                    stored_code = request.session.get('password_verification_code', None)
                    
                    if stored_code and entered_code == stored_code:
                        # Code is correct - retrieve stored form data and change password
                        stored_data = request.session.get('password_form_data', None)
                        if stored_data:
                            form = PasswordChangeForm(user, stored_data)
                            if form.is_valid():
                                logger.info(f"Password change form validated for user {user.username}")
                                
                                # Change password
                                form.save()
                                logger.info(f"Password successfully changed in database for user {user.username}")
                                
                                # Update session to prevent logout
                                update_session_auth_hash(request, user)
                                
                                # Clear all session data related to password change
                                for key in ['password_form_data', 'password_verification_code', 
                                          'password_change_verification', 'verification_code_sent']:
                                    if key in request.session:
                                        del request.session[key]
                                
                                # Log the activity
                                log_activity(
                                    request,
                                    'password_changed',
                                    description=f"Zmiana hasła użytkownika {user.username}"
                                )
                                
                                # Send notification about password change with enhanced logging
                                logger.info(f"SENDING PASSWORD CHANGED EMAIL: Starting notification process for {user.username}")
                                try:
                                    # Generate password reset URL for security
                                    site_url = getattr(settings, 'SITE_URL', 'https://betulait.usermd.net')
                                    password_reset_url = f"{site_url}/password_reset/"
                                    
                                    # Directly call email service with explicit success check
                                    success = EmailNotificationService.send_password_changed_notification(user)
                                    
                                    if success:
                                        logger.info(f"✅ Password changed notification SUCCESSFULLY sent to {user.email}")
                                    else:
                                        logger.error(f"❌ Failed to send password changed notification to {user.email}")
                                except Exception as e:
                                    logger.error(f"❌ CRITICAL ERROR sending password change notification: {str(e)}", exc_info=True)
                                
                                messages.success(request, "Twoje hasło zostało pomyślnie zmienione.")
                                return redirect('dashboard')
                            else:
                                # Form validation error
                                messages.error(request, "Wystąpił błąd z zapisanymi danymi. Spróbuj ponownie.")
                                return redirect('password_change')
                    else:
                        messages.error(request, 'Nieprawidłowy kod weryfikacyjny. Spróbuj ponownie.')
            
            elif 'resend_code' in request.POST:
                # Regenerate and resend verification code
                verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
                request.session['password_verification_code'] = verification_code
                
                # Send verification code via email
                success = EmailNotificationService.send_password_verification_email(user, verification_code)
                if success:
                    messages.success(request, 'Nowy kod weryfikacyjny został wysłany na Twój email. Poprzedni kod nie będzie już ważny.')
                else:
                    messages.error(request, 'Błąd podczas wysyłania emaila. Spróbuj ponownie.')
            
            elif 'cancel' in request.POST:
                # Cancel password change
                for key in ['password_form_data', 'password_verification_code', 'password_change_verification', 'verification_code_sent']:
                    if key in request.session:
                        del request.session[key]
                messages.info(request, 'Zmiana hasła została anulowana.')
                return redirect('dashboard')
        
        verification_form = PasswordChangeVerificationForm()
        return render(request, 'emails/password_change_verification.html', {
            'verification_form': verification_form,
            'verification_step': True,
            'user': user
        })


def verify_email(request):
    """Standalone view for email verification"""
    logger.debug(f"verify_email view accessed by user: {request.user.username if request.user.is_authenticated else 'anonymous'}")
    
    # If user is not logged in and there's no pending user ID in the session, redirect to login
    if not request.user.is_authenticated and 'pending_user_id' not in request.session:
        logger.warning("User not authenticated and no pending_user_id in session")
        messages.error(request, 'Musisz się zalogować, aby zweryfikować email.')
        return redirect('login')
    
    # Get the user - either the authenticated user or from the session
    if request.user.is_authenticated:
        user = request.user
        logger.debug(f"Using authenticated user: {user.username}")
        
        # If user is already verified, redirect appropriately
        if user.profile.email_verified:
            logger.info(f"User {user.username} already has verified email")
            messages.info(request, 'Twój email jest już zweryfikowany.')
            
            if user.profile.is_approved:
                logger.debug(f"User {user.username} is approved, redirecting to dashboard")
                return redirect('dashboard')
            else:
                logger.debug(f"User {user.username} is not approved, redirecting to pending page")
                messages.info(request, 'Twoje konto oczekuje na zatwierdzenie przez administratora.')
                return redirect('register_pending')
    else:
        # Get user from session (for users who just registered)
        user_id = request.session.get('pending_user_id')
        logger.debug(f"Using user from session: {user_id}")
        try:
            user = User.objects.get(id=user_id)
            logger.debug(f"Found user from session: {user.username}")
        except User.DoesNotExist:
            logger.warning(f"User ID {user_id} from session not found")
            messages.error(request, 'Sesja wygasła. Zaloguj się, aby zweryfikować email.')
            return redirect('login')
    
    # Create or retrieve the verification code
    try:
        verification = EmailVerification.objects.get(user=user)
        logger.debug(f"Found existing verification for user {user.username}")
    except EmailVerification.DoesNotExist:
        logger.info(f"No verification record found for {user.username}, creating new one")
        # Create a new verification code
        verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        verification = EmailVerification.objects.create(
            user=user,
            verification_code=verification_code
        )
        # Send the verification email
        EmailNotificationService.send_verification_email(user, verification_code)
        messages.info(request, 'Wysłaliśmy nowy kod weryfikacyjny na Twój adres email. Poprzedni kod nie będzie już ważny.')
        logger.info(f"New verification code sent to {user.email} for user {user.username}")
    
    # Process verification
    if request.method == 'POST':
        if 'verify_email' in request.POST:
            # Process verification code submission
            verification_form = EmailVerificationForm(request.POST)
            logger.debug(f"Email verification form submission for user {user.username}")
            
            if verification_form.is_valid():
                code = verification_form.cleaned_data['verification_code']
                
                try:
                    verification = EmailVerification.objects.get(user=user)
                    
                    if verification.is_expired():
                        logger.warning(f"Verification code expired for user {user.username}")
                        messages.error(request, 'Kod weryfikacyjny wygasł. Wygeneruj nowy kod.')
                        return render(request, 'crm/verify_email.html', {
                            'verification_form': verification_form,
                            'user': user,
                            'expired': True
                        })
                    
                    if verification.verification_code == code:
                        # Email verified successfully
                        logger.info(f"Email verification successful for user {user.username}")
                        verification.is_verified = True
                        verification.verified_at = timezone.now()
                        verification.save()
                        
                        # Update user profile
                        profile = user.profile
                        profile.email_verified = True
                        profile.save()
                        
                        # Activate the user account if not already
                        if not user.is_active:
                            user.is_active = True
                            user.save()
                        
                        # Create default notification settings if needed
                        EmailNotificationSettings.objects.get_or_create(user=user)
                        
                        # Clear session if exists
                        if 'pending_user_id' in request.session:
                            del request.session['pending_user_id']
                        
                        messages.success(request, 'Email został zweryfikowany pomyślnie!')
                        
                        # Redirect to appropriate page
                        if profile.is_approved:
                            # If user is already approved, redirect to dashboard
                            next_url = request.session.get('next_after_verification', 'dashboard')
                            if 'next_after_verification' in request.session:
                                del request.session['next_after_verification']
                            return redirect(next_url)
                        else:
                            # If user is not approved, redirect to pending approval page
                            messages.info(request, 'Twoje konto oczekuje na zatwierdzenie przez administratora.')
                            return redirect('register_pending')
                    else:
                        logger.warning(f"Invalid verification code for user {user.username}")
                        messages.error(request, 'Nieprawidłowy kod weryfikacyjny.')
                        
                except EmailVerification.DoesNotExist:
                    logger.error(f"Verification record not found for user {user.username}")
                    messages.error(request, 'Błąd weryfikacji. Spróbuj ponownie później.')
                    return redirect('login')
                
            return render(request, 'crm/verify_email.html', {
                'verification_form': verification_form,
                'user': user
            })
            
        elif 'resend_code' in request.POST:
            # Resend verification code
            logger.info(f"Resending verification code for user {user.username}")
            try:
                verification = EmailVerification.objects.get(user=user)
                new_code = verification.generate_new_code()
                
                if EmailNotificationService.send_verification_email(user, new_code):
                    logger.info(f"New verification code sent to {user.email}")
                    messages.success(request, 'Nowy kod weryfikacyjny został wysłany na Twój email. Poprzedni kod nie będzie już ważny.')
                else:
                    logger.error(f"Failed to send verification email to {user.email}")
                    messages.error(request, 'Błąd podczas wysyłania emaila. Spróbuj ponownie.')
            except EmailVerification.DoesNotExist:
                # Create new verification if it doesn't exist
                logger.warning(f"Verification record not found for user {user.username} when resending code")
                verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
                verification = EmailVerification.objects.create(
                    user=user,
                    verification_code=verification_code
                )
                if EmailNotificationService.send_verification_email(user, verification_code):
                    messages.success(request, 'Kod weryfikacyjny został wysłany na Twój email.')
                else:
                    messages.error(request, 'Błąd podczas wysyłania emaila. Spróbuj ponownie.')
            
            return render(request, 'crm/verify_email.html', {
                'verification_form': EmailVerificationForm(),
                'user': user
            })
    
    # GET request or other cases
    return render(request, 'crm/verify_email.html', {
        'verification_form': EmailVerificationForm(),
        'user': user
    })


class HTMLEmailPasswordResetView(PasswordResetView):
    """Custom password reset view that sends HTML emails"""
    
    def form_valid(self, form):
        """Override to track which user is resetting their password"""
        # Get the user's email from the form
        email = form.cleaned_data.get('email', '')
        logger.info(f"Password reset requested for email: {email}")
        
        # Try to find the user by email
        try:
            user = User.objects.get(email=email)
            # Store user ID in session for later tracking
            self.request.session['reset_user_email'] = email
            logger.info(f"Stored user email {email} in session for reset tracking")
        except User.DoesNotExist:
            logger.warning(f"Password reset requested for non-existent email: {email}")
            # We'll still process normally to avoid user enumeration
            pass
        
        return super().form_valid(form)
    
    def send_mail(self, subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name=None):
        """
        Override Django's send_mail to use our EmailNotificationService and add tracking
        """
        user = context.get('user')
        if not user:
            logger.error("User not found in context for password reset email")
            return
            
        # Store user ID in global tracker
        email = user.email
        cache_module = importlib.import_module('django.core.cache')
        cache = cache_module.caches['default']
        cache_key = f"reset_user_{user.pk}"
        cache.set(cache_key, user.pk, timeout=86400)  # Store for 24 hours
        logger.info(f"Stored user ID {user.pk} in cache with key {cache_key}")
            
        try:
            subject = loader.render_to_string(subject_template_name, context)
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
            
            # Make sure we have an HTML template path
            if not html_email_template_name:
                html_email_template_name = 'emails/password_reset_email.html'
                logger.warning(f"No HTML template specified, using default: {html_email_template_name}")
                
            # Use our service to send both HTML and plain text versions
            success = EmailNotificationService.send_password_reset_email(
                user=user,
                subject=subject, 
                email_template_name=email_template_name,
                html_email_template_name=html_email_template_name,
                context=context
            )
            
            if success:
                logger.info(f"Password reset email successfully sent to {user.email}")
            else:
                logger.error(f"Failed to send password reset email to {user.email}")
                
        except Exception as e:
            logger.exception(f"Error in send_mail for password reset: {str(e)}")


class EnhancedPasswordResetConfirmView(PasswordResetConfirmView):
    """Enhanced password reset confirmation view with user tracking"""
    
    def dispatch(self, *args, **kwargs):
        """Override to capture user info early in the process"""
        # Extract user ID from uidb64 parameter and store in session
        uidb64 = kwargs.get('uidb64')
        if uidb64:
            from django.utils.http import urlsafe_base64_decode
            from django.utils.encoding import force_str
            
            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user_id = int(uid)
                # Store in session for later retrieval in success view
                self.request.session['_password_reset_user_id'] = user_id
                logger.info(f"Stored reset user ID {user_id} in session from uidb64")
            except (ValueError, TypeError, OverflowError) as e:
                logger.error(f"Failed to decode uidb64 {uidb64}: {str(e)}")
        
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        """Override to track user when form is submitted"""
        user = form.user
        if user:
            # Store user ID for later use in completion handler
            self.request.session['_password_reset_user_id'] = user.pk
            logger.info(f"Stored user ID {user.pk} in session after password reset form submission")
            
            # Also store in cache as backup
            cache_module = importlib.import_module('django.core.cache')
            cache = cache_module.caches['default']
            cache_key = f"reset_complete_user_{user.pk}"
            cache.set(cache_key, user.pk, timeout=3600)  # Store for 1 hour
        
        # Call parent's form_valid
        response = super().form_valid(form)
        
        # Add user_id to the success URL as query parameter for extra reliability
        if user:
            if '?' in self.success_url:
                self.success_url += f"&user_id={user.pk}"
            else:
                self.success_url += f"?user_id={user.pk}"
        
        return response


def custom_password_reset_complete(request):
    """Custom view for password reset completion that sends notification"""
    # Try multiple methods to determine which user just reset their password
    user = None
    user_id = None
    methods_tried = []
    
    # Method 1: Try logged in user
    if request.user.is_authenticated:
        user = request.user
        methods_tried.append("authenticated_user")
        logger.info(f"Found reset user via authenticated session: {user.username}")
    
    # Method 2: Try to get from session (Django's built-in)
    if not user:
        user_id = request.session.get('_password_reset_user_id')
        if user_id:
            methods_tried.append("session_storage")
            logger.info(f"Found reset user ID {user_id} in session")
    
    # Method 3: Try to get from query parameters
    if not user_id:
        url_user_id = request.GET.get('user_id')
        if url_user_id:
            try:
                user_id = int(url_user_id)
                methods_tried.append("url_parameter")
                logger.info(f"Found reset user ID {user_id} in URL parameter")
            except (ValueError, TypeError):
                logger.error(f"Invalid user ID in URL parameter: {url_user_id}")
    
    # Method 4: Check the cache for recent password resets
    if not user and not user_id:
        email = request.session.get('reset_user_email')
        if email:
            methods_tried.append("session_email")
            logger.info(f"Found reset user email in session: {email}")
            try:
                user = User.objects.get(email=email)
                logger.info(f"Retrieved user {user.username} using email {email}")
            except User.DoesNotExist:
                logger.error(f"No user found with email {email}")
    
    # Method 5: Try cache as last resort
    if not user and not user_id:
        # Try to find a recent reset in the cache
        cache_module = importlib.import_module('django.core.cache')
        cache = cache_module.caches['default']
        
        # Get all active users and check if any have a recent reset
        active_users = User.objects.filter(is_active=True)
        for active_user in active_users[:100]:  # Limit to first 100 users to prevent performance issues
            cache_key = f"reset_complete_user_{active_user.pk}"
            cached_id = cache.get(cache_key)
            if cached_id:
                user_id = cached_id
                methods_tried.append("cache_lookup")
                logger.info(f"Found reset user ID {user_id} in cache with key {cache_key}")
                break
    
    # If we have a user_id but not a user object, get the user
    if not user and user_id:
        try:
            user = User.objects.get(pk=user_id)
            logger.info(f"Retrieved user {user.username} from ID {user_id} for reset notification")
            
            # Clean up session
            if '_password_reset_user_id' in request.session:
                del request.session['_password_reset_user_id']
        except User.DoesNotExist:
            logger.error(f"User ID {user_id} not found in database")
    
    # Clean up session variable
    if 'reset_user_email' in request.session:
        email = request.session.get('reset_user_email')
        del request.session['reset_user_email']
        logger.info(f"Cleaned up reset_user_email from session: {email}")
    
    # Send notification if we found the user
    if user:
        logger.info(f"SENDING PASSWORD CHANGED EMAIL: Starting notification after reset for {user.username} (found via {', '.join(methods_tried)})")
        try:
            # Generate password reset URL for security
            site_url = getattr(settings, 'SITE_URL', 'https://betulait.usermd.net')
            password_reset_url = f"{site_url}{reverse('password_reset')}"
            
            # Create a context with support information
            context = {
                'user': user,
                'timestamp': timezone.now(),
                'password_reset_url': password_reset_url,
                'site_name': 'System Helpdesk',
                'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@example.com'),
                'ip_address': request.META.get('REMOTE_ADDR', 'unknown'),
                'browser': request.META.get('HTTP_USER_AGENT', 'unknown'),
            }
            
            # Direct call with explicit success check
            success = EmailNotificationService.send_password_changed_notification(user, context)
            
            if success:
                logger.info(f"✅ Password changed notification SUCCESSFULLY sent after reset to {user.email}")
            else:
                logger.error(f"❌ Failed to send password changed notification after reset to {user.email}")
        except Exception as e:
            logger.error(f"❌ CRITICAL ERROR sending password reset notification: {str(e)}", exc_info=True)
    else:
        logger.warning(f"❓ Could not determine user for password reset notification - NO EMAIL SENT. Methods tried: {', '.join(methods_tried)}")
    
    # Always show the success template
    return render(request, 'emails/password_reset_complete.html')
