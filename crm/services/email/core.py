"""
Core email functionality for the CRM application.

This module contains basic email sending capabilities used by other specialized modules.
"""

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import logging
import socket
import smtplib

# Configure logger
logger = logging.getLogger(__name__)

def send_email(subject, recipient, text_content, html_content):
    """
    Central method for sending all emails with consistent formatting
    
    Args:
        subject: Email subject line
        recipient: Email address of recipient
        text_content: Plain text version of email
        html_content: HTML version of email
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        logger.debug(f"Preparing to send email '{subject}' to {recipient}")
        
        # Set socket timeout to avoid hanging on SMTP connections
        default_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(settings.EMAIL_TIMEOUT)
        
        # Create more robust email message with headers to improve deliverability
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient]
        )
        
        # Add helpful headers to reduce chance of being marked as spam
        msg.extra_headers = {
            'X-Application': 'System Helpdesk',
            'X-Priority': '3',  # Normal priority
            'X-Auto-Response-Suppress': 'OOF, DR, RN, NRN, AutoReply',
        }
        
        msg.attach_alternative(html_content, "text/html")
        
        # Debug connection info before sending
        backend_info = f"Using backend: {settings.EMAIL_BACKEND}"
        if 'smtp' in settings.EMAIL_BACKEND.lower():
            backend_info += f" (host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT})"
        logger.debug(backend_info)
        
        # Attempt to send with detailed error logging
        msg.send(fail_silently=False)
        
        # Reset socket timeout
        socket.setdefaulttimeout(default_timeout)
        
        logger.info(f"Email '{subject}' sent to {recipient}")
        return True
    except smtplib.SMTPException as smtp_error:
        logger.error(f"SMTP Error sending '{subject}' to {recipient}: {str(smtp_error)}", exc_info=True)
        return False
    except socket.timeout:
        logger.error(f"Timeout sending email '{subject}' to {recipient} - check SMTP server connectivity")
        return False
    except Exception as e:
        logger.error(f"Failed to send email '{subject}' to {recipient}: {str(e)}", exc_info=True)
        return False
