"""
Email testing functionality.

This module contains utilities for testing email configuration and connectivity.
"""

from django.conf import settings
import logging
import socket
import smtplib

# Configure logger
logger = logging.getLogger(__name__)

def test_smtp_connection():
    """
    Test SMTP server connectivity directly
    
    Returns:
        dict: Dictionary with connection test results
    """
    if 'smtp' not in settings.EMAIL_BACKEND.lower():
        return {
            'success': False, 
            'message': f"Not using SMTP backend: {settings.EMAIL_BACKEND}"
        }
        
    result = {
        'success': False,
        'host': settings.EMAIL_HOST,
        'port': settings.EMAIL_PORT,
        'use_tls': settings.EMAIL_USE_TLS,
        'use_ssl': settings.EMAIL_USE_SSL,
        'username': settings.EMAIL_HOST_USER,
    }
    
    try:
        logger.info(f"Testing SMTP connection to {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
        
        # Choose the appropriate SMTP class based on SSL setting
        smtp_class = smtplib.SMTP_SSL if settings.EMAIL_USE_SSL else smtplib.SMTP
        
        # Set timeout to avoid hanging
        with smtp_class(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10) as server:
            if settings.EMAIL_USE_TLS and not settings.EMAIL_USE_SSL:
                server.starttls()
            
            if settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD:
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                result['auth_success'] = True
                logger.debug("SMTP authentication successful")
            
            # Get server info
            server_info = server.ehlo()
            result['server_info'] = str(server_info[0]) + " - " + str(server_info[1].decode())
            
            result['success'] = True
            result['message'] = "SMTP connection successful"
            logger.info("SMTP connection test successful")
            
    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP authentication failed - check username and password")
        result['message'] = "Authentication failed - check username and password"
    except socket.timeout:
        logger.error(f"Connection to {settings.EMAIL_HOST}:{settings.EMAIL_PORT} timed out")
        result['message'] = f"Connection timed out after {settings.EMAIL_TIMEOUT}s"
    except Exception as e:
        logger.error(f"SMTP connection test failed: {str(e)}", exc_info=True)
        result['message'] = f"Connection failed: {str(e)}"
        
    return result

def test_account_email(user, approved_by=None):
    """
    Test sending an account approval email directly
    
    Args:
        user: User to send test email to
        approved_by: User who approved the account
        
    Returns:
        dict: Dictionary with test results
    """
    from .account import send_account_approved_email
    
    result = {
        'success': False,
        'user_email': user.email if hasattr(user, 'email') else None,
        'backend': settings.EMAIL_BACKEND,
        'host': settings.EMAIL_HOST,
        'port': settings.EMAIL_PORT,
        'use_tls': settings.EMAIL_USE_TLS,
        'use_ssl': settings.EMAIL_USE_SSL,
    }
    
    try:
        logger.info(f"Testing account approval email to {user.email}")
        
        # Call the function directly
        sent = send_account_approved_email(user, approved_by=approved_by)
        
        if sent:
            result['success'] = True
            result['message'] = f"Email sent successfully to {user.email}"
            logger.info(f"Test account email sent successfully to {user.email}")
        else:
            result['message'] = f"Email sending returned False"
            logger.warning(f"Test account email sending returned False")
            
    except Exception as e:
        result['success'] = False
        result['error'] = str(e)
        result['error_type'] = type(e).__name__
        logger.error(f"Error testing account email: {str(e)}", exc_info=True)
        
    return result
