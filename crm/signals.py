from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import UserProfile
from django.utils import timezone
import logging
from django.core.cache import cache
from django.contrib.auth.signals import user_logged_in, user_logged_out
from .models import ActivityLog

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=UserProfile)
def detect_user_approval(sender, instance, **kwargs):
    """
    Detect when a user is approved and send email notification
    """
    logger.debug(f"Pre-save signal triggered for UserProfile {instance.pk}")
    
    # Skip for new profiles
    if not instance.pk:
        logger.debug("Skipping new profile creation")
        return
        
    try:
        # Get the current state from the database
        old_profile = sender.objects.get(pk=instance.pk)
        
        # Enhanced logging to debug signal firing
        logger.debug(f"Checking approval state change: old={old_profile.is_approved}, new={instance.is_approved}")
        logger.debug(f"Approved by: {instance.approved_by}")

        # Check if this is a new approval (is_approved changed from False to True)
        if not old_profile.is_approved and instance.is_approved:
            logger.info(f"User {instance.user.username} is being approved")
            
            # Import here to avoid circular imports
            from .services.email_service import EmailNotificationService
            
            # Send email notification - don't require approved_by to be set
            email_sent = EmailNotificationService.send_account_approved_email(
                instance.user,
                approved_by=instance.approved_by
            )
            
            if email_sent:
                logger.info(f"Approval notification successfully sent to {instance.user.email}")
            else:
                logger.error(f"Failed to send approval notification to {instance.user.email}")
    except sender.DoesNotExist:
        logger.warning(f"Tried to check approval state for non-existent profile: {instance.pk}")
    except Exception as e:
        logger.error(f"Error in approval notification signal: {str(e)}", exc_info=True)

@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    """Handle user login - log activity and check 2FA"""
    # Get client IP
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    # Log the login
    ActivityLog.objects.create(
        user=user,
        action_type='login',
        description=f"User {user.username} logged in",
        ip_address=ip
    )
    
    # If user is a superuser or admin, add IP to trusted session IPs
    if hasattr(user, 'profile') and (user.is_superuser or user.profile.role == 'admin'):
        # Add IP to trusted session IPs
        trusted_ips = request.session.get('trusted_admin_ips', [])
        if ip not in trusted_ips:
            trusted_ips.append(ip)
            request.session['trusted_admin_ips'] = trusted_ips
            logger.debug(f"Added IP {ip} to trusted admin IPs for this session")
