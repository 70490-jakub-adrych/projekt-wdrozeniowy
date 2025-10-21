# 🔧 Instrukcja Instalacji Systemu Helpdesk

## Spis Treści
1. [Wymagania Systemowe](#wymagania-systemowe)
2. [Przygotowanie Środowiska](#przygotowanie-środowiska)
3. [Instalacja na Linux/macOS](#instalacja-na-linuxmacos)
4. [Instalacja na Windows](#instalacja-na-windows)
5. [Konfiguracja Bazy Danych](#konfiguracja-bazy-danych)
6. [Konfiguracja Powiadomień Email](#konfiguracja-powiadomień-email)
7. [Pierwsze Uruchomienie](#pierwsze-uruchomienie)
8. [Konfiguracja Produkcyjna](#konfiguracja-produkcyjna)
9. [Rozwiązywanie Problemów Instalacji](#rozwiązywanie-problemów-instalacji)

---

## Wymagania Systemowe

### Minimalne Wymagania
- **Python:** 3.8 - 3.12 (zalecane 3.10+)
- **RAM:** 2GB (zalecane 4GB+)
- **Dysk:** 5GB wolnego miejsca
- **Sieć:** Dostęp do internetu (dla instalacji pakietów)

### Zalecane Wymagania
- **Python:** 3.10 lub 3.11
- **RAM:** 8GB+
- **Dysk:** 20GB+ (z kopiami zapasowymi)
- **CPU:** 2+ rdzenie
- **OS:** Ubuntu 20.04+, CentOS 8+, Windows 10+

### Wymagane Oprogramowanie
- **Python** z pip
- **Git** (do klonowania repozytorium)
- **MySQL** (dla produkcji) lub **SQLite** (dla rozwoju)
- **Web Server:** Apache/Nginx (dla produkcji)

---

## Przygotowanie Środowiska

### 1. Sprawdzenie Wersji Python

```bash
python3 --version
# Powinno pokazać: Python 3.8.x lub wyższy

pip3 --version
# Powinno pokazać wersję pip
```

### 2. Aktualizacja pip

```bash
python3 -m pip install --upgrade pip setuptools wheel
```

### 3. Instalacja Git (jeśli nie jest zainstalowany)

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install git
```

**CentOS/RHEL:**
```bash
sudo yum install git
```

**Windows:**
Pobierz z: https://git-scm.com/download/win

---

## Instalacja na Linux/macOS

### Krok 1: Klonowanie Repozytorium

```bash
# Przejdź do katalogu, gdzie chcesz zainstalować system
cd /opt  # lub inny katalog

# Sklonuj repozytorium
git clone https://github.com/70490-jakub-adrych/projekt-wdrozeniowy.git
cd projekt-wdrozeniowy
```

### Krok 2: Utworzenie Wirtualnego Środowiska

```bash
# Utwórz wirtualne środowisko
python3 -m venv venv

# Aktywuj wirtualne środowisko
source venv/bin/activate

# Sprawdź czy środowisko jest aktywne
which python
# Powinno pokazać: /ścieżka/do/projektu/venv/bin/python
```

### Krok 3: Instalacja Zależności

```bash
# Upewnij się, że jesteś w wirtualnym środowisku
pip install --upgrade pip setuptools wheel

# Zainstaluj zależności
pip install -r requirements.txt

# Sprawdź instalację Django
python -c "import django; print(django.__version__)"
# Powinno pokazać: 4.2.22
```

### Krok 4: Pobieranie Bibliotek Statycznych

```bash
# Uruchom skrypt pobierania plików statycznych
bash download_static_files.sh
```

### Krok 5: Konfiguracja Bazy Danych

```bash
# Utwórz migracje
python manage.py makemigrations

# Zastosuj migracje
python manage.py migrate

# Sprawdź czy migracje zostały zastosowane
python manage.py showmigrations
```

### Krok 6: Tworzenie Konta Administratora

```bash
# Utwórz superużytkownika
python manage.py createsuperuser

# Wprowadź dane:
# Username: admin
# Email address: admin@example.com
# Password: admin123 (ZMIEŃ NATYCHMIAST!)
# Password (again): admin123
```

### Krok 7: Tworzenie Danych Demonstracyjnych

```bash
# Utwórz przykładowe dane
python manage.py setup_demo_data
```

### Krok 8: Pierwsze Uruchomienie

```bash
# Uruchom serwer deweloperski
python manage.py runserver

# System będzie dostępny pod adresem:
# http://127.0.0.1:8000/
```

---

## Instalacja na Windows

### Krok 1: Przygotowanie Środowiska

1. **Pobierz Python** z https://python.org/downloads/
2. **Zainstaluj Python** z zaznaczoną opcją "Add Python to PATH"
3. **Otwórz PowerShell** jako administrator

### Krok 2: Klonowanie Repozytorium

```powershell
# Przejdź do katalogu docelowego
cd C:\

# Sklonuj repozytorium
git clone https://github.com/70490-jakub-adrych/projekt-wdrozeniowy.git
cd projekt-wdrozeniowy
```

### Krok 3: Utworzenie Wirtualnego Środowiska

```powershell
# Utwórz wirtualne środowisko
python -m venv venv

# Aktywuj wirtualne środowisko
.\venv\Scripts\Activate.ps1

# Jeśli wystąpi błąd z ExecutionPolicy, uruchom:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Krok 4: Instalacja Zależności

```powershell
# Aktualizuj pip
python -m pip install --upgrade pip setuptools wheel

# Zainstaluj zależności
pip install -r requirements.txt

# Sprawdź instalację Django
python -c "import django; print(django.__version__)"
```

### Krok 5: Pobieranie Bibliotek Statycznych

```powershell
# Uruchom skrypt PowerShell
.\download_static_files.ps1
```

### Krok 6: Konfiguracja Bazy Danych

```powershell
# Utwórz migracje
python manage.py makemigrations

# Zastosuj migracje
python manage.py migrate
```

### Krok 7: Tworzenie Konta Administratora

```powershell
# Utwórz superużytkownika
python manage.py createsuperuser
```

### Krok 8: Pierwsze Uruchomienie

```powershell
# Uruchom serwer deweloperski
python manage.py runserver
```

---

## Konfiguracja Bazy Danych

### SQLite (Domyślne - Development)

SQLite jest skonfigurowane domyślnie i nie wymaga dodatkowej konfiguracji.

**Lokalizacja pliku:** `db.sqlite3` w katalogu głównym projektu

### MySQL (Produkcja)

#### Instalacja MySQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install mysql-server mysql-client
sudo mysql_secure_installation
```

**CentOS/RHEL:**
```bash
sudo yum install mysql-server mysql
sudo systemctl start mysqld
sudo mysql_secure_installation
```

#### Konfiguracja Bazy Danych MySQL

1. **Zaloguj się do MySQL:**
```bash
sudo mysql -u root -p
```

2. **Utwórz bazę danych i użytkownika:**
```sql
CREATE DATABASE helpdesk_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'helpdesk_user'@'localhost' IDENTIFIED BY 'twoje_silne_haslo';
GRANT ALL PRIVILEGES ON helpdesk_db.* TO 'helpdesk_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

3. **Zainstaluj sterownik MySQL:**
```bash
pip install mysqlclient
```

4. **Utwórz plik konfiguracyjny `.env`:**
```bash
# Skopiuj przykładowy plik
cp .env-mysql-example .env

# Edytuj plik .env
nano .env
```

**Zawartość pliku `.env`:**
```env
# Database Configuration
DB_ENGINE=django.db.backends.mysql
DB_NAME=helpdesk_db
DB_USER=helpdesk_user
DB_PASSWORD=twoje_silne_haslo
DB_HOST=localhost
DB_PORT=3306

# Security
SECRET_KEY=twoj-bardzo-dlugi-i-losowy-klucz-sekretny
DEBUG=False

# Email Configuration
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=helpdesk@example.com

# Site Configuration
SITE_URL=https://your-domain.com
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

5. **Zastosuj migracje:**
```bash
python manage.py migrate
```

---

## Konfiguracja Powiadomień Email

### Konfiguracja SMTP

1. **Edytuj plik `.env`:**
```env
# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=helpdesk@your-domain.com
EMAIL_DISPLAY_NAME=System Helpdesk
```

2. **Dla Gmail - Utwórz hasło aplikacji:**
   - Przejdź do https://myaccount.google.com/security
   - Włącz weryfikację dwuetapową
   - Wygeneruj hasło aplikacji
   - Użyj tego hasła w konfiguracji

3. **Testowanie konfiguracji:**
```bash
python manage.py shell
```

```python
from django.core.mail import send_mail
send_mail(
    'Test Email',
    'To jest testowy email.',
    'helpdesk@your-domain.com',
    ['test@example.com'],
    fail_silently=False,
)
```

---

## Pierwsze Uruchomienie

### 1. Uruchomienie Serwera Deweloperskiego

```bash
# Upewnij się, że wirtualne środowisko jest aktywne
source venv/bin/activate  # Linux/macOS
# lub
.\venv\Scripts\Activate.ps1  # Windows

# Uruchom serwer
python manage.py runserver

# System będzie dostępny pod:
# http://127.0.0.1:8000/
```

### 2. Pierwsze Logowanie

1. **Otwórz przeglądarkę** i przejdź do `http://127.0.0.1:8000/`
2. **Kliknij "Zaloguj się"**
3. **Wprowadź dane administratora:**
   - Username: `admin`
   - Password: `admin123`

### 3. Konfiguracja 2FA

**UWAGA:** System wymaga skonfigurowania uwierzytelniania dwuskładnikowego!

1. **Zainstaluj Google Authenticator** na telefonie
2. **Zeskanuj kod QR** wyświetlony na ekranie
3. **Wprowadź kod weryfikacyjny** z aplikacji
4. **Zapisz kod odzyskiwania** w bezpiecznym miejscu

### 4. Zmiana Hasła Administratora

1. **Kliknij na nazwę użytkownika** w prawym górnym rogu
2. **Wybierz "Zmień hasło"**
3. **Wprowadź nowe silne hasło**
4. **Kliknij "Zmień hasło"**

### 5. Sprawdzenie Funkcjonalności

1. **Przejdź do Dashboard** - sprawdź statystyki
2. **Utwórz testowe zgłoszenie** - sprawdź workflow
3. **Przetestuj powiadomienia email** - wyślij test
4. **Sprawdź logi** - przejrzyj aktywność

---

## Konfiguracja Produkcyjna

### 1. Konfiguracja Serwera Web

#### Apache z mod_wsgi

1. **Zainstaluj Apache i mod_wsgi:**
```bash
sudo apt install apache2 libapache2-mod-wsgi-py3
```

2. **Utwórz konfigurację Apache:**
```bash
sudo nano /etc/apache2/sites-available/helpdesk.conf
```

**Zawartość pliku:**
```apache
<VirtualHost *:80>
    ServerName your-domain.com
    ServerAlias www.your-domain.com
    
    DocumentRoot /path/to/projekt-wdrozeniowy
    
    Alias /static /path/to/projekt-wdrozeniowy/public/static
    Alias /media /path/to/projekt-wdrozeniowy/public/media
    
    <Directory /path/to/projekt-wdrozeniowy/public/static>
        Require all granted
    </Directory>
    
    <Directory /path/to/projekt-wdrozeniowy/public/media>
        Require all granted
    </Directory>
    
    WSGIDaemonProcess helpdesk python-path=/path/to/projekt-wdrozeniowy python-home=/path/to/projekt-wdrozeniowy/venv
    WSGIProcessGroup helpdesk
    WSGIScriptAlias / /path/to/projekt-wdrozeniowy/projekt_wdrozeniowy/wsgi.py
    
    <Directory /path/to/projekt-wdrozeniowy/projekt_wdrozeniowy>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>
</VirtualHost>
```

3. **Włącz stronę i moduł:**
```bash
sudo a2ensite helpdesk
sudo a2enmod wsgi
sudo systemctl reload apache2
```

#### Nginx z uWSGI

1. **Zainstaluj Nginx i uWSGI:**
```bash
sudo apt install nginx uwsgi uwsgi-plugin-python3
```

2. **Skonfiguruj uWSGI:**
```bash
sudo nano /etc/uwsgi/apps-available/helpdesk.ini
```

**Zawartość pliku:**
```ini
[uwsgi]
module = projekt_wdrozeniowy.wsgi:application
master = true
processes = 5
socket = /run/uwsgi/helpdesk.sock
chmod-socket = 666
vacuum = true
die-on-term = true
pythonpath = /path/to/projekt-wdrozeniowy
virtualenv = /path/to/projekt-wdrozeniowy/venv
```

3. **Skonfiguruj Nginx:**
```bash
sudo nano /etc/nginx/sites-available/helpdesk
```

**Zawartość pliku:**
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /path/to/projekt-wdrozeniowy/public;
    }
    
    location /media/ {
        root /path/to/projekt-wdrozeniowy/public;
    }
    
    location / {
        include uwsgi_params;
        uwsgi_pass unix:/run/uwsgi/helpdesk.sock;
    }
}
```

### 2. Konfiguracja SSL/HTTPS

#### Let's Encrypt (Certbot)

```bash
# Zainstaluj Certbot
sudo apt install certbot python3-certbot-apache

# Uzyskaj certyfikat
sudo certbot --apache -d your-domain.com -d www.your-domain.com

# Automatyczne odnowienie
sudo crontab -e
# Dodaj linię:
0 12 * * * /usr/bin/certbot renew --quiet
```

### 3. Konfiguracja Firewall

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Firewalld (CentOS)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 4. Automatyczne Kopie Zapasowe

```bash
# Dodaj do crontab
sudo crontab -e

# Dodaj linie:
0 2 * * * cd /path/to/projekt-wdrozeniowy && /path/to/projekt-wdrozeniowy/venv/bin/python manage.py backup_database --format=sql --rotate=7
30 2 * * * cd /path/to/projekt-wdrozeniowy && /path/to/projekt-wdrozeniowy/venv/bin/python manage.py backup_database --format=json --rotate=7 --prefix=json_backup
```

### 5. Monitorowanie

#### Instalacja systemd service

```bash
sudo nano /etc/systemd/system/helpdesk.service
```

**Zawartość pliku:**
```ini
[Unit]
Description=Helpdesk Django Application
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/projekt-wdrozeniowy
Environment=PATH=/path/to/projekt-wdrozeniowy/venv/bin
ExecStart=/path/to/projekt-wdrozeniowy/venv/bin/uwsgi --ini /etc/uwsgi/apps-enabled/helpdesk.ini
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable helpdesk
sudo systemctl start helpdesk
```

---

## Rozwiązywanie Problemów Instalacji

### Problem: Błąd "ModuleNotFoundError: No module named 'django'"

**Przyczyna:** Wirtualne środowisko nie jest aktywne lub Django nie jest zainstalowane.

**Rozwiązanie:**
```bash
# Sprawdź czy środowisko jest aktywne
which python
# Powinno pokazać ścieżkę do venv

# Jeśli nie, aktywuj środowisko
source venv/bin/activate

# Zainstaluj Django
pip install django==4.2.22
```

### Problem: Błąd "django.core.exceptions.ImproperlyConfigured"

**Przyczyna:** Błędna konfiguracja w settings.py lub brak pliku .env.

**Rozwiązanie:**
1. Sprawdź czy plik `.env` istnieje
2. Sprawdź zawartość pliku `.env`
3. Sprawdź czy wszystkie wymagane zmienne są ustawione

### Problem: Błąd połączenia z bazą danych MySQL

**Przyczyna:** Nieprawidłowe dane połączenia lub problemy z uprawnieniami.

**Rozwiązanie:**
```bash
# Sprawdź połączenie z MySQL
mysql -u helpdesk_user -p helpdesk_db

# Sprawdź uprawnienia
mysql -u root -p
SHOW GRANTS FOR 'helpdesk_user'@'localhost';
```

### Problem: Błąd "Permission denied" przy dostępie do plików

**Przyczyna:** Nieprawidłowe uprawnienia do plików.

**Rozwiązanie:**
```bash
# Ustaw właściciela plików
sudo chown -R www-data:www-data /path/to/projekt-wdrozeniowy

# Ustaw uprawnienia
sudo chmod -R 755 /path/to/projekt-wdrozeniowy
sudo chmod -R 777 /path/to/projekt-wdrozeniowy/public/media
```

### Problem: Powiadomienia email nie działają

**Przyczyna:** Błędna konfiguracja SMTP lub problemy z siecią.

**Rozwiązanie:**
1. Sprawdź konfigurację SMTP w pliku `.env`
2. Przetestuj połączenie:
```bash
python manage.py shell
```
```python
from django.core.mail import send_mail
send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
```

### Problem: Statyczne pliki nie są ładowane

**Przyczyna:** Błędna konfiguracja ścieżek statycznych.

**Rozwiązanie:**
```bash
# Zbierz pliki statyczne
python manage.py collectstatic

# Sprawdź konfigurację w settings.py
# STATIC_URL = '/static/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'public', 'static')
```

### Problem: Błąd "CSRF verification failed"

**Przyczyna:** Problemy z tokenami CSRF lub konfiguracją sesji.

**Rozwiązanie:**
1. Sprawdź czy cookies są włączone w przeglądarce
2. Sprawdź konfigurację CSRF w settings.py
3. Wyczyść cache przeglądarki

### Kontakt z Wsparciem

Jeśli problem nie jest opisany powyżej:
1. Sprawdź logi systemu
2. Zbierz informacje o błędzie
3. Skontaktuj się z zespołem wsparcia technicznego

---

## Sprawdzenie Instalacji

### Checklist Po Instalacji

- [ ] System uruchamia się bez błędów
- [ ] Można się zalogować jako administrator
- [ ] 2FA jest skonfigurowane
- [ ] Hasło administratora zostało zmienione
- [ ] Powiadomienia email działają
- [ ] Statyczne pliki są ładowane
- [ ] Baza danych działa poprawnie
- [ ] Kopie zapasowe są tworzone
- [ ] Logi są zapisywane

### Testy Funkcjonalne

1. **Test logowania:**
   - Zaloguj się jako administrator
   - Sprawdź czy dashboard się ładuje

2. **Test tworzenia zgłoszenia:**
   - Utwórz testowe zgłoszenie
   - Sprawdź czy jest widoczne na liście

3. **Test powiadomień:**
   - Wyślij testowy email
   - Sprawdź czy dotarł

4. **Test kopii zapasowych:**
   - Utwórz ręczną kopię zapasową
   - Sprawdź czy plik został utworzony

---

*Ostatnia aktualizacja: Styczeń 2025*
