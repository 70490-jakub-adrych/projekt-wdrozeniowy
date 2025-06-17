from django.db import models
from django.contrib.auth.models import Group

class GroupSettings(models.Model):
    """Extended settings for user groups"""
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='settings')
    
    # Organization settings
    allow_multiple_organizations = models.BooleanField(default=False, 
        verbose_name="Zezwalaj na wiele organizacji",
        help_text="Czy użytkownicy w tej grupie mogą być przypisani do więcej niż jednej organizacji")
    
    # Visibility settings
    show_statistics = models.BooleanField(default=False,
        verbose_name="Pokaż statystyki",
        help_text="Czy użytkownicy w tej grupie mogą widzieć statystyki")
    
    # Access level to attachments
    ATTACHMENT_ACCESS_CHOICES = (
        ('own', 'Tylko własne zgłoszenia'),
        ('organization', 'Zgłoszenia własnej organizacji'),
        ('all', 'Wszystkie zgłoszenia'),
    )
    
    attachments_access_level = models.CharField(
        max_length=15,
        choices=ATTACHMENT_ACCESS_CHOICES,
        default='own',
        verbose_name="Dostęp do załączników"
    )
    
    # Ticket assignment permissions
    can_assign_unassigned_tickets = models.BooleanField(default=False,
        verbose_name="Przypisywanie nieprzypisanych zgłoszeń",
        help_text="Czy użytkownicy mogą przypisywać do siebie nieprzypisane zgłoszenia")
    
    can_assign_tickets_to_others = models.BooleanField(default=False,
        verbose_name="Przypisywanie zgłoszeń innym",
        help_text="Czy użytkownicy mogą przypisywać zgłoszenia innym agentom")
    
    can_reassign_assigned_tickets = models.BooleanField(default=False,
        verbose_name="Przepisywanie przypisanych zgłoszeń",
        help_text="Czy użytkownicy mogą przepisywać już przypisane zgłoszenia")
    
    can_unassign_own_tickets = models.BooleanField(default=False,
        verbose_name="Odwoływanie własnych przypisań",
        help_text="Czy użytkownicy mogą cofać swoje przypisanie do zgłoszenia")
    
    # Ticket management permissions
    can_see_edit_button = models.BooleanField(default=False,
        verbose_name="Widok przycisku edycji",
        help_text="Czy użytkownicy widzą przycisk edycji zgłoszeń")
    
    can_edit_own_tickets = models.BooleanField(default=False,
        verbose_name="Edytowanie własnych zgłoszeń",
        help_text="Czy użytkownicy mogą edytować zgłoszenia, które utworzyli")
    
    can_close_assigned_tickets = models.BooleanField(default=False,
        verbose_name="Zamykanie przypisanych zgłoszeń",
        help_text="Czy użytkownicy mogą zamykać zgłoszenia, które są do nich przypisane")
    
    can_close_any_ticket = models.BooleanField(default=False,
        verbose_name="Zamykanie wszystkich zgłoszeń",
        help_text="Czy użytkownicy mogą zamykać wszystkie zgłoszenia")
    
    def __str__(self):
        return f"Ustawienia dla grupy {self.group.name}"
    
    class Meta:
        verbose_name = "Ustawienia grupy"
        verbose_name_plural = "Ustawienia grup"
