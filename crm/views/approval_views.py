from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction

from ..models import UserProfile, EmailVerification, EmailNotificationSettings
from .helpers import log_activity, check_permissions
import logging

# Configure logger
logger = logging.getLogger(__name__)


@login_required
def reject_user(request, user_id):
    """Reject a user and delete their account"""
    # Check permissions
    if not check_permissions(request.user, ['admin', 'superagent']):
        return forbidden_access(request)
    
    profile = get_object_or_404(UserProfile, user_id=user_id)
    user = profile.user
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Log this action before deletion
                log_activity(
                    user=request.user,
                    action_type='user_rejected',
                    description=f"Rejected account for user: {user.username} ({user.email})",
                    request=request
                )
                
                # Capture email for logging
                username = user.username
                email = user.email
                
                # First delete all related records
                # Delete verification record if exists
                EmailVerification.objects.filter(user=user).delete()
                
                # Delete notification settings if exists
                EmailNotificationSettings.objects.filter(user=user).delete()
                
                # Delete profile
                profile.delete()
                
                # Delete the user account itself (cascade deletes other related objects)
                user.delete()
                
                logger.info(f"User {username} ({email}) rejected and deleted by {request.user.username}")
                messages.success(request, f'Konto użytkownika {username} zostało odrzucone i usunięte z systemu.')
            
            return redirect('pending_approvals')
        except Exception as e:
            logger.error(f"Error rejecting user {user_id}: {str(e)}")
            messages.error(request, f'Wystąpił błąd podczas odrzucania użytkownika: {str(e)}')
            return redirect('pending_approvals')
    
    # Display confirmation page
    return render(request, 'crm/approvals/reject_user.html', {'profile': profile})