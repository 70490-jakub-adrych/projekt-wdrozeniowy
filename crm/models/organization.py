from django.db import models
from django.utils import timezone
from ..validators import phone_regex

class Organization(models.Model):
    """Model organizacji klienta"""
    name = models.CharField(max_length=100, verbose_name="Nazwa")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefon", validators=[phone_regex])
    website = models.URLField(blank=True, null=True, verbose_name="Strona internetowa")
    address = models.TextField(blank=True, null=True, verbose_name="Adres")
    description = models.TextField(blank=True, null=True, verbose_name="Opis")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data utworzenia")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Data aktualizacji")
    
    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name = "Organizacja"
        verbose_name_plural = "Organizacje"
        ordering = ['name']
