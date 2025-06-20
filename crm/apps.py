from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig


class CrmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crm'
    
    def ready(self):
        """Run when the app is ready"""
        # Import signals
        import crm.signals  # noqa
        
        # Set up logging
        import logging
        logger = logging.getLogger(__name__)
        logger.debug("CRM app is ready")


class CrmAdminConfig(AdminConfig):
    default_site = 'crm.admin_site.CrmAdminSite'
