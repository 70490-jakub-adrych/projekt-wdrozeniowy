from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Contact(models.Model):
    """Model for storing contact information"""
    LEAD_SOURCE_CHOICES = (
        ('website', 'Strona internetowa'),
        ('phone', 'Kontakt telefoniczny'),
        ('referral', 'Polecenie'),
        ('social', 'Media społecznościowe'),
        ('other', 'Inne'),
    )
    
    STATUS_CHOICES = (
        ('new', 'Nowy'),
        ('contacted', 'Skontaktowano się'),
        ('active', 'Aktywny'),
        ('inactive', 'Nieaktywny'),
    )
    
    first_name = models.CharField(max_length=100, verbose_name="Imię")
    last_name = models.CharField(max_length=100, verbose_name="Nazwisko")
    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefon")
    company = models.CharField(max_length=100, blank=True, verbose_name="Firma")
    lead_source = models.CharField(max_length=20, choices=LEAD_SOURCE_CHOICES, default='other', verbose_name="Źródło pozyskania")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Status")
    notes = models.TextField(blank=True, verbose_name="Notatki")
    created_by = models.ForeignKey(User, related_name='contacts', on_delete=models.CASCADE, verbose_name="Utworzony przez")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data utworzenia")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Data aktualizacji")
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Kontakt"
        verbose_name_plural = "Kontakty"


class Organization(models.Model):
    """Model for storing organization/company information"""
    name = models.CharField(max_length=255, verbose_name="Nazwa")
    website = models.URLField(blank=True, verbose_name="Strona internetowa")
    address = models.TextField(blank=True, verbose_name="Adres")
    description = models.TextField(blank=True, verbose_name="Opis")
    created_by = models.ForeignKey(User, related_name='organizations', on_delete=models.CASCADE, verbose_name="Utworzony przez")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data utworzenia")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Data aktualizacji")
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name = "Organizacja"
        verbose_name_plural = "Organizacje"


class Deal(models.Model):
    """Model for storing deal/opportunity information"""
    STAGE_CHOICES = (
        ('lead', 'Lead'),
        ('qualified', 'Kwalifikowany'),
        ('proposal', 'Oferta'),
        ('negotiation', 'Negocjacje'),
        ('closed_won', 'Zamknięty - Wygrany'),
        ('closed_lost', 'Zamknięty - Przegrany'),
    )
    
    title = models.CharField(max_length=255, verbose_name="Tytuł")
    contact = models.ForeignKey(Contact, related_name='deals', on_delete=models.CASCADE, verbose_name="Kontakt")
    organization = models.ForeignKey(Organization, related_name='deals', on_delete=models.CASCADE, blank=True, null=True, verbose_name="Organizacja")
    value = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Wartość")
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='lead', verbose_name="Etap")
    expected_close_date = models.DateField(blank=True, null=True, verbose_name="Przewidywana data zamknięcia")
    description = models.TextField(blank=True, verbose_name="Opis")
    created_by = models.ForeignKey(User, related_name='deals', on_delete=models.CASCADE, verbose_name="Utworzony przez")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data utworzenia")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Data aktualizacji")
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Umowa"
        verbose_name_plural = "Umowy"
