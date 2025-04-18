from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from ..forms import UserRegisterForm, UserProfileForm
from ..models import UserProfile, User
from .helpers import log_activity


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
                role = 'admin'
                is_approved = True  # Admin accounts are auto-approved
            else:
                group, _ = Group.objects.get_or_create(name='Klient')
                role = 'client'
                is_approved = False  # Clients need approval
            
            user.groups.add(group)
            
            # Uzupełnienie profilu
            profile = user.profile
            profile.role = role
            profile.phone = profile_form.cleaned_data.get('phone')
            profile.organization = profile_form.cleaned_data.get('organization')
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


def custom_login_view(request):
    """Niestandardowy widok logowania z zapisywaniem logów"""
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
        return HttpResponseForbidden("Brak uprawnień do tej strony.")
    
    # Get pending users based on role
    if user_role == 'admin':
        # Admins see all pending users
        pending_users = UserProfile.objects.filter(is_approved=False)
    else:
        # Agents see only users trying to join their organization
        org = request.user.profile.organization
        if not org:
            messages.warning(request, "Nie masz przypisanej organizacji.")
            return redirect('dashboard')
        pending_users = UserProfile.objects.filter(
            is_approved=False,
            organization=org
        )
    
    return render(request, 'crm/approvals/pending_approvals.html', {
        'pending_users': pending_users
    })


@login_required
def approve_user(request, user_id):
    """Zatwierdzanie konta użytkownika"""
    if request.user.profile.role not in ['admin', 'agent']:
        return HttpResponseForbidden("Brak uprawnień.")
    
    profile = get_object_or_404(UserProfile, user_id=user_id, is_approved=False)
    
    # Check if agent has permission to approve this user
    if request.user.profile.role == 'agent':
        if profile.organization != request.user.profile.organization:
            return HttpResponseForbidden("Możesz zatwierdzać tylko użytkowników z Twojej organizacji.")
    
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
        return HttpResponseForbidden("Brak uprawnień.")
    
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(UserProfile, user=user, is_approved=False)
    
    # Check if agent has permission to reject this user
    if request.user.profile.role == 'agent':
        if profile.organization != request.user.profile.organization:
            return HttpResponseForbidden("Możesz odrzucać tylko użytkowników z Twojej organizacji.")
    
    # Delete the user account
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f"Konto użytkownika {username} zostało odrzucone i usunięte.")
        return redirect('pending_approvals')
    
    return render(request, 'crm/approvals/reject_user.html', {'profile': profile})
