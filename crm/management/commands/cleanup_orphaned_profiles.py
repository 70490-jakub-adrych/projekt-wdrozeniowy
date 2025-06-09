from django.core.management.base import BaseCommand
from crm.models import UserProfile
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Clean up orphaned user profiles that reference non-existent users'

    def handle(self, *args, **options):
        # Find profiles where user_id is not null but doesn't exist in User table
        orphaned_profiles = UserProfile.objects.filter(user_id__isnull=False).exclude(
            user_id__in=User.objects.values_list('id', flat=True)
        )
        
        count = orphaned_profiles.count()
        if count > 0:
            self.stdout.write(f"Found {count} orphaned profiles")
            
            # Get the list of IDs before deletion for logging
            orphaned_ids = list(orphaned_profiles.values_list('id', flat=True))
            user_ids = list(orphaned_profiles.values_list('user_id', flat=True))
            
            # Delete the orphaned profiles
            orphaned_profiles.delete()
            
            self.stdout.write(self.style.SUCCESS(
                f"Successfully deleted {count} orphaned profiles.\n"
                f"Profile IDs: {orphaned_ids}\n"
                f"Referenced user IDs: {user_ids}"
            ))
            
            logger.info(f"Cleaned up {count} orphaned user profiles")
        else:
            self.stdout.write(self.style.SUCCESS("No orphaned profiles found"))
