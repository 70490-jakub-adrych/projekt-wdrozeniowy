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
from django.db import transaction, IntegrityError, connection
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
                        
                        # Log current state before any changes
                        logger.info(f"Registration attempt for username={username}, email={email}")
                        
                        # Check for existing users with this email or username
                        if User.objects.filter(email=email).exists():
                            logger.info(f"Email {email} already exists - rejecting")
                            form.add_error('email', 'Użytkownik z tym adresem email już istnieje.')
                            raise IntegrityError("User with this email already exists")
                            
                        if User.objects.filter(username=username).exists():
                            logger.info(f"Username {username} already exists - rejecting")
                            form.add_error('username', 'Użytkownik z tą nazwą użytkownika już istnieje.')
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
                        user = form.save(commit=False)
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
                            
                        # Handle organizations
                        if profile_form.cleaned_data.get('organizations'):
                            profile.organizations.set(profile_form.cleaned_data['organizations'])
                        
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
        
        # Continue with normal login if email is verified and approved
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
        messages.info(request, 'Wysłaliśmy nowy kod weryfikacyjny na Twój adres email.')
    
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
                    messages.success(request, 'Nowy kod weryfikacyjny został wysłany na Twój email.')
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
