# 🔧 Troubleshooting - System Helpdesk

## Przegląd Rozwiązywania Problemów

Ten dokument zawiera najczęściej występujące problemy w systemie helpdesk oraz procedury ich rozwiązywania. Jest podzielony na kategorie problemów i zawiera szczegółowe instrukcje diagnostyczne.

## Problemy z Logowaniem

### Problem: Użytkownik nie może się zalogować

#### Objawy
- Błąd "Nieprawidłowy email lub hasło"
- Konto zablokowane
- Przekierowanie do strony logowania

#### Diagnostyka
1. **Sprawdź logi aplikacji:**
   ```bash
   tail -f /var/www/helpdesk/logs/django.log | grep "login"
   ```

2. **Sprawdź status konta w bazie:**
   ```sql
   SELECT username, is_active, is_locked, failed_login_attempts 
   FROM auth_user au 
   JOIN crm_userprofile up ON au.id = up.user_id 
   WHERE au.email = 'email_uzytkownika@example.com';
   ```

3. **Sprawdź logi aktywności:**
   ```sql
   SELECT * FROM crm_useractivitylog 
   WHERE user_id = (SELECT id FROM auth_user WHERE email = 'email_uzytkownika@example.com')
   ORDER BY created_at DESC LIMIT 10;
   ```

#### Rozwiązania

##### Konto Zablokowane
```sql
-- Odblokuj konto
UPDATE crm_userprofile 
SET is_locked = 0, failed_login_attempts = 0 
WHERE user_id = (SELECT id FROM auth_user WHERE email = 'email_uzytkownika@example.com');
```

##### Reset Hasła
```bash
# Przez Django shell
python manage.py shell
```
```python
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm

user = User.objects.get(email='email_uzytkownika@example.com')
user.set_password('nowe_haslo_123')
user.save()
```

##### Konto Nieaktywne
```sql
-- Aktywuj konto
UPDATE auth_user 
SET is_active = 1 
WHERE email = 'email_uzytkownika@example.com';
```

### Problem: Błąd 500 przy logowaniu

#### Diagnostyka
1. **Sprawdź logi błędów:**
   ```bash
   tail -f /var/www/helpdesk/logs/error.log
   ```

2. **Sprawdź logi serwera:**
   ```bash
   # Apache
   tail -f /var/log/apache2/helpdesk_error.log
   
   # Nginx
   tail -f /var/log/nginx/helpdesk_error.log
   ```

3. **Sprawdź połączenie z bazą:**
   ```bash
   python manage.py dbshell
   ```

#### Rozwiązania
- **Błąd bazy danych:** Sprawdź połączenie MySQL
- **Błąd pamięci:** Zwiększ RAM lub zoptymalizuj zapytania
- **Błąd uprawnień:** Sprawdź uprawnienia plików

## Problemy z Zgłoszeniami

### Problem: Zgłoszenia się nie ładują

#### Diagnostyka
1. **Sprawdź logi aplikacji:**
   ```bash
   tail -f /var/www/helpdesk/logs/django.log | grep "ticket"
   ```

2. **Sprawdź wydajność bazy:**
   ```sql
   SHOW PROCESSLIST;
   ```

3. **Sprawdź indeksy:**
   ```sql
   SHOW INDEX FROM crm_ticket;
   ```

#### Rozwiązania

##### Wolne Zapytania
```sql
-- Dodaj indeksy
CREATE INDEX idx_ticket_status_org ON crm_ticket(status, organization_id);
CREATE INDEX idx_ticket_created_at ON crm_ticket(created_at);
```

##### Optymalizacja Zapytań
```python
# W views.py - dodaj select_related
tickets = Ticket.objects.select_related('category', 'created_by', 'assigned_to').filter(...)
```

### Problem: Załączniki się nie dodają

#### Diagnostyka
1. **Sprawdź uprawnienia katalogu:**
   ```bash
   ls -la /var/www/helpdesk/media/
   ```

2. **Sprawdź miejsce na dysku:**
   ```bash
   df -h
   ```

3. **Sprawdź logi upload:**
   ```bash
   tail -f /var/www/helpdesk/logs/django.log | grep "upload"
   ```

#### Rozwiązania

##### Uprawnienia
```bash
# Ustaw właściwe uprawnienia
chown -R www-data:www-data /var/www/helpdesk/media/
chmod -R 755 /var/www/helpdesk/media/
```

##### Miejsce na Dysk
```bash
# Wyczyść stare pliki
find /var/www/helpdesk/media/ -type f -mtime +90 -delete

# Lub zwiększ miejsce na dysku
```

### Problem: Powiadomienia email nie działają

#### Diagnostyka
1. **Sprawdź konfigurację email:**
   ```python
   # W Django shell
   python manage.py shell
   ```
   ```python
   from django.core.mail import send_mail
   send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
   ```

2. **Sprawdź logi email:**
   ```bash
   tail -f /var/www/helpdesk/logs/django.log | grep "email"
   ```

3. **Sprawdź ustawienia SMTP:**
   ```python
   # Sprawdź settings.py
   print(EMAIL_HOST, EMAIL_PORT, EMAIL_USE_TLS)
   ```

#### Rozwiązania

##### Konfiguracja SMTP
```python
# settings_production.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'twoj_email@gmail.com'
EMAIL_HOST_PASSWORD = 'twoje_haslo_aplikacji'
```

##### Test Połączenia
```bash
# Test SMTP
telnet smtp.gmail.com 587
```

## Problemy z Bazą Danych

### Problem: Błąd połączenia z bazą

#### Diagnostyka
1. **Sprawdź status MySQL:**
   ```bash
   sudo systemctl status mysql
   ```

2. **Sprawdź połączenie:**
   ```bash
   mysql -u helpdesk_user -p helpdesk_db
   ```

3. **Sprawdź logi MySQL:**
   ```bash
   tail -f /var/log/mysql/error.log
   ```

#### Rozwiązania

##### Uruchomienie MySQL
```bash
sudo systemctl start mysql
sudo systemctl enable mysql
```

##### Reset Hasła
```sql
-- W MySQL jako root
ALTER USER 'helpdesk_user'@'localhost' IDENTIFIED BY 'nowe_haslo_123';
FLUSH PRIVILEGES;
```

### Problem: Wolne zapytania

#### Diagnostyka
1. **Sprawdź wolne zapytania:**
   ```sql
   SHOW PROCESSLIST;
   ```

2. **Sprawdź status indeksów:**
   ```sql
   SHOW INDEX FROM crm_ticket;
   ```

3. **Analizuj zapytania:**
   ```sql
   EXPLAIN SELECT * FROM crm_ticket WHERE status = 'open';
   ```

#### Rozwiązania

##### Optymalizacja Indeksów
```sql
-- Dodaj brakujące indeksy
CREATE INDEX idx_ticket_status_priority ON crm_ticket(status, priority);
CREATE INDEX idx_ticket_organization_status ON crm_ticket(organization_id, status);
```

##### Optymalizacja Zapytań
```python
# Użyj select_related i prefetch_related
tickets = Ticket.objects.select_related('category', 'created_by').prefetch_related('comments')
```

## Problemy z Wydajnością

### Problem: Wolne ładowanie stron

#### Diagnostyka
1. **Sprawdź użycie zasobów:**
   ```bash
   htop
   df -h
   free -h
   ```

2. **Sprawdź logi serwera:**
   ```bash
   tail -f /var/log/apache2/helpdesk_access.log
   ```

3. **Sprawdź cache:**
   ```bash
   # Sprawdź czy cache działa
   python manage.py shell
   ```
   ```python
   from django.core.cache import cache
   cache.set('test', 'value', 60)
   print(cache.get('test'))
   ```

#### Rozwiązania

##### Optymalizacja Apache/Nginx
```apache
# Apache - dodaj do konfiguracji
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresByType text/css "access plus 1 month"
    ExpiresByType application/javascript "access plus 1 month"
    ExpiresByType image/png "access plus 1 month"
    ExpiresByType image/jpg "access plus 1 month"
</IfModule>
```

##### Optymalizacja Django
```python
# settings_production.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### Problem: Wysokie użycie pamięci

#### Diagnostyka
1. **Sprawdź procesy:**
   ```bash
   ps aux | grep python
   ps aux | grep apache
   ```

2. **Sprawdź pamięć:**
   ```bash
   free -h
   cat /proc/meminfo
   ```

#### Rozwiązania

##### Optymalizacja Apache
```apache
# Zmniejsz liczbę procesów
MaxRequestWorkers 50
MaxConnectionsPerChild 1000
```

##### Optymalizacja Django
```python
# Dodaj pagination
from django.core.paginator import Paginator

paginator = Paginator(tickets, 25)
page = request.GET.get('page')
tickets = paginator.get_page(page)
```

## Problemy z Bezpieczeństwem

### Problem: Podejrzane logowania

#### Diagnostyka
1. **Sprawdź logi aktywności:**
   ```sql
   SELECT * FROM crm_useractivitylog 
   WHERE action = 'login' 
   AND created_at > DATE_SUB(NOW(), INTERVAL 1 HOUR)
   ORDER BY created_at DESC;
   ```

2. **Sprawdź nieudane logowania:**
   ```sql
   SELECT * FROM crm_useractivitylog 
   WHERE action = 'login_failed' 
   AND created_at > DATE_SUB(NOW(), INTERVAL 1 HOUR);
   ```

#### Rozwiązania

##### Blokowanie IP
```bash
# Dodaj do iptables
sudo iptables -A INPUT -s PODEJRZANY_IP -j DROP
```

##### Reset Haseł
```sql
-- Wymuś zmianę hasła dla użytkownika
UPDATE crm_userprofile 
SET force_password_change = 1 
WHERE user_id = (SELECT id FROM auth_user WHERE email = 'email@example.com');
```

### Problem: Błąd CSRF

#### Diagnostyka
1. **Sprawdź tokeny CSRF:**
   ```python
   # W Django shell
   from django.middleware.csrf import get_token
   ```

2. **Sprawdź ustawienia:**
   ```python
   # Sprawdź CSRF_COOKIE_SECURE
   print(CSRF_COOKIE_SECURE)
   ```

#### Rozwiązania

##### Konfiguracja CSRF
```python
# settings_production.py
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_TRUSTED_ORIGINS = ['https://twoja-domena.pl']
```

## Problemy z Backup

### Problem: Backup się nie wykonuje

#### Diagnostyka
1. **Sprawdź cron:**
   ```bash
   crontab -l
   ```

2. **Sprawdź uprawnienia skryptu:**
   ```bash
   ls -la /var/www/helpdesk/backup.sh
   ```

3. **Sprawdź logi backup:**
   ```bash
   tail -f /var/www/helpdesk/backups/backup.log
   ```

#### Rozwiązania

##### Napraw Skrypt
```bash
# Ustaw uprawnienia
chmod +x /var/www/helpdesk/backup.sh

# Testuj ręcznie
/var/www/helpdesk/backup.sh
```

##### Dodaj do Cron
```bash
# Edytuj crontab
crontab -e

# Dodaj linię
0 3 * * * /var/www/helpdesk/backup.sh >> /var/www/helpdesk/backups/cron.log 2>&1
```

### Problem: Backup jest uszkodzony

#### Diagnostyka
1. **Sprawdź rozmiar backup:**
   ```bash
   ls -lh /var/www/helpdesk/backups/
   ```

2. **Sprawdź integralność:**
   ```bash
   # Test SQL
   mysql -u helpdesk_user -p helpdesk_db < backup_file.sql
   ```

#### Rozwiązania

##### Napraw Backup
```bash
# Sprawdź czy plik jest kompletny
tail -n 5 backup_file.sql

# Przywróć z poprzedniego backup
cp backup_file_previous.sql backup_file_current.sql
```

## Procedury Awaryjne

### Awaria Systemu

#### Krok 1: Diagnostyka
1. **Sprawdź status serwisów:**
   ```bash
   sudo systemctl status apache2
   sudo systemctl status mysql
   sudo systemctl status gunicorn
   ```

2. **Sprawdź logi błędów:**
   ```bash
   tail -f /var/www/helpdesk/logs/error.log
   ```

#### Krok 2: Naprawa
1. **Restart serwisów:**
   ```bash
   sudo systemctl restart apache2
   sudo systemctl restart mysql
   sudo systemctl restart gunicorn
   ```

2. **Sprawdź funkcjonalność:**
   - Test logowania
   - Test tworzenia zgłoszeń
   - Test email

#### Krok 3: Powiadomienie
1. **Powiadom zespół**
2. **Aktualizuj status**
3. **Dokumentuj problem**

### Utrata Danych

#### Krok 1: Zatrzymanie Systemu
```bash
sudo systemctl stop apache2
sudo systemctl stop gunicorn
```

#### Krok 2: Przywrócenie
```bash
# Przywróć bazę
mysql -u helpdesk_user -p helpdesk_db < backup_file.sql

# Przywróć pliki
tar -xzf files_backup.tar.gz -C /
```

#### Krok 3: Weryfikacja
1. **Sprawdź integralność danych**
2. **Test funkcjonalności**
3. **Uruchom system**

### Atak Bezpieczeństwa

#### Krok 1: Izolacja
1. **Zablokuj dostęp zewnętrzny**
2. **Zatrzymaj usługi**
3. **Zachowaj logi**

#### Krok 2: Analiza
1. **Przeanalizuj logi**
2. **Zidentyfikuj źródło**
3. **Oszacuj szkody**

#### Krok 3: Naprawa
1. **Usuń podatności**
2. **Zmień hasła**
3. **Przywróć z backup**

## Narzędzia Diagnostyczne

### Skrypty Pomocnicze

#### Sprawdzenie Statusu Systemu
```bash
#!/bin/bash
# /var/www/helpdesk/check_status.sh

echo "=== Status Systemu Helpdesk ==="
echo "Data: $(date)"
echo

echo "=== Serwisy ==="
systemctl status apache2 --no-pager -l
systemctl status mysql --no-pager -l
systemctl status gunicorn --no-pager -l

echo
echo "=== Zasoby ==="
df -h
free -h

echo
echo "=== Logi (ostatnie 10 linii) ==="
tail -n 10 /var/www/helpdesk/logs/django.log
```

#### Test Funkcjonalności
```bash
#!/bin/bash
# /var/www/helpdesk/test_functionality.sh

echo "=== Test Funkcjonalności ==="

# Test bazy danych
echo "Test bazy danych..."
python manage.py dbshell -c "SELECT COUNT(*) FROM crm_ticket;" 2>/dev/null

# Test email
echo "Test email..."
python manage.py shell -c "from django.core.mail import send_mail; send_mail('Test', 'Test', 'test@example.com', ['admin@example.com'])" 2>/dev/null

# Test plików statycznych
echo "Test plików statycznych..."
curl -I http://localhost/static/admin/css/base.css 2>/dev/null
```

### Monitoring

#### Skrypt Monitoringu
```bash
#!/bin/bash
# /var/www/helpdesk/monitor.sh

# Sprawdź dostępność
if ! curl -f http://localhost/ > /dev/null 2>&1; then
    echo "ALERT: Strona nie odpowiada" | mail -s "Alert Helpdesk" admin@example.com
fi

# Sprawdź miejsce na dysku
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 90 ]; then
    echo "ALERT: Mało miejsca na dysku: ${DISK_USAGE}%" | mail -s "Alert Helpdesk" admin@example.com
fi

# Sprawdź pamięć
MEM_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ $MEM_USAGE -gt 90 ]; then
    echo "ALERT: Wysokie użycie pamięci: ${MEM_USAGE}%" | mail -s "Alert Helpdesk" admin@example.com
fi
```

---

**Ostatnia aktualizacja:** 18.06.2025 