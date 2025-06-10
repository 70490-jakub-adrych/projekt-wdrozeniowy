from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile
from django.utils import timezone
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

@receiver(post_save, sender=UserProfile)
def user_profile_post_save(sender, instance, created, **kwargs):
    """
    Watch for user profile changes, particularly when a user is approved
    """
    # Skip on profile creation
    if created:
        return
    
    # Check if this is an approval action (profile is approved)
    if instance.is_approved and instance.approved_by:
        logger.debug(f"Processing approved profile for {instance.user.email}")
        
        try:
            # Create a unique key for this approval to prevent duplicates
            # Using a more reliable format that depends on user ID and date
            today = timezone.now().strftime('%Y%m%d')
            cache_key = f"approval_notif_{instance.user.id}_{today}"
            
            # Check if we've already sent a notification for this user today
            if cache.get(cache_key):
                logger.info(f"WATCHER: Already notified {instance.user.email} about approval today, skipping")
                return
            
            # Only send notification if approver is different from the approved user
            if instance.user.id == instance.approved_by.id:
                logger.info(f"WATCHER: Skipping self-approval notification for {instance.user.email}")
                return
            
            logger.info(f"WATCHER: Sending approval notification to {instance.user.email}")
            
            # Import here to avoid circular imports
            from .services.email_service import EmailNotificationService
            
            # Send email notification
            email_sent = EmailNotificationService.send_account_approved_email(
                instance.user,
                approved_by=instance.approved_by
            )
            
            if email_sent:
                # Set a cache flag to prevent duplicate emails for this user today
                cache.set(cache_key, True, 86400)  # 24 hours = 86400 seconds
                logger.info(f"WATCHER: Approval notification successfully sent to {instance.user.email}")
            else:
                logger.error(f"WATCHER: Failed to send approval notification to {instance.user.email}")
        
        except Exception as e:
            logger.error(f"WATCHER: Error sending approval notification: {str(e)}", exc_info=True)
