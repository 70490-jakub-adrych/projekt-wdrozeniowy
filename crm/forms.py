from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from .views.helpers import get_client_ip
from .models import (
    UserProfile, Organization, Ticket,
    TicketComment, TicketAttachment, ActivityLog
)
from .validators import phone_regex


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(label="Email")
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': 'Nazwa użytkownika',
        }


class UserProfileForm(forms.ModelForm):
    phone = forms.CharField(max_length=17, required=False, validators=[phone_regex],
                          widget=forms.TextInput(attrs={'placeholder': '+48 123 456 789'}))
    class Meta:
        model = UserProfile
        fields = ['phone', 'organizations']
        labels = {
            'phone': 'Telefon',
            'organizations': 'Organizacje',
        }


class OrganizationForm(forms.ModelForm):
    phone = forms.CharField(max_length=17, required=False, validators=[phone_regex],
                          widget=forms.TextInput(attrs={'placeholder': '+48 123 456 789'}))
    class Meta:
        model = Organization
        fields = ['name', 'email', 'phone', 'website', 'address', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class TicketForm(forms.ModelForm):
    suggested_category = forms.CharField(
        widget=forms.HiddenInput(), 
        required=False
    )
    
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'category', 'priority', 'assigned_to', 'suggested_category']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }


class ModeratorTicketForm(forms.ModelForm):
    suggested_category = forms.CharField(
        widget=forms.HiddenInput(), 
        required=False
    )
    
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'category', 'priority', 'status', 'assigned_to', 'suggested_category']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }


class ClientTicketForm(forms.ModelForm):
    """Formularz dla klientów ograniczający dostępne pola"""
    suggested_category = forms.CharField(
        widget=forms.HiddenInput(), 
        required=False
    )
    
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'category', 'suggested_category']  # Brak pól status i priorytet
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }


class TicketCommentForm(forms.ModelForm):
    class Meta:
        model = TicketComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'content': 'Treść komentarza',
        }


# Define max file size: 20MB
MAX_UPLOAD_SIZE = 20 * 1024 * 1024  # 20MB in bytes

def validate_file_size(value):
    """Validate that file size is under the limit"""
    if value.size > MAX_UPLOAD_SIZE:
        raise ValidationError(f'Rozmiar pliku przekracza limit 20MB. Twój plik ma {value.size/(1024*1024):.2f}MB.')


class TicketAttachmentForm(forms.ModelForm):
    accepted_policy = forms.BooleanField(
        required=True,
        label="Akceptuję politykę prywatności i regulamin dotyczący załączników",
        error_messages={'required': 'Musisz zaakceptować regulamin, aby dodać załącznik.'}
    )
    
    class Meta:
        model = TicketAttachment
        fields = ['file', 'accepted_policy']
        labels = {
            'file': 'Załącznik',
            'accepted_policy': 'Akceptuję politykę prywatności i regulamin'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add the validator to the file field
        self.fields['file'].validators.append(validate_file_size)
        # Update help_text to inform users about the size limit
        self.fields['file'].help_text = f"Maksymalny rozmiar pliku: 20MB."


class CustomAuthenticationForm(AuthenticationForm):
    """Custom authentication form that logs failed login attempts"""
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                # Log the failed login attempt
                ip_address = get_client_ip(self.request)
                ActivityLog.objects.create(
                    user=None,  # No user since login failed
                    action_type='login_failed',
                    description=f"Failed login attempt for username: {username}",
                    ip_address=ip_address
                )
                
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data
