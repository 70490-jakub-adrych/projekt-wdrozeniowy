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
        
        # Start the scheduler for periodic tasks (auto-close tickets, etc.)
        # Only start in production/when not running management commands
        import sys
        
        # Don't start scheduler when running management commands, migrations, or tests
        skip_scheduler = any([
            'makemigrations' in sys.argv,
            'migrate' in sys.argv,
            'test' in sys.argv,
            'createsuperuser' in sys.argv,
            'shell' in sys.argv,
            'runserver' in sys.argv and '--noreload' not in sys.argv,  # Only run once in runserver
        ])
        
        if not skip_scheduler:
            try:
                from .scheduler import start_scheduler
                start_scheduler()
                logger.info("Periodic task scheduler started successfully")
            except Exception as e:
                logger.error(f"Failed to start scheduler: {e}")
                # Don't crash the app if scheduler fails to start
                pass


class CrmAdminConfig(AdminConfig):
    default_site = 'crm.admin_site.CrmAdminSite'
