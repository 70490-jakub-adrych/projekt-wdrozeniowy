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
- Data wysłania: {timezone.now().strftime("%d.%m.%Y %H:%M:%S")}

Wysłane przez: {request.user.username} ({request.user.email})
"""
                
                send_mail(
                    subject=subject,
                    message=full_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient],
                    fail_silently=False,
                )
                
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
