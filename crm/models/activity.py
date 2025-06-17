from django.db import models
from django.contrib.auth.models import User

class ActivityLog(models.Model):
    """Log of important actions taken by users"""
    ACTION_TYPES = (
        # User account actions
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('login_failed', 'Failed Login'),
        ('password_change', 'Password Change'),
        ('password_reset', 'Password Reset'),
        ('account_locked', 'Account Locked'),
        ('account_unlocked', 'Account Unlocked'),
        ('user_created', 'User Created'),
        ('user_approved', 'User Approved'),
        ('user_rejected', 'User Rejected'),
        
        # Ticket actions
        ('ticket_created', 'Ticket Created'),
        ('ticket_updated', 'Ticket Updated'),
        ('ticket_assigned', 'Ticket Assigned'),
        ('ticket_unassigned', 'Ticket Unassigned'),
        ('ticket_comment', 'Ticket Comment'),
        ('ticket_status_change', 'Ticket Status Change'),
        ('ticket_closed', 'Ticket Closed'),
        ('ticket_reopened', 'Ticket Reopened'),
        
        # Attachment actions
        ('attachment_added', 'Attachment Added'),
        ('attachment_deleted', 'Attachment Deleted'),
        ('attachment_downloaded', 'Attachment Downloaded'),
        
        # Admin actions
        ('settings_change', 'Settings Change'),
        ('admin_action', 'Admin Action'),
        ('log_cleared', 'Logs Cleared'),
    )
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Użytkownik")
    action_type = models.CharField(max_length=30, choices=ACTION_TYPES, verbose_name="Typ akcji")
    description = models.TextField(verbose_name="Opis")
    ticket = models.ForeignKey('Ticket', on_delete=models.SET_NULL, null=True, blank=True, related_name='activity_logs', verbose_name="Zgłoszenie")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Adres IP")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data")
    
    def __str__(self):
        user_str = self.user.username if self.user else "System"
        action_display = dict(self.ACTION_TYPES).get(self.action_type, self.action_type)
        ticket_str = f"#{self.ticket.id}" if self.ticket else ""
        return f"{user_str} - {action_display} {ticket_str}"
    
    class Meta:
        verbose_name = "Log aktywności"
        verbose_name_plural = "Logi aktywności"
        ordering = ['-created_at']
