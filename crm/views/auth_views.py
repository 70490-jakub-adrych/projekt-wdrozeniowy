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
from ..models import UserProfile, User
from .helpers import log_activity
from .error_views import forbidden_access


def landing_page(request):
    """Widok strony głównej przed zalogowaniem"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'crm/landing_page.html')


def register(request):
    """Widok rejestracji nowego użytkownika z wymaganiem zatwierdzenia"""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        
        if form.is_valid() and profile_form.is_valid():
            user = form.save()
            
            # Przypisanie do odpowiedniej grupy na podstawie roli
            if user.is_superuser:
                group, _ = Group.objects.get_or_create(name='Admin')
                is_approved = True  # Admin accounts are auto-approved
            else:
                group, _ = Group.objects.get_or_create(name='Klient')
                is_approved = False  # Clients need approval
            
            user.groups.add(group)
            
            # Profile will be automatically updated with correct role via signal
            # Just update the other fields
            profile = user.profile
            profile.phone = profile_form.cleaned_data.get('phone')
            
            # Update for ManyToManyField - fix: get the organizations (plural) field
            selected_organizations = profile_form.cleaned_data.get('organizations')
            if selected_organizations:
                # Add all selected organizations to the user's profile
                for org in selected_organizations:
                    profile.organizations.add(org)
                    
            profile.is_approved = is_approved
            profile.save()
            
            # Redirect to pending approval page instead of login
            if is_approved:
                login(request, user)
                log_activity(request, 'login')
                messages.success(request, 'Konto zostało utworzone!')
                return redirect('dashboard')
            else:
                messages.info(request, 'Twoje konto zostało utworzone i czeka na zatwierdzenie przez administratora lub agenta.')
                return redirect('register_pending')
    else:
        form = UserRegisterForm()
        profile_form = UserProfileForm()
    
    return render(request, 'crm/register.html', {'form': form, 'profile_form': profile_form})


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
    """Handle successful login - existing function renamed for clarity"""
    # Check if user is approved before proceeding
    if not hasattr(request.user, 'profile') or not request.user.profile.is_approved:
        messages.error(request, 'Twoje konto oczekuje na zatwierdzenie przez administratora lub agenta.')
        logout(request)
        return redirect('login')
        
    # Otherwise log login activity and proceed
    log_activity(request, 'login')
    return redirect('dashboard')

def custom_logout_view(request):
    """Niestandardowy widok wylogowania z zapisywaniem logów"""
    if request.user.is_authenticated:
        log_activity(request, 'logout')
    logout(request)
    return redirect('landing_page')


@login_required
def pending_approvals(request):
    """Widok dla adminów i agentów do zarządzania oczekującymi zatwierdzeniami"""
    user_role = request.user.profile.role
    
    if user_role not in ['admin', 'agent']:
        return forbidden_access(request, "strony zatwierdzeń")
    
    # Get pending users based on role
    if user_role == 'admin':
        # Admins see all pending users
        pending_users = UserProfile.objects.filter(is_approved=False)
    else:
        # Agents see only users trying to join their organizations
        agent_orgs = request.user.profile.organizations.all()
        if not agent_orgs.exists():
            messages.warning(request, "Nie masz przypisanej organizacji.")
            return redirect('dashboard')
        pending_users = UserProfile.objects.filter(
            is_approved=False,
            organizations__in=agent_orgs
        ).distinct()
    
    return render(request, 'crm/approvals/pending_approvals.html', {
        'pending_users': pending_users
    })


@login_required
def approve_user(request, user_id):
    """Zatwierdzanie konta użytkownika"""
    if request.user.profile.role not in ['admin', 'agent']:
        return forbidden_access(request, "funkcji zatwierdzania")
    
    profile = get_object_or_404(UserProfile, user_id=user_id, is_approved=False)
    
    # Check if agent has permission to approve this user
    if request.user.profile.role == 'agent':
        agent_orgs = set(request.user.profile.organizations.values_list('id', flat=True))
        user_orgs = set(profile.organizations.values_list('id', flat=True))
        if not agent_orgs.intersection(user_orgs):
            return forbidden_access(request, "zatwierdzania tego użytkownika", user_id)
    
    # Approve the user
    if request.method == 'POST':
        profile.is_approved = True
        profile.save()
        messages.success(request, f"Konto użytkownika {profile.user.username} zostało zatwierdzone.")
        return redirect('pending_approvals')
    
    return render(request, 'crm/approvals/approve_user.html', {'profile': profile})


@login_required
def reject_user(request, user_id):
    """Odrzucanie konta użytkownika"""
    if request.user.profile.role not in ['admin', 'agent']:
        return forbidden_access(request, "funkcji odrzucania")
    
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(UserProfile, user=user, is_approved=False)
    
    # Check if agent has permission to reject this user
    if request.user.profile.role == 'agent':
        agent_orgs = set(request.user.profile.organizations.values_list('id', flat=True))
        user_orgs = set(profile.organizations.values_list('id', flat=True))
        if not agent_orgs.intersection(user_orgs):
            return forbidden_access(request, "odrzucania tego użytkownika", user_id)
    
    # Delete the user account
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f"Konto użytkownika {username} zostało odrzucone i usunięte.")
        return redirect('pending_approvals')
    
    return render(request, 'crm/approvals/reject_user.html', {'profile': profile})


@login_required
def custom_password_change_view(request):
    """Widok zmiany hasła użytkownika"""
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            # Update the session to prevent the user from being logged out
            update_session_auth_hash(request, form.user)
            log_activity(request, 'password_changed')
            messages.success(request, 'Twoje hasło zostało zmienione pomyślnie!')
            return redirect('dashboard')
    else:
        form = PasswordChangeForm(user=request.user)
    
    return render(request, 'crm/auth/password_change.html', {'form': form})
