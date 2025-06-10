"""
Password-related email functionality.

This module handles sending password reset, verification, and change notification emails.
"""

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
import socket
import logging

# Configure logger
logger = logging.getLogger(__name__)

def send_password_reset_email(user, subject, email_template_name, html_email_template_name, context):
    """
    Send password reset email with proper HTML formatting
    
    Args:
        user: User object of the recipient
        subject: Subject line of the email
        email_template_name: Path to the plain text template
        html_email_template_name: Path to the HTML template
        context: Template context dictionary containing reset link data
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Render both text and HTML versions of the email
        text_content = render_to_string(email_template_name, context)
        html_content = render_to_string(html_email_template_name, context)
        
        logger.debug(f"Sending password reset email to {user.email} using templates:")
        logger.debug(f"Text template: {email_template_name}")
        logger.debug(f"HTML template: {html_email_template_name}")
        
        # Create and send email with both text and HTML content
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        
        logger.info(f"Password reset email sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
        return False

def send_password_verification_email(user, verification_code):
    """
    Send password change verification code
    
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
            html_content = render_to_string('emails/password_verification_code.html', context)
            text_content = render_to_string('emails/password_verification_code.txt', context)
        except Exception as e:
            logger.error(f"Error rendering password verification email template: {str(e)}")
            # Use hardcoded fallback template
            html_content = f"""
            <html>
            <body>
                <h2>Witaj {user.username}!</h2>
                <p>Twój kod weryfikacyjny do zmiany hasła to: <strong>{verification_code}</strong></p>
                <p>Jeśli nie próbowałeś zmienić hasła, zignoruj tę wiadomość lub skontaktuj się z administratorem.</p>
            </body>
            </html>
            """
            text_content = f"""
            Witaj {user.username}!
            Twój kod weryfikacyjny do zmiany hasła to: {verification_code}
            Jeśli nie próbowałeś zmienić hasła, zignoruj tę wiadomość lub skontaktuj się z administratorem.
            """

        msg = EmailMultiAlternatives(
            subject=f'System Helpdesk - Weryfikacja zmiany hasła',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        
        logger.info(f"Password verification email sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send password verification email to {user.email}: {str(e)}")
        return False

def send_password_changed_notification(user, context=None):
    """
    Send notification about successful password change
    
    Args:
        user: User object of the recipient
        context: Optional additional context for the email template
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        logger.info(f"🔵 PASSWORD CHANGED EMAIL: Starting process for {user.username} ({user.email})")
        
        # Generate password reset URL
        site_url = getattr(settings, 'SITE_URL', 'https://betulait.usermd.net')
        password_reset_url = f"{site_url}/password_reset/"
        
        # Default context
        template_context = {
            'user': user,
            'site_name': 'System Helpdesk',
            'timestamp': timezone.now(),
            'password_reset_url': password_reset_url,
            'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@example.com'),
        }
        
        # Add any additional context
        if context:
            template_context.update(context)
        
        # Try to render email templates
        try:
            logger.info(f"🔵 Attempting to render password change success templates for {user.email}")
            html_content = render_to_string('emails/password_change_success.html', template_context)
            text_content = render_to_string('emails/password_change_success.txt', template_context)
            logger.info("✅ Successfully rendered email templates")
        except Exception as e:
            logger.error(f"❌ Error rendering password change templates: {str(e)}", exc_info=True)
            # Use hardcoded fallback template
            logger.warning("⚠️ Using fallback hardcoded email templates")
            html_content = f"""
            <html>
            <body>
                <h2>Witaj {user.username}!</h2>
                <p>Twoje hasło do systemu Helpdesk zostało pomyślnie zmienione.</p>
                <p>Data zmiany: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Jeśli nie dokonywałeś tej zmiany, skontaktuj się natychmiast z administratorem.</p>
                <p><a href="{password_reset_url}">Kliknij tutaj, aby zresetować hasło</a></p>
            </body>
            </html>
            """
            text_content = f"""
            Witaj {user.username}!
            Twoje hasło do systemu Helpdesk zostało pomyślnie zmienione.
            Data zmiany: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
            Jeśli nie dokonywałeś tej zmiany, skontaktuj się natychmiast z administratorem.
            Możesz zresetować hasło pod adresem: {password_reset_url}
            """

        # Log email details before sending
        logger.info(f"🔵 Preparing to send email to {user.email} about password change")
        logger.info(f"Using email backend: {settings.EMAIL_BACKEND}")
        
        # Create more robust email message with headers to improve deliverability
        msg = EmailMultiAlternatives(
            subject=f'System Helpdesk - Hasło zostało zmienione',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        msg.attach_alternative(html_content, "text/html")
        
        # Add helpful headers for security notifications
        msg.extra_headers = {
            'X-Application': 'System Helpdesk',
            'X-Priority': '1',  # High priority for security notification
            'X-Auto-Response-Suppress': 'OOF, DR, RN, NRN, AutoReply',
            'Precedence': 'high',
            'Importance': 'high',
        }
        
        # Set socket timeout for email sending
        default_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(15)  # Use longer timeout for this critical email
        
        try:
            logger.info(f"🔵 SENDING NOW: Password change notification to {user.email}")
            msg.send(fail_silently=False)
            # Reset socket timeout
            socket.setdefaulttimeout(default_timeout)
            logger.info(f"✅ Password change notification SUCCESSFULLY sent to {user.email}")
            return True
        except Exception as send_error:
            logger.error(f"❌ Failed to send password change notification: {str(send_error)}", exc_info=True)
            # Try again with a different subject (to avoid spam filters)
            try:
                logger.info("🔄 Retrying with alternate subject...")
                msg.subject = "Ważna informacja dotycząca Twojego konta w systemie Helpdesk"
                msg.send(fail_silently=False)
                logger.info(f"✅ Password notification sent with alternate subject to {user.email}")
                return True
            except Exception as retry_error:
                logger.error(f"❌ Second attempt also failed: {str(retry_error)}")
                socket.setdefaulttimeout(default_timeout)
                return False
    except Exception as e:
        logger.error(f"❌ Failed to prepare password notification: {str(e)}", exc_info=True)
        return False
