"""
API views for AJAX requests
"""
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods


@login_required
@require_http_methods(["GET"])
def user_contact_info(request, user_id):
    """
    API endpoint to get user contact information for popup display
    Only accessible to non-client users
    """
    try:
        # Check if user has permission to view contact information
        if request.user.profile.role == 'client':
            return JsonResponse({
                'success': False,
                'error': 'Brak uprawnień do przeglądania informacji kontaktowych'
            }, status=403)
        
        user = get_object_or_404(User, id=user_id)
        
        # Build full name
        full_name = ""
        if user.first_name or user.last_name:
            full_name = f"{user.first_name} {user.last_name}".strip()
        
        # Get role display name
        role_display = ""
        if hasattr(user, 'profile') and user.profile:
            role_choices = dict(user.profile.USER_ROLES)
            role_display = role_choices.get(user.profile.role, user.profile.role)
        
        # Get organizations
        organizations = []
        if hasattr(user, 'profile') and user.profile:
            organizations = [org.name for org in user.profile.organizations.all()]
        
        # Get contact information
        email = user.email if user.email else ""
        phone = ""
        if hasattr(user, 'profile') and user.profile and user.profile.phone:
            phone = user.profile.phone
        
        return JsonResponse({
            'success': True,
            'username': user.username,
            'full_name': full_name,
            'email': email,
            'phone': phone,
            'role': role_display,
            'organizations': organizations
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
def toggle_theme(request):
    """
    API endpoint to toggle user theme preference
    """
    try:
        theme = request.POST.get('theme', 'light')
        
        # Validate theme value
        if theme not in ['light', 'dark']:
            theme = 'light'
        
        # Create response and set cookie
        response = JsonResponse({
            'success': True,
            'theme': theme
        })
        
        # Set theme cookie with 1 year expiration
        response.set_cookie(
            'theme', 
            theme, 
            max_age=31536000,  # 1 year
            samesite='Lax'
        )
        
        return response
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
