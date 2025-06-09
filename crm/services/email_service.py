from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
import logging
import os

logger = logging.getLogger(__name__)

class EmailNotificationService:
    """Service for sending email notifications"""
    
    @staticmethod
    def send_verification_email(user, verification_code):
        """Send email verification code to a newly registered user"""
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
    
    @staticmethod
    def notify_ticket_stakeholders(notification_type, ticket, triggered_by=None, **kwargs):
        """Send notification to all stakeholders of a ticket"""
        try:
            stakeholders = []
            
            # Always notify the ticket creator if different from triggered_by
            if ticket.created_by != triggered_by:
                stakeholders.append(ticket.created_by)
            
            # Notify the assigned agent if exists and different from triggered_by
            if ticket.assigned_to and ticket.assigned_to != triggered_by:
                stakeholders.append(ticket.assigned_to)
            
            # Get agents from the ticket's organization if notification type is 'created'
            if notification_type == 'created':
                from ..models import UserProfile
                agent_profiles = UserProfile.objects.filter(
                    organizations=ticket.organization,
                    role__in=['agent', 'superagent']
                ).exclude(user=triggered_by)
                
                for profile in agent_profiles:
                    if profile.user not in stakeholders:
                        stakeholders.append(profile.user)
            
            # Send notifications to each stakeholder
            results = []
            for user in stakeholders:
                try:
                    result = EmailNotificationService.send_ticket_notification(
                        notification_type, ticket, user, **kwargs
                    )
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error notifying user {user.username} about ticket #{ticket.id}: {str(e)}")
                    results.append(False)
            
            # Return True if at least one notification was sent successfully
            return any(results)
        except Exception as e:
            logger.error(f"Error in notify_ticket_stakeholders: {str(e)}")
            return False

    @staticmethod
    def send_ticket_notification(notification_type, ticket, user, **kwargs):
        """Send ticket-related notification"""
        from ..models import EmailNotificationSettings
        
        try:
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
            except Exception as settings_error:
                logger.warning(f"Error checking notification settings for {user.username}: {settings_error}")
                # Continue with sending notification by default
            
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
            
            site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
            
            context = {
                'user': user,
                'ticket': ticket,
                'notification_type': notification_type,
                'site_name': 'System Helpdesk',
                'ticket_url': f"{site_url}/tickets/{ticket.id}/",
                **kwargs
            }
            
            # Try to render specific templates for this notification type
            try:
                html_template = f'emails/ticket_{notification_type}.html'
                text_template = f'emails/ticket_{notification_type}.txt'
                
                # Check if template files exist first
                html_exists = os.path.exists(os.path.join(settings.BASE_DIR, 'crm', 'templates', html_template))
                text_exists = os.path.exists(os.path.join(settings.BASE_DIR, 'crm', 'templates', text_template))
                
                if html_exists and text_exists:
                    html_content = render_to_string(html_template, context)
                    text_content = render_to_string(text_template, context)
                else:
                    # Fall back to generic templates
                    logger.warning(f"Specific template for {notification_type} not found, using generic")
                    html_content = render_to_string('emails/ticket_generic.html', context)
                    text_content = render_to_string('emails/ticket_generic.txt', context)
                
            except Exception as template_error:
                logger.warning(f"Error rendering email template for {notification_type}: {str(template_error)}")
                # Use simple fallback content if template rendering fails
                text_content = f"""
                {context['site_name']} - Powiadomienie o zgłoszeniu #{ticket.id}
                
                Witaj {user.first_name or user.username}!
                
                Nastąpiła zmiana w zgłoszeniu "{ticket.title}" (#{ticket.id}).
                
                Typ zmiany: {notification_type}
                
                Aby zobaczyć szczegóły, odwiedź:
                {context['ticket_url']}
                """
                
                html_content = f"""
                <html>
                <body>
                    <h2>{context['site_name']} - Powiadomienie o zgłoszeniu #{ticket.id}</h2>
                    <p>Witaj {user.first_name or user.username}!</p>
                    <p>Nastąpiła zmiana w zgłoszeniu "{ticket.title}" (#{ticket.id}).</p>
                    <p>Typ zmiany: {notification_type}</p>
                    <p><a href="{context['ticket_url']}">Kliknij tutaj, aby zobaczyć szczegóły</a></p>
                </body>
                </html>
                """
            
            try:
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
            except Exception as email_error:
                logger.error(f"Failed to send email to {user.email}: {str(email_error)}")
                return False
        
        except Exception as e:
            logger.error(f"Unexpected error in send_ticket_notification: {str(e)}")
            return False
