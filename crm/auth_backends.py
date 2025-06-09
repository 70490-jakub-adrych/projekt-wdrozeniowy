from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import ActivityLog
import logging
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

logger = logging.getLogger(__name__)

User = get_user_model()

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log user login using Django's built-in signal"""
    # Get client IP
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    # Create activity log entry
    ActivityLog.objects.create(
        user=user,
        action_type='login',
        description=f"User {user.username} logged in",
        ip_address=ip
    )

class EmailOrUsernameModelBackend(ModelBackend):
    """
    Backend that allows authentication with either username or email
    Also allows authentication of inactive users with unverified emails
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Check if this is an email address
            user = User.objects.get(Q(username__iexact=username) | Q(email__iexact=username))
            
            # Check the password
            if user.check_password(password):
                logger.debug(f"Password check successful for user {user.username}")
                
                # Check if user is inactive due to pending email verification
                has_verification = False
                try:
                    has_verification = hasattr(user, 'emailverification') and not user.emailverification.is_verified
                    email_verified = hasattr(user, 'profile') and user.profile.email_verified
                    logger.debug(f"User {user.username}: has_verification={has_verification}, email_verified={email_verified}")
                    
                    if not user.is_active and (has_verification or not email_verified):
                        logger.info(f"Allowing inactive user {user.username} to authenticate for email verification")
                        return user
                except Exception as e:
                    logger.error(f"Error checking verification status: {str(e)}")
                
                # Normal authentication for active users
                if user.is_active:
                    logger.debug(f"User {user.username} is active, authentication successful")
                    return user
                else:
                    logger.warning(f"User {user.username} is inactive and not pending verification")
                    return None
            else:
                logger.debug(f"Password check failed for user {user.username}")
                return None
        except User.DoesNotExist:
            logger.debug(f"No user found with username or email: {username}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in authentication: {str(e)}")
            return None
