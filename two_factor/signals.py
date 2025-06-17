from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import TwoFactorAuth

@receiver(post_save, sender=User)
def create_two_factor_profile(sender, instance, created, **kwargs):
    """Create a 2FA profile for new users"""
    if created:
        TwoFactorAuth.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_two_factor_profile(sender, instance, **kwargs):
    """Ensure 2FA profile is saved when user is saved"""
    try:
        instance.two_factor.save()
    except TwoFactorAuth.DoesNotExist:
        # Create it if it doesn't exist
        TwoFactorAuth.objects.create(user=instance)
