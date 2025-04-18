from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.models import Group

from ..forms import UserRegisterForm, UserProfileForm
from .helpers import log_activity


def landing_page(request):
    """Widok strony głównej przed zalogowaniem"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'crm/landing_page.html')


def register(request):
    """Widok rejestracji nowego użytkownika"""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        
        if form.is_valid() and profile_form.is_valid():
            user = form.save()
            
            # Przypisanie do odpowiedniej grupy na podstawie roli
            if user.is_superuser:
                group, _ = Group.objects.get_or_create(name='Admin')
                role = 'admin'
            else:
                group, _ = Group.objects.get_or_create(name='Klient')
                role = 'client'
            
            user.groups.add(group)
            
            # Uzupełnienie profilu
            profile = user.profile
            profile.role = role
            profile.phone = profile_form.cleaned_data.get('phone')
            profile.organization = profile_form.cleaned_data.get('organization')
            profile.save()
            
            login(request, user)
            log_activity(request, 'login')
            messages.success(request, 'Konto zostało utworzone!')
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
        profile_form = UserProfileForm()
    
    return render(request, 'crm/register.html', {'form': form, 'profile_form': profile_form})


def custom_login_view(request):
    """Niestandardowy widok logowania z zapisywaniem logów"""
    # Always log login activity, since this view is only accessed after successful authentication
    log_activity(request, 'login')
    return redirect('dashboard')


def custom_logout_view(request):
    """Niestandardowy widok wylogowania z zapisywaniem logów"""
    if request.user.is_authenticated:
        log_activity(request, 'logout')
    logout(request)
    return redirect('landing_page')
