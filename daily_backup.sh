#!/bin/bash

# Daily database backup script for mydevil.net hosting
# Place this script in your home directory and add to crontab

# Configuration
PROJECT_DIR="$HOME/domains/betulait.usermd.net/public_python"
BACKUP_DIR="$PROJECT_DIR/backups/database"
LOG_FILE="$PROJECT_DIR/backup.log"
PYTHON_PATH="python3.12"  # Adjust based on your Python version
KEEP_DAYS=7  # Number of days to keep backups

# Function to log with timestamp
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Function to send email notification (optional)
send_notification() {
    local subject="$1"
    local message="$2"
    
    # Uncomment and configure if you want email notifications
    # echo "$message" | mail -s "$subject" your-email@example.com
}

# Start backup process
log "Starting database backup"

# Change to project directory
cd "$PROJECT_DIR" || {
    log "ERROR: Cannot change to project directory: $PROJECT_DIR"
    send_notification "Backup Failed" "Cannot access project directory"
    exit 1
}

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    log "Activated virtual environment"
elif [ -d ".venv" ]; then
    source .venv/bin/activate
    log "Activated virtual environment"
fi

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Run backup command
log "Creating database backup..."
if $PYTHON_PATH manage.py backup_database --format=sql --compress --rotate=$KEEP_DAYS; then
    BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
    log "Backup completed successfully. Backup directory size: $BACKUP_SIZE"
    send_notification "Backup Successful" "Database backup completed. Directory size: $BACKUP_SIZE"
else
    log "ERROR: Backup command failed"
    send_notification "Backup Failed" "Database backup command failed. Check logs for details."
    exit 1
fi

# Optional: Create additional JSON backup for extra safety
log "Creating additional JSON backup..."
if $PYTHON_PATH manage.py backup_database --format=json --compress --rotate=$KEEP_DAYS --prefix=json_backup; then
    log "JSON backup completed successfully"
else
    log "WARNING: JSON backup failed"
fi

# Clean up old log files (keep last 30 days)
find "$(dirname "$LOG_FILE")" -name "backup.log.*" -mtime +30 -delete 2>/dev/null

# Rotate current log if it's too large (>10MB)
if [ -f "$LOG_FILE" ] && [ $(stat -f%z "$LOG_FILE" 2>/dev/null || stat -c%s "$LOG_FILE" 2>/dev/null || echo 0) -gt 10485760 ]; then
    mv "$LOG_FILE" "$LOG_FILE.$(date +%Y%m%d)"
    log "Log file rotated"
fi

log "Backup process completed"

# Optional: Upload to external storage (uncomment and configure as needed)
# log "Uploading to external storage..."
# rsync -avz "$BACKUP_DIR/" user@backup-server:/path/to/backups/
# or
# rclone sync "$BACKUP_DIR/" remote:backup-folder/

exit 0
