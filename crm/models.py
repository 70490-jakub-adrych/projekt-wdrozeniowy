from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Model rozszerzający standardowego użytkownika o dodatkowe pola"""
    USER_ROLES = (
        ('admin', 'Administrator'),
        ('agent', 'Agent'),
        ('client', 'Klient'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=USER_ROLES, default='client', verbose_name="Rola")
    organization = models.ForeignKey('Organization', on_delete=models.SET_NULL, null=True, blank=True, related_name='members', verbose_name="Organizacja")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefon")
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


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Zapisywanie profilu przy zapisie użytkownika"""
    instance.profile.save()


class Organization(models.Model):
    """Model przechowujący informacje o organizacjach klientów"""
    name = models.CharField(max_length=255, verbose_name="Nazwa")
    email = models.EmailField(blank=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefon")
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
        ('ticket_created', 'Utworzenie zgłoszenia'),
        ('ticket_updated', 'Aktualizacja zgłoszenia'),
        ('ticket_commented', 'Komentarz do zgłoszenia'),
        ('ticket_resolved', 'Rozwiązanie zgłoszenia'),
        ('ticket_closed', 'Zamknięcie zgłoszenia'),
        ('ticket_reopened', 'Ponowne otwarcie zgłoszenia'),
    )
    
    user = models.ForeignKey(User, related_name='activities', on_delete=models.CASCADE, verbose_name="Użytkownik")
    action_type = models.CharField(max_length=30, choices=ACTION_TYPES, verbose_name="Typ akcji")
    ticket = models.ForeignKey(Ticket, related_name='activities', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Zgłoszenie")
    description = models.TextField(blank=True, verbose_name="Opis")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Adres IP")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data")
    
    def __str__(self):
        return f"{self.get_action_type_display()} - {self.user.username} - {self.created_at}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Log aktywności"
        verbose_name_plural = "Logi aktywności"
