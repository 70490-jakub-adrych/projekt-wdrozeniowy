from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class EmailNotificationService:
    """Service for sending email notifications"""
    
    @staticmethod
    def send_verification_email(user, verification_code):
        """Send email verification code to user"""
        subject = 'Kod weryfikacyjny - System Helpdesk'
        
        context = {
            'user': user,
            'verification_code': verification_code,
            'site_name': 'System Helpdesk'
        }
        
        html_content = render_to_string('emails/verification_code.html', context)
        text_content = render_to_string('emails/verification_code.txt', context)
        
        try:
            msg = EmailMultiAlternatives(
                subject=subject,
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
    
    @staticmethod
    def send_ticket_notification(notification_type, ticket, user, **kwargs):
        """Send ticket-related notification"""
        from ..models import EmailNotificationSettings
        
        # Check if user wants this type of notification
        try:
            settings_obj = EmailNotificationSettings.objects.get(user=user)
            notification_field = f'notify_ticket_{notification_type}'
            if not getattr(settings_obj, notification_field, True):
                logger.info(f"User {user.username} has disabled {notification_type} notifications")
                return False
        except EmailNotificationSettings.DoesNotExist:
            # Default to sending notifications if settings don't exist
            pass
        
        # Don't send notification to the user who triggered the action
        if 'triggered_by' in kwargs and kwargs['triggered_by'] == user:
            return False
        
        subject_templates = {
            'created': 'Nowe zgłoszenie #{ticket_id}: {ticket_title}',
            'assigned': 'Zgłoszenie #{ticket_id} zostało Ci przypisane',
            'status_changed': 'Zmiana statusu zgłoszenia #{ticket_id}: {ticket_title}',
            'commented': 'Nowy komentarz do zgłoszenia #{ticket_id}: {ticket_title}',
            'updated': 'Aktualizacja zgłoszenia #{ticket_id}: {ticket_title}',
            'closed': 'Zgłoszenie #{ticket_id} zostało zamknięte',
            'reopened': 'Zgłoszenie #{ticket_id} zostało ponownie otwarte'
        }
        
        subject = subject_templates.get(notification_type, 'Powiadomienie o zgłoszeniu #{ticket_id}').format(
            ticket_id=ticket.id,
            ticket_title=ticket.title
        )
        
        context = {
            'user': user,
            'ticket': ticket,
            'notification_type': notification_type,
            'site_name': 'System Helpdesk',
            'ticket_url': f"{settings.SITE_URL or 'http://localhost:8000'}/tickets/{ticket.id}/",
            **kwargs
        }
        
        try:
            html_content = render_to_string(f'emails/ticket_{notification_type}.html', context)
            text_content = render_to_string(f'emails/ticket_{notification_type}.txt', context)
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            logger.info(f"Ticket {notification_type} notification sent to {user.email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send ticket {notification_type} notification to {user.email}: {str(e)}")
            return False
    
    @staticmethod
    def send_account_approved_notification(user):
        """Send account approval notification"""
        subject = 'Twoje konto zostało zatwierdzone - System Helpdesk'
        
        context = {
            'user': user,
            'site_name': 'System Helpdesk',
            'login_url': f"{settings.SITE_URL or 'http://localhost:8000'}/login/"
        }
        
        try:
            html_content = render_to_string('emails/account_approved.html', context)
            text_content = render_to_string('emails/account_approved.txt', context)
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            logger.info(f"Account approved notification sent to {user.email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send account approved notification to {user.email}: {str(e)}")
            return False
    
    @staticmethod
    def notify_ticket_stakeholders(notification_type, ticket, triggered_by=None, **kwargs):
        """Notify all stakeholders of a ticket about changes"""
        stakeholders = set()
        
        # Always notify ticket creator
        if ticket.created_by and ticket.created_by.email:
            stakeholders.add(ticket.created_by)
        
        # Always notify assigned agent
        if ticket.assigned_to and ticket.assigned_to.email:
            stakeholders.add(ticket.assigned_to)
        
        # For new tickets, notify all agents who can handle tickets for this organization
        if notification_type == 'created':
            from ..models import UserProfile
            agents = UserProfile.objects.filter(
                role__in=['admin', 'superagent', 'agent'],
                organizations=ticket.organization,
                user__email__isnull=False
            ).exclude(user__email='')
            
            for profile in agents:
                stakeholders.add(profile.user)
        
        # Remove the user who triggered the action
        if triggered_by:
            stakeholders.discard(triggered_by)
        
        # Send notifications
        success_count = 0
        for user in stakeholders:
            if EmailNotificationService.send_ticket_notification(
                notification_type, ticket, user, triggered_by=triggered_by, **kwargs
            ):
                success_count += 1
        
        logger.info(f"Sent {success_count} {notification_type} notifications for ticket {ticket.id}")
        return success_count
