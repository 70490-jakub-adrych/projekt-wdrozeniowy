# Database Backup System

This directory contains comprehensive database backup tools for the Django CRM application.

## Overview

The backup system provides:
- **Automated daily backups** with rotation
- **Multiple backup formats** (MySQL dumps + Django fixtures)
- **Compression** to save space
- **Monitoring and status reporting**
- **Easy restore functionality**

## Quick Start

### 1. Test the backup system

```bash
# Create a backup manually
python manage.py backup_database

# Check backup status
python manage.py backup_status

# List available backups
ls -la backups/database/
```

### 2. Set up automated backups

**On mydevil.net (Linux hosting):**

1. Make the script executable:
```bash
chmod +x daily_backup.sh
```

2. Add to crontab for daily backups at 2 AM:
```bash
crontab -e
# Add this line:
0 2 * * * /home/username/domains/betulait.usermd.net/public_python/daily_backup.sh
```

**On Windows (development):**

1. Use Task Scheduler to run `daily_backup.bat` daily
2. Or run manually: `daily_backup.bat`

## Commands

### backup_database

Creates database backups with various options.

```bash
# Basic backup (MySQL dump, compressed)
python manage.py backup_database

# JSON fixture backup
python manage.py backup_database --format=json

# Custom location and retention
python manage.py backup_database --output-dir=custom/path --rotate=14

# Uncompressed backup
python manage.py backup_database --compress=False
```

**Options:**
- `--format`: `sql` (MySQL dump) or `json` (Django fixture)
- `--output-dir`: Custom backup directory (default: `backups/database`)
- `--compress`: Enable/disable gzip compression (default: enabled)
- `--rotate`: Number of backups to keep (default: 7)
- `--prefix`: Custom filename prefix (default: `backup`)

### restore_database

Restores database from backup files.

```bash
# Restore from specific backup
python manage.py restore_database backups/database/backup_mysql_20231214_143022.sql.gz

# Auto-detect format
python manage.py restore_database backups/database/backup_django_20231214_143022.json.gz

# Skip confirmation (dangerous!)
python manage.py restore_database --confirm backup_file.sql
```

**⚠️ WARNING:** This will completely replace your current database!

### backup_status

Shows comprehensive backup status and health check.

```bash
# Show backup status
python manage.py backup_status

# Analyze longer period
python manage.py backup_status --days=60

# Check specific directory
python manage.py backup_status --backup-dir=custom/backup/path
```

## File Structure

```
backups/
└── database/
    ├── backup_mysql_20231214_020001.sql.gz    # MySQL dump (compressed)
    ├── backup_mysql_20231213_020001.sql.gz
    ├── json_backup_django_20231214_020001.json.gz  # Django fixture (compressed)
    └── json_backup_django_20231213_020001.json.gz

logs/
└── backup.log  # Backup operation logs
```

## Backup Formats

### MySQL Dumps (.sql)
- **Pros**: Fast, efficient, database-native format
- **Cons**: Requires MySQL client tools to restore
- **Best for**: Production environments, large databases

### Django Fixtures (.json)
- **Pros**: Database-agnostic, can restore to any Django-supported DB
- **Cons**: Slower, larger file size, doesn't include all metadata
- **Best for**: Development, migration between database types

## mydevil.net Specific Setup

To set up automated backups on mydevil.net hosting:

1. **Upload the daily_backup.sh script** to your domain directory
2. **Make it executable**: `chmod +x daily_backup.sh`
3. **Set up cron job** in your hosting panel or via command line:
   ```bash
   crontab -e
   # Add this line for daily 2 AM backups:
   0 2 * * * /home/yourusername/domains/betulait.usermd.net/public_python/daily_backup.sh
   ```

4. **Test the setup**:
   ```bash
   ./daily_backup.sh
   python manage.py backup_status
   ```

## Best Practices

1. **Multiple formats**: Keep both SQL and JSON backups
2. **Regular testing**: Test restore process monthly  
3. **Monitor regularly**: Check `backup_status` weekly
4. **Retention policy**: Balance storage costs with recovery needs (default: 7 days)

## Security Notes

- Backup files contain sensitive data - protect them appropriately
- Limit access to backup directories
- Consider off-site backup copies for critical data
