"""
Account-related email functionality.

This module handles sending emails related to account status changes,
such as approval, rejection, etc.
"""

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import logging
import os
import socket
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
    logger.info(f"🔶 ACCOUNT APPROVAL EMAIL: Starting process for {user.username} ({user.email})")
    logger.info(f"🔶 Email backend: {settings.EMAIL_BACKEND}")
    
    start_time = time.time()
    
    try:
        # Check if user is valid
        if not user or not hasattr(user, 'email') or not user.email:
            logger.error("❌ Invalid user provided to send_account_approved_email")
            return False
            
        # Generate login URL
        site_url = getattr(settings, 'SITE_URL', 'https://betulait.usermd.net')
        login_url = f"{site_url}/login/"
        logger.debug(f"Login URL generated: {login_url}")
        
        context = {
            'user': user,
            'approved_by': approved_by,
            'site_name': 'System Helpdesk',
            'login_url': login_url,
        }
        
        # Check if templates exist
        template_dir = os.path.join(settings.BASE_DIR, 'crm', 'templates')
        html_template = 'emails/account_approved.html'
        text_template = 'emails/account_approved.txt'
        
        html_path = os.path.join(template_dir, html_template)
        text_path = os.path.join(template_dir, text_template)
        
        html_exists = os.path.exists(html_path)
        text_exists = os.path.exists(text_path)
        
        logger.info(f"Template paths - HTML: {html_path} (exists: {html_exists}), Text: {text_path} (exists: {text_exists})")
        
        try:
            logger.debug(f"Attempting to render templates for {user.email}")
            if html_exists and text_exists:
                html_content = render_to_string(html_template, context)
                text_content = render_to_string(text_template, context)
                logger.info(f"✅ Successfully rendered account approval templates")
            else:
                # Use fallback templates if files don't exist
                logger.warning(f"⚠️ Templates not found, using fallback templates")
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
        except Exception as e:
            logger.error(f"❌ Error rendering account approval templates: {str(e)}", exc_info=True)
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
        
        logger.debug(f"Creating email message for {user.email}")
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
        
        # Set a longer timeout for this operation
        default_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(10)  # 10 seconds
        
        try:
            logger.info(f"🔶 SENDING NOW: Account approval notification to {user.email}")
            msg.send(fail_silently=False)
            elapsed_time = time.time() - start_time
            logger.info(f"✅ Account approval notification SUCCESSFULLY sent to {user.email} in {elapsed_time:.2f}s")
            socket.setdefaulttimeout(default_timeout)
            return True
        except Exception as send_error:
            logger.error(f"❌ Failed to send email: {str(send_error)}", exc_info=True)
            # Try again with a different approach
            try:
                logger.info("🔄 Retrying with direct Django send_mail...")
                from django.core.mail import send_mail
                send_mail(
                    subject=f'System Helpdesk - Konto zatwierdzone',
                    message=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                    html_message=html_content
                )
                logger.info(f"✅ Account approval notification sent on second attempt to {user.email}")
                return True
            except Exception as retry_error:
                logger.error(f"❌ Second attempt also failed: {str(retry_error)}")
                socket.setdefaulttimeout(default_timeout)
                return False
            
    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(f"❌ Failed to send account approval email to {user.email}: {str(e)} (after {elapsed_time:.2f}s)", exc_info=True)
        return False
