"""
Database backup management command
Creates MySQL dumps with compression and rotation
"""

import os
import gzip
import shutil
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.management import call_command
from io import StringIO
import subprocess
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Create database backup with optional rotation'

    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            default='sql',
            choices=['sql', 'json'],
            help='Backup format (sql for MySQL dump, json for Django fixture)'
        )
        parser.add_argument(
            '--output-dir',
            default='backups/database',
            help='Directory to store backups (relative to project root)'
        )
        parser.add_argument(
            '--compress',
            action='store_true',
            default=True,
            help='Compress backup files with gzip'
        )
        parser.add_argument(
            '--rotate',
            type=int,
            default=7,
            help='Number of backup files to keep (0 = no rotation)'
        )
        parser.add_argument(
            '--prefix',
            default='backup',
            help='Prefix for backup filenames'
        )

    def handle(self, *args, **options):
        try:
            backup_dir = self._ensure_backup_directory(options['output_dir'])
            
            if options['format'] == 'sql':
                backup_file = self._create_mysql_backup(backup_dir, options)
            else:
                backup_file = self._create_django_backup(backup_dir, options)
            
            if options['rotate'] > 0:
                self._rotate_backups(backup_dir, options['rotate'], options['prefix'])
            
            self.stdout.write(
                self.style.SUCCESS(f'Backup created successfully: {backup_file}')
            )
            
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            raise CommandError(f'Backup failed: {str(e)}')

    def _ensure_backup_directory(self, output_dir):
        """Create backup directory if it doesn't exist"""
        backup_dir = os.path.join(settings.BASE_DIR, output_dir)
        os.makedirs(backup_dir, exist_ok=True)
        return backup_dir

    def _create_mysql_backup(self, backup_dir, options):
        """Create MySQL dump backup"""
        db_config = settings.DATABASES['default']
        
        if 'mysql' not in db_config['ENGINE']:
            raise CommandError('MySQL backup requested but database is not MySQL')
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{options['prefix']}_mysql_{timestamp}.sql"
        
        if options['compress']:
            filename += '.gz'
        
        backup_file = os.path.join(backup_dir, filename)
        
        # Build mysqldump command
        cmd = [
            'mysqldump',
            '--single-transaction',
            '--routines',
            '--triggers',
            '--add-drop-table',
            '--extended-insert',
            f"--host={db_config['HOST']}",
            f"--port={db_config['PORT'] or '3306'}",
            f"--user={db_config['USER']}",
            f"--password={db_config['PASSWORD']}",
            db_config['NAME']
        ]
        
        self.stdout.write(f'Creating MySQL backup: {backup_file}')
        
        try:
            # Run mysqldump
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Write to file (compressed or uncompressed)
            if options['compress']:
                with gzip.open(backup_file, 'wt', encoding='utf-8') as f:
                    f.write(result.stdout)
            else:
                with open(backup_file, 'w', encoding='utf-8') as f:
                    f.write(result.stdout)
                    
        except subprocess.CalledProcessError as e:
            raise CommandError(f'mysqldump failed: {e.stderr}')
        except FileNotFoundError:
            raise CommandError('mysqldump command not found. Please install MySQL client tools.')
        
        return backup_file

    def _create_django_backup(self, backup_dir, options):
        """Create Django fixture backup (works with any database)"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{options['prefix']}_django_{timestamp}.json"
        
        if options['compress']:
            filename += '.gz'
        
        backup_file = os.path.join(backup_dir, filename)
        
        self.stdout.write(f'Creating Django fixture backup: {backup_file}')
        
        # Capture dumpdata output
        output = StringIO()
        call_command('dumpdata', 
                    stdout=output,
                    natural_foreign=True,
                    natural_primary=True,
                    exclude=['contenttypes', 'auth.permission', 'sessions.session'])
        
        # Write to file (compressed or uncompressed)
        if options['compress']:
            with gzip.open(backup_file, 'wt', encoding='utf-8') as f:
                f.write(output.getvalue())
        else:
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(output.getvalue())
        
        return backup_file

    def _rotate_backups(self, backup_dir, keep_count, prefix):
        """Remove old backup files, keeping only the specified number"""
        try:
            # Get all backup files matching the prefix
            backup_files = []
            for filename in os.listdir(backup_dir):
                if filename.startswith(prefix) and (filename.endswith('.sql') or 
                                                   filename.endswith('.sql.gz') or
                                                   filename.endswith('.json') or
                                                   filename.endswith('.json.gz')):
                    file_path = os.path.join(backup_dir, filename)
                    backup_files.append((file_path, os.path.getmtime(file_path)))
            
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # Remove old files
            files_to_remove = backup_files[keep_count:]
            
            for file_path, _ in files_to_remove:
                os.remove(file_path)
                self.stdout.write(f'Removed old backup: {os.path.basename(file_path)}')
                
            if files_to_remove:
                self.stdout.write(f'Rotation complete: kept {keep_count} newest backups')
                
        except Exception as e:
            logger.warning(f"Backup rotation failed: {str(e)}")
            self.stdout.write(
                self.style.WARNING(f'Warning: Backup rotation failed: {str(e)}')
            )
