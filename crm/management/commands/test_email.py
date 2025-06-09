from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

class Command(BaseCommand):
    help = 'Send a test email to verify email configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--to',
            type=str,
            help='Email address to send test email to',
        )

    def handle(self, *args, **options):
        recipient = options.get('to') or settings.TEST_EMAIL_RECIPIENT
        
        if not recipient:
            self.stdout.write(
                self.style.ERROR(
                    'No recipient specified. Use --to email@example.com or set TEST_EMAIL_RECIPIENT in .env'
                )
            )
            return

        self.stdout.write(f'Sending test email to: {recipient}')
        self.stdout.write(f'Using email backend: {settings.EMAIL_BACKEND}')
        self.stdout.write(f'SMTP Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}')
        self.stdout.write(f'From email: {settings.DEFAULT_FROM_EMAIL}')
        
        try:
            send_mail(
                subject='Test Email - System Helpdesk',
                message=f'''
Witaj!

To jest testowy email z systemu Helpdesk.

Konfiguracja email:
- Backend: {settings.EMAIL_BACKEND}
- Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}
- TLS: {settings.EMAIL_USE_TLS}
- SSL: {settings.EMAIL_USE_SSL}
- Od: {settings.DEFAULT_FROM_EMAIL}

Data wysłania: {timezone.now().strftime("%d.%m.%Y %H:%M:%S")}

Jeśli otrzymujesz ten email, konfiguracja działa poprawnie!

--
System Helpdesk
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Test email sent successfully to {recipient}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to send test email: {str(e)}')
            )
            self.stdout.write(
                self.style.ERROR(f'Error type: {type(e).__name__}')
            )
