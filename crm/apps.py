from django.apps import AppConfig


class CrmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crm'
    
    def ready(self):
        # Import signals to register them
        import crm.auth_backends
