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
    
    # Check if this is an approval action
    if instance.is_approved:
        try:
            # Get the approval timestamp, default to current time if not set
            approval_time = instance.approved_at or timezone.now()
            
            # Only process recent approvals (within the last minute)
            # This prevents duplicate notifications on subsequent saves
            if timezone.now() - approval_time < timezone.timedelta(minutes=1):
                # Create a unique key for this approval to prevent duplicates
                cache_key = f"approval_notification_sent_{instance.user.id}_{approval_time.strftime('%Y%m%d%H%M')}"
                
                # Check if we've already sent a notification for this approval
                if cache.get(cache_key):
                    logger.info(f"⚠️ WATCHER: Skipping duplicate notification for {instance.user.email}")
                    return
                
                logger.info(f"🔍 WATCHER: Detected user approval for {instance.user.email}")
                
                # Import here to avoid circular imports
                from .services.email_service import EmailNotificationService
                
                # Send email notification
                email_sent = EmailNotificationService.send_account_approved_email(
                    instance.user,
                    approved_by=getattr(instance, 'approved_by', None)  # Safely get approved_by
                )
                
                if email_sent:
                    # Set a cache flag to prevent duplicate emails
                    # Keep this flag for 5 minutes, which should be more than enough
                    # to prevent duplicates during the transaction
                    cache.set(cache_key, True, 300)  # 300 seconds = 5 minutes
                    logger.info(f"✅ WATCHER: Approval notification successfully sent to {instance.user.email}")
                else:
                    logger.error(f"❌ WATCHER: Failed to send approval notification to {instance.user.email}")
        except Exception as e:
            logger.error(f"❌ WATCHER: Error sending approval notification: {str(e)}", exc_info=True)
