@echo off
REM Daily database backup script for Windows
REM Configure this script for your local development environment

setlocal enabledelayedexpansion

REM Configuration
set PROJECT_DIR=%~dp0
set BACKUP_DIR=%PROJECT_DIR%backups\database
set LOG_FILE=%PROJECT_DIR%backup.log
set PYTHON_CMD=python
set KEEP_DAYS=7

REM Function to log with timestamp
:log
echo %date% %time% - %~1 >> "%LOG_FILE%"
echo %date% %time% - %~1
exit /b

REM Start backup process
call :log "Starting database backup"

REM Change to project directory
cd /d "%PROJECT_DIR%" || (
    call :log "ERROR: Cannot change to project directory: %PROJECT_DIR%"
    exit /b 1
)

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    call :log "Activated virtual environment"
) else if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    call :log "Activated virtual environment"
)

REM Create backup directory if it doesn't exist
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

REM Run backup command
call :log "Creating database backup..."
%PYTHON_CMD% manage.py backup_database --format=sql --compress --rotate=%KEEP_DAYS%
if !errorlevel! equ 0 (
    call :log "Backup completed successfully"
) else (
    call :log "ERROR: Backup command failed"
    exit /b 1
)

REM Optional: Create additional JSON backup for extra safety
call :log "Creating additional JSON backup..."
%PYTHON_CMD% manage.py backup_database --format=json --compress --rotate=%KEEP_DAYS% --prefix=json_backup
if !errorlevel! equ 0 (
    call :log "JSON backup completed successfully"
) else (
    call :log "WARNING: JSON backup failed"
)

call :log "Backup process completed"

REM Clean up old log files (keep last 30 days)
forfiles /p "%PROJECT_DIR%" /m "backup.log.*" /d -30 /c "cmd /c del @path" 2>nul

endlocal
exit /b 0
