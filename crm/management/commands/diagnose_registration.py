from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import connection
from crm.models import UserProfile, EmailVerification
import logging
import json

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Diagnose user registration issues and database integrity'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            help='Check specific email for issues',
        )
        parser.add_argument(
            '--username',
            help='Check specific username for issues',
        )
        parser.add_argument(
            '--repair',
            action='store_true',
            help='Attempt to repair issues',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show more detailed information',
        )
        
    def handle(self, *args, **options):
        email = options.get('email')
        username = options.get('username')
        repair = options.get('repair')
        verbose = options.get('verbose')
        
        self.stdout.write("Running registration system diagnostics...")
        
        # Check database auto-increment values
        self._check_auto_increment_values()
        
        # Check for orphaned profiles
        self._check_orphaned_profiles(repair)
        
        # Check for duplicate email addresses
        self._check_duplicate_emails()
        
        # Check for users without profiles
        self._check_users_without_profiles(repair)
        
        # Check for verification issues
        self._check_verification_issues(repair)
        
        # Check specific user if provided
        if email or username:
            self._check_specific_user(email, username, verbose, repair)
            
        self.stdout.write(self.style.SUCCESS("Diagnostics completed"))
            
    def _check_auto_increment_values(self):
        """Check current auto-increment values for key tables"""
        self.stdout.write("\nChecking auto-increment values...")
        
        tables = ['auth_user', 'crm_userprofile', 'crm_emailverification']
        
        with connection.cursor() as cursor:
            for table in tables:
                cursor.execute(f"SELECT MAX(id) FROM {table}")
                max_id = cursor.fetchone()[0] or 0
                
                cursor.execute(f"""
                    SELECT AUTO_INCREMENT 
                    FROM information_schema.TABLES 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = '{table}'
                """)
                auto_inc = cursor.fetchone()[0]
                
                if auto_inc <= max_id:
                    self.stdout.write(self.style.ERROR(
                        f"{table}: AUTO_INCREMENT ({auto_inc}) ≤ MAX ID ({max_id}) - This can cause conflicts!"
                    ))
                else:
                    self.stdout.write(self.style.SUCCESS(
                        f"{table}: AUTO_INCREMENT={auto_inc}, MAX ID={max_id} - OK"
                    ))
    
    def _check_orphaned_profiles(self, repair):
        """Check for orphaned profiles"""
        self.stdout.write("\nChecking orphaned profiles...")
        
        orphaned_profiles = UserProfile.objects.filter(user_id__isnull=False).exclude(
            user_id__in=User.objects.values_list('id', flat=True)
        )
        
        if orphaned_profiles.exists():
            count = orphaned_profiles.count()
            self.stdout.write(self.style.ERROR(
                f"Found {count} orphaned profiles! These can cause registration conflicts."
            ))
            
            for profile in orphaned_profiles:
                self.stdout.write(f"Orphaned profile ID={profile.id}, user_id={profile.user_id}")
            
            if repair:
                orphaned_profiles.delete()
                self.stdout.write(self.style.SUCCESS(f"Deleted {count} orphaned profiles"))
        else:
            self.stdout.write(self.style.SUCCESS("No orphaned profiles found"))
    
    def _check_duplicate_emails(self):
        """Check for duplicate email addresses"""
        self.stdout.write("\nChecking for duplicate emails...")
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT email, COUNT(*) as count
                FROM auth_user
                GROUP BY email
                HAVING COUNT(*) > 1
            """)
            duplicates = cursor.fetchall()
        
        if duplicates:
            self.stdout.write(self.style.ERROR(
                f"Found {len(duplicates)} duplicate email addresses!"
            ))
            for email, count in duplicates:
                self.stdout.write(f"Email '{email}' is used by {count} users")
                
                # Find the users with this email
                users = User.objects.filter(email=email)
                for user in users:
                    self.stdout.write(f"  - User ID={user.id}, username={user.username}, active={user.is_active}")
        else:
            self.stdout.write(self.style.SUCCESS("No duplicate emails found"))
    
    def _check_users_without_profiles(self, repair):
        """Check for users without profiles"""
        self.stdout.write("\nChecking for users without profiles...")
        
        users_without_profiles = User.objects.filter(
            ~Q(id__in=UserProfile.objects.values_list('user_id', flat=True))
        )
        
        if users_without_profiles.exists():
            count = users_without_profiles.count()
            self.stdout.write(self.style.WARNING(
                f"Found {count} users without profiles"
            ))
            
            for user in users_without_profiles:
                self.stdout.write(f"User ID={user.id}, username={user.username}, email={user.email}")
                
                if repair:
                    # Create profile for this user
                    UserProfile.objects.create(
                        user=user,
                        role='client',
                        is_approved=False,
                        email_verified=False
                    )
                    self.stdout.write(f"  - Created profile for user ID={user.id}")
        else:
            self.stdout.write(self.style.SUCCESS("All users have profiles"))
    
    def _check_verification_issues(self, repair):
        """Check for verification issues"""
        self.stdout.write("\nChecking email verification issues...")
        
        # Find orphaned verifications
        orphaned_verifications = EmailVerification.objects.filter(user_id__isnull=False).exclude(
            user_id__in=User.objects.values_list('id', flat=True)
        )
        
        if orphaned_verifications.exists():
            count = orphaned_verifications.count()
            self.stdout.write(self.style.ERROR(
                f"Found {count} orphaned verification records!"
            ))
            
            for verification in orphaned_verifications:
                self.stdout.write(f"Orphaned verification ID={verification.id}, user_id={verification.user_id}")
                
            if repair:
                orphaned_verifications.delete()
                self.stdout.write(self.style.SUCCESS(f"Deleted {count} orphaned verifications"))
        else:
            self.stdout.write(self.style.SUCCESS("No orphaned verification records"))
    
    def _check_specific_user(self, email, username, verbose, repair):
        """Check a specific user for issues"""
        query = {}
        if email:
            query['email'] = email
        if username:
            query['username'] = username
        
        if not query:
            return
            
        users = User.objects.filter(**query)
        
        self.stdout.write(f"\nChecking specific user(s): {query}...")
        
        if not users.exists():
            self.stdout.write(self.style.WARNING("No users found matching criteria"))
            return
            
        for user in users:
            self.stdout.write(f"\nUser ID={user.id}, username={user.username}, email={user.email}")
            
            # Check if profile exists
            try:
                profile = user.profile
                self.stdout.write(self.style.SUCCESS(f"Profile exists: ID={profile.id}, role={profile.role}"))
            except UserProfile.DoesNotExist:
                self.stdout.write(self.style.ERROR("No profile found for this user!"))
                if repair:
                    profile = UserProfile.objects.create(
                        user=user,
                        role='client',
                        is_approved=False,
                        email_verified=False
                    )
                    self.stdout.write(self.style.SUCCESS(f"Created new profile with ID={profile.id}"))
            
            # Check if verification exists
            try:
                verification = EmailVerification.objects.get(user=user)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Verification record exists: ID={verification.id}, "
                        f"verified={verification.is_verified}, "
                        f"code={'*****' + verification.verification_code[-1] if verification.verification_code else None}"
                    )
                )
            except EmailVerification.DoesNotExist:
                self.stdout.write(self.style.WARNING("No verification record found for this user"))
                if repair and not (hasattr(user, 'profile') and user.profile.email_verified):
                    # Create verification record
                    verification_code = ''.join(['0' for _ in range(6)])
                    verification = EmailVerification.objects.create(
                        user=user,
                        verification_code=verification_code
                    )
                    self.stdout.write(self.style.SUCCESS(f"Created verification record with ID={verification.id}"))
            
            # Show all related objects for this user
            if verbose:
                self.stdout.write("\nDatabase details:")
                with connection.cursor() as cursor:
                    # Check in UserProfile
                    cursor.execute("SELECT * FROM crm_userprofile WHERE user_id = %s", [user.id])
                    columns = [col[0] for col in cursor.description]
                    profiles = [dict(zip(columns, row)) for row in cursor.fetchall()]
                    self.stdout.write(f"UserProfiles: {json.dumps(profiles, default=str)}")
                    
                    # Check in EmailVerification
                    cursor.execute("SELECT * FROM crm_emailverification WHERE user_id = %s", [user.id])
                    columns = [col[0] for col in cursor.description]
                    verifications = [dict(zip(columns, row)) for row in cursor.fetchall()]
                    self.stdout.write(f"EmailVerifications: {json.dumps(verifications, default=str)}")
                    
                    # Check in EmailNotificationSettings
                    cursor.execute("SELECT * FROM crm_emailnotificationsettings WHERE user_id = %s", [user.id])
                    columns = [col[0] for col in cursor.description]
                    notifications = [dict(zip(columns, row)) for row in cursor.fetchall()]
                    self.stdout.write(f"EmailNotificationSettings: {json.dumps(notifications, default=str)}")
