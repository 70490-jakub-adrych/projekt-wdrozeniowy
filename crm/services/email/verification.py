"""
Email verification functionality.

This module handles sending verification emails during registration and other processes.
"""

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import logging

# Configure logger
logger = logging.getLogger(__name__)

def send_verification_email(user, verification_code):
    """
    Send email verification code to a newly registered user
    
    Args:
        user: User object of the recipient
        verification_code: The verification code to include in the email
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        context = {
            'user': user,
            'verification_code': verification_code,
            'site_name': 'System Helpdesk',
        }
        
        # Try to render email templates
        try:
            html_content = render_to_string('emails/verification_code.html', context)
            text_content = render_to_string('emails/verification_code.txt', context)
        except Exception as e:
            logger.error(f"Error rendering verification email template: {str(e)}")
            # Use hardcoded fallback template
            html_content = f"""
            <html>
            <body>
                <h2>Witaj {user.username}!</h2>
                <p>Twój kod weryfikacyjny to: <strong>{verification_code}</strong></p>
                <p>Wprowadź ten kod, aby potwierdzić swój adres email.</p>
            </body>
            </html>
            """
            text_content = f"""
            Witaj {user.username}!
            Twój kod weryfikacyjny to: {verification_code}
            Wprowadź ten kod, aby potwierdzić swój adres email.
            """

        msg = EmailMultiAlternatives(
            subject=f'System Helpdesk - Weryfikacja adresu email',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        
        logger.info(f"Verification email sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
        return False
