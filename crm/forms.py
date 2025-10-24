from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from .views.helpers import get_client_ip
from .models import (
    UserProfile, Organization, Ticket,
    TicketComment, TicketAttachment, ActivityLog, EmailVerification
)
from .validators import phone_regex
import logging  # Add this import

# Configure logger
logger = logging.getLogger(__name__)  # Add this line


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        label="Email",
        required=True,
        help_text="Podaj aktywny adres email - wyślemy na niego kod weryfikacyjny"
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Użytkownik z tym adresem email już istnieje.")
        return email

class EmailVerificationForm(forms.Form):
    verification_code = forms.CharField(
        max_length=6,
        min_length=6,
        label="Kod weryfikacyjny",
        help_text="Wprowadź 6-cyfrowy kod otrzymany na email",
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center',
            'placeholder': '123456',
            'style': 'font-size: 1.2em; letter-spacing: 0.2em;'
        })
    )
    
    def clean_verification_code(self):
        code = self.cleaned_data.get('verification_code')
        if not code.isdigit():
            raise ValidationError("Kod weryfikacyjny musi składać się z cyfr.")
        return code


class UserProfileForm(forms.ModelForm):
    phone = forms.CharField(max_length=17, required=False, validators=[phone_regex],
                          widget=forms.TextInput(attrs={'placeholder': '+48 123 456 789'}))
    class Meta:
        model = UserProfile
        fields = ['phone']  # Remove 'organizations' field from registration
        labels = {
            'phone': 'Telefon',
        }

    def __init__(self, *args, **kwargs):
        # Add option to include organizations field for admin/approval context
        include_organizations = kwargs.pop('include_organizations', False)
        super().__init__(*args, **kwargs)
        
        if include_organizations:
            self.fields['organizations'] = forms.ModelMultipleChoiceField(
                queryset=Organization.objects.all(),
                required=False,
                label='Organizacje',
            )
            self.Meta.fields.append('organizations')


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
    title = forms.CharField(
        label="Tytuł",
        min_length=8,
        max_length=255,
        error_messages={
            'min_length': 'Tytuł powinien zawierać minimum 8 znaków, aby dokładnie opisać problem.'
        }
    )
    description = forms.CharField(
        label="Opis",
        min_length=20, 
        widget=forms.Textarea(attrs={'rows': 5}),
        error_messages={
            'min_length': 'Opis powinien zawierać minimum 20 znaków, aby umożliwić analizę problemu.'
        }
    )
    suggested_category = forms.CharField(
        widget=forms.HiddenInput(), 
        required=False
    )
    
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'category', 'priority', 'assigned_to', 'suggested_category']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit assigned_to field to only show admins, superagents, and agents
        from django.contrib.auth.models import User
        self.fields['assigned_to'].queryset = User.objects.filter(
            profile__role__in=['admin', 'superagent', 'agent']
        ).select_related('profile').order_by('username')
        self.fields['assigned_to'].label_from_instance = lambda obj: (
            f"{obj.username} ({obj.get_full_name() or obj.email}) - "
            f"{'Administrator' if obj.profile.role == 'admin' else 'Superagent' if obj.profile.role == 'superagent' else 'Agent'}"
        )


class ModeratorTicketForm(forms.ModelForm):
    title = forms.CharField(
        label="Tytuł",
        min_length=8,
        max_length=255,
        error_messages={
            'min_length': 'Tytuł powinien zawierać minimum 8 znaków, aby dokładnie opisać problem.'
        }
    )
    description = forms.CharField(
        label="Opis",
        min_length=20, 
        widget=forms.Textarea(attrs={'rows': 5}),
        error_messages={
            'min_length': 'Opis powinien zawierać minimum 20 znaków, aby umożliwić analizę problemu.'
        }
    )
    suggested_category = forms.CharField(
        widget=forms.HiddenInput(), 
        required=False
    )
    
    STATUS_CHOICES_WITHOUT_WAITING = (
        ('new', 'Nowe'),
        ('in_progress', 'W trakcie'),
        ('unresolved', 'Nierozwiązany'),
        ('resolved', 'Rozwiązane'),
        ('closed', 'Zamknięte'),
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES_WITHOUT_WAITING,
        label="Status"
    )
    
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'category', 'priority', 'status', 'assigned_to', 'suggested_category']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit assigned_to field to only show admins, superagents, and agents
        from django.contrib.auth.models import User
        self.fields['assigned_to'].queryset = User.objects.filter(
            profile__role__in=['admin', 'superagent', 'agent']
        ).select_related('profile').order_by('username')
        self.fields['assigned_to'].label_from_instance = lambda obj: (
            f"{obj.username} ({obj.get_full_name() or obj.email}) - "
            f"{'Administrator' if obj.profile.role == 'admin' else 'Superagent' if obj.profile.role == 'superagent' else 'Agent'}"
        )


class ClientTicketForm(forms.ModelForm):
    """Formularz dla klientów ograniczający dostępne pola"""
    title = forms.CharField(
        label="Tytuł",
        min_length=8,
        max_length=255,
        error_messages={
            'min_length': 'Tytuł powinien zawierać minimum 8 znaków, aby dokładnie opisać problem.'
        }
    )
    description = forms.CharField(
        label="Opis",
        min_length=20, 
        widget=forms.Textarea(attrs={'rows': 5}),
        error_messages={
            'min_length': 'Opis powinien zawierać minimum 20 znaków, aby umożliwić analizę problemu i sugestię kategorii.'
        }
    )
    suggested_category = forms.CharField(
        widget=forms.HiddenInput(), 
        required=False
    )
    
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'category', 'suggested_category']  # Brak pól status i priorytet


class TicketCommentForm(forms.ModelForm):
    class Meta:
        model = TicketComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'content': 'Treść odpowiedzi',
        }


# Define max file size: 20MB
MAX_UPLOAD_SIZE = 20 * 1024 * 1024  # 20MB in bytes

def validate_file_size(value):
    """Validate that file size is under the limit"""
    if value.size > MAX_UPLOAD_SIZE:
        raise ValidationError(f'Rozmiar pliku przekracza limit 20MB. Twój plik ma {value.size/(1024*1024):.2f}MB.')


class TicketAttachmentForm(forms.ModelForm):
    file = forms.FileField(
        required=False,
        label='Załączniki (opcjonalnie)',
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
        help_text='Możesz wybrać wiele plików jednocześnie'
    )
    accepted_policy = forms.BooleanField(
        required=False,  # Changed to False, validation will be handled in clean()
        label="Akceptuję politykę prywatności i regulamin dotyczący załączników",
        error_messages={'required': 'Musisz zaakceptować regulamin, aby dodać załącznik.'}
    )
    
    class Meta:
        model = TicketAttachment
        fields = ['file', 'accepted_policy']
        labels = {
            'file': 'Załączniki (opcjonalnie)',
            'accepted_policy': 'Akceptuję politykę prywatności i regulamin'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add the validator to the file field
        self.fields['file'].validators.append(validate_file_size)
        # Update help_text to inform users about the size limit
        self.fields['file'].help_text = f"Maksymalny rozmiar pliku: 20MB."
        # Make file field optional
        self.fields['file'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        accepted_policy = cleaned_data.get('accepted_policy')
        
        # Only require policy acceptance if a file is uploaded
        if file and not accepted_policy:
            self.add_error(
                'accepted_policy', 
                'Musisz zaakceptować regulamin, aby dodać załącznik.'
            )
        
        return cleaned_data


class CustomAuthenticationForm(AuthenticationForm):
    """Custom authentication form that logs failed login attempts"""
    
    def confirm_login_allowed(self, user):
        """Override to allow inactive users with pending email verification"""
        logger.debug(f"confirm_login_allowed check for user {user.username}, active: {user.is_active}")
        
        # Check if user is inactive because of pending email verification
        if not user.is_active:
            logger.debug(f"User {user.username} is inactive, checking if due to pending verification")
            try:
                # Check if there's a pending verification record
                has_verification = hasattr(user, 'emailverification')
                logger.debug(f"User {user.username} has email verification object: {has_verification}")
                
                if has_verification:
                    # User has a verification record, allow authentication
                    logger.info(f"Allowing inactive user {user.username} to authenticate for email verification")
                    return
                    
                # Otherwise, check if the profile exists but email is not verified
                elif hasattr(user, 'profile') and not user.profile.email_verified:
                    logger.info(f"User {user.username} has unverified email, allowing authentication")
                    return
            except Exception as e:
                logger.error(f"Error in confirm_login_allowed for {user.username}: {str(e)}")
            
            logger.warning(f"Inactive user {user.username} denied login - not due to pending verification")
                
        # For all other cases, use the default behavior
        super().confirm_login_allowed(user)
        
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            logger.debug(f"Authenticating user: {username}")
            
            # Check if user exists and is locked
            try:
                user = User.objects.get(username=username)
                logger.debug(f"User {username} found, checking lock status")
                
                if hasattr(user, 'profile') and user.profile.is_locked:
                    # Log the attempt on locked account
                    ip_address = get_client_ip(self.request)
                    logger.warning(f"Login attempt on locked account: {username} from IP: {ip_address}")
                    
                    ActivityLog.objects.create(
                        user=user,
                        action_type='login_failed',
                        description=f"Login attempt on locked account: {username}",
                        ip_address=ip_address
                    )
                    raise forms.ValidationError(
                        "Twoje konto zostało zablokowane z powodu zbyt wielu nieudanych prób logowania. "
                        "Skontaktuj się ze swoim agentem, aby odblokować konto.",
                        code='account_locked',
                    )
                    
                # Check if the user is inactive but has an EmailVerification record
                if not user.is_active:
                    logger.debug(f"User {username} is inactive, checking if due to pending verification")
                    # Just log here, actual authentication will happen below
            
            except User.DoesNotExist:
                logger.debug(f"User does not exist: {username}")
                pass  # User doesn't exist, continue with normal authentication
            
            # Try to authenticate the user
            self.user_cache = authenticate(self.request, username=username, password=password)
            
            if self.user_cache is None:
                # Handle failed authentication
                logger.debug(f"Authentication failed for user: {username}")
                ip_address = get_client_ip(self.request)
                
                # Try to get user and increment failed attempts
                try:
                    user = User.objects.get(username=username)
                    if hasattr(user, 'profile'):
                        user.profile.increment_failed_login()
                        
                        # Log the failed attempt with current count
                        ActivityLog.objects.create(
                            user=user,
                            action_type='login_failed',
                            description=f"Failed login attempt #{user.profile.failed_login_attempts} for username: {username}",
                            ip_address=ip_address
                        )
                        
                        # If account was just locked, log that too
                        if user.profile.is_locked:
                            ActivityLog.objects.create(
                                user=user,
                                action_type='account_locked',
                                description=f"Account locked after 5 failed login attempts",
                                ip_address=ip_address
                            )
                    else:
                        # Log failed attempt for user without profile
                        ActivityLog.objects.create(
                            user=None,
                            action_type='login_failed',
                            description=f"Failed login attempt for username: {username}",
                            ip_address=ip_address
                        )
                except User.DoesNotExist:
                    # Log failed attempt for non-existent user
                    ActivityLog.objects.create(
                        user=None,
                        action_type='login_failed',
                        description=f"Failed login attempt for non-existent username: {username}",
                        ip_address=ip_address
                    )
                
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                # Successful authentication - reset failed attempts if not locked
                logger.debug(f"Authentication successful for user: {username}")
                
                if hasattr(self.user_cache, 'profile') and not self.user_cache.profile.is_locked:
                    self.user_cache.profile.reset_failed_login()
                
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

class GroupSelectionForm(forms.Form):
    """Form for selecting a group when approving a user"""
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        label="Przypisz do grupy",
        required=True,
        help_text="Wybierz grupę, do której użytkownik powinien być przypisany.",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    organizations = forms.ModelMultipleChoiceField(
        queryset=Organization.objects.all(),
        label="Przypisz do organizacji",
        required=True,
        help_text="Wybierz organizacje, do których użytkownik powinien mieć dostęp.",
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        # Get available groups that this approver can assign
        available_groups = kwargs.pop('available_groups', None)
        available_organizations = kwargs.pop('available_organizations', None)
        initial_organizations = kwargs.pop('initial_organizations', None)
        super().__init__(*args, **kwargs)
        
        if available_groups is not None:
            self.fields['group'].queryset = available_groups
            
        if available_organizations is not None:
            self.fields['organizations'].queryset = available_organizations
            
        if initial_organizations is not None:
            self.fields['organizations'].initial = initial_organizations

class PasswordChangeVerificationForm(forms.Form):
    """Form for verifying password change with 6-digit code"""
    verification_code = forms.CharField(
        max_length=6,
        min_length=6,
        label="Kod weryfikacyjny",
        help_text="Wprowadź 6-cyfrowy kod otrzymany na email",
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center',
            'placeholder': '123456',
            'style': 'font-size: 1.2em; letter-spacing: 0.2em;'
        })
    )
    
    def clean_verification_code(self):
        code = self.cleaned_data.get('verification_code')
        if not code.isdigit():
            raise ValidationError("Kod weryfikacyjny musi składać się z cyfr.")
        return code

class TOTPVerificationForm(forms.Form):
    """Form for verifying TOTP code during 2FA setup or login"""
    verification_code = forms.CharField(
        max_length=6,
        min_length=6,
        label="Kod weryfikacyjny",
        help_text="Wprowadź 6-cyfrowy kod z aplikacji Google Authenticator",
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center',
            'placeholder': '123456',
            'autocomplete': 'off',
            'inputmode': 'numeric',
            'pattern': '[0-9]*',
            'style': 'font-size: 1.2em; letter-spacing: 0.2em;'
        })
    )
    
    def clean_verification_code(self):
        code = self.cleaned_data.get('verification_code')
        if not code.isdigit():
            raise ValidationError("Kod weryfikacyjny musi składać się tylko z cyfr.")
        return code
