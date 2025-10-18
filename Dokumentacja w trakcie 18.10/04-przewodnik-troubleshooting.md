# 🔧 Przewodnik Rozwiązywania Problemów

## Spis Treści
1. [Wprowadzenie](#wprowadzenie)
2. [Problemy z Logowaniem](#problemy-z-logowaniem)
3. [Problemy z 2FA](#problemy-z-2fa)
4. [Problemy z Powiadomieniami Email](#problemy-z-powiadomieniami-email)
5. [Problemy z Załącznikami](#problemy-z-załącznikami)
6. [Problemy z Wydajnością](#problemy-z-wydajnością)
7. [Problemy z Bazą Danych](#problemy-z-bazą-danych)
8. [Problemy z Przeglądarką](#problemy-z-przeglądarką)
9. [Problemy z Uprawnieniami](#problemy-z-uprawnieniami)
10. [Problemy z Kopiami Zapasowymi](#problemy-z-kopiami-zapasowymi)
11. [Diagnostyka Systemu](#diagnostyka-systemu)
12. [Kontakt z Wsparciem](#kontakt-z-wsparciem)

---

## Wprowadzenie

Ten przewodnik zawiera rozwiązania najczęstszych problemów występujących w systemie helpdesk. Przed skontaktowaniem się z wsparciem technicznym, sprawdź czy Twój problem nie jest opisany poniżej.

### Jak Używać Tego Przewodnika

1. **Zidentyfikuj kategorię** problemu
2. **Znajdź konkretny problem** w sekcji
3. **Wykonaj kroki** rozwiązywania
4. **Sprawdź czy problem został rozwiązany**
5. **Skontaktuj się z wsparciem** jeśli problem nadal występuje

### Poziomy Trudności

- 🟢 **Łatwy** - można rozwiązać samodzielnie
- 🟡 **Średni** - wymaga podstawowej wiedzy technicznej
- 🔴 **Trudny** - wymaga pomocy administratora

---

## Problemy z Logowaniem

### Problem: "Nieprawidłowa nazwa użytkownika lub hasło"

#### 🟢 Rozwiązania dla Użytkownika

1. **Sprawdź pisownię:**
   - Nazwa użytkownika (wielkość liter ma znaczenie)
   - Hasło (sprawdź Caps Lock)

2. **Wyczyść cache przeglądarki:**
   - Chrome: Ctrl+Shift+Delete
   - Firefox: Ctrl+Shift+Delete
   - Safari: Cmd+Option+E

3. **Spróbuj w trybie incognito/prywatnym**

4. **Sprawdź czy konto nie jest zablokowane:**
   - Skontaktuj się z administratorem

#### 🟡 Rozwiązania dla Administratora

1. **Sprawdź status konta:**
```bash
python manage.py shell
```
```python
from django.contrib.auth.models import User
user = User.objects.get(username='nazwa_uzytkownika')
print(f"Konto aktywne: {user.is_active}")
print(f"Konto zablokowane: {user.profile.is_locked}")
print(f"Nieudane próby: {user.profile.failed_login_attempts}")
```

2. **Odblokuj konto:**
```python
user.profile.is_locked = False
user.profile.failed_login_attempts = 0
user.profile.save()
```

3. **Zresetuj hasło:**
```bash
python manage.py changepassword nazwa_uzytkownika
```

### Problem: "Konto zostało zablokowane"

#### 🟡 Rozwiązanie

**Przyczyna:** 5 nieudanych prób logowania

**Rozwiązanie dla Administratora:**
1. Przejdź do Panelu Administratora → Użytkownicy
2. Znajdź zablokowanego użytkownika
3. W sekcji "Blokada konta":
   - Odznacz "Konto zablokowane"
   - Ustaw "Nieudane próby logowania" na 0
4. Kliknij "Zapisz"

**Rozwiązanie przez kod:**
```bash
python manage.py shell
```
```python
from django.contrib.auth.models import User
user = User.objects.get(username='nazwa_uzytkownika')
user.profile.unlock_account()
```

### Problem: "Sesja wygasła"

#### 🟢 Rozwiązanie

1. **Odśwież stronę** (F5)
2. **Zaloguj się ponownie**
3. **Sprawdź czy cookies są włączone**

#### 🟡 Rozwiązanie dla Administratora

**Zwiększ czas sesji w settings.py:**
```python
SESSION_COOKIE_AGE = 3600  # 1 godzina w sekundach
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
```

---

## Problemy z 2FA

### Problem: "Nieprawidłowy kod weryfikacyjny"

#### 🟢 Rozwiązania

1. **Sprawdź czas na telefonie:**
   - Upewnij się, że czas jest zsynchronizowany
   - Google Authenticator automatycznie synchronizuje czas

2. **Sprawdź kod w aplikacji:**
   - Upewnij się, że wpisujesz aktualny kod
   - Kody zmieniają się co 30 sekund

3. **Spróbuj ponownie:**
   - Poczekaj na nowy kod (30 sekund)
   - Wprowadź nowy kod

#### 🟡 Rozwiązanie z Kodem Odzyskiwania

1. **Kliknij "Użyj kodu odzyskiwania"**
2. **Wprowadź kod odzyskiwania** (zapisany podczas konfiguracji)
3. **Po zalogowaniu skonfiguruj 2FA ponownie**

#### 🔴 Rozwiązanie dla Administratora

**Wyłączenie 2FA dla użytkownika:**
1. Przejdź do profilu użytkownika
2. W sekcji "Uwierzytelnianie dwuskładnikowe":
   - Odznacz "2FA włączone"
   - Wyczyść "Klucz tajny 2FA"
3. Kliknij "Zapisz"

**Wygenerowanie nowego kodu odzyskiwania:**
1. Wybierz użytkowników z listy
2. Kliknij "Wygeneruj nowy kod odzyskiwania 2FA"
3. Przekaż kod użytkownikowi bezpiecznym kanałem

### Problem: "Nie mogę zeskanować kodu QR"

#### 🟢 Rozwiązania

1. **Sprawdź jakość ekranu:**
   - Wyczyść ekran
   - Zwiększ jasność
   - Zbliż telefon do ekranu

2. **Spróbuj ręcznego wprowadzenia:**
   - Kliknij "Nie mogę zeskanować kodu"
   - Wprowadź klucz ręcznie

3. **Sprawdź aplikację:**
   - Upewnij się, że Google Authenticator jest aktualna
   - Spróbuj ponownie zainstalować aplikację

### Problem: "Aplikacja Google Authenticator została usunięta"

#### 🟡 Rozwiązanie

1. **Użyj kodu odzyskiwania** (jeśli masz)
2. **Skontaktuj się z administratorem** w celu wyłączenia 2FA
3. **Skonfiguruj 2FA ponownie** po odzyskaniu dostępu

---

## Problemy z Powiadomieniami Email

### Problem: "Nie otrzymuję powiadomień email"

#### 🟢 Rozwiązania dla Użytkownika

1. **Sprawdź folder spam:**
   - Przejrzyj folder spam/niechciane
   - Dodaj adres nadawcy do kontaktów

2. **Sprawdź ustawienia powiadomień:**
   - Przejdź do profilu użytkownika
   - Sprawdź sekcję "Ustawienia powiadomień"
   - Włącz potrzebne powiadomienia

3. **Sprawdź adres email:**
   - Upewnij się, że adres jest poprawny
   - Sprawdź czy email jest zweryfikowany

#### 🟡 Rozwiązania dla Administratora

1. **Sprawdź konfigurację SMTP:**
```bash
python manage.py shell
```
```python
from django.core.mail import send_mail
try:
    send_mail(
        'Test Email',
        'To jest testowy email.',
        'helpdesk@example.com',
        ['test@example.com'],
        fail_silently=False,
    )
    print("Email wysłany pomyślnie")
except Exception as e:
    print(f"Błąd: {e}")
```

2. **Sprawdź logi serwera:**
```bash
tail -f /var/log/mail.log
# lub
journalctl -u postfix -f
```

3. **Sprawdź ustawienia w .env:**
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Problem: "Email przychodzi jako spam"

#### 🟡 Rozwiązanie

1. **Skonfiguruj SPF record:**
```
v=spf1 include:_spf.google.com ~all
```

2. **Skonfiguruj DKIM:**
   - Skontaktuj się z dostawcą email
   - Skonfiguruj podpis DKIM

3. **Skonfiguruj DMARC:**
```
v=DMARC1; p=quarantine; rua=mailto:dmarc@your-domain.com
```

### Problem: "Błąd SMTP: Authentication failed"

#### 🟡 Rozwiązanie

**Dla Gmail:**
1. Włącz weryfikację dwuetapową
2. Wygeneruj hasło aplikacji
3. Użyj hasła aplikacji zamiast zwykłego hasła

**Dla innych dostawców:**
1. Sprawdź ustawienia SMTP
2. Upewnij się, że używasz prawidłowych danych
3. Sprawdź czy port jest otwarty (587, 465)

---

## Problemy z Załącznikami

### Problem: "Nie mogę pobrać załącznika"

#### 🟢 Rozwiązania

1. **Sprawdź uprawnienia:**
   - Upewnij się, że masz dostęp do zgłoszenia
   - Sprawdź czy załącznik nie został usunięty

2. **Spróbuj ponownie:**
   - Odśwież stronę (F5)
   - Kliknij ponownie na załącznik

3. **Sprawdź przeglądarkę:**
   - Wyczyść cache
   - Spróbuj w innej przeglądarce

#### 🟡 Rozwiązanie dla Administratora

1. **Sprawdź uprawnienia plików:**
```bash
ls -la /path/to/projekt-wdrozeniowy/public/media/
```

2. **Sprawdź konfigurację MEDIA:**
```python
# settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'public', 'media')
```

3. **Sprawdź szyfrowanie:**
```bash
python manage.py shell
```
```python
from crm.models import TicketAttachment
attachment = TicketAttachment.objects.get(id=attachment_id)
try:
    content = attachment.get_decrypted_content()
    print("Szyfrowanie działa poprawnie")
except Exception as e:
    print(f"Błąd szyfrowania: {e}")
```

### Problem: "Załącznik nie można przesłać"

#### 🟢 Rozwiązania

1. **Sprawdź rozmiar pliku:**
   - Maksymalny rozmiar: 10MB
   - Skompresuj duże pliki

2. **Sprawdź typ pliku:**
   - Sprawdź czy typ pliku jest dozwolony
   - Unikaj plików wykonywalnych

3. **Sprawdź połączenie:**
   - Upewnij się, że połączenie internetowe jest stabilne
   - Spróbuj ponownie

#### 🟡 Rozwiązanie dla Administratora

**Zwiększ limit rozmiaru pliku:**
```python
# settings.py
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
```

---

## Problemy z Wydajnością

### Problem: "System działa bardzo wolno"

#### 🟢 Rozwiązania dla Użytkownika

1. **Sprawdź połączenie internetowe:**
   - Test prędkości: speedtest.net
   - Sprawdź czy inne strony działają szybko

2. **Wyczyść cache przeglądarki:**
   - Chrome: Ctrl+Shift+Delete
   - Firefox: Ctrl+Shift+Delete

3. **Zamknij niepotrzebne karty:**
   - Zamknij nieużywane karty przeglądarki
   - Zamknij inne aplikacje

#### 🟡 Rozwiązania dla Administratora

1. **Sprawdź wykorzystanie zasobów:**
```bash
# CPU i RAM
top
htop

# Dysk
df -h
du -sh /path/to/projekt-wdrozeniowy/

# Sieć
netstat -tuln
```

2. **Sprawdź logi błędów:**
```bash
tail -f /var/log/apache2/error.log
# lub
tail -f /var/log/nginx/error.log
```

3. **Zoptymalizuj bazę danych:**
```bash
python manage.py shell
```
```python
from django.db import connection
cursor = connection.cursor()
cursor.execute("SHOW PROCESSLIST")
for row in cursor.fetchall():
    print(row)
```

4. **Zwiększ zasoby serwera:**
   - Dodaj więcej RAM
   - Użyj szybszego dysku (SSD)
   - Zwiększ liczbę procesorów

### Problem: "Strona się nie ładuje"

#### 🟢 Rozwiązania

1. **Odśwież stronę** (F5)
2. **Sprawdź połączenie internetowe**
3. **Spróbuj w trybie incognito**
4. **Sprawdź czy serwer nie jest w konserwacji**

#### 🟡 Rozwiązanie dla Administratora

1. **Sprawdź status serwera:**
```bash
systemctl status apache2
# lub
systemctl status nginx
```

2. **Sprawdź logi:**
```bash
journalctl -u apache2 -f
# lub
journalctl -u nginx -f
```

3. **Restart serwera:**
```bash
sudo systemctl restart apache2
# lub
sudo systemctl restart nginx
```

---

## Problemy z Bazą Danych

### Problem: "Błąd połączenia z bazą danych"

#### 🔴 Rozwiązanie dla Administratora

1. **Sprawdź status MySQL:**
```bash
systemctl status mysql
```

2. **Sprawdź połączenie:**
```bash
mysql -u helpdesk_user -p helpdesk_db
```

3. **Sprawdź konfigurację w .env:**
```env
DB_ENGINE=django.db.backends.mysql
DB_NAME=helpdesk_db
DB_USER=helpdesk_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
```

4. **Restart MySQL:**
```bash
sudo systemctl restart mysql
```

### Problem: "Błąd migracji"

#### 🔴 Rozwiązanie dla Administratora

1. **Sprawdź status migracji:**
```bash
python manage.py showmigrations
```

2. **Zastosuj migracje:**
```bash
python manage.py migrate
```

3. **Jeśli błąd nadal występuje:**
```bash
python manage.py migrate --fake-initial
```

4. **Sprawdź logi:**
```bash
python manage.py migrate --verbosity=2
```

### Problem: "Baza danych jest uszkodzona"

#### 🔴 Rozwiązanie dla Administratora

1. **Sprawdź integralność:**
```bash
mysqlcheck -u root -p helpdesk_db
```

2. **Napraw bazę danych:**
```bash
mysqlcheck -u root -p --repair helpdesk_db
```

3. **Przywróć z kopii zapasowej:**
```bash
python manage.py restore_database backups/database/backup_mysql_YYYYMMDD_HHMMSS.sql.gz
```

---

## Problemy z Przeglądarką

### Problem: "Strona wygląda nieprawidłowo"

#### 🟢 Rozwiązania

1. **Wyczyść cache przeglądarki:**
   - Chrome: Ctrl+Shift+Delete
   - Firefox: Ctrl+Shift+Delete
   - Safari: Cmd+Option+E

2. **Sprawdź czy JavaScript jest włączony:**
   - Chrome: Settings → Advanced → Content settings → JavaScript
   - Firefox: about:config → javascript.enabled

3. **Sprawdź czy cookies są włączone:**
   - Chrome: Settings → Advanced → Content settings → Cookies
   - Firefox: Settings → Privacy & Security → Cookies

4. **Spróbuj w innej przeglądarce**

#### 🟡 Rozwiązanie dla Administratora

1. **Sprawdź pliki statyczne:**
```bash
python manage.py collectstatic --noinput
```

2. **Sprawdź konfigurację STATIC:**
```python
# settings.py
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'public', 'static')
```

### Problem: "Błąd CSRF verification failed"

#### 🟢 Rozwiązania

1. **Odśwież stronę** (F5)
2. **Wyczyść cache przeglądarki**
3. **Sprawdź czy cookies są włączone**
4. **Spróbuj w trybie incognito**

#### 🟡 Rozwiązanie dla Administratora

1. **Sprawdź konfigurację CSRF:**
```python
# settings.py
CSRF_COOKIE_SECURE = False  # dla HTTP
CSRF_COOKIE_SECURE = True   # dla HTTPS
```

2. **Sprawdź middleware:**
```python
MIDDLEWARE = [
    'django.middleware.csrf.CsrfViewMiddleware',
    # inne middleware...
]
```

---

## Problemy z Uprawnieniami

### Problem: "Nie masz uprawnień do wykonania tej akcji"

#### 🟢 Rozwiązania dla Użytkownika

1. **Sprawdź swoją rolę:**
   - Przejdź do profilu użytkownika
   - Sprawdź przypisaną rolę

2. **Skontaktuj się z administratorem:**
   - Poproś o przypisanie odpowiedniej roli
   - Wyjaśnij jakie uprawnienia potrzebujesz

#### 🟡 Rozwiązanie dla Administratora

1. **Sprawdź uprawnienia użytkownika:**
```bash
python manage.py shell
```
```python
from django.contrib.auth.models import User
user = User.objects.get(username='nazwa_uzytkownika')
print(f"Rola: {user.profile.role}")
print(f"Grupy: {user.groups.all()}")
```

2. **Przypisz odpowiednią rolę:**
   - Przejdź do profilu użytkownika
   - Zmień rolę w sekcji "Profil"
   - Zapisz zmiany

3. **Sprawdź uprawnienia grupy:**
   - Przejdź do Grupy
   - Sprawdź ustawienia grupy
   - Skonfiguruj uprawnienia

### Problem: "Nie możesz edytować tego zgłoszenia"

#### 🟢 Rozwiązania

1. **Sprawdź czy zgłoszenie jest przypisane do Ciebie**
2. **Sprawdź czy masz odpowiednią rolę**
3. **Skontaktuj się z Super Agentem lub Administratorem**

---

## Problemy z Kopiami Zapasowymi

### Problem: "Kopia zapasowa nie została utworzona"

#### 🔴 Rozwiązanie dla Administratora

1. **Sprawdź uprawnienia:**
```bash
ls -la backups/
```

2. **Sprawdź logi:**
```bash
python manage.py backup_database --verbosity=2
```

3. **Sprawdź miejsce na dysku:**
```bash
df -h
```

4. **Utwórz katalog kopii zapasowych:**
```bash
mkdir -p backups/database
chmod 755 backups/database
```

### Problem: "Nie można przywrócić z kopii zapasowej"

#### 🔴 Rozwiązanie dla Administratora

1. **Sprawdź dostępne kopie:**
```bash
python manage.py backup_status
```

2. **Sprawdź integralność pliku:**
```bash
file backups/database/backup_mysql_YYYYMMDD_HHMMSS.sql.gz
```

3. **Sprawdź uprawnienia:**
```bash
ls -la backups/database/
```

4. **Przywróć krok po kroku:**
```bash
# Zatrzymaj serwer web
sudo systemctl stop apache2

# Przywróć bazę danych
python manage.py restore_database backups/database/backup_mysql_YYYYMMDD_HHMMSS.sql.gz

# Uruchom serwer web
sudo systemctl start apache2
```

---

## Diagnostyka Systemu

### Sprawdzanie Statusu Systemu

#### 🟡 Podstawowe Sprawdzenia

1. **Status serwera web:**
```bash
systemctl status apache2
# lub
systemctl status nginx
```

2. **Status bazy danych:**
```bash
systemctl status mysql
```

3. **Wykorzystanie zasobów:**
```bash
top
htop
```

4. **Miejsce na dysku:**
```bash
df -h
```

#### 🔴 Zaawansowane Sprawdzenia

1. **Logi aplikacji:**
```bash
tail -f django.log
tail -f sql.log
```

2. **Logi serwera web:**
```bash
tail -f /var/log/apache2/error.log
tail -f /var/log/nginx/error.log
```

3. **Logi bazy danych:**
```bash
tail -f /var/log/mysql/error.log
```

4. **Test połączenia z bazą:**
```bash
python manage.py shell
```
```python
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT 1")
print("Połączenie z bazą danych działa")
```

### Narzędzia Diagnostyczne

#### 🟡 Sprawdzenie Konfiguracji Django

```bash
python manage.py check
python manage.py check --deploy
```

#### 🟡 Test Wszystkich Komponentów

```bash
python manage.py shell
```
```python
# Test email
from django.core.mail import send_mail
send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])

# Test bazy danych
from django.contrib.auth.models import User
print(f"Liczba użytkowników: {User.objects.count()}")

# Test plików statycznych
import os
static_path = os.path.join(settings.STATIC_ROOT)
print(f"Pliki statyczne: {os.path.exists(static_path)}")
```

---

## Kontakt z Wsparciem

### Kiedy Szukać Pomocy

- **Problem nie jest opisany** w tym przewodniku
- **Rozwiązania nie działają** po kilku próbach
- **Problem dotyczy bezpieczeństwa** systemu
- **Potrzebujesz pomocy** z konfiguracją zaawansowaną

### Jak Przygotować Zgłoszenie

#### Informacje Podstawowe
- **Opis problemu** - co dokładnie się dzieje
- **Kroki do odtworzenia** - jak powtórzyć problem
- **Oczekiwany rezultat** - co powinno się stać
- **Rzeczywisty rezultat** - co się dzieje

#### Informacje Techniczne
- **Wersja systemu** - Django, Python, OS
- **Przeglądarka** - Chrome, Firefox, Safari
- **Błędy** - komunikaty błędów
- **Logi** - fragmenty logów systemu

#### Informacje o Środowisku
- **Rola użytkownika** - Admin, Agent, Klient
- **Czas wystąpienia** - kiedy problem się pojawił
- **Częstotliwość** - czy problem występuje zawsze
- **Wpływ** - jak problem wpływa na pracę

### Przykład Zgłoszenia

```
Temat: Problem z logowaniem - błąd 2FA

Opis problemu:
Nie mogę się zalogować do systemu. Po wprowadzeniu nazwy użytkownika i hasła, 
system prosi o kod 2FA, ale po wprowadzeniu kodu wyświetla błąd "Nieprawidłowy kod weryfikacyjny".

Kroki do odtworzenia:
1. Przechodzę na stronę logowania
2. Wprowadzam nazwę użytkownika: agent1
3. Wprowadzam hasło: agent123
4. Wprowadzam kod z Google Authenticator
5. Klikam "Zaloguj się"
6. Otrzymuję błąd "Nieprawidłowy kod weryfikacyjny"

Informacje techniczne:
- System: Ubuntu 20.04
- Przeglądarka: Chrome 91.0
- Czas: 2025-01-15 14:30
- Rola: Agent

Próbowane rozwiązania:
- Sprawdziłem czas na telefonie
- Wygenerowałem nowy kod
- Wyczyściłem cache przeglądarki

Proszę o pomoc w rozwiązaniu tego problemu.
```

### Kanały Kontaktu

1. **Email** - helpdesk-support@example.com
2. **Telefon** - +48 123 456 789
3. **Ticket** - utwórz zgłoszenie w systemie
4. **Chat** - jeśli dostępny

### Czas Odpowiedzi

- **Krytyczne** (system nie działa) - 2 godziny
- **Wysokie** (znaczące utrudnienia) - 4 godziny
- **Średnie** (drobne problemy) - 24 godziny
- **Niskie** (pytania) - 48 godzin

---

## FAQ - Najczęściej Zadawane Pytania

### P: Czy mogę używać systemu na telefonie?
**O:** Tak, system jest w pełni responsywny i działa na urządzeniach mobilnych.

### P: Jak często są tworzone kopie zapasowe?
**O:** Automatyczne kopie zapasowe są tworzone codziennie o 2:00. Można też tworzyć kopie ręcznie.

### P: Czy mogę wyłączyć 2FA?
**O:** Nie, 2FA jest wymagane dla wszystkich użytkowników ze względów bezpieczeństwa.

### P: Jak długo są przechowywane logi?
**O:** Logi są przechowywane bez ograniczeń czasowych, ale można je wyczyścić ręcznie.

### P: Czy mogę eksportować dane zgłoszeń?
**O:** Tak, administrator może eksportować dane w formacie Excel lub CSV.

### P: Jak zmienić hasło?
**O:** Kliknij na swoją nazwę użytkownika → "Zmień hasło" → wprowadź nowe hasło.

### P: Czy system działa offline?
**O:** Nie, system wymaga połączenia z internetem.

### P: Jak skontaktować się z administratorem?
**O:** Użyj funkcji "Kontakt" w systemie lub skontaktuj się bezpośrednio.

---

*Ostatnia aktualizacja: Styczeń 2025*
