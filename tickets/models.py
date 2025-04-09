from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Custom user with extra fields
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    company_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)

    REQUIRED_FIELDS = ['email', 'company_name', 'phone_number', 'first_name', 'last_name']

    def __str__(self):
        return self.username

# Main Ticket model
class Ticket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Otwarte'),
        ('in_progress', 'W trakcie'),
        ('pending_closure', 'Oczekuje na potwierdzenie zamknięcia'),
        ('closed', 'Zamknięte'),
    ]
    title = models.CharField(max_length=255)
    problem_group = models.CharField(max_length=100)
    description = models.TextField()
    created_by = models.ForeignKey(CustomUser, related_name='tickets', on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(CustomUser, null=True, blank=True, related_name='assigned_tickets', on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    sensitive_data_warning = models.BooleanField(default=False)  # Confirmation of sensitive data awareness

    def __str__(self):
        return self.title

# Model to store multiple attachments for a ticket
class TicketAttachment(models.Model):
    ticket = models.ForeignKey(Ticket, related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField(upload_to='attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

# Model to store history of changes for a ticket
class TicketHistory(models.Model):
    ticket = models.ForeignKey(Ticket, related_name='history', on_delete=models.CASCADE)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    change_note = models.TextField()

    def __str__(self):
        return f"History for {self.ticket.title} at {self.changed_at}"
