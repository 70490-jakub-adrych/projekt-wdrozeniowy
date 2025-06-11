"""
Email service for the CRM application.

This module imports and re-exports all email-related functionality from specialized modules,
ensuring backward compatibility with existing code.
"""

import logging
from django.conf import settings
from .models import Ticket

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
from .email.account import send_account_approved_email
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
    
    # Test utilities
    test_smtp_connection = staticmethod(test_smtp_connection)
    
    @classmethod
    def notify_ticket_stakeholders(cls, notification_type, ticket, triggered_by=None, old_status=None, **kwargs):
        """Notify all stakeholders of a ticket about an update"""
        # Convert status codes to display names for better readability in emails
        if old_status:
            # Convert old_status from code to display name
            old_status_display = dict(Ticket.STATUS_CHOICES).get(old_status, old_status)
            
        # Build basic context shared by all notifications
        context = {
            'ticket': ticket,
            'ticket_url': f"{base_url}{ticket_url}",
            'site_name': settings.SITE_NAME,
            'notification_type': notification_type,
            'old_status': old_status_display if old_status else None,
            # ...existing code...
        }
        
        # ...existing code...
