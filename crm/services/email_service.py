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
    
    @staticmethod
    def notify_ticket_stakeholders(notification_type, ticket, triggered_by=None, **context):
        """Send email notifications to all stakeholders of a ticket based on notification type"""
        # Get notification settings and templates
        subject, template = EmailNotificationService._get_ticket_notification_templates(notification_type)
        
        # Add the ticket to the context
        context['ticket'] = ticket
        context['triggered_by'] = triggered_by
        
        # Common URLs
        site_url = settings.SITE_URL
        ticket_url = f"{site_url}/tickets/{ticket.id}/"
        context['ticket_url'] = ticket_url
        context['site_name'] = EmailNotificationService._get_site_name()
        
        # List of recipients
        recipients = []
        
        # Always notify the ticket creator, but not if they triggered the action
        if ticket.created_by != triggered_by:
            recipients.append(ticket.created_by)
        
        # Notify assigned agent if exists and not the one who triggered the action
        if ticket.assigned_to and ticket.assigned_to != triggered_by:
            recipients.append(ticket.assigned_to)
            
        # Find superagents of the ticket's organization and notify them
        from django.contrib.auth.models import Group
        from django.db.models import Q
        
        try:
            # Find users in Superagent group who belong to the ticket's organization
            superagent_group = Group.objects.get(name='Superagent')
            superagents = superagent_group.user_set.filter(
                Q(profile__organizations=ticket.organization) & 
                ~Q(id=triggered_by.id if triggered_by else 0)
            ).distinct()
            
            # Add all superagents to recipients
            recipients.extend(superagents)
        except Group.DoesNotExist:
            pass  # Superagent group doesn't exist
            
        # Send email to each recipient based on their notification preferences
        for recipient in recipients:
            # Skip if user has no email
            if not recipient.email:
                continue
                
            # Check if user wants to receive this type of notification
            if not EmailNotificationService._should_send_notification(recipient, notification_type):
                continue
                
            # Send the actual email
            EmailNotificationService._send_ticket_notification_email(
                recipient, subject, template, ticket, context
            )
        
        return len(recipients) > 0
    
    @staticmethod
    def _send_ticket_notification_email(user, subject, template, ticket, context):
        """Send notification email about ticket to a specific user"""
        # ...existing code...
