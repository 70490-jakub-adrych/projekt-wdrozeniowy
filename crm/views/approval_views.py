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
        
        # Check if the form was properly confirmed via JavaScript
        is_confirmed = 'confirmed' in request.POST
        logger.info(f"Approval form submission for user {user_id} - confirmed via JS: {is_confirmed}")
        
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
            # This ensures the email is sent even if there's a later error
            try:
                logger.info(f"🔵 Starting approval email process to {approved_user.email}")
                
                # Try both import methods for robustness
                try:
                    # First try direct import from specialized module
                    from ..services.email.account import send_account_approved_email
                    logger.info("✅ Successfully imported send_account_approved_email from specialized module")
                except ImportError:
                    # Fall back to EmailNotificationService if specialized module import fails
                    from ..services.email_service import EmailNotificationService
                    send_account_approved_email = EmailNotificationService.send_account_approved_email
                    logger.info("⚠️ Using EmailNotificationService fallback for send_account_approved_email")
                
                # Direct call to the function
                email_sent = send_account_approved_email(
                    approved_user, 
                    approved_by=approver
                )
                
                if email_sent:
                    logger.info(f"✅ Approval notification successfully sent to {approved_user.email}")
                    messages.success(request, f"Email powiadomienia o zatwierdzeniu został wysłany do {approved_user.email}")
                else:
                    logger.error(f"❌ Failed to send approval notification to {approved_user.email}")
                    messages.warning(request, f"Konto zostało zatwierdzone, ale nie udało się wysłać powiadomienia email.")
            except Exception as email_error:
                logger.error(f"❌ Error sending approval notification: {str(email_error)}", exc_info=True)
                messages.warning(request, f"Konto zostało zatwierdzone, ale wystąpił błąd podczas wysyłania powiadomienia: {str(email_error)}")
                # Don't raise the exception - we still want to redirect to success page
            
            return redirect('approved_users')
        except Exception as e:
            logger.error(f"Error approving user {user_id}: {str(e)}")
            messages.error(request, f'Wystąpił błąd podczas zatwierdzania użytkownika: {str(e)}')
            return redirect('pending_approvals')
    
    # Display approval confirmation page
    return render(request, 'crm/approvals/approve_user.html', {'profile': profile})