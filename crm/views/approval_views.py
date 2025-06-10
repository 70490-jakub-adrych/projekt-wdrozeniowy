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
                
                # First delete all related records EXCEPT the profile
                # Delete verification record if exists
                EmailVerification.objects.filter(user=user).delete()
                
                # Delete notification settings if exists
                EmailNotificationSettings.objects.filter(user=user).delete()
                
                # Important: Delete the profile BEFORE deleting the user
                # This prevents orphaned profile records
                profile_id = profile.id
                profile.delete()
                logger.info(f"Deleted UserProfile with ID {profile_id}")
                
                # Now delete the user account itself
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

@login_required
def approve_user(request, user_id):
    """View for approving a pending user."""
    # Check permissions
    if not check_permissions(request.user, ['admin', 'superagent']):
        return forbidden_access(request)
    
    profile = get_object_or_404(UserProfile, user_id=user_id)
    user = profile.user
    
    if request.method == 'POST':
        # Store these variables outside the transaction block to use for email later
        approved_user = user
        approver = request.user
        
        try:
            with transaction.atomic():
                # Log this action
                log_activity(
                    user=request.user,
                    action_type='user_approved',
                    description=f"Approved account for user: {user.username} ({user.email})",
                    request=request
                )
                
                # Update the user's profile status to approved
                profile.is_approved = True
                profile.approved_by = request.user
                profile.approved_at = timezone.now()
                profile.save()
                
                logger.info(f"User {user.username} approved by {request.user.username}")
                messages.success(request, f'Użytkownik {user.username} został pomyślnie zatwierdzony.')
            
            # IMPORTANT: Send email notification OUTSIDE the transaction block
            try:
                logger.info(f"🔵 APPROVAL EMAIL: Starting notification for {approved_user.email}")
                
                # Import using absolute path to avoid relative import issues
                from crm.services.email_service import EmailNotificationService
                
                # Call with explicit success check
                email_sent = EmailNotificationService.send_account_approved_email(
                    approved_user, 
                    approved_by=approver
                )
                
                if email_sent:
                    logger.info(f"✅ Approval notification SUCCESSFULLY sent to {approved_user.email}")
                else:
                    logger.error(f"❌ Failed to send approval notification to {approved_user.email}")
            except Exception as email_error:
                logger.error(f"❌ CRITICAL ERROR sending approval notification: {str(email_error)}", exc_info=True)
            
            # Check if 'approved_users' URL exists, if not fall back to 'pending_approvals'
            try:
                from django.urls import reverse
                reverse('approved_users')
                return redirect('approved_users')
            except:
                logger.warning("URL 'approved_users' not found, redirecting to 'pending_approvals'")
                return redirect('pending_approvals')
        except Exception as e:
            logger.error(f"Error approving user {user_id}: {str(e)}")
            messages.error(request, f'Wystąpił błąd podczas zatwierdzania użytkownika: {str(e)}')
            return redirect('pending_approvals')
    
    # Display approval confirmation page
    return render(request, 'crm/approvals/approve_user.html', {'profile': profile})