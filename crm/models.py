from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
import os
import uuid
import tempfile
from django.conf import settings
from cryptography.fernet import Fernet
import base64
from .validators import phone_regex


class UserProfile(models.Model):
    """Model rozszerzający standardowego użytkownika o dodatkowe pola"""
    USER_ROLES = (
        ('admin', 'Administrator'),
        ('agent', 'Agent'),
        ('client', 'Klient'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=USER_ROLES, default='client', verbose_name="Rola")
    organizations = models.ManyToManyField('Organization', blank=True, related_name='members', verbose_name="Organizacje")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefon", validators=[phone_regex])
    is_approved = models.BooleanField(default=False, verbose_name="Zatwierdzony")
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    class Meta:
        verbose_name = "Profil użytkownika"
        verbose_name_plural = "Profile użytkowników"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatyczne tworzenie profilu dla nowego użytkownika"""
    if created:
        # Create profile with role based on user type
        role = 'admin' if instance.is_superuser else 'client'
        # Set approved status based on role (admins are auto-approved)
        is_approved = True if instance.is_superuser else False
        UserProfile.objects.create(user=instance, role=role, is_approved=is_approved)
        
        # Add user to appropriate group based on role
        if role == 'admin':
            group, _ = Group.objects.get_or_create(name='Admin')
            instance.groups.add(group)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Zapisywanie profilu przy zapisie użytkownika"""
    instance.profile.save()


@receiver(m2m_changed, sender=User.groups.through)
def sync_user_groups_with_role(sender, instance, action, **kwargs):
    """Synchronize user role when groups change"""
    if action in ['post_add', 'post_remove', 'post_clear']:
        if hasattr(instance, 'profile'):
            # Set role based on group membership
            if instance.groups.filter(name='Admin').exists():
                instance.profile.role = 'admin'
                instance.profile.is_approved = True
            elif instance.groups.filter(name='Agent').exists():
                instance.profile.role = 'agent'
                instance.profile.is_approved = True
            else:
                instance.profile.role = 'client'
            
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
        ('waiting', 'Oczekujące'),
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
    )
    
    user = models.ForeignKey(User, related_name='activities', on_delete=models.CASCADE, 
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
