from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import hashlib
import os
import string
import random

class TwoFactorAuth(models.Model):
    """Store Google Authenticator settings and recovery codes for users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='two_factor')
    ga_enabled = models.BooleanField(default=False, verbose_name="Google Authenticator aktywny")
    ga_secret = models.CharField(max_length=32, blank=True, null=True, verbose_name="Sekret Google Authenticator")
    ga_enabled_on = models.DateTimeField(blank=True, null=True, verbose_name="Data włączenia 2FA")
    ga_last_authenticated = models.DateTimeField(blank=True, null=True, verbose_name="Ostatnia weryfikacja 2FA")
    recovery_code_hash = models.CharField(max_length=128, blank=True, null=True, verbose_name="Hash kodu odzyskiwania")
    recovery_code_generated = models.DateTimeField(blank=True, null=True, verbose_name="Data wygenerowania kodu odzyskiwania")
    
    class Meta:
        verbose_name = "Uwierzytelnianie dwuskładnikowe"
        verbose_name_plural = "Uwierzytelnianie dwuskładnikowe"
    
    def __str__(self):
        return f"2FA dla {self.user.username}"
    
    def can_regenerate_recovery_code(self):
        """Check if user can regenerate a recovery code (once per 24h)"""
        if not self.recovery_code_generated:
            return True
        
        time_since_generation = timezone.now() - self.recovery_code_generated
        return time_since_generation.total_seconds() > 86400  # 24 hours
    
    def generate_recovery_code(self):
        """Generate a new recovery code and store its hash"""
        if not self.can_regenerate_recovery_code():
            return None
            
        # Generate a secure 16-character alphanumeric code
        chars = string.ascii_letters + string.digits
        recovery_code = ''.join(random.choice(chars) for _ in range(16))
        
        # Store only the hash of the code
        salt = os.urandom(32)
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256', 
            recovery_code.encode(), 
            salt, 
            100000
        )
        
        # Store the salt + hash
        self.recovery_code_hash = salt.hex() + hash_obj.hex()
        self.recovery_code_generated = timezone.now()
        self.save()
        
        return recovery_code
    
    def verify_recovery_code(self, code):
        """Verify a recovery code against the stored hash"""
        if not self.recovery_code_hash:
            return False
            
        # Extract salt from stored hash
        salt_hex = self.recovery_code_hash[:64]
        salt = bytes.fromhex(salt_hex)
        
        # Hash the provided code with the same salt
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256', 
            code.encode(), 
            salt, 
            100000
        )
        
        # Compare with stored hash
        expected_hash = self.recovery_code_hash[64:]
        if hash_obj.hex() == expected_hash:
            # Recovery code is valid, invalidate it after use
            self.recovery_code_hash = None
            self.save()
            return True
            
        return False


class TrustedDevice(models.Model):
    """Track trusted devices and IP addresses for 2FA"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trusted_devices')
    device_identifier = models.CharField(max_length=255, verbose_name="Identyfikator urządzenia")
    ip_address = models.GenericIPAddressField(verbose_name="Adres IP")
    user_agent = models.TextField(verbose_name="User Agent")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    last_used = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Zaufane urządzenie"
        verbose_name_plural = "Zaufane urządzenia"
        unique_together = ('user', 'device_identifier')
    
    def __str__(self):
        return f"Urządzenie: {self.user.username} z {self.ip_address}"
    
    def is_valid(self):
        """Check if device trust is still valid (not expired)"""
        return timezone.now() < self.expires_at
    
    @classmethod
    def create(cls, user, request):
        """Create a new trusted device entry for a user"""
        device_id = cls.generate_device_id(request)
        # Trust for 30 days per requirement #6
        expires = timezone.now() + timezone.timedelta(days=30)
        
        return cls.objects.create(
            user=user,
            device_identifier=device_id,
            ip_address=cls.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            expires_at=expires
        )
    
    @staticmethod
    def generate_device_id(request):
        """Generate a unique device identifier based on multiple factors"""
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        ip = TrustedDevice.get_client_ip(request)
        # Add additional browser fingerprinting parameters
        browser_data = request.META.get('HTTP_SEC_CH_UA', '')
        platform = request.META.get('HTTP_SEC_CH_UA_PLATFORM', '')
        
        # Combine factors to create a device fingerprint
        fingerprint_data = f"{user_agent}|{ip}|{browser_data}|{platform}"
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()
    
    @staticmethod
    def get_client_ip(request):
        """Extract client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
