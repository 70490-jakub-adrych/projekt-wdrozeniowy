from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Ticket

class CustomUserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    company_name = forms.CharField(max_length=255, required=True)
    phone_number = forms.CharField(max_length=20, required=True)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "company_name", "phone_number", "password1", "password2")

class TicketForm(forms.ModelForm):
    attachments = forms.FileField(
        widget=forms.ClearableFileInput(attrs={}),
        required=False
    )
    sensitive_data_warning = forms.BooleanField(
        required=True, 
        label="Potwierdzam, że zapoznałem się z informacją o danych wrażliwych w załączniku."
    )

    class Meta:
        model = Ticket
        fields = ['title', 'problem_group', 'description', 'sensitive_data_warning']

class TicketEditForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'problem_group', 'description', 'status', 'assigned_to']
