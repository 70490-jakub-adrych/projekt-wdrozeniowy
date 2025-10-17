"""
Email service for the CRM application.

This module imports and re-exports all email-related functionality from specialized modules,
ensuring backward compatibility with existing code.
"""

import logging
from django.conf import settings
from ..models import Ticket  # Fix import path to look in parent directory

# Import from specialized modules
from .email.core import send_email
from .email.verification import send_verification_email
from .email.password import (
    send_password_reset_email,
    send_password_verification_email,
    send_password_changed_notification
)
from .email.ticket import (
    notify_ticket_stakeholders,
    send_ticket_notification
)
from .email.account import send_account_approved_email, send_new_user_notification_to_admins
from .email.test import test_smtp_connection

# Configure logger
logger = logging.getLogger(__name__)

class EmailNotificationService:
    """
    Service for sending email notifications throughout the application
    
    This central service handles all email sending operations to ensure consistent
    formatting, styling, and delivery across the entire application. All emails
    should be sent through this service rather than using Django's send_mail directly.
    """
    
    # Core email functionality
    send_email = staticmethod(send_email)
    
    # Verification emails
    send_verification_email = staticmethod(send_verification_email)
    
    # Password-related emails
    send_password_reset_email = staticmethod(send_password_reset_email)
    send_password_verification_email = staticmethod(send_password_verification_email)
    send_password_changed_notification = staticmethod(send_password_changed_notification)
    
    # Ticket notifications
    notify_ticket_stakeholders = staticmethod(notify_ticket_stakeholders)
    send_ticket_notification = staticmethod(send_ticket_notification)
    
    # Account emails
    send_account_approved_email = staticmethod(send_account_approved_email)
    send_new_user_notification_to_admins = staticmethod(send_new_user_notification_to_admins)
    
    # Test utilities
    test_smtp_connection = staticmethod(test_smtp_connection)
    
    @staticmethod
    def _get_site_name():
        """Get site name from settings or use default value"""
        return getattr(settings, 'EMAIL_DISPLAY_NAME', 'System Helpdesk')
        
    @staticmethod
    def _should_send_notification(user, notification_type):
        """Check if user wants to receive this type of notification"""
        try:
            from ..models import EmailNotificationSettings
            settings_obj = EmailNotificationSettings.objects.get(user=user)
            notification_field = f'notify_ticket_{notification_type}'
            return getattr(settings_obj, notification_field, True)
        except Exception:
            # Default to sending notification if settings check fails
            return True
