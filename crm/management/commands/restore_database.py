"""
Database restore management command
Restores from MySQL dumps or Django fixtures
"""

import os
import gzip
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.management import call_command
import subprocess
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Restore database from backup file'

    def add_arguments(self, parser):
        parser.add_argument(
            'backup_file',
            help='Path to backup file to restore'
        )
        parser.add_argument(
            '--format',
            choices=['sql', 'json', 'auto'],
            default='auto',
            help='Backup format (auto-detect by file extension)'
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Skip confirmation prompt (dangerous!)'
        )

    def handle(self, *args, **options):
        backup_file = options['backup_file']
        
        # Make path absolute if relative
        if not os.path.isabs(backup_file):
            backup_file = os.path.join(settings.BASE_DIR, backup_file)
        
        if not os.path.exists(backup_file):
            raise CommandError(f'Backup file not found: {backup_file}')
        
        # Auto-detect format
        backup_format = options['format']
        if backup_format == 'auto':
            if backup_file.endswith(('.sql', '.sql.gz')):
                backup_format = 'sql'
            elif backup_file.endswith(('.json', '.json.gz')):
                backup_format = 'json'
            else:
                raise CommandError('Cannot auto-detect backup format. Use --format option.')
        
        # Safety confirmation
        if not options['confirm']:
            db_name = settings.DATABASES['default']['NAME']
            self.stdout.write(
                self.style.WARNING(
                    f'WARNING: This will REPLACE all data in database "{db_name}"!'
                )
            )
            self.stdout.write('Current data will be PERMANENTLY LOST!')
            
            confirm = input('Type "yes" to confirm: ')
            if confirm.lower() != 'yes':
                self.stdout.write('Restore cancelled.')
                return
        
        try:
            if backup_format == 'sql':
                self._restore_mysql_backup(backup_file)
            else:
                self._restore_django_backup(backup_file)
            
            self.stdout.write(
                self.style.SUCCESS(f'Database restored successfully from: {backup_file}')
            )
            
        except Exception as e:
            logger.error(f"Restore failed: {str(e)}")
            raise CommandError(f'Restore failed: {str(e)}')

    def _restore_mysql_backup(self, backup_file):
        """Restore from MySQL dump"""
        db_config = settings.DATABASES['default']
        
        if 'mysql' not in db_config['ENGINE']:
            raise CommandError('MySQL restore requested but database is not MySQL')
        
        self.stdout.write(f'Restoring MySQL backup: {backup_file}')
        
        # Build mysql command
        cmd = [
            'mysql',
            f"--host={db_config['HOST']}",
            f"--port={db_config['PORT'] or '3306'}",
            f"--user={db_config['USER']}",
            f"--password={db_config['PASSWORD']}",
            db_config['NAME']
        ]
        
        try:
            # Read backup file (handle compression)
            if backup_file.endswith('.gz'):
                with gzip.open(backup_file, 'rt', encoding='utf-8') as f:
                    sql_data = f.read()
            else:
                with open(backup_file, 'r', encoding='utf-8') as f:
                    sql_data = f.read()
            
            # Run mysql restore
            result = subprocess.run(cmd, input=sql_data, text=True, 
                                  capture_output=True, check=True)
            
        except subprocess.CalledProcessError as e:
            raise CommandError(f'MySQL restore failed: {e.stderr}')
        except FileNotFoundError:
            raise CommandError('mysql command not found. Please install MySQL client tools.')

    def _restore_django_backup(self, backup_file):
        """Restore from Django fixture"""
        self.stdout.write(f'Restoring Django fixture: {backup_file}')
        
        # Read backup file (handle compression)
        if backup_file.endswith('.gz'):
            import tempfile
            # Extract to temporary file for loaddata
            with gzip.open(backup_file, 'rt', encoding='utf-8') as gz_file:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', 
                                               delete=False, encoding='utf-8') as temp_file:
                    temp_file.write(gz_file.read())
                    temp_backup_file = temp_file.name
            
            try:
                # Flush current data (optional - can be dangerous)
                self.stdout.write('Flushing current database...')
                call_command('flush', '--noinput')
                
                # Load data
                call_command('loaddata', temp_backup_file)
            finally:
                os.unlink(temp_backup_file)
        else:
            # Flush current data (optional - can be dangerous)
            self.stdout.write('Flushing current database...')
            call_command('flush', '--noinput')
            
            # Load data
            call_command('loaddata', backup_file)
