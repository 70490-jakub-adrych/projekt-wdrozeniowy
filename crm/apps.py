from django.apps import AppConfig


class CrmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crm'
    
    def ready(self):
        """Run when the app is ready"""
        # Import signals
        import crm.signals
        
        # Set up logging
        import logging
        logger = logging.getLogger(__name__)
        logger.debug("CRM app is ready")
