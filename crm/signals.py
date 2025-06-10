from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import UserProfile
from django.utils import timezone
import logging
from django.core.cache import cache

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

# Keep other signals like post_save if you have them
