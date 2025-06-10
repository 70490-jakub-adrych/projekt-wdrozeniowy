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
    # Skip for new profiles (they can't be "just approved")
    if not instance.pk:
        return
        
    try:
        # Get the current state from the database (before the save)
        old_profile = sender.objects.get(pk=instance.pk)
        
        # Check if this is a new approval (is_approved changed from False to True)
        # and we have an approver set
        if not old_profile.is_approved and instance.is_approved and instance.approved_by:
            logger.info(f"User {instance.user.username} is being approved by {instance.approved_by.username}")
            
            # Only send notification if approver is different from the approved user
            if instance.user.id != instance.approved_by.id:
                # Import here to avoid circular imports
                from .services.email_service import EmailNotificationService
                
                # Send email notification
                email_sent = EmailNotificationService.send_account_approved_email(
                    instance.user,
                    approved_by=instance.approved_by
                )
                
                if email_sent:
                    logger.info(f"Approval notification successfully sent to {instance.user.email}")
                else:
                    logger.error(f"Failed to send approval notification to {instance.user.email}")
    except sender.DoesNotExist:
        # This shouldn't happen, but just in case
        logger.warning(f"Tried to check approval state for non-existent profile: {instance.pk}")

# Keep other signals like post_save if you have them
