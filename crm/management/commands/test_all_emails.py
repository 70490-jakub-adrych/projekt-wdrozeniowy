from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from crm.models import Ticket
from crm.services.email_service import EmailNotificationService
from django.urls import reverse
from django.utils import timezone

class Command(BaseCommand):
    help = 'Test all types of email notifications'

    def add_arguments(self, parser):
        parser.add_argument('--email', required=True, help='Email to send test notifications to')
        parser.add_argument('--ticket-id', type=int, help='Specific ticket ID to use')

    def handle(self, *args, **options):
        email = options['email']
        ticket_id = options.get('ticket_id')
        
        # Find a user with the provided email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'No user found with email {email}'))
            return
            
        # Find a ticket to use for testing
        try:
            if ticket_id:
                ticket = Ticket.objects.get(id=ticket_id)
            else:
                ticket = Ticket.objects.first()
                if not ticket:
                    self.stdout.write(self.style.ERROR('No tickets found in the database'))
                    return
        except Ticket.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'No ticket found with ID {ticket_id}'))
            return
            
        # Test all ticket notification types
        notification_types = [
            'created', 'updated', 'commented', 'assigned', 
            'closed', 'reopened', 'status_changed'
        ]
        
        self.stdout.write(self.style.SUCCESS('Starting email template tests...'))
        
        for notification_type in notification_types:
            self.stdout.write(f'Testing {notification_type} notification...')
            success = EmailNotificationService.send_ticket_notification(
                notification_type, ticket, user,
                triggered_by=None,
                changes="This is a test change",
                comment_content="This is a test comment",
                old_status="old_status"
            )
               
            if success:
                self.stdout.write(self.style.SUCCESS(f'✅ Successfully sent {notification_type} notification'))
            else:
                self.stdout.write(self.style.ERROR(f'❌ Failed to send {notification_type} notification'))
                   
        # Test password verification email
        self.stdout.write('Testing password verification email...')
        verification_success = EmailNotificationService.send_password_verification_email(user, '123456')
        if verification_success:
            self.stdout.write(self.style.SUCCESS('✅ Successfully sent password verification email'))
        else:
            self.stdout.write(self.style.ERROR('❌ Failed to send password verification email'))
            
        # Test account approved email
        self.stdout.write('Testing account approved email...')
        from django.conf import settings
        site_url = getattr(settings, 'SITE_URL', 'https://betulait.usermd.net')
        login_url = f"{site_url}/login/"
        
        html_content = render_to_string('emails/account_approved.html', {
            'user': user,
            'approved_by': user,
            'site_name': 'System Helpdesk',
            'login_url': login_url
        })
        text_content = render_to_string('emails/account_approved.txt', {
            'user': user,
            'approved_by': user,
            'site_name': 'System Helpdesk',
            'login_url': login_url
        })
        
        msg = EmailMultiAlternatives(
            subject="System Helpdesk - Konto zatwierdzone",
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        msg.attach_alternative(html_content, "text/html")
        
        try:
            msg.send()
            self.stdout.write(self.style.SUCCESS('✅ Successfully sent account approved email'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Failed to send account approved email: {str(e)}'))
            
        self.stdout.write(self.style.SUCCESS('Email tests completed!'))
