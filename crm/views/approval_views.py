from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction

from ..models import UserProfile, EmailVerification, EmailNotificationSettings
from .helpers import log_activity, check_permissions
from .error_views import forbidden_access  # Add this import
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
    
    logger.info(f"🔵 APPROVAL PROCESS: Starting for user {user.username} (ID: {user_id})")
    logger.info(f"🔵 Request method: {request.method}")
    logger.info(f"🔵 POST data: {dict(request.POST)}")  # Better logging of POST data
    
    if request.method == 'POST':
        # Store these variables outside the transaction block to use for email later
        approved_user = user
        approver = request.user
        
        # Check if the form was properly confirmed via JavaScript
        is_confirmed = 'confirmed' in request.POST
        logger.info(f"🔵 Form confirmation status: {is_confirmed}")
        
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
                
                logger.info(f"✅ Database update successful: User {user.username} approved by {request.user.username}")
                messages.success(request, f'Użytkownik {user.username} został pomyślnie zatwierdzony.')
            
            # CRITICAL: Send email notification OUTSIDE the transaction block
            logger.info(f"🔵 STARTING EMAIL PROCESS: About to send approval email to {approved_user.email}")
            
            try:
                # Import with enhanced error handling
                logger.info("🔵 Attempting to import email function...")
                
                try:
                    from ..services.email.account import send_account_approved_email
                    logger.info("✅ Successfully imported from specialized module")
                    import_method = "specialized_module"
                except ImportError as e:
                    logger.warning(f"⚠️ Specialized module import failed: {e}")
                    try:
                        from ..services.email_service import EmailNotificationService
                        send_account_approved_email = EmailNotificationService.send_account_approved_email
                        logger.info("✅ Using EmailNotificationService fallback")
                        import_method = "email_service"
                    except ImportError as e2:
                        logger.error(f"❌ Both import methods failed: {e2}")
                        raise ImportError("Could not import email function")
                
                # Enhanced function call with debugging
                logger.info(f"🔵 Calling email function (via {import_method}) for user: {approved_user.username}")
                logger.info(f"🔵 User email: {approved_user.email}")
                logger.info(f"🔵 User is_active: {approved_user.is_active}")
                logger.info(f"🔵 Approver: {approver.username}")
                
                # Call the email function with explicit error checking
                email_sent = send_account_approved_email(
                    user=approved_user, 
                    approved_by=approver
                )
                
                logger.info(f"🔵 Email function returned: {email_sent} (type: {type(email_sent)})")
                
                if email_sent is True:
                    logger.info(f"✅ SUCCESS: Approval notification sent to {approved_user.email}")
                    messages.success(request, f"✅ Email powiadomienia o zatwierdzeniu został wysłany do {approved_user.email}")
                else:
                    logger.error(f"❌ FAILURE: Email function returned {email_sent} for {approved_user.email}")
                    messages.warning(request, f"⚠️ Konto zostało zatwierdzone, ale nie udało się wysłać powiadomienia email (returned: {email_sent})")
                    
            except ImportError as import_error:
                logger.error(f"❌ IMPORT ERROR: {str(import_error)}", exc_info=True)
                messages.warning(request, f"⚠️ Konto zostało zatwierdzone, ale wystąpił błąd importu funkcji email: {str(import_error)}")
            except Exception as email_error:
                logger.error(f"❌ CRITICAL ERROR: Exception during email sending: {str(email_error)}", exc_info=True)
                messages.warning(request, f"⚠️ Konto zostało zatwierdzone, ale wystąpił błąd podczas wysyłania powiadomienia: {str(email_error)}")
            
            logger.info(f"🔵 Redirecting to pending_approvals page")
            return redirect('pending_approvals')  # Changed from 'approved_users' to 'pending_approvals'
            
        except Exception as e:
            logger.error(f"❌ CRITICAL ERROR: Database transaction failed for user {user_id}: {str(e)}", exc_info=True)
            messages.error(request, f'❌ Wystąpił błąd podczas zatwierdzania użytkownika: {str(e)}')
            return redirect('pending_approvals')
    
    # GET request - display approval confirmation page (this template might be missing)
    logger.info(f"🔵 Displaying approval form for user {user.username}")
    
    # Check if the template has the form fields we need
    context = {
        'profile': profile,
        'user': user  # Add user to context for better template access
    }
    
    return render(request, 'crm/approvals/approve_user.html', context)