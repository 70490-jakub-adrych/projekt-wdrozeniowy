from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from ..models import UserProfile
from .helpers import log_activity
import logging

logger = logging.getLogger(__name__)


@login_required
def switch_user_perspective(request):
    """Allows admin to switch to a different user's perspective for testing"""
    if request.user.profile.role != 'admin':
        return HttpResponseForbidden("Dostęp tylko dla administratorów")
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        organization_ids = request.POST.getlist('organization_ids')
        
        if user_id == 'reset':
            # Reset to original admin view
            if 'impersonated_user_id' in request.session:
                original_user_id = request.session.get('original_user_id', request.user.id)
                impersonated_user_id = request.session['impersonated_user_id']
                
                # Log activity
                log_activity(
                    request, 
                    'user_impersonation_stop', 
                    None,
                    f'Zakończono symulację użytkownika ID: {impersonated_user_id}'
                )
                
                # Clear all impersonation session data
                keys_to_delete = ['impersonated_user_id', 'original_user_id', 'impersonated_organizations']
                for key in keys_to_delete:
                    if key in request.session:
                        del request.session[key]
                
                messages.success(request, 'Powrócono do normalnego widoku administratora')
            
            return redirect('dashboard')
        
        if user_id:
            try:
                target_user = User.objects.get(id=user_id)
                
                # Store original user info
                request.session['original_user_id'] = request.user.id
                request.session['impersonated_user_id'] = target_user.id
                
                # Handle organization simulation
                if organization_ids:
                    from ..models import Organization
                    # Validate that organizations exist
                    valid_orgs = Organization.objects.filter(id__in=organization_ids)
                    if valid_orgs.exists():
                        request.session['impersonated_organizations'] = list(valid_orgs.values_list('id', flat=True))
                        org_names = ', '.join(valid_orgs.values_list('name', flat=True))
                    else:
                        request.session['impersonated_organizations'] = []
                        org_names = "brak"
                else:
                    request.session['impersonated_organizations'] = []
                    org_names = "brak"
                
                # Log activity
                log_activity(
                    request, 
                    'user_impersonation_start', 
                    None,
                    f'Rozpoczęto symulację użytkownika: {target_user.username} (ID: {target_user.id}) z organizacjami: {org_names}'
                )
                
                messages.success(
                    request, 
                    f'Przełączono na perspektywę użytkownika: {target_user.get_full_name() or target_user.username} ({target_user.profile.get_role_display()}) z organizacjami: {org_names}'
                )
                
                return redirect('dashboard')
                
            except User.DoesNotExist:
                messages.error(request, 'Nie znaleziono wybranego użytkownika')
    
    # Get all users for the dropdown
    users = User.objects.select_related('profile').filter(
        is_active=True
    ).exclude(
        id=request.user.id
    ).order_by('profile__role', 'first_name', 'last_name', 'username')
    
    # Get all organizations for the dropdown
    from ..models import Organization
    organizations = Organization.objects.all().order_by('name')
    
    context = {
        'users': users,
        'organizations': organizations,
        'current_impersonation': request.session.get('impersonated_user_id'),
        'current_organizations': request.session.get('impersonated_organizations', []),
    }
    
    return render(request, 'crm/admin/user_impersonation.html', context)


@login_required
def get_impersonation_status(request):
    """API endpoint to check current impersonation status"""
    if request.user.profile.role != 'admin':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    impersonated_user_id = request.session.get('impersonated_user_id')
    
    if impersonated_user_id:
        try:
            impersonated_user = User.objects.get(id=impersonated_user_id)
            impersonated_orgs = request.session.get('impersonated_organizations', [])
            
            org_names = []
            if impersonated_orgs:
                from ..models import Organization
                org_names = list(Organization.objects.filter(id__in=impersonated_orgs).values_list('name', flat=True))
            
            return JsonResponse({
                'is_impersonating': True,
                'impersonated_user': {
                    'id': impersonated_user.id,
                    'username': impersonated_user.username,
                    'full_name': impersonated_user.get_full_name(),
                    'role': impersonated_user.profile.get_role_display(),
                },
                'impersonated_organizations': org_names
            })
        except User.DoesNotExist:
            # Clean up invalid session
            keys_to_delete = ['impersonated_user_id', 'original_user_id', 'impersonated_organizations']
            for key in keys_to_delete:
                if key in request.session:
                    del request.session[key]
    
    return JsonResponse({'is_impersonating': False})


def get_effective_user(request):
    """Get the effective user for role checking during impersonation"""
    if hasattr(request, 'user') and request.user.is_authenticated:
        if request.user.profile.role == 'admin':
            impersonated_user_id = request.session.get('impersonated_user_id')
            if impersonated_user_id:
                try:
                    return User.objects.get(id=impersonated_user_id)
                except User.DoesNotExist:
                    # Clean up invalid session
                    keys_to_delete = ['impersonated_user_id', 'original_user_id', 'impersonated_organizations']
                    for key in keys_to_delete:
                        if key in request.session:
                            del request.session[key]
        
        return request.user
    
    return None


def get_effective_organizations(request):
    """Get the effective organizations for the current session"""
    if not hasattr(request, 'user') or not request.user.is_authenticated:
        return []
    
    # If admin is impersonating and has set specific organizations
    if request.user.profile.role == 'admin' and request.session.get('impersonated_user_id'):
        impersonated_orgs = request.session.get('impersonated_organizations')
        if impersonated_orgs is not None:  # Could be empty list for testing "no organizations"
            from ..models import Organization
            return Organization.objects.filter(id__in=impersonated_orgs)
    
    # Get effective user's organizations
    effective_user = get_effective_user(request)
    if effective_user and hasattr(effective_user, 'profile'):
        return effective_user.profile.organizations.all()
    
    return []
