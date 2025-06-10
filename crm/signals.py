from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import UserProfile
from django.utils import timezone
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Add a pre_save receiver to track approval status changes
@receiver(pre_save, sender=UserProfile)
def track_approval_changes(sender, instance, **kwargs):
    """Track if a profile is being approved (changing from not approved to approved)"""
    if instance.pk:  # Only for existing instances (not new ones)
        try:
            # Get previous state
            old_instance = UserProfile.objects.get(pk=instance.pk)
            
            # Check if this is an approval action (status changing from False to True)
            if not old_instance.is_approved and instance.is_approved:
                # Cache that this is a genuine approval, not just any save operation
                cache_key = f"genuine_approval_{instance.pk}_{timezone.now().strftime('%Y%m%d%H%M%S')}"
                cache.set(cache_key, True, 60)  # Store for 1 minute
                logger.info(f"TRACKER: Detected genuine approval change for {instance.user.email}")
        except Exception as e:
            logger.error(f"TRACKER: Error tracking approval change: {str(e)}")

@receiver(post_save, sender=UserProfile)
def user_profile_post_save(sender, instance, created, **kwargs):
    """
    Watch for user profile changes, particularly when a user is approved
    """
    # Skip on profile creation
    if created:
        return
    
    # Check if this is an approval action
    if instance.is_approved and instance.approved_by and instance.approved_at:
        try:
            # Get the approval timestamp, default to current time if not set
            approval_time = instance.approved_at or timezone.now()
            
            # Check if this is a recent approval (within last minute)
            recent_approval = timezone.now() - approval_time < timezone.timedelta(minutes=1)
            
            # Look for evidence this is a genuine approval action (not just a login or other save)
            prefix = f"genuine_approval_{instance.pk}_"
            is_genuine_approval = False
            
            # Check multiple timestamps in the last minute
            for seconds in range(60):
                check_time = timezone.now() - timezone.timedelta(seconds=seconds)
                cache_key = f"{prefix}{check_time.strftime('%Y%m%d%H%M%S')}"
                if cache.get(cache_key):
                    is_genuine_approval = True
                    logger.info(f"WATCHER: Confirmed genuine approval action for {instance.user.email}")
                    break
            
            # Only proceed if a genuine approval was detected or update_fields includes is_approved
            update_fields = kwargs.get('update_fields')
            has_approved_field = update_fields and 'is_approved' in update_fields
            
            if (is_genuine_approval or has_approved_field) and recent_approval:
                # Create a unique key for this approval to prevent duplicates
                cache_key = f"approval_notification_sent_{instance.user.id}_{approval_time.strftime('%Y%m%d%H%M')}"
                
                # Check if we've already sent a notification for this approval
                if cache.get(cache_key):
                    logger.info(f"WATCHER: Skipping duplicate notification for {instance.user.email}")
                    return
                
                logger.info(f"WATCHER: Detected user approval for {instance.user.email}")
                
                # Import here to avoid circular imports
                from .services.email_service import EmailNotificationService
                
                # Send email notification
                email_sent = EmailNotificationService.send_account_approved_email(
                    instance.user,
                    approved_by=instance.approved_by
                )
                
                if email_sent:
                    # Set a cache flag to prevent duplicate emails
                    cache.set(cache_key, True, 300)  # 300 seconds = 5 minutes
                    logger.info(f"WATCHER: Approval notification successfully sent to {instance.user.email}")
                else:
                    logger.error(f"WATCHER: Failed to send approval notification to {instance.user.email}")
            elif instance.is_approved:
                logger.debug(f"WATCHER: Skipping notification - not a genuine approval action for {instance.user.email}")
        except Exception as e:
            logger.error(f"WATCHER: Error sending approval notification: {str(e)}", exc_info=True)
