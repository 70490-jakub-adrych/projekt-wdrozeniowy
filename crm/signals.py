from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=UserProfile)
def user_profile_post_save(sender, instance, created, **kwargs):
    """
    Watch for user profile changes, particularly when a user is approved
    """
    # Skip on profile creation
    if created:
        return
    
    # Check if this is an approval action by checking if approved status changed and is now True
    if instance.is_approved and instance.approved_at and instance.approved_by:
        try:
            # Skip if the instance was just created and approved at the same time
            # or if the approval happened more than a minute ago (to avoid double notifications)
            if timezone.now() - instance.approved_at < timezone.timedelta(minutes=1):
                logger.info(f"🔍 WATCHER: Detected user approval for {instance.user.email}")
                
                # Import here to avoid circular imports
                from .services.email_service import EmailNotificationService
                
                # Send email notification
                email_sent = EmailNotificationService.send_account_approved_email(
                    instance.user,
                    approved_by=instance.approved_by
                )
                
                if email_sent:
                    logger.info(f"✅ WATCHER: Approval notification successfully sent to {instance.user.email}")
                else:
                    logger.error(f"❌ WATCHER: Failed to send approval notification to {instance.user.email}")
        except Exception as e:
            logger.error(f"❌ WATCHER: Error sending approval notification: {str(e)}", exc_info=True)
