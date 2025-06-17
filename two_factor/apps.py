from django.apps import AppConfig

class TwoFactorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'two_factor'
    verbose_name = 'Two-Factor Authentication'
    
    def ready(self):
        # Import signals to register them
        import two_factor.signals
