from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from crm.services.email_service import EmailNotificationService
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Test password change email notifications'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, required=True, help='Email address to send test emails to')

    def handle(self, *args, **options):
        email = options['email']
        self.stdout.write(self.style.SUCCESS(f"Testing email notifications to {email}"))
        
        # Find the user with this email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"No user found with email {email}"))
            return
            
        # Test sending password change notification
        self.stdout.write("Testing password change notification...")
        success = EmailNotificationService.send_password_changed_notification(user)
        
        if success:
            self.stdout.write(self.style.SUCCESS("✅ Password change notification sent successfully!"))
        else:
            self.stdout.write(self.style.ERROR("❌ Failed to send password change notification"))
            
        # Test password verification email
        self.stdout.write("Testing password verification email...")
        success = EmailNotificationService.send_password_verification_email(user, "123456")
        
        if success:
            self.stdout.write(self.style.SUCCESS("✅ Password verification email sent successfully!"))
        else:
            self.stdout.write(self.style.ERROR("❌ Failed to send password verification email"))
