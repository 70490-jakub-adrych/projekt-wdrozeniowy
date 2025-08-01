from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.db.models.signals import post_save, m2m_changed, post_delete
from django.dispatch import receiver
import os
import uuid
import tempfile
from django.conf import settings
from cryptography.fernet import Fernet
import base64
from datetime import timedelta  # Make sure this import is present and not commented out
from .validators import phone_regex


class UserProfile(models.Model):
    """Model rozszerzający standardowego użytkownika o dodatkowe pola"""
    USER_ROLES = (
        ('admin', 'Administrator'),
        ('superagent', 'Super Agent'),
        ('agent', 'Agent'),
        ('client', 'Klient'),
        ('viewer', 'Przeglądający'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=USER_ROLES, default='client', verbose_name="Rola")
    organizations = models.ManyToManyField('Organization', blank=True, related_name='members', verbose_name="Organizacje")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefon", validators=[phone_regex])
    is_approved = models.BooleanField(default=False, verbose_name="Zatwierdzony")
    email_verified = models.BooleanField(default=False, verbose_name="Email zweryfikowany")
    
    # Add approval tracking fields
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='approved_users', verbose_name="Zatwierdzony przez")
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="Data zatwierdzenia")
    
    # Account locking fields
    failed_login_attempts = models.IntegerField(default=0, verbose_name="Nieudane próby logowania")
    is_locked = models.BooleanField(default=False, verbose_name="Konto zablokowane")
    locked_at = models.DateTimeField(null=True, blank=True, verbose_name="Data blokady")
    
    # Google Authenticator (2FA) fields
    ga_enabled = models.BooleanField(default=False, verbose_name="2FA włączone")
    ga_enabled_on = models.DateTimeField(null=True, blank=True, verbose_name="Data włączenia 2FA")
    ga_last_authenticated = models.DateTimeField(null=True, blank=True, verbose_name="Ostatnie uwierzytelnienie 2FA")
    ga_recovery_hash = models.CharField(max_length=128, blank=True, null=True, verbose_name="Hash kodu odzyskiwania")
    ga_recovery_last_generated = models.DateTimeField(null=True, blank=True, verbose_name="Ostatnia generacja kodu odzyskiwania")
    ga_secret_key = models.CharField(max_length=64, blank=True, null=True, verbose_name="Klucz tajny 2FA")
    device_fingerprint = models.CharField(max_length=255, blank=True, null=True, verbose_name="Odcisk urządzenia")
    trusted_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="Zaufany adres IP")
    trusted_until = models.DateTimeField(null=True, blank=True, verbose_name="Zaufany do")
    
    def lock_account(self):
        """Lock the user account"""
        self.is_locked = True
        self.locked_at = timezone.now()
        self.save()
    
    def unlock_account(self):
        """Unlock the user account and reset failed attempts"""
        self.is_locked = False
        self.locked_at = None
        self.failed_login_attempts = 0
        self.save()
    
    def increment_failed_login(self):
        """Increment failed login attempts and lock if necessary"""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.lock_account()
        else:
            self.save()
    
    def reset_failed_login(self):
        """Reset failed login attempts after successful login"""
        self.failed_login_attempts = 0
        self.save()
        
    def generate_recovery_code(self):
        """Generate a new recovery code for 2FA"""
        import secrets
        import string
        import hashlib
        from django.utils import timezone
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Always generate a new code regardless of previous state
        # Get recovery code length from settings or use default
        from django.conf import settings
        recovery_code_length = getattr(settings, 'GOOGLE_AUTHENTICATOR', {}).get('RECOVERY_CODE_LENGTH', 20)
        
        # Generate a strong recovery code (alphanumeric)
        alphabet = string.ascii_letters + string.digits
        recovery_code = ''.join(secrets.choice(alphabet) for _ in range(recovery_code_length))
        
        # Hash the recovery code for storage
        hashed_code = hashlib.sha256(recovery_code.encode()).hexdigest()
        
        # Store the hash and update timestamp
        self.ga_recovery_hash = hashed_code
        self.ga_recovery_last_generated = timezone.now()
        self.save(update_fields=['ga_recovery_hash', 'ga_recovery_last_generated'])
        
        logger.info(f"Generated new recovery code for user {self.user.username}")
        return True, recovery_code
        
    def verify_recovery_code(self, code):
        """Verify a recovery code and disable 2FA if valid"""
        import hashlib
        
        if not self.ga_recovery_hash:
            return False
        
        # Hash the provided code
        hashed_code = hashlib.sha256(code.encode()).hexdigest()
        
        # Compare with stored hash
        if hashed_code == self.ga_recovery_hash:
            # Disable 2FA upon successful recovery
            self.ga_enabled = False
            self.ga_recovery_hash = None
            self.ga_secret_key = None
            self.trusted_ip = None
            self.trusted_until = None
            self.device_fingerprint = None
            self.save(update_fields=[
                'ga_enabled', 'ga_recovery_hash', 'ga_secret_key',
                'trusted_ip', 'trusted_until', 'device_fingerprint'
            ])
            return True
        
        return False
        
    def needs_2fa_verification(self, request_ip=None):
        """Check if user needs to verify with 2FA based on IP, device and time"""
        if not self.ga_enabled:
            return False
        
        # If no trusted_until or it's expired
        if not self.trusted_until or timezone.now() > self.trusted_until:
            return True
            
        # If IP changed and it's not exempt
        if request_ip and self.trusted_ip and request_ip != self.trusted_ip:
            return True
            
        return False
        
    def set_device_trusted(self, request_ip, fingerprint):
        """Set a device as trusted for 30 days"""
        self.trusted_ip = request_ip
        self.device_fingerprint = fingerprint
        self.trusted_until = timezone.now() + timedelta(days=30)
        self.ga_last_authenticated = timezone.now()
        self.save(update_fields=['trusted_ip', 'device_fingerprint', 
                                'trusted_until', 'ga_last_authenticated'])
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    class Meta:
        verbose_name = "Profil użytkownika"
        verbose_name_plural = "Profile użytkowników"
        indexes = [
            models.Index(fields=['trusted_until'], name='idx_trusted_until'),
            models.Index(fields=['ga_enabled'], name='idx_ga_enabled'),
        ]


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatyczne tworzenie profilu dla nowego użytkownika"""
    if created:
        # Create profile with role based on user type
        role = 'admin' if instance.is_superuser else 'client'
        # Set approved status based on role (admins and superagents are auto-approved)
        is_approved = True if instance.is_superuser else False
        UserProfile.objects.create(
            user=instance, 
            role=role, 
            is_approved=is_approved,
            ga_enabled=False,  # Explicitly set ga_enabled to False for new users
            email_verified=False  # Also ensure email_verified is explicitly set
        )
        
        # Add user to appropriate group based on role
        if role == 'admin':
            group, _ = Group.objects.get_or_create(name='Admin')
            instance.groups.add(group)
        elif role == 'superagent':
            group, _ = Group.objects.get_or_create(name='Superagent')
            instance.groups.add(group)
        elif role == 'agent':
            group, _ = Group.objects.get_or_create(name='Agent')
            instance.groups.add(group)
        elif role == 'viewer':
            group, _ = Group.objects.get_or_create(name='Viewer')
            instance.groups.add(group)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Zapisywanie profilu przy zapisie użytkownika"""
    if hasattr(instance, 'profile'):
        instance.profile.save()


@receiver(m2m_changed, sender=User.groups.through)
def sync_user_groups_with_role(sender, instance, action, **kwargs):
    """Synchronize user role when groups change"""
    if action in ['post_add', 'post_remove', 'post_clear']:
        if hasattr(instance, 'profile'):
            # Set role based on group membership (priority order: admin > superagent > agent > viewer > client)
            if instance.groups.filter(name='Admin').exists():
                instance.profile.role = 'admin'
                instance.profile.is_approved = True
            elif instance.groups.filter(name='Superagent').exists():
                instance.profile.role = 'superagent'  # Make sure this is lowercase to match USER_ROLES
                instance.profile.is_approved = True
                # Force save to ensure the role is updated correctly
                instance.profile.save()
            elif instance.groups.filter(name='Agent').exists():
                instance.profile.role = 'agent'
                instance.profile.is_approved = True
            elif instance.groups.filter(name='Viewer').exists():
                instance.profile.role = 'viewer'
                instance.profile.is_approved = True
            else:
                instance.profile.role = 'client'
                # Don't auto-approve clients
            
            # Save profile without triggering the post_save signal recursively
            UserProfile.objects.filter(pk=instance.profile.pk).update(
                role=instance.profile.role,
                is_approved=instance.profile.is_approved
            )


class Organization(models.Model):
    """Model przechowujący informacje o organizacjach klientów"""
    name = models.CharField(max_length=255, verbose_name="Nazwa")
    email = models.EmailField(blank=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefon", validators=[phone_regex])
    website = models.URLField(blank=True, verbose_name="Strona internetowa")
    address = models.TextField(blank=True, verbose_name="Adres")
    description = models.TextField(blank=True, verbose_name="Opis")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data utworzenia")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Data aktualizacji")
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name = "Organizacja"
        verbose_name_plural = "Organizacje"


class Ticket(models.Model):
    """Model przechowujący informacje o zgłoszeniach"""
    STATUS_CHOICES = (
        ('new', 'Nowe'),
        ('in_progress', 'W trakcie'),
        ('unresolved', 'Nierozwiązany'),  # Renamed from 'waiting' to 'unresolved'
        ('resolved', 'Rozwiązane'),
        ('closed', 'Zamknięte'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Niski'),
        ('medium', 'Średni'),
        ('high', 'Wysoki'),
        ('critical', 'Krytyczny'),
    )
    
    CATEGORY_CHOICES = (
        ('hardware', 'Sprzęt'),
        ('software', 'Oprogramowanie'),
        ('network', 'Sieć'),
        ('account', 'Konto'),
        ('other', 'Inne'),
    )
    
    title = models.CharField(max_length=255, verbose_name="Tytuł")
    description = models.TextField(verbose_name="Opis problemu")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Status")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name="Priorytet")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other', verbose_name="Kategoria")
    created_by = models.ForeignKey(User, related_name='created_tickets', on_delete=models.CASCADE, verbose_name="Utworzony przez")
    assigned_to = models.ForeignKey(User, related_name='assigned_tickets', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Przypisany do")
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE, verbose_name="Organizacja")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data utworzenia")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Data aktualizacji")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="Data rozwiązania")
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name="Data zamknięcia")
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Ustawienie daty rozwiązania/zamknięcia przy zmianie statusu
        if self.pk:
            old_ticket = Ticket.objects.get(pk=self.pk)
            if old_ticket.status != 'resolved' and self.status == 'resolved':
                self.resolved_at = timezone.now()
            if old_ticket.status != 'closed' and self.status == 'closed':
                self.closed_at = timezone.now()
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Zgłoszenie"
        verbose_name_plural = "Zgłoszenia"


class TicketComment(models.Model):
    """Model przechowujący komentarze do zgłoszeń"""
    ticket = models.ForeignKey(Ticket, related_name='comments', on_delete=models.CASCADE, verbose_name="Zgłoszenie")
    author = models.ForeignKey(User, related_name='ticket_comments', on_delete=models.CASCADE, verbose_name="Autor")
    content = models.TextField(verbose_name="Treść")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data utworzenia")
    
    def __str__(self):
        return f"Komentarz do {self.ticket.title} przez {self.author.username}"
    
    class Meta:
        ordering = ['created_at']
        verbose_name = "Komentarz do zgłoszenia"
        verbose_name_plural = "Komentarze do zgłoszeń"


class TicketAttachment(models.Model):
    """Model przechowujący załączniki do zgłoszeń"""
    ticket = models.ForeignKey(Ticket, related_name='attachments', on_delete=models.CASCADE, verbose_name="Zgłoszenie")
    file = models.FileField(upload_to='ticket_attachments/', verbose_name="Plik")
    filename = models.CharField(max_length=255, verbose_name="Nazwa pliku")
    uploaded_by = models.ForeignKey(User, related_name='ticket_attachments', on_delete=models.CASCADE, verbose_name="Dodany przez")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Data dodania")
    encryption_key = models.BinaryField(blank=True, null=True, verbose_name="Klucz szyfrowania")
    accepted_policy = models.BooleanField(default=False, verbose_name="Zaakceptowano regulamin")
    
    def save(self, *args, **kwargs):
        # Generate encryption key if it doesn't exist
        if not self.encryption_key:
            # Generate a random key for this file
            self.encryption_key = Fernet.generate_key()
            
            if self.file and hasattr(self.file, 'file'):
                # Read the file content
                self.file.file.seek(0)
                file_content = self.file.file.read()
                
                # Encrypt the content
                fernet = Fernet(self.encryption_key)
                encrypted_content = fernet.encrypt(file_content)
                
                # Create a temporary file with encrypted content using tempfile module
                fd, temp_path = tempfile.mkstemp()
                try:
                    with os.fdopen(fd, 'wb') as temp_file:
                        temp_file.write(encrypted_content)
                    
                    # Replace the file with encrypted version
                    with open(temp_path, 'rb') as f:
                        self.file.save(self.file.name, f, save=False)
                        
                finally:
                    # Clean up the temp file
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
        
        super().save(*args, **kwargs)
    
    def get_decrypted_content(self):
        """Return decrypted content of the file"""
        if self.encryption_key:
            fernet = Fernet(self.encryption_key)
            
            # Read the encrypted content
            self.file.open('rb')
            encrypted_content = self.file.read()
            self.file.close()
            
            # Decrypt and return
            return fernet.decrypt(encrypted_content)
        
        # If no encryption key, return the file as is
        self.file.open('rb')
        content = self.file.read()
        self.file.close()
        return content
    
    def __str__(self):
        return self.filename
    
    class Meta:
        verbose_name = "Załącznik do zgłoszenia"
        verbose_name_plural = "Załączniki do zgłoszeń"


class ActivityLog(models.Model):
    """Model przechowujący logi aktywności w systemie"""
    ACTION_TYPES = (
        ('login', 'Zalogowanie'),
        ('logout', 'Wylogowanie'),
        ('login_failed', 'Nieudane logowanie'),
        ('account_locked', 'Blokada konta'),
        ('account_unlocked', 'Odblokowanie konta'),
        ('ticket_created', 'Utworzenie'),
        ('ticket_updated', 'Aktualizacja'),
        ('ticket_commented', 'Komentarz'),
        ('ticket_resolved', 'Rozwiązanie'),
        ('ticket_closed', 'Zamknięcie'),
        ('ticket_reopened', 'Wznowienie'),
        ('preferences_updated', 'Aktualizacja preferencji'),
        ('password_changed', 'Zmiana hasła'),
        ('404_error', 'Błąd 404 - Strona nie znaleziona'),
        ('403_error', 'Błąd 403 - Brak dostępu'),
        ('ticket_attachment_added', 'Dodano załącznik'),
        ('logs_wiped', 'Wyczyszczono logi'),  # Add new action type for log wiping
    )
    
    user = models.ForeignKey(User, related_name='activities', on_delete=models.SET_NULL, 
                            null=True, blank=True, verbose_name="Użytkownik")
    action_type = models.CharField(max_length=30, choices=ACTION_TYPES, verbose_name="Typ akcji")
    ticket = models.ForeignKey(Ticket, related_name='activities', on_delete=models.SET_NULL, 
                              null=True, blank=True, verbose_name="Zgłoszenie")
    description = models.TextField(blank=True, verbose_name="Opis")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Adres IP")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data")
    
    def __str__(self):
        username = self.user.username if self.user else "Anonimowy"
        return f"{self.get_action_type_display()} - {username} - {self.created_at}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Log aktywności"
        verbose_name_plural = "Logi aktywności"


class UserPreference(models.Model):
    """Model przechowujący preferencje użytkownika"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    show_closed_tickets = models.BooleanField(default=False, verbose_name="Pokaż zamknięte zgłoszenia")
    items_per_page = models.IntegerField(default=10, verbose_name="Elementów na stronę")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Preferencje użytkownika {self.user.username}"
    
    class Meta:
        verbose_name = "Preferencja użytkownika"
        verbose_name_plural = "Preferencje użytkownika"


@receiver(post_save, sender=User)
def create_user_preferences(sender, instance, created, **kwargs):
    """Automatyczne tworzenie preferencji dla nowego użytkownika"""
    if created:
        UserPreference.objects.create(user=instance)


class ViewPermission(models.Model):
    """Model defining which views (pages) are accessible to users"""
    VIEW_CHOICES = (
        ('dashboard', 'Panel główny'),
        ('tickets', 'Zgłoszenia'),
        ('organizations', 'Organizacje'),
        ('approvals', 'Zatwierdzanie kont'),
        ('logs', 'Logi'),
        ('admin_panel', 'Panel admina'),
    )
    
    name = models.CharField(max_length=30, choices=VIEW_CHOICES, unique=True, verbose_name="Nazwa widoku")
    description = models.CharField(max_length=255, verbose_name="Opis")
    
    def __str__(self):
        return self.get_name_display()
    
    class Meta:
        verbose_name = "Uprawnienie do widoku"
        verbose_name_plural = "Uprawnienia do widoków"


class GroupViewPermission(models.Model):
    """Connects groups with allowed views"""
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='view_permissions', verbose_name="Grupa")
    view = models.ForeignKey(ViewPermission, on_delete=models.CASCADE, verbose_name="Widok")
    
    class Meta:
        unique_together = ('group', 'view')
        verbose_name = "Uprawnienie grupy do widoku"
        verbose_name_plural = "Uprawnienia grup do widoków"


class UserViewPermission(models.Model):
    """Additional view permissions for individual users beyond their group permissions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='extra_view_permissions', verbose_name="Użytkownik")
    view = models.ForeignKey(ViewPermission, on_delete=models.CASCADE, verbose_name="Widok")
    is_granted = models.BooleanField(default=True, verbose_name="Przyznane")
    
    class Meta:
        unique_together = ('user', 'view')
        verbose_name = "Dodatkowe uprawnienie użytkownika"
        verbose_name_plural = "Dodatkowe uprawnienia użytkowników"


# Update GroupSettings to include default view permissions
class GroupSettings(models.Model):
    """Extension for Django Group model to add additional settings"""
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='settings')
    allow_multiple_organizations = models.BooleanField(
        default=False, 
        verbose_name="Zezwól na wiele organizacji",
        help_text="Jeśli zaznaczone, użytkownicy w tej grupie mogą być przypisani do więcej niż jednej organizacji."
    )
    show_statistics = models.BooleanField(
        default=False,
        verbose_name="Pokaż statystyki",
        help_text="Jeśli zaznaczone, użytkownicy w tej grupie mają dostęp do panelu statystyk."
    )
    exempt_from_2fa = models.BooleanField(
        default=False,
        verbose_name="Zwolnij z 2FA",
        help_text="Jeśli zaznaczone, użytkownicy w tej grupie nie będą musieli konfigurować uwierzytelniania dwuskładnikowego."
    )
    show_navbar = models.BooleanField(
        default=True,
        verbose_name="Pokaż pasek nawigacyjny",
        help_text="Jeśli zaznaczone, użytkownicy w tej grupie będą widzieć górny pasek nawigacyjny. Jeśli odznaczone, pasek będzie ukryty."
    )
    attachments_access_level = models.CharField(
        max_length=20,
        choices=[
            ('own', 'Tylko własne załączniki'),
            ('organization', 'Załączniki organizacji'),
            ('all', 'Wszystkie załączniki'),
        ],
        default='own',
        verbose_name="Poziom dostępu do załączników",
        help_text="Określa, które załączniki użytkownicy w tej grupie mogą przeglądać."
    )
    
    # Ticket assignment permissions
    can_assign_unassigned_tickets = models.BooleanField(
        default=True,
        verbose_name="Może przypisywać nieprzydzielone zgłoszenia do siebie",
        help_text="Jeśli zaznaczone, użytkownicy w tej grupie mogą przypisywać do siebie nieprzydzielone zgłoszenia."
    )
    can_assign_tickets_to_others = models.BooleanField(
        default=False,
        verbose_name="Może przypisywać zgłoszenia innym użytkownikom",
        help_text="Jeśli zaznaczone, użytkownicy w tej grupie mogą przypisywać zgłoszenia innym użytkownikom w ich organizacji."
    )
    can_reassign_assigned_tickets = models.BooleanField(
        default=False,
        verbose_name="Może zmieniać przypisanie już przypisanych zgłoszeń",
        help_text="Jeśli zaznaczone, użytkownicy w tej grupie mogą zmieniać przypisanie zgłoszeń, które są już do kogoś przypisane."
    )
    can_unassign_own_tickets = models.BooleanField(
        default=False,
        verbose_name="Może cofać przypisanie własnych zgłoszeń",
        help_text="Jeśli zaznaczone, użytkownicy w tej grupie mogą cofać przypisanie zgłoszeń, które są do nich przypisane."
    )
    
    # Ticket management permissions
    can_see_edit_button = models.BooleanField(
        default=False,
        verbose_name="Może widzieć przycisk edycji dla wszystkich zgłoszeń",
        help_text="Jeśli zaznaczone, użytkownicy w tej grupie widzą przycisk edycji dla wszystkich zgłoszeń."
    )
    can_edit_own_tickets = models.BooleanField(
        default=False,
        verbose_name="Może edytować swoje zgłoszenia",
        help_text="Jeśli zaznaczone, użytkownicy w tej grupie mogą edytować zgłoszenia, które sami utworzyli."
    )
    can_close_assigned_tickets = models.BooleanField(
        default=False,
        verbose_name="Może oznaczać zgłoszenia jako rozwiązane",
        help_text="Jeśli zaznaczone, użytkownicy w tej grupie mogą oznaczać jako rozwiązane zgłoszenia, które są do nich przypisane."
    )
    can_close_any_ticket = models.BooleanField(
        default=False,
        verbose_name="Może zamykać dowolne zgłoszenie",
        help_text="Jeśli zaznaczone, użytkownicy w tej grupie mogą zamykać dowolne zgłoszenia (nawet jeśli nie są do nich przypisane)."
    )

    def __str__(self):
        return f"Ustawienia grupy: {self.group.name}"

    class Meta:
        verbose_name = "Ustawienia grupy"
        verbose_name_plural = "Ustawienia grup"


@receiver(post_save, sender=Group)
def create_group_settings(sender, instance, created, **kwargs):
    """Automatically create settings when a group is created"""
    if created:
        # Set default permissions based on group name
        allow_multiple = instance.name in ['Admin', 'Superagent', 'Agent']
        
        # Set default attachment access level based on group name
        if instance.name in ['Admin', 'Superagent']:
            attachments_access = 'all'
        elif instance.name == 'Agent':
            attachments_access = 'organization'
        else:
            attachments_access = 'own'
        
        # Set default ticket management permissions based on role
        if instance.name == 'Admin':
            # Admin - only edit, no assigning or reverting no closing
            settings = {
                'can_assign_unassigned_tickets': False,
                'can_assign_tickets_to_others': False,
                'can_reassign_assigned_tickets': False,
                'can_unassign_own_tickets': False,
                'can_see_edit_button': True,
                'can_edit_own_tickets': True,
                'can_close_assigned_tickets': False,
                'can_close_any_ticket': False
            }
        elif instance.name == 'Superagent':
            # Superagent - can edit, assign to workers, can't assign to self, can reassign already assigned
            settings = {
                'can_assign_unassigned_tickets': False,
                'can_assign_tickets_to_others': True,
                'can_reassign_assigned_tickets': True,
                'can_unassign_own_tickets': False,
                'can_see_edit_button': True,
                'can_edit_own_tickets': True,
                'can_close_assigned_tickets': True,
                'can_close_any_ticket': True
            }
        elif instance.name == 'Agent':
            # Agent - can assign to self, can't assign to others, can revert own tickets, can close own tickets
            settings = {
                'can_assign_unassigned_tickets': True,
                'can_assign_tickets_to_others': False,
                'can_reassign_assigned_tickets': False,
                'can_unassign_own_tickets': True,
                'can_see_edit_button': False,
                'can_edit_own_tickets': False,
                'can_close_assigned_tickets': True,
                'can_close_any_ticket': False
            }
        else:
            # Client/Viewer - no permissions
            settings = {
                'can_assign_unassigned_tickets': False,
                'can_assign_tickets_to_others': False,
                'can_reassign_assigned_tickets': False,
                'can_unassign_own_tickets': False,
                'can_see_edit_button': False,
                'can_edit_own_tickets': False,
                'can_close_assigned_tickets': False,
                'can_close_any_ticket': False
            }
            
        GroupSettings.objects.create(
            group=instance, 
            allow_multiple_organizations=allow_multiple,
            attachments_access_level=attachments_access,
            **settings
        )
            
        # Setup default view permissions based on group name
        _setup_default_view_permissions(instance)


def _setup_default_view_permissions(group):
    """Set up default view permissions for a group based on its name"""
    # Create views if they don't exist
    for view_code, view_name in ViewPermission.VIEW_CHOICES:
        ViewPermission.objects.get_or_create(
            name=view_code, 
            defaults={"description": view_name}
        )
    
    # Clear existing permissions
    GroupViewPermission.objects.filter(group=group).delete()
    
    # Set default permissions based on group
    if group.name == 'Admin':
        # Admin gets all views
        for view in ViewPermission.objects.all():
            GroupViewPermission.objects.create(group=group, view=view)
    
    elif group.name == 'Superagent':
        # Superagent gets all views except admin panel
        for view in ViewPermission.objects.exclude(name='admin_panel'):
            GroupViewPermission.objects.create(group=group, view=view)
    
    elif group.name == 'Agent':
        # Agent gets dashboard, tickets, organizations, and approvals
        for view_name in ['dashboard', 'tickets', 'organizations', 'approvals']:
            view = ViewPermission.objects.get(name=view_name)
            GroupViewPermission.objects.create(group=group, view=view)
    
    elif group.name == 'Klient' or group.name == 'Client':
        # Client gets only dashboard and tickets
        for view_name in ['dashboard', 'tickets']:
            view = ViewPermission.objects.get(name=view_name)
            GroupViewPermission.objects.create(group=group, view=view)
    
    elif group.name == 'Viewer':
        # Viewer gets only tickets (special view)
        for view_name in ['tickets']:
            view = ViewPermission.objects.get(name=view_name)
            GroupViewPermission.objects.create(group=group, view=view)


# New models for statistics
class WorkHours(models.Model):
    """Define work hours for calculating agent activity metrics"""
    day_of_week_choices = [
        (0, "Poniedziałek"),
        (1, "Wtorek"),
        (2, "Środa"),
        (3, "Czwartek"),
        (4, "Piątek"),
        (5, "Sobota"),
        (6, "Niedziela"),
    ]
    day_of_week = models.IntegerField(choices=day_of_week_choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_working_day = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Godziny pracy"
        verbose_name_plural = "Godziny pracy"
        ordering = ['day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.get_day_of_week_display()} {self.start_time} - {self.end_time}"


class TicketStatistics(models.Model):
    """Store aggregated ticket statistics"""
    PERIOD_CHOICES = [
        ('day', 'Dzień'),
        ('week', 'Tydzień'),
        ('month', 'Miesiąc'),
        ('year', 'Rok'),
    ]
    
    period_type = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    period_start = models.DateField()
    period_end = models.DateField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    agent = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, 
                             related_name='agent_statistics')
    
    # Ticket counts
    tickets_opened = models.IntegerField(default=0)
    tickets_closed = models.IntegerField(default=0)
    tickets_resolved = models.IntegerField(default=0)
    
    # Time metrics (in minutes)
    avg_resolution_time = models.FloatField(default=0)
    avg_first_response_time = models.FloatField(default=0)
    avg_agent_work_time = models.FloatField(default=0)
    
    # Categorical breakdowns
    priority_distribution = models.JSONField(default=dict)  # {'low': 5, 'medium': 10, etc.}
    category_distribution = models.JSONField(default=dict)  # {'hardware': 8, 'software': 12, etc.}
    
    # Performance indicators
    satisfaction_score = models.FloatField(null=True, blank=True)  # Could be from a survey
    sla_compliance = models.FloatField(null=True, blank=True)  # % of tickets meeting SLA
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Statystyka zgłoszeń"
        verbose_name_plural = "Statystyki zgłoszeń"
        indexes = [
            models.Index(fields=['period_type', 'period_start']),
            models.Index(fields=['organization']),
            models.Index(fields=['agent']),
        ]
    
    def __str__(self):
        base = f"{self.get_period_type_display()}: {self.period_start} - {self.period_end}"
        if self.organization:
            base += f", {self.organization.name}"
        if self.agent:
            base += f", {self.agent.username}"
        return base


class AgentWorkLog(models.Model):
    """Track agent activity on tickets for accurate time calculations"""
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='work_logs')
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='work_logs')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True) 
    work_time_minutes = models.FloatField(default=0)  # Calculated work time
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Log pracy agenta"
        verbose_name_plural = "Logi pracy agentów"
        ordering = ['-start_time']
    
    def __str__(self):
        return f"{self.agent.username} - #{self.ticket.id} - {self.start_time}"


class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Użytkownik")
    verification_code = models.CharField(max_length=6, verbose_name="Kod weryfikacyjny")
    is_verified = models.BooleanField(default=False, verbose_name="Zweryfikowany")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data utworzenia")
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name="Data weryfikacji")
    
    def __str__(self):
        return f"Weryfikacja dla {self.user.username}"
    
    def is_expired(self):
        """Check if verification code is expired (valid for 24 hours)"""
        return timezone.now() > self.created_at + timedelta(hours=24)
    
    def generate_new_code(self):
        """Generate new 6-digit verification code"""
        import random
        self.verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        self.created_at = timezone.now()
        self.save()
        return self.verification_code
    
    class Meta:
        verbose_name = "Weryfikacja email"
        verbose_name_plural = "Weryfikacje email"


class EmailNotificationSettings(models.Model):
    """User email notification preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Użytkownik")
    
    # Ticket notifications
    notify_ticket_created = models.BooleanField(default=True, verbose_name="Nowe zgłoszenie")
    notify_ticket_assigned = models.BooleanField(default=True, verbose_name="Przypisanie zgłoszenia")
    notify_ticket_status_changed = models.BooleanField(default=True, verbose_name="Zmiana statusu")
    notify_ticket_commented = models.BooleanField(default=True, verbose_name="Nowy komentarz")
    notify_ticket_updated = models.BooleanField(default=True, verbose_name="Aktualizacja zgłoszenia")
    notify_ticket_closed = models.BooleanField(default=True, verbose_name="Zamknięcie zgłoszenia")
    notify_ticket_reopened = models.BooleanField(default=True, verbose_name="Ponowne otwarcie")
    
    # System notifications
    notify_account_approved = models.BooleanField(default=True, verbose_name="Zatwierdzenie konta")
    notify_password_reset = models.BooleanField(default=True, verbose_name="Reset hasła")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Ustawienia powiadomień dla {self.user.username}"
    
    class Meta:
        verbose_name = "Ustawienia powiadomień email"
        verbose_name_plural = "Ustawienia powiadomień email"
    
    class Meta:
        verbose_name = "Ustawienia powiadomień email"
        verbose_name_plural = "Ustawienia powiadomień email"
