from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from .models import (
    UserProfile, Organization, Ticket,
    TicketComment, TicketAttachment
)


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(label="Email")
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': 'Nazwa użytkownika',
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'organizations']
        labels = {
            'phone': 'Telefon',
            'organizations': 'Organizacje',
        }


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'email', 'phone', 'website', 'address', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'category', 'priority']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }


class ModeratorTicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'category', 'priority', 'status', 'assigned_to']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }


class ClientTicketForm(forms.ModelForm):
    """Formularz dla klientów ograniczający dostępne pola"""
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'category']  # Brak pól status i priorytet
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
