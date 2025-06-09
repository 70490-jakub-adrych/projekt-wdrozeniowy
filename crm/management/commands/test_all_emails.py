from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from crm.models import Ticket
from crm.services.email_service import EmailNotificationService

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
            
        self.stdout.write(self.style.SUCCESS('Starting email template tests...'))
        
        # 1. Test all ticket notification types
        notification_types = [
            'created', 'updated', 'commented', 'assigned', 
            'closed', 'reopened', 'status_changed'
        ]
        
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
        
        # 2. Test email verification code
        self.stdout.write('Testing email verification code...')
        verification_success = EmailNotificationService.send_verification_email(user, '123456')
        if verification_success:
            self.stdout.write(self.style.SUCCESS('✅ Successfully sent email verification code'))
        else:
            self.stdout.write(self.style.ERROR('❌ Failed to send email verification code'))
        
        # 3. Test password verification email for password change
        self.stdout.write('Testing password verification email...')
        verification_success = EmailNotificationService.send_password_verification_email(user, '654321')
        if verification_success:
            self.stdout.write(self.style.SUCCESS('✅ Successfully sent password verification email'))
        else:
            self.stdout.write(self.style.ERROR('❌ Failed to send password verification email'))
        
        # 4. Test password change success notification
        self.stdout.write('Testing password change success notification...')
        password_changed_success = EmailNotificationService.send_password_changed_notification(user)
        if password_changed_success:
            self.stdout.write(self.style.SUCCESS('✅ Successfully sent password change success notification'))
        else:
            self.stdout.write(self.style.ERROR('❌ Failed to send password change success notification'))
            
        # 5. Test password reset email with link
        self.stdout.write('Testing password reset email with link...')
        
        # Create password reset context similar to Django's PasswordResetForm
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        
        context = {
            'user': user,
            'uid': uid,
            'token': token,
            'protocol': 'https',
            'domain': settings.SITE_URL.replace('https://', '').replace('http://', '')
        }
        
        # Use our service to send password reset email
        reset_success = EmailNotificationService.send_password_reset_email(
            user=user,
            subject="System Helpdesk - Resetowanie hasła",
            email_template_name='emails/password_reset_email.txt',
            html_email_template_name='emails/password_reset_email.html',
            context=context
        )
        
        if reset_success:
            self.stdout.write(self.style.SUCCESS('✅ Successfully sent password reset email'))
        else:
            self.stdout.write(self.style.ERROR('❌ Failed to send password reset email'))
        
        # 6. Test account approved email
        self.stdout.write('Testing account approved email...')
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
