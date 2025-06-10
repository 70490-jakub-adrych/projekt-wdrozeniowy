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
    
    # Check if this is an approval action:
    # 1. Profile is approved
    # 2. Has approval metadata
    if instance.is_approved and instance.approved_by and instance.approved_at:
        try:
            # Only consider recent approvals (within the last minute)
            approval_time = instance.approved_at
            recent_approval = timezone.now() - approval_time < timezone.timedelta(minutes=1)
            
            # Skip if user and approver are the same person
            self_approval = instance.user.id == instance.approved_by.id
            
            # Only proceed if it's a recent approval and not self-approval
            if recent_approval and not self_approval:
                # Create a unique key for this approval to prevent duplicates
                cache_key = f"approval_notification_{instance.user.id}_{approval_time.strftime('%Y%m%d%H%M%S')}"
                
                # Check if we've already sent a notification for this approval
                if cache.get(cache_key):
                    logger.info(f"WATCHER: Skipping duplicate notification for {instance.user.email}")
                    return
                
                logger.info(f"WATCHER: Detected user approval for {instance.user.email}")
                
                # Import here to avoid circular imports
                from .services.email_service import EmailNotificationService
                
                # Send email notification with a simple retry mechanism
                try:
                    email_sent = EmailNotificationService.send_account_approved_email(
                        instance.user,
                        approved_by=instance.approved_by
                    )
                    
                    if email_sent:
                        # Set the cache flag to prevent duplicate emails
                        cache.set(cache_key, True, 300)  # 300 seconds = 5 minutes
                        logger.info(f"WATCHER: Approval notification successfully sent to {instance.user.email}")
                    else:
                        logger.error(f"WATCHER: Failed to send approval notification to {instance.user.email}")
                except Exception as email_error:
                    logger.error(f"WATCHER: Email service error: {str(email_error)}")
                    
        except Exception as e:
            logger.error(f"WATCHER: Error in approval notification process: {str(e)}", exc_info=True)
