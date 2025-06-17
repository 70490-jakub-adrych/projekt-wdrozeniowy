from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
import os
import uuid
import tempfile
from cryptography.fernet import Fernet
import base64
from datetime import timedelta

class Ticket(models.Model):
    """Model zgłoszenia"""
    STATUS_CHOICES = (
        ('new', 'Nowe'),
        ('in_progress', 'W trakcie'),
        ('waiting', 'Oczekujące'),
        ('unresolved', 'Nierozwiązany'),
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
    
    title = models.CharField(max_length=200, verbose_name="Tytuł")
    description = models.TextField(verbose_name="Opis")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Status")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name="Priorytet")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other', verbose_name="Kategoria")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tickets', verbose_name="Utworzone przez")
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets', verbose_name="Przypisane do")
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE, related_name='tickets', verbose_name="Organizacja")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data utworzenia")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Data aktualizacji")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="Data rozwiązania")
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name="Data zamknięcia")
    solution_confirmed = models.BooleanField(default=False, verbose_name="Rozwiązanie potwierdzone")
    
    def __str__(self):
        return f"#{self.id} {self.title}"
    
    def resolve(self):
        """Mark ticket as resolved"""
        if self.status not in ['resolved', 'closed']:
            self.status = 'resolved'
            self.resolved_at = timezone.now()
            self.save()
    
    def close(self):
        """Mark ticket as closed"""
        self.status = 'closed'
        self.closed_at = timezone.now()
        self.save()
    
    def reopen(self):
        """Reopen a resolved or closed ticket"""
        if self.status in ['resolved', 'closed']:
            self.status = 'in_progress'
            self.resolved_at = None
            self.closed_at = None
            self.solution_confirmed = False
            self.save()
    
    @property
    def is_closed(self):
        return self.status == 'closed'
    
    @property
    def is_resolved(self):
        return self.status == 'resolved'
    
    @property
    def resolution_time(self):
        """Calculate the time from creation to resolution"""
        if not self.resolved_at:
            return None
        return self.resolved_at - self.created_at
    
    @property
    def time_in_queue(self):
        """Calculate the time from creation to first assignment"""
        first_assignment = self.ticket_events.filter(event_type='assigned').order_by('timestamp').first()
        if not first_assignment:
            return timezone.now() - self.created_at if self.status == 'new' else None
        return first_assignment.timestamp - self.created_at
    
    class Meta:
        verbose_name = "Zgłoszenie"
        verbose_name_plural = "Zgłoszenia"
        ordering = ['-created_at']


class TicketComment(models.Model):
    """Comments on tickets"""
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments', verbose_name="Zgłoszenie")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ticket_comments', verbose_name="Autor")
    content = models.TextField(verbose_name="Treść")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data utworzenia")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Data aktualizacji")
    is_internal = models.BooleanField(default=False, verbose_name="Wewnętrzny (widoczny tylko dla agentów)")
    
    def __str__(self):
        return f"Komentarz do #{self.ticket.id} od {self.author.username}"
    
    class Meta:
        verbose_name = "Komentarz do zgłoszenia"
        verbose_name_plural = "Komentarze do zgłoszeń"
        ordering = ['created_at']


def get_attachment_upload_path(instance, filename):
    """Generate a secure, unique path for ticket attachments"""
    # Generate a UUID-based directory to store files securely
    unique_dir = str(uuid.uuid4())
    # Sanitize filename - replace spaces with underscores
    safe_filename = filename.replace(" ", "_")
    # Return the full path
    return os.path.join('tickets', str(instance.ticket.id), unique_dir, safe_filename)


class TicketAttachment(models.Model):
    """File attachments for tickets"""
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='attachments', verbose_name="Zgłoszenie")
    file = models.FileField(upload_to=get_attachment_upload_path, verbose_name="Plik")
    filename = models.CharField(max_length=255, verbose_name="Nazwa pliku")
    file_size = models.IntegerField(verbose_name="Rozmiar pliku (bajty)")
    content_type = models.CharField(max_length=100, verbose_name="Typ pliku")
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ticket_attachments', verbose_name="Dodane przez")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Data dodania")
    encrypted = models.BooleanField(default=True, verbose_name="Zaszyfrowany")
    encryption_key = models.BinaryField(null=True, blank=True)
    
    def __str__(self):
        return f"Załącznik do #{self.ticket.id}: {self.filename}"
    
    def save(self, *args, **kwargs):
        # Automatically set the filename from the file field if not set
        if not self.filename and self.file:
            self.filename = os.path.basename(self.file.name)
        
        # Save the instance first to get the ID assigned
        super().save(*args, **kwargs)
        
        # Encrypt the file content if encryption is enabled and not already encrypted
        if self.encrypted and not self.encryption_key:
            self._encrypt_file()
    
    def _encrypt_file(self):
        """Encrypt the uploaded file using Fernet symmetric encryption"""
        if not self.file:
            return
        
        try:
            # Generate a new encryption key
            key = Fernet.generate_key()
            cipher = Fernet(key)
            
            # Read the original file
            self.file.open('rb')
            original_data = self.file.read()
            self.file.close()
            
            # Encrypt the data
            encrypted_data = cipher.encrypt(original_data)
            
            # Create a temporary file to store encrypted content
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(encrypted_data)
                temp_file_path = temp_file.name
            
            # Update the file with encrypted content
            with open(temp_file_path, 'rb') as temp_file:
                self.file.save(self.file.name, temp_file, save=False)
            
            # Store the encryption key
            self.encryption_key = key
            
            # Clean up the temporary file
            os.unlink(temp_file_path)
            
            # Save the model again with the encrypted file and key
            super().save(update_fields=['file', 'encryption_key'])
            
        except Exception as e:
            # Log the error but don't expose encryption details
            print(f"Error encrypting file: {str(e)}")
    
    def get_decrypted_content(self):
        """Decrypt and return the file content"""
        if not self.encrypted or not self.encryption_key:
            # Not encrypted or no key, return the file as is
            self.file.open('rb')
            content = self.file.read()
            self.file.close()
            return content
        
        try:
            # Create a cipher with the stored key
            cipher = Fernet(self.encryption_key)
            
            # Read the encrypted file
            self.file.open('rb')
            encrypted_data = self.file.read()
            self.file.close()
            
            # Decrypt the data
            decrypted_data = cipher.decrypt(encrypted_data)
            return decrypted_data
            
        except Exception as e:
            # Log the error but don't expose decryption details
            print(f"Error decrypting file: {str(e)}")
            return None
    
    class Meta:
        verbose_name = "Załącznik do zgłoszenia"
        verbose_name_plural = "Załączniki do zgłoszeń"


class AgentWorkLog(models.Model):
    """Records time spent by agents working on tickets"""
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='work_logs', verbose_name="Agent")
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='work_logs', verbose_name="Zgłoszenie")
    start_time = models.DateTimeField(verbose_name="Czas rozpoczęcia")
    end_time = models.DateTimeField(verbose_name="Czas zakończenia")
    notes = models.TextField(blank=True, null=True, verbose_name="Notatki")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data utworzenia")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Data aktualizacji")
    
    @property
    def work_time_minutes(self):
        if not self.end_time or not self.start_time:
            return 0
        
        delta = self.end_time - self.start_time
        return int(delta.total_seconds() / 60)
    
    def __str__(self):
        return f"{self.agent.username} - #{self.ticket.id} - {self.work_time_minutes}min"
    
    class Meta:
        verbose_name = "Log pracy agenta"
        verbose_name_plural = "Logi pracy agentów"
        ordering = ['-start_time']


class WorkHours(models.Model):
    """System working hours for SLA calculations"""
    DAY_CHOICES = (
        (1, 'Poniedziałek'),
        (2, 'Wtorek'),
        (3, 'Środa'),
        (4, 'Czwartek'),
        (5, 'Piątek'),
        (6, 'Sobota'),
        (7, 'Niedziela'),
    )
    
    day_of_week = models.IntegerField(choices=DAY_CHOICES, verbose_name="Dzień tygodnia")
    start_time = models.TimeField(verbose_name="Czas rozpoczęcia", default='09:00')
    end_time = models.TimeField(verbose_name="Czas zakończenia", default='17:00')
    is_working_day = models.BooleanField(default=True, verbose_name="Dzień pracujący")
    
    def get_day_of_week_display(self):
        return dict(self.DAY_CHOICES).get(self.day_of_week)
    
    def __str__(self):
        status = "pracujący" if self.is_working_day else "niepracujący"
        return f"{self.get_day_of_week_display()} ({status}): {self.start_time} - {self.end_time}"
    
    class Meta:
        verbose_name = "Godziny pracy"
        verbose_name_plural = "Godziny pracy"
        ordering = ['day_of_week']
        unique_together = ['day_of_week']


class TicketStatistics(models.Model):
    """Pre-calculated statistics for reporting"""
    PERIOD_CHOICES = (
        ('daily', 'Dzień'),
        ('weekly', 'Tydzień'),
        ('monthly', 'Miesiąc'),
        ('quarterly', 'Kwartał'),
        ('yearly', 'Rok'),
    )
    
    period_type = models.CharField(max_length=20, choices=PERIOD_CHOICES, verbose_name="Typ okresu")
    period_start = models.DateField(verbose_name="Początek okresu")
    period_end = models.DateField(verbose_name="Koniec okresu")
    organization = models.ForeignKey('Organization', null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Organizacja")
    agent = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="agent_stats", verbose_name="Agent")
    
    # Ticket counts
    tickets_opened = models.IntegerField(default=0, verbose_name="Liczba otwartych zgłoszeń")
    tickets_closed = models.IntegerField(default=0, verbose_name="Liczba zamkniętych zgłoszeń")
    tickets_resolved = models.IntegerField(default=0, verbose_name="Liczba rozwiązanych zgłoszeń")
    
    # Response time metrics (in minutes)
    avg_response_time = models.FloatField(null=True, blank=True, verbose_name="Średni czas odpowiedzi (minuty)")
    avg_resolution_time = models.FloatField(null=True, blank=True, verbose_name="Średni czas rozwiązania (minuty)")
    
    # JSON fields to store detailed breakdowns
    category_breakdown = models.JSONField(null=True, blank=True, verbose_name="Zgłoszenia według kategorii")
    priority_breakdown = models.JSONField(null=True, blank=True, verbose_name="Zgłoszenia według priorytetu")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data utworzenia")
    
    def __str__(self):
        period_str = f"{self.period_start} do {self.period_end}"
        
        if self.organization:
            return f"Statystyki {self.get_period_type_display()} dla {self.organization.name}: {period_str}"
        elif self.agent:
            return f"Statystyki {self.get_period_type_display()} dla agenta {self.agent.username}: {period_str}"
        else:
            return f"Statystyki {self.get_period_type_display()}: {period_str}"
    
    class Meta:
        verbose_name = "Statystyka zgłoszeń"
        verbose_name_plural = "Statystyki zgłoszeń"
        unique_together = [
            ('period_type', 'period_start', 'period_end', 'organization', 'agent')
        ]
