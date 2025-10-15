#!/bin/bash
# Simple one-liner backup for mydevil.net cron
# Usage in cron: 0 2 * * * /home/username/domains/betulait.usermd.net/public_python/simple_backup.sh

cd ~/domains/betulait.usermd.net/public_python && python manage.py backup_database --format=sql --rotate=7 >> backup_cron.log 2>&1
