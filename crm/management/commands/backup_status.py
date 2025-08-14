"""
Backup monitoring management command
Shows backup status and statistics
"""

import os
import gzip
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone

class Command(BaseCommand):
    help = 'Show backup status and statistics'

    def add_arguments(self, parser):
        parser.add_argument(
            '--backup-dir',
            default='backups/database',
            help='Directory to check for backups (relative to project root)'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to analyze'
        )

    def handle(self, *args, **options):
        backup_dir = os.path.join(settings.BASE_DIR, options['backup_dir'])
        
        if not os.path.exists(backup_dir):
            self.stdout.write(
                self.style.WARNING(f'Backup directory not found: {backup_dir}')
            )
            return
        
        self._show_backup_status(backup_dir, options['days'])

    def _show_backup_status(self, backup_dir, days):
        """Show comprehensive backup status"""
        self.stdout.write(self.style.SUCCESS('=== BACKUP STATUS REPORT ==='))
        self.stdout.write(f'Backup Directory: {backup_dir}')
        self.stdout.write(f'Analysis Period: Last {days} days')
        self.stdout.write('')
        
        # Get all backup files
        backup_files = []
        total_size = 0
        
        try:
            for filename in os.listdir(backup_dir):
                if (filename.endswith('.sql') or filename.endswith('.sql.gz') or
                    filename.endswith('.json') or filename.endswith('.json.gz')):
                    
                    file_path = os.path.join(backup_dir, filename)
                    file_stat = os.stat(file_path)
                    file_time = datetime.fromtimestamp(file_stat.st_mtime)
                    file_size = file_stat.st_size
                    
                    backup_files.append({
                        'name': filename,
                        'path': file_path,
                        'time': file_time,
                        'size': file_size,
                        'age_days': (datetime.now() - file_time).days
                    })
                    
                    total_size += file_size
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error reading backup directory: {str(e)}')
            )
            return
        
        if not backup_files:
            self.stdout.write(self.style.WARNING('No backup files found!'))
            return
        
        # Sort by date (newest first)
        backup_files.sort(key=lambda x: x['time'], reverse=True)
        
        # Filter by days
        recent_backups = [b for b in backup_files if b['age_days'] <= days]
        
        # Summary statistics
        self.stdout.write(self.style.SUCCESS('SUMMARY:'))
        self.stdout.write(f'Total backup files: {len(backup_files)}')
        self.stdout.write(f'Recent backups ({days} days): {len(recent_backups)}')
        self.stdout.write(f'Total size: {self._format_size(total_size)}')
        
        if backup_files:
            newest = backup_files[0]
            oldest = backup_files[-1]
            self.stdout.write(f'Newest backup: {newest["time"].strftime("%Y-%m-%d %H:%M:%S")} ({newest["age_days"]} days ago)')
            self.stdout.write(f'Oldest backup: {oldest["time"].strftime("%Y-%m-%d %H:%M:%S")} ({oldest["age_days"]} days ago)')
        
        # Health check
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('HEALTH CHECK:'))
        
        # Check if we have recent backups
        if recent_backups:
            latest_backup_age = recent_backups[0]['age_days']
            if latest_backup_age == 0:
                self.stdout.write(self.style.SUCCESS('✓ Fresh backup available (today)'))
            elif latest_backup_age == 1:
                self.stdout.write(self.style.SUCCESS('✓ Recent backup available (yesterday)'))
            elif latest_backup_age <= 3:
                self.stdout.write(self.style.WARNING(f'⚠ Last backup is {latest_backup_age} days old'))
            else:
                self.stdout.write(self.style.ERROR(f'✗ Last backup is {latest_backup_age} days old - STALE!'))
        else:
            self.stdout.write(self.style.ERROR('✗ No recent backups found!'))
        
        # Check backup frequency
        if len(recent_backups) >= days * 0.8:  # 80% coverage
            self.stdout.write(self.style.SUCCESS('✓ Good backup frequency'))
        elif len(recent_backups) >= days * 0.5:  # 50% coverage
            self.stdout.write(self.style.WARNING('⚠ Moderate backup frequency'))
        else:
            self.stdout.write(self.style.ERROR('✗ Poor backup frequency'))
        
        # Check for both SQL and JSON backups
        sql_backups = [b for b in recent_backups if '.sql' in b['name']]
        json_backups = [b for b in recent_backups if '.json' in b['name']]
        
        if sql_backups and json_backups:
            self.stdout.write(self.style.SUCCESS('✓ Both SQL and JSON backups available'))
        elif sql_backups:
            self.stdout.write(self.style.WARNING('⚠ Only SQL backups available'))
        elif json_backups:
            self.stdout.write(self.style.WARNING('⚠ Only JSON backups available'))
        else:
            self.stdout.write(self.style.ERROR('✗ No recognized backup format found'))
        
        # Recent backup details
        if recent_backups:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('RECENT BACKUPS:'))
            self.stdout.write(f'{"Filename":<30} {"Date":<20} {"Age":<12} {"Size":<10}')
            self.stdout.write('-' * 75)
            
            for backup in recent_backups[:10]:  # Show last 10
                age_str = f"{backup['age_days']}d ago" if backup['age_days'] > 0 else "today"
                size_str = self._format_size(backup['size'])
                date_str = backup['time'].strftime('%Y-%m-%d %H:%M')
                
                self.stdout.write(f'{backup["name"]:<30} {date_str:<20} {age_str:<12} {size_str:<10}')
        
        # Disk space check
        try:
            backup_dir_stat = os.statvfs(backup_dir)
            free_space = backup_dir_stat.f_frsize * backup_dir_stat.f_bavail
            total_space = backup_dir_stat.f_frsize * backup_dir_stat.f_blocks
            used_percent = ((total_space - free_space) / total_space) * 100
            
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('DISK SPACE:'))
            self.stdout.write(f'Free space: {self._format_size(free_space)}')
            self.stdout.write(f'Used: {used_percent:.1f}%')
            
            if used_percent > 90:
                self.stdout.write(self.style.ERROR('✗ Disk space critical!'))
            elif used_percent > 80:
                self.stdout.write(self.style.WARNING('⚠ Disk space low'))
            else:
                self.stdout.write(self.style.SUCCESS('✓ Disk space OK'))
                
        except AttributeError:
            # statvfs not available on Windows
            pass

    def _format_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024.0 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f}{size_names[i]}"
