from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..forms import UserProfileEditForm
from ..decorators import two_factor_required, sensitive_view

@login_required
def user_profile_view(request):
    """View user profile details"""
    user = request.user
    context = {
        'user': user,
        'profile': user.profile if hasattr(user, 'profile') else None,
    }
    return render(request, 'crm/profile/profile.html', context)

@login_required
@sensitive_view  # Always require 2FA for profile changes
def user_profile_edit(request):
    """Edit user profile"""
    user = request.user
    profile = user.profile if hasattr(user, 'profile') else None
    
    if not profile:
        messages.error(request, 'Profil użytkownika nie istnieje.')
        return redirect('dashboard')
    
    # Just a placeholder - implement actual edit functionality as needed
    # form = UserProfileEditForm(request.POST or None, instance=profile)
    # if request.method == 'POST' and form.is_valid():
    #     form.save()
    #     messages.success(request, 'Profil został zaktualizowany.')
    #     return redirect('profile')
    
    context = {
        'user': user,
        'profile': profile,
        # 'form': form,
    }
    return render(request, 'crm/profile/profile_edit.html', context)
