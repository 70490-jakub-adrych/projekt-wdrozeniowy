from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from crm.models import Ticket
from crm.services.email_service import EmailNotificationService

class Command(BaseCommand):
    help = 'Send test notifications to verify email system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email address to send test to',
            required=True
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['verification', 'ticket_created', 'ticket_assigned', 'account_approved'],
            help='Type of notification to test',
            default='verification'
        )

    def handle(self, *args, **options):
        email = options['email']
        notification_type = options['type']
        
        # Create or get test user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': 'test_user',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        if notification_type == 'verification':
            success = EmailNotificationService.send_verification_email(user, '123456')
            
        elif notification_type == 'account_approved':
            success = EmailNotificationService.send_account_approved_notification(user)
            
        elif notification_type in ['ticket_created', 'ticket_assigned']:
            # Get first ticket or create a test one
            ticket = Ticket.objects.first()
            if not ticket:
                self.stdout.write(self.style.ERROR('No tickets found. Create a ticket first.'))
                return
                
            success = EmailNotificationService.send_ticket_notification(
                notification_type.replace('ticket_', ''), ticket, user
            )
        
        if success:
            self.stdout.write(
                self.style.SUCCESS(f'Test {notification_type} notification sent to {email}')
            )
        else:
            self.stdout.write(
                self.style.ERROR(f'Failed to send {notification_type} notification to {email}')
            )
