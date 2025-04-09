from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Contact, Organization, Deal


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(label="Email")
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': 'Nazwa użytkownika',
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['first_name', 'last_name', 'email', 'phone', 'company', 
                  'lead_source', 'status', 'notes']


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'website', 'address', 'description']


class DealForm(forms.ModelForm):
    class Meta:
        model = Deal
        fields = ['title', 'contact', 'organization', 'value', 'stage', 
                  'expected_close_date', 'description']
        widgets = {
            'expected_close_date': forms.DateInput(attrs={'type': 'date'}),
        }
