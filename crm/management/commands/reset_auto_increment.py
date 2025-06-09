from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Resets auto-increment values for specified tables in the database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--table',
            help='Reset auto-increment for a specific table (e.g., auth_user)'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Reset auto-increment for all important tables'
        )
        parser.add_argument(
            '--value',
            type=int,
            default=1,
            help='Reset auto-increment to this value (default: 1)'
        )
    
    def handle(self, *args, **options):
        table_name = options.get('table')
        reset_all = options.get('all')
        reset_value = options.get('value')
        
        if not (table_name or reset_all):
            self.stdout.write(self.style.ERROR(
                "Please specify either --table or --all option"
            ))
            return
        
        # Check if database is MySQL
        if 'mysql' not in settings.DATABASES['default']['ENGINE']:
            self.stdout.write(self.style.ERROR(
                "This command only works with MySQL databases"
            ))
            return
        
        with connection.cursor() as cursor:
            if reset_all:
                tables_to_reset = [
                    'auth_user',
                    'crm_userprofile',
                    'crm_emailverification',
                    'crm_emailnotificationsettings',
                ]
                for table in tables_to_reset:
                    self._reset_table(cursor, table, reset_value)
            elif table_name:
                self._reset_table(cursor, table_name, reset_value)
        
        self.stdout.write(self.style.SUCCESS("Auto-increment reset completed"))
    
    def _reset_table(self, cursor, table_name, reset_value):
        try:
            # Get current max ID and determine new auto_increment value
            cursor.execute(f"SELECT MAX(id) FROM {table_name}")
            max_id = cursor.fetchone()[0] or 0
            effective_reset = max(max_id + 1, reset_value)
            
            # Reset the auto_increment
            cursor.execute(f"ALTER TABLE {table_name} AUTO_INCREMENT = {effective_reset}")
            
            self.stdout.write(self.style.SUCCESS(
                f"Reset auto_increment for {table_name} to {effective_reset} (max id was {max_id})"
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f"Error resetting auto_increment for {table_name}: {str(e)}"
            ))
