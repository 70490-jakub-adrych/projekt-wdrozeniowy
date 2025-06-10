from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile
from django.utils import timezone
import logging
from django.core.cache import cache
from django.db.models import F

logger = logging.getLogger(__name__)

@receiver(post_save, sender=UserProfile)
def user_profile_post_save(sender, instance, created, **kwargs):
    """
    Watch for user profile changes, particularly when a user is approved
    """
    # Skip on profile creation
    if created:
        return
    
    # Get the 'update_fields' argument which tells us which fields were updated
    # This is set when you call obj.save(update_fields=[...])
    update_fields = kwargs.get('update_fields')
    
    # Check if this is a genuine approval action:
    # 1. Profile is approved
    # 2. It has approval metadata
    # 3. The approval is recent
    if instance.is_approved and instance.approved_by and instance.approved_at:
        try:
            # Only consider recent approvals (within the last minute)
            approval_time = instance.approved_at
            
            # Only process if the approval happened very recently
            if timezone.now() - approval_time < timezone.timedelta(minutes=1):
                # Skip if user and approver are the same person
                if instance.user.id == instance.approved_by.id:
                    logger.info(f"WATCHER: Skipping notification for self-approval for {instance.user.email}")
                    return
                
                # Create a unique key for this approval to prevent duplicates
                cache_key = f"approval_notification_sent_{instance.user.id}_{approval_time.strftime('%Y%m%d%H%M%S')}"
                
                # Check if we've already sent a notification for this approval in this session
                if cache.get(cache_key):
                    logger.info(f"WATCHER: Skipping duplicate notification for {instance.user.email}")
                    return
                
                # Only log as a detection if we know it's a new approval
                # This is less noisy and more accurate
                if update_fields and 'is_approved' in update_fields:
                    logger.info(f"WATCHER: Detected user approval for {instance.user.email}")
                    
                    # Import here to avoid circular imports
                    from .services.email_service import EmailNotificationService
                    
                    # Send email notification 
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
        except Exception as e:
            logger.error(f"WATCHER: Error sending approval notification: {str(e)}", exc_info=True)
