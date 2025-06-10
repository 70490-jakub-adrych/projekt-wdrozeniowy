from django.apps import AppConfig


class CrmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crm'
    
    def ready(self):
        """
        Import signals when Django is ready to ensure they're registered
        """
        import crm.signals  # This ensures signals are connected
