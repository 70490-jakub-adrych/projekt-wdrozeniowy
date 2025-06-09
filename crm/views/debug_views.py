from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.shortcuts import get_object_or_404
import logging

logger = logging.getLogger(__name__)

def is_admin(user):
    """Check if user is an admin"""
    return user.is_superuser or getattr(user, 'profile', None) and user.profile.role == 'admin'

@login_required
@user_passes_test(is_admin)
def test_password_reset_email(request, user_id):
    """Test view for sending password reset emails (admin only)"""
    try:
        target_user = get_object_or_404(User, pk=user_id)
        
        # Use Django's built-in password reset token generator
        token = default_token_generator.make_token(target_user)
        uid = urlsafe_base64_encode(force_bytes(target_user.pk))
        
        # Get domain from settings or request
        domain = getattr(settings, 'SITE_DOMAIN', request.get_host())
        protocol = 'https' if request.is_secure() else 'http'
        
        # Create context similar to what PasswordResetView would create
        context = {
            'email': target_user.email,
            'domain': domain,
            'site_name': 'System Helpdesk',
            'uid': uid,
            'user': target_user,
            'token': token,
            'protocol': protocol,
        }
        
        # Import at function level to avoid circular imports
        from django.contrib.auth.views import PasswordResetView
        from ..views.auth_views import HTMLEmailPasswordResetView
        
        # Create an instance of our custom view and call its email method
        view = HTMLEmailPasswordResetView()
        view.send_mail(
            'emails/password_reset_subject.txt',
            'emails/password_reset_email.txt',
            context,
            settings.DEFAULT_FROM_EMAIL,
            target_user.email,
            html_email_template_name='emails/password_reset_email.html'
        )
        
        return JsonResponse({'status': 'success', 'message': f'Test reset email sent to {target_user.email}'})
    
    except Exception as e:
        logger.error(f"Error in test_password_reset_email: {str(e)}", exc_info=True)
        return JsonResponse({'status': 'error', 'message': str(e)})
