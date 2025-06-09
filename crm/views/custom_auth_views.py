from django.contrib.auth.views import PasswordResetView
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class CustomPasswordResetForm(PasswordResetForm):
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Override the send_mail method to send HTML emails with proper formatting
        """
        try:
            subject = render_to_string(subject_template_name, context)
            subject = ''.join(subject.splitlines())  # Email subject must be single line
            
            # Render both text and HTML versions
            text_content = render_to_string(email_template_name, context)
            html_content = render_to_string(html_email_template_name or email_template_name, context)
            
            # Create email message with both versions
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            logger.info(f"Password reset email sent to {to_email} in HTML format")
        except Exception as e:
            logger.error(f"Failed to send password reset email: {str(e)}")


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
