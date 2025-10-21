# 9. Wdrożenie

## 9.1 Instalacja i uruchomienie

### 9.1.1 Instalacja systemu (Linux/macOS)

#### Wymagania wstępne:
- Python 3.8 - 3.12
- Git
- Dostęp do internetu

#### Kroki instalacji:

**1. Klonowanie repozytorium:**
```bash
git clone https://github.com/70490-jakub-adrych/projekt-wdrozeniowy.git
cd projekt-wdrozeniowy
```

**2. Utworzenie wirtualnego środowiska:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Sprawdzenie aktywacji:**
```bash
which python
which pip
# Powinno pokazać ścieżki do wirtualnego środowiska
```

**4. Instalacja zależności:**
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

**5. Weryfikacja instalacji Django:**
```bash
python -c "import django; print(django.__version__)"
```

**6. Pobieranie plików statycznych:**
```bash
bash download_static_files.sh
```

**7. Konfiguracja bazy danych:**
```bash
python manage.py makemigrations
python manage.py migrate
```

**8. Tworzenie danych demonstracyjnych:**
```bash
python manage.py setup_demo_data
```

**9. Uruchomienie serwera:**
```bash
python manage.py runserver
```

### 9.1.2 Instalacja systemu (Windows)

#### Wymagania wstępne:
- Python 3.8 - 3.12
- Git
- PowerShell

#### Kroki instalacji:

**1. Klonowanie repozytorium:**
```powershell
git clone https://github.com/70490-jakub-adrych/projekt-wdrozeniowy.git
cd projekt-wdrozeniowy
```

**2. Utworzenie wirtualnego środowiska:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**3. Instalacja zależności:**
```powershell
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

**4. Pobieranie plików statycznych:**
```powershell
.\download_static_files.ps1
```

**5. Konfiguracja bazy danych:**
```powershell
python manage.py makemigrations
python manage.py migrate
```

**6. Tworzenie danych demonstracyjnych:**
```powershell
python manage.py setup_demo_data
```

**7. Uruchomienie serwera:**
```powershell
python manage.py runserver
```

### 9.1.3 Konfiguracja MySQL dla produkcji

#### Instalacja MySQL:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server

# CentOS/RHEL
sudo yum install mysql-server
```

#### Konfiguracja bazy danych:
```sql
CREATE DATABASE helpdesk_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'helpdesk_user'@'localhost' IDENTIFIED BY 'twoje_bezpieczne_haslo';
GRANT ALL PRIVILEGES ON helpdesk_db.* TO 'helpdesk_user'@'localhost';
FLUSH PRIVILEGES;
```

#### Konfiguracja aplikacji:
```bash
# Skopiuj plik konfiguracyjny
cp .env-mysql-example .env

# Edytuj plik .env
nano .env
```

**Przykładowa konfiguracja .env:**
```env
DEBUG=False
SECRET_KEY=twoj-bardzo-bezpieczny-klucz-sekretny
DB_ENGINE=django.db.backends.mysql
DB_NAME=helpdesk_db
DB_USER=helpdesk_user
DB_PASSWORD=twoje_bezpieczne_haslo
DB_HOST=localhost
DB_PORT=3306
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=twoj-email@gmail.com
EMAIL_HOST_PASSWORD=haslo-aplikacji
DEFAULT_FROM_EMAIL=noreply@twoja-domena.com
SITE_URL=https://twoja-domena.com
```

#### Uruchomienie z MySQL:
```bash
python manage.py migrate
python manage.py setup_demo_data
python manage.py runserver
```

## 9.2 Konta demonstracyjne

### 9.2.1 Dostęp do systemu

Po uruchomieniu aplikacja będzie dostępna pod adresem:
- **Lokalnie:** http://127.0.0.1:8000/
- **Produkcja:** https://twoja-domena.com

### 9.2.2 Konta testowe

#### Administrator:
- **Nazwa użytkownika:** admin
- **Hasło:** admin123
- **Uprawnienia:** Pełny dostęp do systemu

#### Super Agent:
- **Nazwa użytkownika:** superagent
- **Hasło:** superagent123
- **Uprawnienia:** Zarządzanie zgłoszeniami i agentami

#### Agent:
- **Nazwa użytkownika:** agent1
- **Hasło:** agent123
- **Uprawnienia:** Obsługa przypisanych zgłoszeń

#### Klient:
- **Nazwa użytkownika:** client1
- **Hasło:** client123
- **Uprawnienia:** Zgłaszanie problemów

#### Viewer:
- **Nazwa użytkownika:** viewer
- **Hasło:** viewer123
- **Uprawnienia:** Tylko podgląd zgłoszeń

## 9.3 Backup i przywracanie danych

### 9.3.1 Automatyczne kopie zapasowe

#### Konfiguracja przez cron (Linux):
```bash
# Edytuj crontab
crontab -e

# Dodaj zadania backupu
# Codziennie o 2:00 - backup MySQL
0 2 * * * cd /path/to/projekt-wdrozeniowy && python manage.py backup_database --format=sql --rotate=7

# Tygodniowo o 2:30 - backup JSON
30 2 * * 0 cd /path/to/projekt-wdrozeniowy && python manage.py backup_database --format=json --rotate=4
```

#### Konfiguracja na mydevil.net:
1. **Zaloguj się do panelu mydevil.net**
2. **Przejdź do sekcji "Cron"**
3. **Dodaj nowe zadanie cron:**
   - **Komenda:** `cd ~/domains/twoja-domena.com/public_python && python manage.py backup_database --format=sql --rotate=7`
   - **Częstotliwość:** Codziennie o 2:00
   - **Czas:** `0 2 * * *`

### 9.3.2 Ręczne tworzenie kopii zapasowych

#### Przez wiersz poleceń:
```bash
# Backup MySQL (zalecane)
python manage.py backup_database --format=sql

# Backup JSON (uniwersalne)
python manage.py backup_database --format=json

# Sprawdzenie statusu backupów
python manage.py backup_status
```

#### Przez interfejs web:
1. Zaloguj się jako administrator
2. Przejdź do sekcji "Administracja" → "Backup"
3. Kliknij "Utwórz backup teraz"
4. Wybierz typ backupu
5. Kliknij "Rozpocznij backup"

### 9.3.3 Przywracanie z kopii zapasowej

#### Procedura przywracania:
```bash
# Wyświetl dostępne kopie zapasowe
python manage.py backup_status

# Przywróć z konkretnej kopii (UWAGA: zastąpi obecne dane!)
python manage.py restore_database backups/database/backup_mysql_20250117_020000.sql.gz
```

#### Bezpieczne przywracanie:
1. **Zatrzymaj aplikację** (jeśli działa)
2. **Utwórz kopię obecnej bazy** (na wszelki wypadek)
3. **Wykonaj przywracanie** z wybranej kopii
4. **Sprawdź integralność** danych
5. **Uruchom aplikację** ponownie

## 9.4 Konfiguracja serwera produkcyjnego

### 9.4.1 Konfiguracja Apache

#### Instalacja mod_wsgi:
```bash
# Ubuntu/Debian
sudo apt install libapache2-mod-wsgi-py3

# CentOS/RHEL
sudo yum install mod_wsgi
```

#### Konfiguracja Apache:
```apache
<VirtualHost *:80>
    ServerName twoja-domena.com
    Redirect permanent / https://twoja-domena.com/
</VirtualHost>

<VirtualHost *:443>
    ServerName twoja-domena.com
    DocumentRoot /path/to/projekt-wdrozeniowy/public
    
    WSGIDaemonProcess helpdesk python-path=/path/to/projekt-wdrozeniowy python-home=/path/to/projekt-wdrozeniowy/venv
    WSGIProcessGroup helpdesk
    WSGIScriptAlias / /path/to/projekt-wdrozeniowy/projekt_wdrozeniowy/wsgi.py
    
    Alias /static/ /path/to/projekt-wdrozeniowy/public/static/
    Alias /media/ /path/to/projekt-wdrozeniowy/public/media/
    
    <Directory /path/to/projekt-wdrozeniowy/public/static>
        Require all granted
    </Directory>
    
    <Directory /path/to/projekt-wdrozeniowy/public/media>
        Require all granted
    </Directory>
    
    SSLEngine on
    SSLCertificateFile /path/to/certificate.crt
    SSLCertificateKeyFile /path/to/private.key
</VirtualHost>
```

### 9.4.2 Konfiguracja Nginx

#### Instalacja Nginx:
```bash
# Ubuntu/Debian
sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx
```

#### Konfiguracja Nginx:
```nginx
server {
    listen 80;
    server_name twoja-domena.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name twoja-domena.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /path/to/projekt-wdrozeniowy/public/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /path/to/projekt-wdrozeniowy/public/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### 9.4.3 Konfiguracja Gunicorn

#### Instalacja Gunicorn:
```bash
pip install gunicorn
```

#### Konfiguracja Gunicorn:
```bash
# Uruchomienie Gunicorn
gunicorn --bind 127.0.0.1:8000 projekt_wdrozeniowy.wsgi:application

# Z konfiguracją
gunicorn --config gunicorn.conf.py projekt_wdrozeniowy.wsgi:application
```

#### Plik gunicorn.conf.py:
```python
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
```

## 9.5 Monitoring i utrzymanie

### 9.5.1 Monitoring systemu

#### Logi aplikacji:
```bash
# Przeglądanie logów Django
tail -f django.log

# Przeglądanie logów SQL
tail -f sql.log

# Przeglądanie logów serwera web
tail -f /var/log/apache2/error.log
tail -f /var/log/nginx/error.log
```

#### Monitoring wydajności:
```bash
# Sprawdzenie wykorzystania zasobów
htop
df -h
free -h

# Sprawdzenie połączeń sieciowych
netstat -tulpn
ss -tulpn
```

### 9.5.2 Utrzymanie systemu

#### Czyszczenie logów:
```bash
# Wyczyść logi starsze niż 30 dni
python manage.py clean_logs --days=30

# Wyczyść sesje wygasłe
python manage.py clearsessions

# Wyczyść cache
python manage.py clear_cache
```

#### Optymalizacja bazy danych:
```bash
# Analiza wydajności (MySQL)
mysql -u root -p
USE helpdesk_db;
ANALYZE TABLE crm_ticket;
ANALYZE TABLE crm_userprofile;
ANALYZE TABLE crm_activitylog;

# Defragmentacja (MySQL)
OPTIMIZE TABLE crm_ticket;
OPTIMIZE TABLE crm_userprofile;
OPTIMIZE TABLE crm_activitylog;
```

#### Aktualizacja systemu:
```bash
# Aktualizacja zależności
pip install --upgrade -r requirements.txt

# Migracje bazy danych
python manage.py makemigrations
python manage.py migrate

# Kolekcja plików statycznych
python manage.py collectstatic --noinput
```

## 9.6 Rozwiązywanie problemów

### 9.6.1 Najczęstsze problemy

#### Problem: Błąd "ModuleNotFoundError"
**Rozwiązanie:**
```bash
# Sprawdź czy wirtualne środowisko jest aktywne
which python
# Powinno pokazać ścieżkę do venv

# Jeśli nie, aktywuj środowisko
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\Activate.ps1  # Windows
```

#### Problem: Błąd połączenia z bazą danych
**Rozwiązanie:**
```bash
# Sprawdź ustawienia bazy danych
python manage.py dbshell

# Sprawdź czy MySQL działa
sudo systemctl status mysql

# Sprawdź logi MySQL
sudo tail -f /var/log/mysql/error.log
```

#### Problem: Błędy 500 (Internal Server Error)
**Rozwiązanie:**
```bash
# Sprawdź logi Django
tail -f django.log

# Sprawdź uprawnienia plików
ls -la
chmod 755 manage.py
chmod -R 755 static/
chmod -R 755 media/

# Sprawdź konfigurację DEBUG
python manage.py shell
>>> from django.conf import settings
>>> print(settings.DEBUG)
```

#### Problem: Powiadomienia email nie działają
**Rozwiązanie:**
```bash
# Przetestuj połączenie SMTP
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])

# Sprawdź ustawienia email w settings.py
# Sprawdź logi serwera SMTP
```

### 9.6.2 Kontakt z pomocą techniczną

#### Wsparcie techniczne:
- **Email:** admin@betulait.usermd.net
- **GitHub:** Sprawdź issues w repozytorium projektu
- **Dokumentacja:** Przeczytaj odpowiednie sekcje dokumentacji

#### Logi do przesłania:
- `django.log` - logi aplikacji Django
- `sql.log` - logi zapytań SQL
- Logi serwera web (Apache/Nginx)
- Logi systemu operacyjnego

#### Informacje o systemie:
```bash
# Informacje o systemie
python --version
pip list
python manage.py version

# Informacje o bazie danych
python manage.py dbshell
# W MySQL: SELECT VERSION();

# Informacje o konfiguracji
python manage.py diffsettings
```

## 9.7 Rekomendacje do utrzymania i rozwoju

### 9.7.1 Utrzymanie systemu

#### Codzienne zadania:
- Sprawdzenie logów błędów
- Monitorowanie wykorzystania zasobów
- Sprawdzenie statusu backupów
- Monitorowanie wydajności

#### Tygodniowe zadania:
- Przegląd logów bezpieczeństwa
- Sprawdzenie aktualizacji bezpieczeństwa
- Analiza wydajności systemu
- Czyszczenie starych logów

#### Miesięczne zadania:
- Pełny backup systemu
- Testowanie procedur przywracania
- Przegląd uprawnień użytkowników
- Analiza trendów użycia

### 9.7.2 Rozwój systemu

#### Krótkoterminowe ulepszenia:
- Integracja z Active Directory/LDAP
- Rozszerzenie systemu powiadomień (SMS)
- Ulepszenie interfejsu mobilnego
- Dodanie modułu bazy wiedzy

#### Długoterminowe cele:
- Mikroserwisy architektura
- Integracja z systemami monitoringu
- Machine learning dla klasyfikacji zgłoszeń
- Aplikacje mobilne (iOS/Android)

#### Monitoring rozwoju:
- Zbieranie feedbacku od użytkowników
- Analiza metryk użycia
- Regularne przeglądy bezpieczeństwa
- Planowanie aktualizacji technologicznych
