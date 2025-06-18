# 🚀 Deployment - System Helpdesk

## Przegląd Wdrożenia

System Helpdesk jest zaprojektowany do wdrożenia na hostingach internetowych z obsługą Python/Django. Głównym celem jest zapewnienie stabilnego, bezpiecznego i skalowalnego środowiska produkcyjnego.

## Wymagania Serwera

### Minimalne Wymagania
- **RAM:** 1GB (zalecane 2GB)
- **CPU:** 1 rdzeń (zalecane 2 rdzenie)
- **Dysk:** 10GB wolnego miejsca
- **Sieć:** Stabilne połączenie internetowe

### Zalecane Specyfikacje
- **RAM:** 4GB
- **CPU:** 4 rdzenie
- **Dysk:** SSD 50GB
- **Backup:** Automatyczny backup bazy danych

### Wymagania Oprogramowania
- **Python:** 3.8 - 3.12
- **Web Server:** Apache/Nginx
- **Database:** MySQL 5.7+ lub PostgreSQL 12+
- **SSL:** Certyfikat SSL/TLS

## Konfiguracja Środowiska

### 1. Przygotowanie Serwera

#### Aktualizacja Systemu
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

#### Instalacja Python
```bash
# Ubuntu/Debian
sudo apt install python3 python3-pip python3-venv

# CentOS/RHEL
sudo yum install python3 python3-pip
```

#### Instalacja MySQL
```bash
# Ubuntu/Debian
sudo apt install mysql-server mysql-client

# CentOS/RHEL
sudo yum install mysql-server mysql
```

### 2. Konfiguracja Bazy Danych

#### Tworzenie Bazy Danych
```sql
CREATE DATABASE helpdesk_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'helpdesk_user'@'localhost' IDENTIFIED BY 'silne_haslo_123';
GRANT ALL PRIVILEGES ON helpdesk_db.* TO 'helpdesk_user'@'localhost';
FLUSH PRIVILEGES;
```

#### Konfiguracja MySQL
```ini
# /etc/mysql/mysql.conf.d/mysqld.cnf
[mysqld]
max_connections = 200
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
query_cache_size = 64M
```

### 3. Konfiguracja Aplikacji

#### Struktura Katalogów
```
/var/www/helpdesk/
├── app/                    # Kod aplikacji
├── static/                 # Pliki statyczne
├── media/                  # Załączniki użytkowników
├── logs/                   # Logi aplikacji
├── backups/                # Backupy bazy danych
└── venv/                   # Środowisko wirtualne
```

#### Plik Konfiguracyjny
```python
# settings_production.py
import os
from decouple import config

DEBUG = False
ALLOWED_HOSTS = ['twoja-domena.pl', 'www.twoja-domena.pl']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default='helpdesk_db'),
        'USER': config('DB_USER', default='helpdesk_user'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

# Bezpieczeństwo
SECRET_KEY = config('SECRET_KEY')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', default=587)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

# Logi
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/www/helpdesk/logs/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## Deployment na mydevil.net

### 1. Przygotowanie Plików

#### Struktura Projektu
```
public_html/
├── passenger_wsgi.py       # Konfiguracja WSGI
├── app/                    # Kod aplikacji
├── static/                 # Pliki statyczne
├── media/                  # Załączniki
├── logs/                   # Logi
└── requirements.txt        # Zależności
```

#### Konfiguracja passenger_wsgi.py
```python
import os
import sys

# Ścieżka do aplikacji
path = '/home/username/public_html'
if path not in sys.path:
    sys.path.append(path)

# Zmienne środowiskowe
os.environ['DJANGO_SETTINGS_MODULE'] = 'projekt_wdrozeniowy.settings_production'

# Import aplikacji Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 2. Upload Plików

#### Metoda 1: FTP/SFTP
1. **Połącz się z serwerem** przez FTP/SFTP
2. **Prześlij pliki** do katalogu `public_html/`
3. **Ustaw uprawnienia:**
   ```bash
   chmod 755 public_html/
   chmod 644 public_html/*.py
   chmod -R 755 public_html/static/
   chmod -R 777 public_html/media/
   chmod -R 777 public_html/logs/
   ```

#### Metoda 2: Git
```bash
# Na serwerze
cd public_html
git clone https://github.com/username/projekt-wdrozeniowy.git .
git checkout production
```

### 3. Konfiguracja Środowiska

#### Instalacja Zależności
```bash
cd public_html
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Konfiguracja Bazy Danych
```bash
# Utworzenie pliku .env
cat > .env << EOF
DB_NAME=helpdesk_db
DB_USER=helpdesk_user
DB_PASSWORD=twoje_haslo
DB_HOST=localhost
SECRET_KEY=twoj_sekretny_klucz
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=twoj_email@gmail.com
EMAIL_HOST_PASSWORD=twoje_haslo_email
EOF
```

#### Migracje i Setup
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py setup_demo_data
```

## Konfiguracja Web Server

### Apache z mod_wsgi

#### Konfiguracja Virtual Host
```apache
<VirtualHost *:80>
    ServerName twoja-domena.pl
    ServerAlias www.twoja-domena.pl
    
    DocumentRoot /var/www/helpdesk/public_html
    
    Alias /static/ /var/www/helpdesk/static/
    Alias /media/ /var/www/helpdesk/media/
    
    <Directory /var/www/helpdesk/static>
        Require all granted
    </Directory>
    
    <Directory /var/www/helpdesk/media>
        Require all granted
    </Directory>
    
    WSGIDaemonProcess helpdesk python-path=/var/www/helpdesk:/var/www/helpdesk/venv/lib/python3.8/site-packages
    WSGIProcessGroup helpdesk
    WSGIScriptAlias / /var/www/helpdesk/passenger_wsgi.py
    
    <Directory /var/www/helpdesk>
        <Files passenger_wsgi.py>
            Require all granted
        </Files>
    </Directory>
    
    ErrorLog ${APACHE_LOG_DIR}/helpdesk_error.log
    CustomLog ${APACHE_LOG_DIR}/helpdesk_access.log combined
</VirtualHost>
```

### Nginx z Gunicorn

#### Konfiguracja Nginx
```nginx
server {
    listen 80;
    server_name twoja-domena.pl www.twoja-domena.pl;
    
    location /static/ {
        alias /var/www/helpdesk/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /var/www/helpdesk/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Konfiguracja Gunicorn
```bash
# /etc/systemd/system/helpdesk.service
[Unit]
Description=Helpdesk Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/helpdesk
Environment="PATH=/var/www/helpdesk/venv/bin"
ExecStart=/var/www/helpdesk/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 projekt_wdrozeniowy.wsgi:application

[Install]
WantedBy=multi-user.target
```

## SSL/TLS Konfiguracja

### Let's Encrypt (Certbot)

#### Instalacja Certbot
```bash
# Ubuntu/Debian
sudo apt install certbot python3-certbot-apache

# CentOS/RHEL
sudo yum install certbot python3-certbot-apache
```

#### Generowanie Certyfikatu
```bash
sudo certbot --apache -d twoja-domena.pl -d www.twoja-domena.pl
```

#### Automatyczne Odnawianie
```bash
# Dodaj do crontab
0 12 * * * /usr/bin/certbot renew --quiet
```

## Monitoring i Logi

### Konfiguracja Logów

#### Logi Aplikacji
```python
# settings_production.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/www/helpdesk/logs/django.log',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/www/helpdesk/logs/error.log',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'crm': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

#### Logi Serwera
```bash
# Apache
tail -f /var/log/apache2/helpdesk_error.log
tail -f /var/log/apache2/helpdesk_access.log

# Nginx
tail -f /var/log/nginx/helpdesk_error.log
tail -f /var/log/nginx/helpdesk_access.log
```

### Monitoring Wydajności

#### System Monitoring
```bash
# Sprawdzenie użycia zasobów
htop
df -h
free -h

# Sprawdzenie procesów
ps aux | grep python
ps aux | grep gunicorn
```

#### Aplikacja Monitoring
```python
# Dodaj do requirements.txt
django-debug-toolbar==3.2.4
django-extensions==3.1.5

# Konfiguracja w settings
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1']
```

## Backup i Odzyskiwanie

### Automatyczny Backup

#### Skrypt Backup
```bash
#!/bin/bash
# /var/www/helpdesk/backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/www/helpdesk/backups"
DB_NAME="helpdesk_db"
DB_USER="helpdesk_user"
DB_PASSWORD="twoje_haslo"

# Backup bazy danych
mysqldump -u$DB_USER -p$DB_PASSWORD $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql

# Backup plików
tar -czf $BACKUP_DIR/files_backup_$DATE.tar.gz /var/www/helpdesk/media

# Usuwanie starych backupów (starszych niż 30 dni)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE" >> $BACKUP_DIR/backup.log
```

#### Cron Job
```bash
# Dodaj do crontab (backup codziennie o 3:00)
0 3 * * * /var/www/helpdesk/backup.sh
```

### Procedura Odzyskiwania

#### Odzyskiwanie Bazy Danych
```bash
# Zatrzymanie aplikacji
sudo systemctl stop apache2
sudo systemctl stop gunicorn

# Przywrócenie bazy
mysql -u$DB_USER -p$DB_PASSWORD $DB_NAME < backup_file.sql

# Uruchomienie aplikacji
sudo systemctl start apache2
sudo systemctl start gunicorn
```

#### Odzyskiwanie Plików
```bash
# Przywrócenie plików
tar -xzf files_backup_DATE.tar.gz -C /

# Sprawdzenie uprawnień
chown -R www-data:www-data /var/www/helpdesk/media
chmod -R 755 /var/www/helpdesk/media
```

## Bezpieczeństwo

### Firewall
```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# iptables (CentOS)
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -P INPUT DROP
```

### Fail2ban
```bash
# Instalacja
sudo apt install fail2ban

# Konfiguracja
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local

# Edycja konfiguracji
sudo nano /etc/fail2ban/jail.local
```

### Regularne Aktualizacje
```bash
# Skrypt aktualizacji
#!/bin/bash
# /var/www/helpdesk/update.sh

cd /var/www/helpdesk
source venv/bin/activate

# Backup przed aktualizacją
./backup.sh

# Aktualizacja kodu
git pull origin production

# Aktualizacja zależności
pip install -r requirements.txt

# Migracje
python manage.py migrate

# Restart serwisów
sudo systemctl restart apache2
sudo systemctl restart gunicorn

echo "Update completed: $(date)" >> /var/www/helpdesk/logs/update.log
```

---

**Ostatnia aktualizacja:** 18.06.2025 