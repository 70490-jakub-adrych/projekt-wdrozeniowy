from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
import logging
import os

logger = logging.getLogger(__name__)

class EmailNotificationService:
    """
    Service for sending email notifications throughout the application
    
    This central service handles all email sending operations to ensure consistent
    formatting, styling, and delivery across the entire application. All emails
    should be sent through this service rather than using Django's send_mail directly.
    """
    
    @staticmethod
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
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            logger.info(f"Email '{subject}' sent to {recipient}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email '{subject}' to {recipient}: {str(e)}")
            return False
    
    @staticmethod
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
    
    @staticmethod
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
            
            # Use the centralized email sending method
            return EmailNotificationService.send_email(
                subject=subject,
                recipient=user.email,
                text_content=text_content,
                html_content=html_content
            )
        except Exception as e:
            logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
            return False
    
    @staticmethod
    def notify_ticket_stakeholders(notification_type, ticket, triggered_by=None, **kwargs):
        """
        Send notification to all stakeholders of a ticket
        
        Args:
            notification_type: Type of notification (created, updated, commented, etc.)
            ticket: The ticket object related to this notification
            triggered_by: User who triggered the action (will not receive notification)
            **kwargs: Additional context data for the email template
            
        Returns:
            bool: True if at least one notification was sent successfully
        """
        try:
            logger.info(f"Starting notification for {notification_type} on ticket #{ticket.id}")
            stakeholders = []
            
            # Always notify the ticket creator if different from triggered_by
            if ticket.created_by != triggered_by:
                stakeholders.append(ticket.created_by)
                logger.debug(f"Added creator {ticket.created_by.username} to stakeholders")
            
            # Notify the assigned agent if exists and different from triggered_by
            if ticket.assigned_to and ticket.assigned_to != triggered_by:
                stakeholders.append(ticket.assigned_to)
                logger.debug(f"Added assignee {ticket.assigned_to.username} to stakeholders")
            
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
                        logger.debug(f"Added agent {profile.user.username} to stakeholders")
            
            # Send notifications to each stakeholder
            results = []
            logger.info(f"Sending {notification_type} notifications to {len(stakeholders)} stakeholders")
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
            sent_count = sum(1 for r in results if r)
            logger.info(f"Successfully sent {sent_count} notifications out of {len(results)}")
            return any(results)
        except Exception as e:
            logger.error(f"Error in notify_ticket_stakeholders: {str(e)}")
            return False

    @staticmethod
    def send_ticket_notification(notification_type, ticket, user, **kwargs):
        """
        Send ticket-related notification to a specific user
        
        Args:
            notification_type: Type of notification (created, updated, commented, etc.)
            ticket: The ticket object related to this notification
            user: User who should receive the notification
            **kwargs: Additional context data for the email template
            
        Returns:
            bool: True if notification was sent successfully
        """
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
                logger.debug(f"No notification settings found for {user.username}, using defaults")
                pass
            except Exception as settings_error:
                logger.warning(f"Error checking notification settings for {user.username}: {settings_error}")
                # Continue with sending notification by default
            
            # Don't send notification to the user who triggered the action
            if 'triggered_by' in kwargs and kwargs['triggered_by'] == user:
                logger.debug(f"Skipping notification to {user.username} (triggered by same user)")
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
            
            # Change this to use the production domain
            site_url = getattr(settings, 'SITE_URL', 'https://betulait.usermd.net')
            
            # Make sure there's no double slash in the path
            ticket_path = f"/tickets/{ticket.id}/"
            if site_url.endswith('/'):
                ticket_path = ticket_path.lstrip('/')
            
            ticket_url = f"{site_url}{ticket_path}"
            
            context = {
                'user': user,
                'ticket': ticket,
                'notification_type': notification_type,
                'site_name': 'System Helpdesk',
                'ticket_url': ticket_url,
                **kwargs
            }
            
            # Log which template we're going to try
            logger.debug(f"Trying to render {notification_type} template for user {user.username}")
            
            # Try to render specific templates for this notification type
            try:
                html_template = f'emails/ticket_{notification_type}.html'
                text_template = f'emails/ticket_{notification_type}.txt'
                
                # Check if template files exist first
                template_dir = os.path.join(settings.BASE_DIR, 'crm', 'templates')
                html_path = os.path.join(template_dir, html_template)
                text_path = os.path.join(template_dir, text_template)
                
                html_exists = os.path.exists(html_path)
                text_exists = os.path.exists(text_path)
                
                if html_exists and text_exists:
                    logger.debug(f"Using specific templates for {notification_type}")
                    html_content = render_to_string(html_template, context)
                    text_content = render_to_string(text_template, context)
                else:
                    # Fall back to generic templates
                    logger.warning(f"Specific template for {notification_type} not found at {html_path}, using generic")
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
                {ticket_url}
                """
                
                html_content = f"""
                <html>
                <body>
                    <h2>{context['site_name']} - Powiadomienie o zgłoszeniu #{ticket.id}</h2>
                    <p>Witaj {user.first_name or user.username}!</p>
                    <p>Nastąpiła zmiana w zgłoszeniu "{ticket.title}" (#{ticket.id}).</p>
                    <p>Typ zmiany: {notification_type}</p>
                    <p><a href="{ticket_url}">Kliknij tutaj, aby zobaczyć szczegóły</a></p>
                </body>
                </html>
                """
            
            try:
                logger.debug(f"Sending email to {user.email} subject: {subject}")
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
    
    @staticmethod
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
