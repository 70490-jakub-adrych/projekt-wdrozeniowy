"""
Account-related email functionality.

This module handles sending emails related to account status changes,
such as approval, rejection, etc.
"""

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import logging
import time

# Configure logger
logger = logging.getLogger(__name__)

def send_account_approved_email(user, approved_by=None):
    """
    Send notification to a user when their account is approved
    
    Args:
        user: User object whose account was approved
        approved_by: User object who approved the account (optional)
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        logger.info(f"Starting account approval notification to {user.email}")
        
        # Generate login URL
        site_url = getattr(settings, 'SITE_URL', 'https://betulait.usermd.net')
        login_url = f"{site_url}/login/"
        
        context = {
            'user': user,
            'approved_by': approved_by,
            'site_name': 'System Helpdesk',
            'login_url': login_url,
        }
        
        try:
            html_content = render_to_string('emails/account_approved.html', context)
            text_content = render_to_string('emails/account_approved.txt', context)
            logger.info(f"Successfully rendered account approval templates for {user.email}")
        except Exception as e:
            logger.error(f"Error rendering account approval templates: {str(e)}", exc_info=True)
            # Fallback to simple content if template rendering fails
            html_content = f"""
            <html>
            <body>
                <h2>Witaj {user.username}!</h2>
                <p>Twoje konto w systemie Helpdesk zostało zatwierdzone.</p>
                <p>Możesz teraz zalogować się i korzystać z pełnej funkcjonalności systemu.</p>
                <p><a href="{login_url}">Zaloguj się</a></p>
            </body>
            </html>
            """
            text_content = f"""
            Witaj {user.username}!
            
            Twoje konto w systemie Helpdesk zostało zatwierdzone.
            Możesz teraz zalogować się i korzystać z pełnej funkcjonalności systemu.
            
            Aby się zalogować, odwiedź: {login_url}
            """
        
        msg = EmailMultiAlternatives(
            subject=f'System Helpdesk - Konto zatwierdzone',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        msg.attach_alternative(html_content, "text/html")
        
        # Add helpful headers
        msg.extra_headers = {
            'X-Application': 'System Helpdesk',
            'X-Priority': '3',  # Normal priority
            'X-Auto-Response-Suppress': 'OOF, DR, RN, NRN, AutoReply',
        }
        
        msg.send(fail_silently=False)
        logger.info(f"Account approval notification sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send account approval email to {user.email}: {str(e)}", exc_info=True)
        return False


def send_new_user_notification_to_admins(user):
    """
    Send notification to admins/superagents when a new user registers and needs approval
    
    Args:
        user: User object who just registered
        
    Returns:
        bool: True if at least one notification was sent successfully
    """
    try:
        logger.info(f"Starting new user notification for {user.email}")
        
        # Get all admins, superagents, and agents who should be notified
        from ...models import UserProfile
        
        recipients = UserProfile.objects.filter(
            role__in=['admin', 'superagent', 'agent'],
            user__is_active=True
        ).select_related('user')
        
        if not recipients.exists():
            logger.warning("No admins/superagents/agents found to notify about new user")
            return False
        
        # Generate approval URL
        site_url = getattr(settings, 'SITE_URL', 'https://betulait.usermd.net')
        approval_url = f"{site_url}/approvals/"
        
        context = {
            'new_user': user,
            'site_name': 'System Helpdesk',
            'approval_url': approval_url,
        }
        
        success_count = 0
        recipients_list = list(recipients)
        
        for index, recipient_profile in enumerate(recipients_list):
            recipient = recipient_profile.user
            
            # Skip if no email
            if not recipient.email:
                logger.warning(f"Skipping {recipient.username} - no email address")
                continue
            
            try:
                # Add recipient info to context
                context['recipient'] = recipient
                
                html_content = render_to_string('emails/new_user_pending_approval.html', context)
                text_content = render_to_string('emails/new_user_pending_approval.txt', context)
                
                msg = EmailMultiAlternatives(
                    subject=f'System Helpdesk - Nowy użytkownik oczekuje na zatwierdzenie',
                    body=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[recipient.email]
                )
                msg.attach_alternative(html_content, "text/html")
                
                # Add helpful headers
                msg.extra_headers = {
                    'X-Application': 'System Helpdesk',
                    'X-Priority': '3',
                    'X-Auto-Response-Suppress': 'OOF, DR, RN, NRN, AutoReply',
                }
                
                msg.send(fail_silently=False)
                logger.info(f"New user notification sent to {recipient.email}")
                success_count += 1
                
                # Add 5 second delay between emails to avoid spam detection (except for last email)
                if index < len(recipients_list) - 1:
                    time.sleep(5)
                
            except Exception as e:
                logger.error(f"Failed to send new user notification to {recipient.email}: {str(e)}")
                continue
        
        logger.info(f"Sent new user notification to {success_count}/{recipients.count()} recipients")
        return success_count > 0
        
    except Exception as e:
        logger.error(f"Error in send_new_user_notification_to_admins: {str(e)}", exc_info=True)
        return False
