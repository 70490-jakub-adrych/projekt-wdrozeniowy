from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse
from django import forms
import logging

logger = logging.getLogger(__name__)

class TestEmailForm(forms.Form):
    recipient = forms.EmailField(
        label='Adres email odbiorcy',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'test@example.com'})
    )
    subject = forms.CharField(
        label='Temat',
        initial='Test Email - System Helpdesk',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    message = forms.CharField(
        label='Wiadomość',
        initial='To jest testowy email z systemu Helpdesk.',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5})
    )

@login_required
def test_email_view(request):
    """View for testing email configuration (admin only)"""
    if request.user.profile.role != 'admin':
        messages.error(request, 'Tylko administratorzy mogą testować konfigurację email.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = TestEmailForm(request.POST)
        if form.is_valid():
            try:
                recipient = form.cleaned_data['recipient']
                subject = form.cleaned_data['subject']
                message_text = form.cleaned_data['message']
                
                # Add configuration info to message
                full_message = f"""{message_text}

---
Informacje o konfiguracji:
- Backend: {settings.EMAIL_BACKEND}
- Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}
- TLS: {settings.EMAIL_USE_TLS}
- SSL: {settings.EMAIL_USE_SSL}
- Od: {settings.DEFAULT_FROM_EMAIL}
- Data wysłania: {timezone.now().strftime("%d.m.Y %H:%M:%S")}

Wysłane przez: {request.user.username} ({request.user.email})
"""
                
                # Use EmailMultiAlternatives to send HTML version too
                from django.core.mail import EmailMultiAlternatives
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=full_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[recipient]
                )
                
                # Create HTML version with styling
                html_content = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
                        .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
                        .content {{ background-color: #f8f9fa; padding: 30px; border-radius: 0 0 5px 5px; border: 1px solid #dee2e6; }}
                        .info {{ background-color: #e2f0fb; padding: 15px; border-left: 4px solid #17a2b8; margin: 20px 0; }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>Test Email - System Helpdesk</h1>
                    </div>
                    <div class="content">
                        <h2>Witaj!</h2>
                        <p>{message_text}</p>
                        <div class="info">
                            <h3>Informacje o konfiguracji:</h3>
                            <ul>
                                <li><strong>Backend:</strong> {settings.EMAIL_BACKEND}</li>
                                <li><strong>Host:</strong> {settings.EMAIL_HOST}:{settings.EMAIL_PORT}</li>
                                <li><strong>TLS:</strong> {settings.EMAIL_USE_TLS}</li>
                                <li><strong>SSL:</strong> {settings.EMAIL_USE_SSL}</li>
                                <li><strong>Od:</strong> {settings.DEFAULT_FROM_EMAIL}</li>
                                <li><strong>Data wysłania:</strong> {timezone.now().strftime("%d.m.Y %H:%M:%S")}</li>
                            </ul>
                            <p>Wysłane przez: {request.user.username} ({request.user.email})</p>
                        </div>
                    </div>
                </body>
                </html>
                """
                msg.attach_alternative(html_content, "text/html")
                msg.send(fail_silently=False)
                
                logger.info(f"Test email sent successfully to {recipient} by {request.user.username}")
                messages.success(request, f'Email testowy został wysłany pomyślnie na adres: {recipient}')
                
                # If AJAX request, return JSON response
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'Email wysłany pomyślnie na {recipient}'
                    })
                    
            except Exception as e:
                error_msg = f'Błąd podczas wysyłania emaila: {str(e)}'
                logger.error(f"Failed to send test email: {str(e)}")
                messages.error(request, error_msg)
                
                # If AJAX request, return JSON response
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': error_msg
                    })
    else:
        # Pre-fill form with admin's email if available
        initial_data = {}
        if request.user.email:
            initial_data['recipient'] = request.user.email
        form = TestEmailForm(initial=initial_data)
    
    # Get current email configuration for display
    email_config = {
        'backend': settings.EMAIL_BACKEND,
        'host': settings.EMAIL_HOST,
        'port': settings.EMAIL_PORT,
        'use_tls': settings.EMAIL_USE_TLS,
        'use_ssl': settings.EMAIL_USE_SSL,
        'from_email': settings.DEFAULT_FROM_EMAIL,
        'host_user': settings.EMAIL_HOST_USER,
    }
    
    return render(request, 'crm/admin/test_email.html', {
        'form': form,
        'email_config': email_config
    })
