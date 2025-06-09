from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from crm.models import UserProfile, EmailVerification, EmailNotificationSettings
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Cleans up orphaned user-related records and duplicates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            help='Clean records for a specific email',
        )
        parser.add_argument(
            '--username',
            help='Clean records for a specific username',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without making changes',
        )
        parser.add_argument(
            '--force-delete',
            action='store_true',
            help='Force delete user accounts even if verified/approved',
        )

    def handle(self, *args, **options):
        email = options.get('email')
        username = options.get('username')
        dry_run = options.get('dry_run')
        force_delete = options.get('force_delete')
        
        with transaction.atomic():
            # If we're targeting specific email or username
            if email or username:
                query = Q()
                if email:
                    query |= Q(email=email)
                if username:
                    query |= Q(username=username)
                
                users = User.objects.filter(query)
                if users.exists():
                    user_count = users.count()
                    self.stdout.write(f"Found {user_count} user(s) matching criteria")
                    
                    for user in users:
                        # Check if user is verified and approved
                        is_verified = hasattr(user, 'emailverification') and user.emailverification.is_verified
                        is_approved = hasattr(user, 'profile') and user.profile.is_approved
                        
                        if not force_delete and (is_verified or is_approved):
                            self.stdout.write(self.style.WARNING(
                                f"Skipping user {user.username} ({user.email}) - verified={is_verified}, approved={is_approved}. Use --force-delete to override."
                            ))
                            continue
                        
                        if dry_run:
                            self.stdout.write(f"Would delete user: {user.username} ({user.email})")
                        else:
                            self.stdout.write(f"Deleting user: {user.username} ({user.email})")
                            # Delete related records first
                            EmailVerification.objects.filter(user=user).delete()
                            EmailNotificationSettings.objects.filter(user=user).delete()
                            # Profile delete is handled by CASCADE
                            user.delete()
                else:
                    self.stdout.write("No users found matching criteria")
            
            # Clean up orphaned profile records
            orphaned_profiles = UserProfile.objects.filter(user_id__isnull=False).exclude(
                user_id__in=User.objects.values_list('id', flat=True)
            )
            
            if orphaned_profiles.exists():
                count = orphaned_profiles.count()
                self.stdout.write(f"Found {count} orphaned profiles")
                
                if dry_run:
                    self.stdout.write(f"Would delete {count} orphaned profiles")
                else:
                    orphaned_profiles.delete()
                    self.stdout.write(self.style.SUCCESS(f"Deleted {count} orphaned profiles"))
            else:
                self.stdout.write("No orphaned profiles found")
            
            # Clean up orphaned verification records
            orphaned_verifications = EmailVerification.objects.filter(user_id__isnull=False).exclude(
                user_id__in=User.objects.values_list('id', flat=True)
            )
            
            if orphaned_verifications.exists():
                count = orphaned_verifications.count()
                self.stdout.write(f"Found {count} orphaned verification records")
                
                if dry_run:
                    self.stdout.write(f"Would delete {count} orphaned verification records")
                else:
                    orphaned_verifications.delete()
                    self.stdout.write(self.style.SUCCESS(f"Deleted {count} orphaned verification records"))
            else:
                self.stdout.write("No orphaned verification records found")
            
            # Clean up orphaned notification settings records
            orphaned_notifications = EmailNotificationSettings.objects.filter(user_id__isnull=False).exclude(
                user_id__in=User.objects.values_list('id', flat=True)
            )
            
            if orphaned_notifications.exists():
                count = orphaned_notifications.count()
                self.stdout.write(f"Found {count} orphaned notification settings")
                
                if dry_run:
                    self.stdout.write(f"Would delete {count} orphaned notification settings")
                else:
                    orphaned_notifications.delete()
                    self.stdout.write(self.style.SUCCESS(f"Deleted {count} orphaned notification settings"))
            else:
                self.stdout.write("No orphaned notification settings found")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN - No changes were made to the database"))
        else:
            self.stdout.write(self.style.SUCCESS("Database cleanup completed"))
