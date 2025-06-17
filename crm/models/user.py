from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from ..validators import phone_regex

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
        # Set approved status based on role (admins and superagents are auto-approved)
        is_approved = True if instance.is_superuser else False
        UserProfile.objects.create(user=instance, role=role, is_approved=is_approved)
        
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
    """Synchronizacja roli użytkownika przy zmianie grup"""
    if action == 'post_add' and hasattr(instance, 'profile'):
        # Get the latest group added (or any group if multiple)
        groups = instance.groups.all()
        if groups.exists():
            group = groups.last()  # Get the most recently added group
            
            # Map group names to roles
            group_to_role = {
                'Admin': 'admin',
                'Superagent': 'superagent',
                'Agent': 'agent',
                'Klient': 'client', 
                'Viewer': 'viewer'
            }
            
            # Update the role based on the group name
            if group.name in group_to_role:
                instance.profile.role = group_to_role[group.name]
                instance.profile.save()


class ViewPermission(models.Model):
    """Model definiujący uprawnienia do widoków aplikacji"""
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.description
    
    def get_name_display(self):
        """Konwertuje kod uprawnienia na przyjazną nazwę"""
        name_map = {
            'dashboard': 'Panel główny',
            'tickets': 'Zgłoszenia',
            'organizations': 'Organizacje',
            'approvals': 'Zatwierdzanie kont',
            'logs': 'Logi',
            'admin_panel': 'Panel admina',
        }
        return name_map.get(self.name, self.name)

    class Meta:
        verbose_name = "Uprawnienie do widoku"
        verbose_name_plural = "Uprawnienia do widoków"


class GroupViewPermission(models.Model):
    """Połączenie grup z uprawnieniami do widoków"""
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='view_permissions')
    view = models.ForeignKey(ViewPermission, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.group.name} - {self.view.name}"
    
    class Meta:
        unique_together = ('group', 'view')
        verbose_name = "Uprawnienie grupy do widoku"
        verbose_name_plural = "Uprawnienia grup do widoków"


class UserViewPermission(models.Model):
    """Indywidualne uprawnienia użytkownika do widoków (nadpisuje grupowe)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='view_permissions')
    view = models.ForeignKey(ViewPermission, on_delete=models.CASCADE)
    is_granted = models.BooleanField(default=True, help_text="Zaznacz, aby nadać dostęp. Odznacz, aby jawnie zakazać dostępu.")
    
    def __str__(self):
        action = "ma dostęp do" if self.is_granted else "nie ma dostępu do"
        return f"{self.user.username} {action} {self.view.name}"
    
    class Meta:
        unique_together = ('user', 'view')
        verbose_name = "Uprawnienie użytkownika do widoku"
        verbose_name_plural = "Uprawnienia użytkowników do widoków"


class EmailVerification(models.Model):
    """Model przechowujący kody weryfikacyjne email"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    verification_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    verification_attempts = models.IntegerField(default=0)
    
    def __str__(self):
        status = "zweryfikowany" if self.is_verified else "niezweryfikowany"
        return f"{self.user.username} - {status}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def verify(self, code):
        """Verify the email with the given code"""
        if self.is_expired():
            return False
        
        if self.verification_attempts >= 5:
            return False
            
        if self.verification_code == code:
            self.is_verified = True
            self.save()
            
            # Update the user profile as well
            profile = self.user.profile
            profile.email_verified = True
            profile.save()
            
            # If the account is approved but inactive, activate it
            if profile.is_approved and not self.user.is_active:
                self.user.is_active = True
                self.user.save()
                
            return True
        else:
            self.verification_attempts += 1
            self.save()
            return False
    
    class Meta:
        verbose_name = "Weryfikacja email"
        verbose_name_plural = "Weryfikacje email"


class EmailNotificationSettings(models.Model):
    """User preferences for email notifications"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_settings')
    
    # Ticket notifications
    notify_ticket_created = models.BooleanField(default=True, verbose_name="Nowe zgłoszenie")
    notify_ticket_assigned = models.BooleanField(default=True, verbose_name="Przypisanie zgłoszenia")
    notify_ticket_status_changed = models.BooleanField(default=True, verbose_name="Zmiana statusu")
    notify_ticket_commented = models.BooleanField(default=True, verbose_name="Nowy komentarz")
    notify_ticket_updated = models.BooleanField(default=True, verbose_name="Aktualizacja zgłoszenia")
    
    # User account notifications
    notify_account_changes = models.BooleanField(default=True, verbose_name="Zmiany konta")
    notify_password_changes = models.BooleanField(default=True, verbose_name="Zmiany hasła")
    
    # Additional notifications
    notify_maintenance = models.BooleanField(default=True, verbose_name="Planowane przerwy serwisowe")
    
    def __str__(self):
        return f"Ustawienia powiadomień dla {self.user.username}"
    
    class Meta:
        verbose_name = "Ustawienie powiadomień email"
        verbose_name_plural = "Ustawienia powiadomień email"
