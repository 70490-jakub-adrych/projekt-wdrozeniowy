# 🔄 Procedury Aktualizacji

## Spis Treści
1. [Wprowadzenie](#wprowadzenie)
2. [Strategia Aktualizacji](#strategia-aktualizacji)
3. [Środowiska](#środowiska)
4. [Procedura Aktualizacji Aplikacji](#procedura-aktualizacji-aplikacji)
5. [Procedura Aktualizacji Bazy Danych](#procedura-aktualizacji-bazy-danych)
6. [Procedura Aktualizacji Systemu](#procedura-aktualizacji-systemu)
7. [Procedura Rollback](#procedura-rollback)
8. [Testowanie Aktualizacji](#testowanie-aktualizacji)
9. [Komunikacja i Dokumentacja](#komunikacja-i-dokumentacja)
10. [Automatyzacja Aktualizacji](#automatyzacja-aktualizacji)
11. [Monitoring Aktualizacji](#monitoring-aktualizacji)
12. [Troubleshooting Aktualizacji](#troubleshooting-aktualizacji)

---

## Wprowadzenie

Dokument zawiera szczegółowe procedury aktualizacji systemu helpdesk, obejmujące aktualizacje aplikacji, bazy danych, systemu operacyjnego i zależności. Procedury te zapewniają bezpieczne i kontrolowane wdrażanie zmian w środowisku produkcyjnym.

### Cel Dokumentu
- **Bezpieczne wdrażanie** aktualizacji
- **Minimalizacja przestojów** systemu
- **Zapewnienie ciągłości** działania
- **Kontrola jakości** wdrożeń
- **Dokumentacja procesów** aktualizacji

### Odbiorcy
- **Administratorzy systemu** - główni wykonawcy aktualizacji
- **Zespół IT** - wsparcie techniczne
- **Deweloperzy** - wdrażanie zmian aplikacji
- **Kierownictwo** - nadzór i kontrola

### Zasady Aktualizacji
- **Zero-downtime** - minimalizacja przestojów
- **Rollback ready** - możliwość szybkiego wycofania
- **Testowanie** - wszystkie zmiany testowane przed wdrożeniem
- **Dokumentacja** - pełna dokumentacja wszystkich zmian

---

## Strategia Aktualizacji

### Typy Aktualizacji

#### 1. Aktualizacje Krytyczne
- **Bezpieczeństwo** - łaty bezpieczeństwa
- **Błędy krytyczne** - błędy powodujące niedostępność
- **Zgodność** - aktualizacje wymagane przez prawo
- **Czas reakcji:** W ciągu 24 godzin

#### 2. Aktualizacje Ważne
- **Nowe funkcjonalności** - funkcje wymagane przez biznes
- **Optymalizacje** - poprawa wydajności
- **Błędy średnie** - błędy wpływające na funkcjonalność
- **Czas reakcji:** W ciągu 1 tygodnia

#### 3. Aktualizacje Rutynowe
- **Drobne poprawki** - kosmetyczne zmiany
- **Aktualizacje zależności** - biblioteki i pakiety
- **Dokumentacja** - aktualizacje dokumentacji
- **Czas reakcji:** W ciągu 1 miesiąca

### Harmonogram Aktualizacji

#### 1. Planowanie
- **Miesięczne** - planowanie aktualizacji na miesiąc
- **Tygodniowe** - szczegółowe planowanie na tydzień
- **Dzienne** - aktualizacje krytyczne
- **Nagłe** - aktualizacje awaryjne

#### 2. Okna Czasowe
- **Aktualizacje krytyczne** - 24/7
- **Aktualizacje ważne** - weekendy 22:00-06:00
- **Aktualizacje rutynowe** - niedziele 02:00-06:00
- **Aktualizacje testowe** - dni robocze 18:00-20:00

### Matryca Ryzyka

| Typ Aktualizacji | Ryzyko | Czas Wdrożenia | Rollback | Testowanie |
|------------------|--------|----------------|----------|------------|
| Krytyczne | Wysokie | < 2h | < 30min | Minimalne |
| Ważne | Średnie | < 4h | < 1h | Podstawowe |
| Rutynowe | Niskie | < 8h | < 2h | Pełne |

---

## Środowiska

### Architektura Środowisk

#### 1. Środowisko Deweloperskie (DEV)
- **Cel:** Rozwój i testowanie nowych funkcji
- **Dane:** Dane testowe/syntetyczne
- **Dostęp:** Zespół deweloperski
- **Aktualizacje:** Codziennie
- **Backup:** Codziennie

#### 2. Środowisko Testowe (TEST)
- **Cel:** Testowanie integracji i funkcjonalności
- **Dane:** Dane testowe + kopie produkcyjne
- **Dostęp:** Zespół QA + deweloperzy
- **Aktualizacje:** Tygodniowo
- **Backup:** Codziennie

#### 3. Środowisko Staging (STAGING)
- **Cel:** Finalne testowanie przed produkcją
- **Dane:** Kopie produkcyjne (zanonimizowane)
- **Dostęp:** Zespół IT + kierownictwo
- **Aktualizacje:** Przed każdym wdrożeniem
- **Backup:** Codziennie

#### 4. Środowisko Produkcyjne (PROD)
- **Cel:** System produkcyjny
- **Dane:** Dane rzeczywiste
- **Dostęp:** Użytkownicy końcowi
- **Aktualizacje:** Według harmonogramu
- **Backup:** Co 4 godziny

### Przepływ Aktualizacji

```
DEV → TEST → STAGING → PROD
  ↓      ↓       ↓       ↓
Testy  Testy   Testy   Produkcja
jednostkowe integracji akceptacyjne
```

### Konfiguracja Środowisk

#### 1. Zmienne Środowiskowe
```bash
# .env.dev
DEBUG=True
DATABASE_URL=sqlite:///db_dev.sqlite3
SECRET_KEY=dev-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# .env.test
DEBUG=False
DATABASE_URL=mysql://user:pass@localhost/helpdesk_test
SECRET_KEY=test-secret-key
ALLOWED_HOSTS=test.helpdesk.com

# .env.staging
DEBUG=False
DATABASE_URL=mysql://user:pass@staging-db/helpdesk_staging
SECRET_KEY=staging-secret-key
ALLOWED_HOSTS=staging.helpdesk.com

# .env.prod
DEBUG=False
DATABASE_URL=mysql://user:pass@prod-db/helpdesk_prod
SECRET_KEY=prod-secret-key
ALLOWED_HOSTS=helpdesk.com,www.helpdesk.com
```

#### 2. Konfiguracja Django
```python
# settings.py
import os
from decouple import config

# Środowisko
ENVIRONMENT = config('ENVIRONMENT', default='dev')

# Debug
DEBUG = config('DEBUG', default=False, cast=bool)

# Baza danych
if ENVIRONMENT == 'dev':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db_dev.sqlite3',
        }
    }
elif ENVIRONMENT == 'test':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'helpdesk_test',
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST'),
            'PORT': config('DB_PORT'),
        }
    }
elif ENVIRONMENT == 'staging':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'helpdesk_staging',
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST'),
            'PORT': config('DB_PORT'),
        }
    }
elif ENVIRONMENT == 'prod':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'helpdesk_prod',
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST'),
            'PORT': config('DB_PORT'),
        }
    }
```

---

## Procedura Aktualizacji Aplikacji

### 1. Przygotowanie Aktualizacji

#### 1.1 Planowanie
```bash
#!/bin/bash
# Skrypt planowania aktualizacji

# Sprawdź aktualną wersję
CURRENT_VERSION=$(git describe --tags --abbrev=0)
echo "Aktualna wersja: $CURRENT_VERSION"

# Sprawdź dostępne aktualizacje
git fetch --tags
LATEST_VERSION=$(git describe --tags --abbrev=0)
echo "Najnowsza wersja: $LATEST_VERSION"

# Sprawdź różnice
git log --oneline $CURRENT_VERSION..$LATEST_VERSION

# Sprawdź konflikty
git merge-base $CURRENT_VERSION $LATEST_VERSION
```

#### 1.2 Przygotowanie Środowiska
```bash
#!/bin/bash
# Skrypt przygotowania środowiska

# Utwórz kopię zapasową
python manage.py backup_database --format=sql

# Sprawdź status Git
git status

# Sprawdź czy nie ma niezatwierdzonych zmian
if [ -n "$(git status --porcelain)" ]; then
    echo "UWAGA: Są niezatwierdzone zmiany!"
    git status
    exit 1
fi

# Sprawdź czy jesteś na właściwej gałęzi
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "UWAGA: Nie jesteś na gałęzi main!"
    exit 1
fi
```

### 2. Wdrażanie Aktualizacji

#### 2.1 Aktualizacja Kodu
```bash
#!/bin/bash
# Skrypt aktualizacji kodu

# Pobierz najnowsze zmiany
git fetch origin

# Przełącz na najnowszą wersję
git checkout $LATEST_VERSION

# Sprawdź czy aktualizacja się powiodła
if [ $? -ne 0 ]; then
    echo "BŁĄD: Nie udało się przełączyć na wersję $LATEST_VERSION"
    exit 1
fi

# Sprawdź różnice
git diff $CURRENT_VERSION..$LATEST_VERSION
```

#### 2.2 Aktualizacja Zależności
```bash
#!/bin/bash
# Skrypt aktualizacji zależności

# Sprawdź czy requirements.txt się zmienił
if git diff $CURRENT_VERSION..$LATEST_VERSION --name-only | grep -q "requirements.txt"; then
    echo "Aktualizacja zależności..."
    
    # Utwórz kopię zapasową aktualnych zależności
    pip freeze > requirements_backup.txt
    
    # Zainstaluj nowe zależności
    pip install -r requirements.txt
    
    # Sprawdź czy instalacja się powiodła
    if [ $? -ne 0 ]; then
        echo "BŁĄD: Instalacja zależności nie powiodła się"
        # Przywróć poprzednie zależności
        pip install -r requirements_backup.txt
        exit 1
    fi
fi
```

#### 2.3 Aktualizacja Statycznych Plików
```bash
#!/bin/bash
# Skrypt aktualizacji plików statycznych

# Sprawdź czy pliki statyczne się zmieniły
if git diff $CURRENT_VERSION..$LATEST_VERSION --name-only | grep -q "static/"; then
    echo "Aktualizacja plików statycznych..."
    
    # Zbierz pliki statyczne
    python manage.py collectstatic --noinput
    
    # Sprawdź czy zbieranie się powiodło
    if [ $? -ne 0 ]; then
        echo "BŁĄD: Zbieranie plików statycznych nie powiodło się"
        exit 1
    fi
fi
```

### 3. Testowanie Aktualizacji

#### 3.1 Testy Podstawowe
```bash
#!/bin/bash
# Skrypt testów podstawowych

# Sprawdź konfigurację Django
python manage.py check --deploy

# Sprawdź migracje
python manage.py showmigrations

# Sprawdź czy są nowe migracje
if python manage.py showmigrations | grep -q "\[ \]"; then
    echo "UWAGA: Są niezaplikowane migracje!"
    python manage.py showmigrations
fi

# Sprawdź dostępność bazy danych
python manage.py dbshell -c "SELECT 1;"

# Sprawdź dostępność plików statycznych
curl -I http://localhost/static/admin/css/base.css
```

#### 3.2 Testy Funkcjonalne
```bash
#!/bin/bash
# Skrypt testów funkcjonalnych

# Test logowania
python manage.py shell -c "
from django.contrib.auth.models import User
from django.test import Client
client = Client()
user = User.objects.first()
if user:
    response = client.post('/login/', {'username': user.username, 'password': 'test'})
    print('Test logowania:', response.status_code)
else:
    print('Brak użytkowników do testowania')
"

# Test tworzenia zgłoszenia
python manage.py shell -c "
from crm.models import Ticket, Organization
from django.contrib.auth.models import User
org = Organization.objects.first()
user = User.objects.first()
if org and user:
    ticket = Ticket.objects.create(
        title='Test aktualizacji',
        description='Test po aktualizacji',
        created_by=user,
        organization=org
    )
    print('Test tworzenia zgłoszenia: OK')
    ticket.delete()
else:
    print('Brak danych do testowania')
"
```

### 4. Wdrożenie na Produkcję

#### 4.1 Procedura Wdrożenia
```bash
#!/bin/bash
# Skrypt wdrożenia na produkcję

# Zatrzymaj usługi
systemctl stop apache2

# Utwórz kopię zapasową
python manage.py backup_database --format=sql

# Zastosuj migracje
python manage.py migrate

# Sprawdź czy migracje się powiodły
if [ $? -ne 0 ]; then
    echo "BŁĄD: Migracje nie powiodły się"
    # Przywróć kopię zapasową
    python manage.py restore_database /backups/database/latest.sql.gz
    systemctl start apache2
    exit 1
fi

# Zbierz pliki statyczne
python manage.py collectstatic --noinput

# Sprawdź czy zbieranie się powiodło
if [ $? -ne 0 ]; then
    echo "BŁĄD: Zbieranie plików statycznych nie powiodło się"
    exit 1
fi

# Uruchom usługi
systemctl start apache2

# Sprawdź czy usługi działają
systemctl status apache2

# Test funkcjonalności
python manage.py check --deploy
```

#### 4.2 Weryfikacja Wdrożenia
```bash
#!/bin/bash
# Skrypt weryfikacji wdrożenia

# Sprawdź dostępność systemu
curl -I https://helpdesk.com

# Sprawdź logi błędów
tail -100 /var/log/apache2/error.log | grep -i error

# Sprawdź logi Django
tail -100 /var/log/django.log | grep -i error

# Sprawdź wydajność
python manage.py shell -c "
from django.db import connection
from crm.models import Ticket
import time

start = time.time()
tickets = Ticket.objects.all()[:10]
end = time.time()
print(f'Czas zapytania: {end - start:.3f}s')
print(f'Liczba zapytań: {len(connection.queries)}')
"
```

---

## Procedura Aktualizacji Bazy Danych

### 1. Przygotowanie Migracji

#### 1.1 Analiza Migracji
```bash
#!/bin/bash
# Skrypt analizy migracji

# Sprawdź dostępne migracje
python manage.py showmigrations

# Sprawdź które migracje będą zastosowane
python manage.py showmigrations --plan

# Sprawdź różnice w schemacie
python manage.py sqlmigrate crm 0001

# Sprawdź czy migracje są bezpieczne
python manage.py check --deploy
```

#### 1.2 Testowanie Migracji
```bash
#!/bin/bash
# Skrypt testowania migracji

# Utwórz kopię zapasową
python manage.py backup_database --format=sql

# Zastosuj migracje na kopii testowej
python manage.py migrate --dry-run

# Sprawdź czy migracje są bezpieczne
python manage.py check --deploy

# Test funkcjonalności po migracji
python manage.py shell -c "
from crm.models import Ticket
print('Liczba zgłoszeń:', Ticket.objects.count())
"
```

### 2. Wdrażanie Migracji

#### 2.1 Procedura Migracji
```bash
#!/bin/bash
# Skrypt wdrażania migracji

# Zatrzymaj usługi
systemctl stop apache2

# Utwórz pełną kopię zapasową
python manage.py backup_database --format=sql --rotate=7

# Sprawdź integralność bazy danych
python manage.py dbshell -c "CHECK TABLE crm_ticket;"

# Zastosuj migracje
python manage.py migrate

# Sprawdź czy migracje się powiodły
if [ $? -ne 0 ]; then
    echo "BŁĄD: Migracje nie powiodły się"
    # Przywróć kopię zapasową
    python manage.py restore_database /backups/database/latest.sql.gz
    systemctl start apache2
    exit 1
fi

# Sprawdź integralność po migracji
python manage.py dbshell -c "CHECK TABLE crm_ticket;"

# Uruchom usługi
systemctl start apache2

# Test funkcjonalności
python manage.py check --deploy
```

#### 2.2 Weryfikacja Migracji
```bash
#!/bin/bash
# Skrypt weryfikacji migracji

# Sprawdź status migracji
python manage.py showmigrations

# Sprawdź integralność danych
python manage.py shell -c "
from crm.models import Ticket, User, Organization
print('Zgłoszenia:', Ticket.objects.count())
print('Użytkownicy:', User.objects.count())
print('Organizacje:', Organization.objects.count())
"

# Sprawdź wydajność zapytań
python manage.py shell -c "
from django.db import connection
from crm.models import Ticket
import time

start = time.time()
tickets = Ticket.objects.select_related('created_by', 'organization')[:100]
list(tickets)
end = time.time()
print(f'Czas zapytania: {end - start:.3f}s')
"
```

### 3. Migracje Danych

#### 3.1 Migracje z Danymi
```python
# Przykład migracji z danymi
from django.db import migrations

def populate_new_field(apps, schema_editor):
    """Wypełnia nowe pole danymi"""
    Ticket = apps.get_model('crm', 'Ticket')
    for ticket in Ticket.objects.all():
        if ticket.status == 'resolved' and not ticket.resolution_notes:
            ticket.resolution_notes = "Zgłoszenie rozwiązane automatycznie"
            ticket.save()

def reverse_populate_new_field(apps, schema_editor):
    """Cofa wypełnienie nowego pola"""
    Ticket = apps.get_model('crm', 'Ticket')
    Ticket.objects.update(resolution_notes='')

class Migration(migrations.Migration):
    dependencies = [
        ('crm', '0004_add_resolution_notes'),
    ]
    
    operations = [
        migrations.RunPython(
            populate_new_field,
            reverse_populate_new_field
        ),
    ]
```

#### 3.2 Migracje Strukturalne
```python
# Przykład migracji strukturalnej
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('crm', '0003_auto_20240115_1400'),
    ]
    
    operations = [
        # Dodaj nowe pole
        migrations.AddField(
            model_name='ticket',
            name='resolution_notes',
            field=models.TextField(blank=True, null=True),
        ),
        
        # Dodaj indeks
        migrations.RunSQL(
            "CREATE INDEX idx_ticket_resolution_notes ON crm_ticket(resolution_notes(100));",
            reverse_sql="DROP INDEX idx_ticket_resolution_notes ON crm_ticket;"
        ),
        
        # Dodaj ograniczenie
        migrations.RunSQL(
            "ALTER TABLE crm_ticket ADD CONSTRAINT chk_ticket_status CHECK (status IN ('new', 'in_progress', 'resolved', 'closed'));",
            reverse_sql="ALTER TABLE crm_ticket DROP CONSTRAINT chk_ticket_status;"
        ),
    ]
```

---

## Procedura Aktualizacji Systemu

### 1. Aktualizacje Systemu Operacyjnego

#### 1.1 Przygotowanie Aktualizacji
```bash
#!/bin/bash
# Skrypt przygotowania aktualizacji systemu

# Sprawdź aktualną wersję
lsb_release -a

# Sprawdź dostępne aktualizacje
apt update
apt list --upgradable

# Sprawdź krytyczne aktualizacje bezpieczeństwa
apt list --upgradable | grep -i security

# Utwórz kopię zapasową konfiguracji
cp -r /etc /backups/config_$(date +%Y%m%d)
```

#### 1.2 Wdrażanie Aktualizacji
```bash
#!/bin/bash
# Skrypt wdrażania aktualizacji systemu

# Zatrzymaj usługi
systemctl stop apache2
systemctl stop mysql

# Utwórz kopię zapasową bazy danych
python manage.py backup_database --format=sql

# Zainstaluj aktualizacje bezpieczeństwa
apt upgrade -y

# Sprawdź czy instalacja się powiodła
if [ $? -ne 0 ]; then
    echo "BŁĄD: Instalacja aktualizacji nie powiodła się"
    exit 1
fi

# Uruchom usługi
systemctl start mysql
systemctl start apache2

# Sprawdź czy usługi działają
systemctl status apache2
systemctl status mysql
```

### 2. Aktualizacje Oprogramowania

#### 2.1 Aktualizacje Apache
```bash
#!/bin/bash
# Skrypt aktualizacji Apache

# Sprawdź aktualną wersję
apache2 -v

# Sprawdź dostępne aktualizacje
apt list --upgradable | grep apache2

# Zatrzymaj Apache
systemctl stop apache2

# Zainstaluj aktualizacje
apt upgrade apache2 -y

# Sprawdź konfigurację
apache2ctl configtest

# Uruchom Apache
systemctl start apache2

# Sprawdź status
systemctl status apache2
```

#### 2.2 Aktualizacje MySQL
```bash
#!/bin/bash
# Skrypt aktualizacji MySQL

# Sprawdź aktualną wersję
mysql --version

# Sprawdź dostępne aktualizacje
apt list --upgradable | grep mysql

# Zatrzymaj MySQL
systemctl stop mysql

# Utwórz kopię zapasową
mysqldump -u root -p --all-databases > /backups/mysql_full_$(date +%Y%m%d).sql

# Zainstaluj aktualizacje
apt upgrade mysql-server -y

# Uruchom MySQL
systemctl start mysql

# Sprawdź status
systemctl status mysql

# Sprawdź integralność bazy danych
mysql -u root -p -e "CHECK TABLE crm_ticket;"
```

### 3. Aktualizacje Python

#### 3.1 Aktualizacje Python
```bash
#!/bin/bash
# Skrypt aktualizacji Python

# Sprawdź aktualną wersję
python3 --version

# Sprawdź dostępne aktualizacje
apt list --upgradable | grep python3

# Zatrzymaj usługi
systemctl stop apache2

# Zainstaluj aktualizacje
apt upgrade python3 -y

# Sprawdź czy instalacja się powiodła
if [ $? -ne 0 ]; then
    echo "BŁĄD: Instalacja Python nie powiodła się"
    exit 1
fi

# Sprawdź nową wersję
python3 --version

# Uruchom usługi
systemctl start apache2
```

---

## Procedura Rollback

### 1. Przygotowanie Rollback

#### 1.1 Identyfikacja Problemu
```bash
#!/bin/bash
# Skrypt identyfikacji problemu

# Sprawdź logi błędów
tail -100 /var/log/apache2/error.log | grep -i error
tail -100 /var/log/django.log | grep -i error

# Sprawdź status usług
systemctl status apache2
systemctl status mysql

# Sprawdź dostępność systemu
curl -I https://helpdesk.com

# Sprawdź wydajność
python manage.py shell -c "
from django.db import connection
from crm.models import Ticket
import time

start = time.time()
tickets = Ticket.objects.all()[:10]
end = time.time()
print(f'Czas zapytania: {end - start:.3f}s')
"
```

#### 1.2 Decyzja o Rollback
```bash
#!/bin/bash
# Skrypt decyzji o rollback

# Sprawdź czy problem jest krytyczny
if curl -I https://helpdesk.com | grep -q "200 OK"; then
    echo "System działa - rollback nie jest konieczny"
    exit 0
fi

# Sprawdź czy problem jest związany z aktualizacją
if [ -f "/tmp/last_update.log" ]; then
    echo "Ostatnia aktualizacja: $(cat /tmp/last_update.log)"
fi

# Sprawdź dostępność kopii zapasowych
if [ -f "/backups/database/latest.sql.gz" ]; then
    echo "Kopia zapasowa dostępna"
else
    echo "BŁĄD: Brak kopii zapasowej!"
    exit 1
fi
```

### 2. Wykonanie Rollback

#### 2.1 Rollback Aplikacji
```bash
#!/bin/bash
# Skrypt rollback aplikacji

# Zatrzymaj usługi
systemctl stop apache2

# Przywróć poprzednią wersję kodu
git checkout $PREVIOUS_VERSION

# Sprawdź czy przywrócenie się powiodło
if [ $? -ne 0 ]; then
    echo "BŁĄD: Nie udało się przywrócić poprzedniej wersji"
    exit 1
fi

# Przywróć poprzednie zależności
if [ -f "requirements_backup.txt" ]; then
    pip install -r requirements_backup.txt
fi

# Uruchom usługi
systemctl start apache2

# Sprawdź czy usługi działają
systemctl status apache2
```

#### 2.2 Rollback Bazy Danych
```bash
#!/bin/bash
# Skrypt rollback bazy danych

# Zatrzymaj usługi
systemctl stop apache2
systemctl stop mysql

# Utwórz kopię zapasową aktualnego stanu
python manage.py backup_database --format=sql --output=/backups/rollback_$(date +%Y%m%d_%H%M%S).sql.gz

# Przywróć poprzedni stan bazy danych
python manage.py restore_database /backups/database/latest.sql.gz

# Sprawdź czy przywrócenie się powiodło
if [ $? -ne 0 ]; then
    echo "BŁĄD: Przywrócenie bazy danych nie powiodło się"
    exit 1
fi

# Sprawdź integralność bazy danych
python manage.py dbshell -c "CHECK TABLE crm_ticket;"

# Uruchom usługi
systemctl start mysql
systemctl start apache2

# Sprawdź czy usługi działają
systemctl status mysql
systemctl status apache2
```

### 3. Weryfikacja Rollback

#### 3.1 Test Funkcjonalności
```bash
#!/bin/bash
# Skrypt testu funkcjonalności po rollback

# Sprawdź dostępność systemu
curl -I https://helpdesk.com

# Sprawdź logowanie
python manage.py shell -c "
from django.contrib.auth.models import User
from django.test import Client
client = Client()
user = User.objects.first()
if user:
    response = client.post('/login/', {'username': user.username, 'password': 'test'})
    print('Test logowania:', response.status_code)
"

# Sprawdź tworzenie zgłoszenia
python manage.py shell -c "
from crm.models import Ticket, Organization
from django.contrib.auth.models import User
org = Organization.objects.first()
user = User.objects.first()
if org and user:
    ticket = Ticket.objects.create(
        title='Test rollback',
        description='Test po rollback',
        created_by=user,
        organization=org
    )
    print('Test tworzenia zgłoszenia: OK')
    ticket.delete()
"
```

#### 3.2 Dokumentacja Rollback
```bash
#!/bin/bash
# Skrypt dokumentacji rollback

# Utwórz raport rollback
cat > /tmp/rollback_report.txt << EOF
ROLLBACK REPORT
===============
Data: $(date)
Wersja przed rollback: $CURRENT_VERSION
Wersja po rollback: $PREVIOUS_VERSION
Przyczyna rollback: $ROLLBACK_REASON
Czas rollback: $ROLLBACK_TIME
Status: $ROLLBACK_STATUS

LOGI BŁĘDÓW:
$(tail -50 /var/log/apache2/error.log)

LOGI DJANGO:
$(tail -50 /var/log/django.log)

TESTY FUNKCJONALNOŚCI:
$(python manage.py check --deploy)
EOF

# Wyślij raport
mail -s "Rollback Report - $(date)" admin@company.com < /tmp/rollback_report.txt
```

---

## Testowanie Aktualizacji

### 1. Testy Jednostkowe

#### 1.1 Uruchomienie Testów
```bash
#!/bin/bash
# Skrypt uruchamiania testów jednostkowych

# Uruchom wszystkie testy
python manage.py test

# Uruchom testy dla konkretnej aplikacji
python manage.py test crm

# Uruchom testy z pokryciem
coverage run --source='.' manage.py test
coverage report
coverage html

# Sprawdź czy testy przeszły
if [ $? -eq 0 ]; then
    echo "Wszystkie testy przeszły"
else
    echo "BŁĄD: Niektóre testy nie przeszły"
    exit 1
fi
```

#### 1.2 Testy Integracyjne
```bash
#!/bin/bash
# Skrypt testów integracyjnych

# Test bazy danych
python manage.py shell -c "
from django.db import connection
from crm.models import Ticket
import time

start = time.time()
tickets = Ticket.objects.select_related('created_by', 'organization')[:100]
list(tickets)
end = time.time()
print(f'Czas zapytania: {end - start:.3f}s')
"

# Test API
python manage.py shell -c "
from django.test import Client
client = Client()
response = client.get('/api/tickets/')
print('API Status:', response.status_code)
"

# Test email
python manage.py shell -c "
from django.core.mail import send_mail
try:
    send_mail('Test', 'Test message', 'test@example.com', ['admin@company.com'])
    print('Email test: OK')
except Exception as e:
    print('Email test: FAILED -', str(e))
"
```

### 2. Testy Wydajności

#### 2.1 Testy Obciążeniowe
```bash
#!/bin/bash
# Skrypt testów obciążeniowych

# Test równoczesnych użytkowników
python manage.py shell -c "
from django.test import Client
import threading
import time

def test_user():
    client = Client()
    for i in range(10):
        response = client.get('/tickets/')
        print(f'User {threading.current_thread().name}: {response.status_code}')

threads = []
for i in range(5):
    t = threading.Thread(target=test_user, name=f'User-{i}')
    threads.append(t)
    t.start()

for t in threads:
    t.join()
"

# Test wydajności bazy danych
python manage.py shell -c "
from django.db import connection
from crm.models import Ticket
import time

# Test zapytań
start = time.time()
for i in range(100):
    tickets = Ticket.objects.filter(status='new')[:10]
    list(tickets)
end = time.time()
print(f'100 zapytań: {end - start:.3f}s')
"
```

#### 2.2 Testy Bezpieczeństwa
```bash
#!/bin/bash
# Skrypt testów bezpieczeństwa

# Test uwierzytelniania
python manage.py shell -c "
from django.test import Client
client = Client()

# Test nieprawidłowych danych logowania
response = client.post('/login/', {'username': 'admin', 'password': 'wrong'})
print('Invalid login:', response.status_code)

# Test SQL injection
response = client.get('/tickets/?search=1\' OR 1=1--')
print('SQL injection test:', response.status_code)
"

# Test CSRF
python manage.py shell -c "
from django.test import Client
client = Client()

# Test bez tokenu CSRF
response = client.post('/tickets/create/', {'title': 'Test', 'description': 'Test'})
print('CSRF test:', response.status_code)
"
```

### 3. Testy Akceptacyjne

#### 3.1 Testy Użytkownika
```bash
#!/bin/bash
# Skrypt testów akceptacyjnych

# Test przepływu użytkownika
python manage.py shell -c "
from django.test import Client
from django.contrib.auth.models import User
from crm.models import Organization

# Utwórz użytkownika testowego
user = User.objects.create_user('testuser', 'test@example.com', 'testpass')
org = Organization.objects.create(name='Test Org', email='test@org.com')

# Test logowania
client = Client()
response = client.post('/login/', {'username': 'testuser', 'password': 'testpass'})
print('Login test:', response.status_code)

# Test tworzenia zgłoszenia
response = client.post('/tickets/create/', {
    'title': 'Test Ticket',
    'description': 'Test Description',
    'organization': org.id
})
print('Create ticket test:', response.status_code)

# Cleanup
user.delete()
org.delete()
"
```

#### 3.2 Testy Regresji
```bash
#!/bin/bash
# Skrypt testów regresji

# Test wszystkich funkcji
python manage.py shell -c "
from django.test import Client
from django.contrib.auth.models import User
from crm.models import Ticket, Organization

client = Client()
user = User.objects.first()
org = Organization.objects.first()

if user and org:
    # Test logowania
    response = client.post('/login/', {'username': user.username, 'password': 'test'})
    print('Login:', response.status_code)
    
    # Test listy zgłoszeń
    response = client.get('/tickets/')
    print('Ticket list:', response.status_code)
    
    # Test tworzenia zgłoszenia
    response = client.post('/tickets/create/', {
        'title': 'Regression Test',
        'description': 'Test Description',
        'organization': org.id
    })
    print('Create ticket:', response.status_code)
    
    # Test edycji zgłoszenia
    ticket = Ticket.objects.first()
    if ticket:
        response = client.post(f'/tickets/{ticket.id}/edit/', {
            'title': ticket.title,
            'description': ticket.description,
            'status': 'in_progress'
        })
        print('Edit ticket:', response.status_code)
"
```

---

## Komunikacja i Dokumentacja

### 1. Komunikacja z Użytkownikami

#### 1.1 Powiadomienia o Aktualizacjach
```bash
#!/bin/bash
# Skrypt powiadamiania użytkowników

# Wyślij email do wszystkich użytkowników
python manage.py shell -c "
from django.core.mail import send_mass_mail
from django.contrib.auth.models import User

users = User.objects.filter(is_active=True)
messages = []

for user in users:
    message = (
        'Aktualizacja systemu helpdesk',
        f'Drogi {user.first_name},\n\nInformujemy o planowanej aktualizacji systemu helpdesk.\n\nData: $(date)\nCzas: 02:00-06:00\n\nPodczas aktualizacji system może być czasowo niedostępny.\n\nPozdrawiamy,\nZespół IT',
        'noreply@helpdesk.com',
        [user.email]
    )
    messages.append(message)

send_mass_mail(messages)
print(f'Wysłano {len(messages)} powiadomień')
"
```

#### 1.2 Status Page
```bash
#!/bin/bash
# Skrypt aktualizacji status page

# Sprawdź status systemu
STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://helpdesk.com)

if [ "$STATUS" = "200" ]; then
    SYSTEM_STATUS="operational"
else
    SYSTEM_STATUS="degraded"
fi

# Zaktualizuj status page
curl -X POST "https://status.helpdesk.com/api/status" \
  -H "Content-Type: application/json" \
  -d "{
    \"status\": \"$SYSTEM_STATUS\",
    \"message\": \"System aktualizowany\",
    \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
  }"
```

### 2. Dokumentacja Aktualizacji

#### 2.1 Changelog
```bash
#!/bin/bash
# Skrypt generowania changelog

# Pobierz zmiany z Git
git log --oneline $PREVIOUS_VERSION..$CURRENT_VERSION > /tmp/changes.txt

# Utwórz changelog
cat > /tmp/changelog.md << EOF
# Changelog - $(date +%Y-%m-%d)

## Wersja $CURRENT_VERSION

### Nowe funkcjonalności
$(git log --oneline $PREVIOUS_VERSION..$CURRENT_VERSION | grep -i "feat:" | sed 's/^/- /')

### Poprawki
$(git log --oneline $PREVIOUS_VERSION..$CURRENT_VERSION | grep -i "fix:" | sed 's/^/- /')

### Zmiany bezpieczeństwa
$(git log --oneline $PREVIOUS_VERSION..$CURRENT_VERSION | grep -i "security:" | sed 's/^/- /')

### Inne zmiany
$(git log --oneline $PREVIOUS_VERSION..$CURRENT_VERSION | grep -v -i "feat:\|fix:\|security:" | sed 's/^/- /')
EOF

# Wyślij changelog
mail -s "Changelog - $CURRENT_VERSION" admin@company.com < /tmp/changelog.md
```

#### 2.2 Raport Aktualizacji
```bash
#!/bin/bash
# Skrypt generowania raportu aktualizacji

# Utwórz raport
cat > /tmp/update_report.txt << EOF
RAPORT AKTUALIZACJI
===================
Data: $(date)
Wersja przed: $PREVIOUS_VERSION
Wersja po: $CURRENT_VERSION
Czas aktualizacji: $UPDATE_TIME
Status: $UPDATE_STATUS

ZMIANY:
$(git log --oneline $PREVIOUS_VERSION..$CURRENT_VERSION)

TESTY:
$(python manage.py check --deploy)

WYDAJNOŚĆ:
$(python manage.py shell -c "
from django.db import connection
from crm.models import Ticket
import time

start = time.time()
tickets = Ticket.objects.all()[:10]
end = time.time()
print(f'Czas zapytania: {end - start:.3f}s')
")

LOGI:
$(tail -20 /var/log/apache2/error.log)
EOF

# Wyślij raport
mail -s "Raport aktualizacji - $CURRENT_VERSION" admin@company.com < /tmp/update_report.txt
```

---

## Automatyzacja Aktualizacji

### 1. CI/CD Pipeline

#### 1.1 Konfiguracja GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.10
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          python manage.py test
      - name: Run security checks
        run: |
          pip install bandit
          bandit -r .

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to production
        run: |
          # Deploy script
          ./scripts/deploy.sh
```

#### 1.2 Skrypt Deploy
```bash
#!/bin/bash
# scripts/deploy.sh

set -e

# Konfiguracja
SERVER="prod-server"
APP_DIR="/var/www/helpdesk"
BACKUP_DIR="/backups"

# Utwórz kopię zapasową
ssh $SERVER "cd $APP_DIR && python manage.py backup_database --format=sql"

# Wdróż kod
ssh $SERVER "cd $APP_DIR && git pull origin main"

# Zainstaluj zależności
ssh $SERVER "cd $APP_DIR && pip install -r requirements.txt"

# Zastosuj migracje
ssh $SERVER "cd $APP_DIR && python manage.py migrate"

# Zbierz pliki statyczne
ssh $SERVER "cd $APP_DIR && python manage.py collectstatic --noinput"

# Restart usług
ssh $SERVER "systemctl restart apache2"

# Test funkcjonalności
ssh $SERVER "cd $APP_DIR && python manage.py check --deploy"
```

### 2. Automatyczne Aktualizacje

#### 2.1 Skrypt Automatycznej Aktualizacji
```bash
#!/bin/bash
# scripts/auto_update.sh

# Konfiguracja
UPDATE_LOG="/var/log/auto_update.log"
NOTIFICATION_EMAIL="admin@company.com"

# Funkcja logowania
log() {
    echo "$(date): $1" >> $UPDATE_LOG
}

# Sprawdź dostępne aktualizacje
log "Sprawdzanie dostępnych aktualizacji..."
git fetch --tags
CURRENT_VERSION=$(git describe --tags --abbrev=0)
LATEST_VERSION=$(git describe --tags --abbrev=0 origin/main)

if [ "$CURRENT_VERSION" = "$LATEST_VERSION" ]; then
    log "Brak nowych aktualizacji"
    exit 0
fi

log "Znaleziono nową wersję: $LATEST_VERSION"

# Sprawdź czy aktualizacja jest bezpieczna
if git log --oneline $CURRENT_VERSION..$LATEST_VERSION | grep -q "BREAKING"; then
    log "UWAGA: Aktualizacja zawiera zmiany BREAKING - wymagana interwencja ręczna"
    mail -s "Wymagana interwencja - aktualizacja BREAKING" $NOTIFICATION_EMAIL << EOF
Znaleziono aktualizację zawierającą zmiany BREAKING.

Wersja aktualna: $CURRENT_VERSION
Wersja nowa: $LATEST_VERSION

Wymagana interwencja ręczna.
EOF
    exit 1
fi

# Wykonaj aktualizację
log "Rozpoczynanie automatycznej aktualizacji..."

# Utwórz kopię zapasową
python manage.py backup_database --format=sql

# Wdróż aktualizację
git checkout $LATEST_VERSION
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
systemctl restart apache2

# Test funkcjonalności
if python manage.py check --deploy; then
    log "Aktualizacja zakończona pomyślnie"
    mail -s "Aktualizacja zakończona pomyślnie" $NOTIFICATION_EMAIL << EOF
Automatyczna aktualizacja zakończona pomyślnie.

Wersja: $LATEST_VERSION
Data: $(date)
EOF
else
    log "BŁĄD: Test funkcjonalności nie powiódł się"
    # Rollback
    git checkout $CURRENT_VERSION
    pip install -r requirements.txt
    python manage.py restore_database /backups/database/latest.sql.gz
    systemctl restart apache2
    
    mail -s "BŁĄD: Aktualizacja nie powiodła się" $NOTIFICATION_EMAIL << EOF
Automatyczna aktualizacja nie powiodła się.

Wersja docelowa: $LATEST_VERSION
Wersja przywrócona: $CURRENT_VERSION
Data: $(date)

Wykonano rollback.
EOF
fi
```

#### 2.2 Harmonogram Automatycznych Aktualizacji
```bash
# Crontab dla automatycznych aktualizacji
# Sprawdzanie aktualizacji co godzinę
0 * * * * /path/to/scripts/auto_update.sh

# Aktualizacje bezpieczeństwa natychmiast
@reboot /path/to/scripts/security_update.sh

# Aktualizacje rutynowe w niedziele o 2:00
0 2 * * 0 /path/to/scripts/routine_update.sh
```

---

## Monitoring Aktualizacji

### 1. Monitoring Stanu Systemu

#### 1.1 Skrypt Monitoringu
```bash
#!/bin/bash
# scripts/monitor_system.sh

# Konfiguracja
MONITOR_LOG="/var/log/system_monitor.log"
ALERT_EMAIL="admin@company.com"

# Funkcja logowania
log() {
    echo "$(date): $1" >> $MONITOR_LOG
}

# Sprawdź dostępność systemu
if curl -s -o /dev/null -w "%{http_code}" https://helpdesk.com | grep -q "200"; then
    log "System dostępny"
else
    log "BŁĄD: System niedostępny"
    mail -s "ALERT: System niedostępny" $ALERT_EMAIL << EOF
System helpdesk jest niedostępny.

Data: $(date)
Status: $(curl -s -o /dev/null -w "%{http_code}" https://helpdesk.com)
EOF
fi

# Sprawdź użycie dysku
DISK_USAGE=$(df /var/www/helpdesk | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    log "UWAGA: Wysokie użycie dysku: $DISK_USAGE%"
    mail -s "UWAGA: Wysokie użycie dysku" $ALERT_EMAIL << EOF
Wysokie użycie dysku: $DISK_USAGE%

Data: $(date)
EOF
fi

# Sprawdź użycie pamięci
MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
if [ $MEMORY_USAGE -gt 90 ]; then
    log "UWAGA: Wysokie użycie pamięci: $MEMORY_USAGE%"
    mail -s "UWAGA: Wysokie użycie pamięci" $ALERT_EMAIL << EOF
Wysokie użycie pamięci: $MEMORY_USAGE%

Data: $(date)
EOF
fi

# Sprawdź logi błędów
ERROR_COUNT=$(tail -100 /var/log/apache2/error.log | grep -i error | wc -l)
if [ $ERROR_COUNT -gt 10 ]; then
    log "UWAGA: Wysoka liczba błędów: $ERROR_COUNT"
    mail -s "UWAGA: Wysoka liczba błędów" $ALERT_EMAIL << EOF
Wysoka liczba błędów w logach: $ERROR_COUNT

Data: $(date)
EOF
fi
```

#### 1.2 Dashboard Monitoringu
```python
# monitoring/dashboard.py
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import psutil
import requests
import time

@require_http_methods(["GET"])
def system_status(request):
    """Zwraca status systemu"""
    try:
        # Sprawdź dostępność systemu
        response = requests.get('https://helpdesk.com', timeout=5)
        system_available = response.status_code == 200
    except:
        system_available = False
    
    # Sprawdź użycie zasobów
    cpu_usage = psutil.cpu_percent()
    memory_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent
    
    # Sprawdź status usług
    services = {
        'apache2': check_service('apache2'),
        'mysql': check_service('mysql'),
    }
    
    return JsonResponse({
        'system_available': system_available,
        'cpu_usage': cpu_usage,
        'memory_usage': memory_usage,
        'disk_usage': disk_usage,
        'services': services,
        'timestamp': time.time(),
    })

def check_service(service_name):
    """Sprawdza status usługi"""
    try:
        result = subprocess.run(['systemctl', 'is-active', service_name], 
                              capture_output=True, text=True)
        return result.stdout.strip() == 'active'
    except:
        return False
```

### 2. Alerty i Powiadomienia

#### 2.1 System Alertów
```bash
#!/bin/bash
# scripts/alert_system.sh

# Konfiguracja
ALERT_EMAIL="admin@company.com"
SLACK_WEBHOOK="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"

# Funkcja wysyłania alertu
send_alert() {
    local severity=$1
    local message=$2
    
    # Email
    mail -s "[$severity] System Alert" $ALERT_EMAIL << EOF
$message

Data: $(date)
Serwer: $(hostname)
EOF
    
    # Slack
    curl -X POST -H 'Content-type: application/json' \
      --data "{\"text\":\"[$severity] $message\"}" \
      $SLACK_WEBHOOK
}

# Sprawdź dostępność systemu
if ! curl -s -o /dev/null -w "%{http_code}" https://helpdesk.com | grep -q "200"; then
    send_alert "CRITICAL" "System helpdesk jest niedostępny"
fi

# Sprawdź użycie dysku
DISK_USAGE=$(df /var/www/helpdesk | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 90 ]; then
    send_alert "CRITICAL" "Krytyczne użycie dysku: $DISK_USAGE%"
elif [ $DISK_USAGE -gt 80 ]; then
    send_alert "WARNING" "Wysokie użycie dysku: $DISK_USAGE%"
fi

# Sprawdź użycie pamięci
MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
if [ $MEMORY_USAGE -gt 95 ]; then
    send_alert "CRITICAL" "Krytyczne użycie pamięci: $MEMORY_USAGE%"
elif [ $MEMORY_USAGE -gt 85 ]; then
    send_alert "WARNING" "Wysokie użycie pamięci: $MEMORY_USAGE%"
fi
```

---

## Troubleshooting Aktualizacji

### 1. Częste Problemy

#### 1.1 Problemy z Migracjami
```bash
#!/bin/bash
# Skrypt rozwiązywania problemów z migracjami

# Sprawdź status migracji
python manage.py showmigrations

# Sprawdź które migracje nie zostały zastosowane
python manage.py showmigrations --plan | grep "\[ \]"

# Sprawdź błędy migracji
python manage.py migrate --verbosity=2

# Jeśli migracja się nie powiedzie, sprawdź logi
tail -100 /var/log/django.log | grep -i migration

# Przywróć poprzedni stan
python manage.py migrate crm 0003  # Przejdź do poprzedniej migracji
```

#### 1.2 Problemy z Zależnościami
```bash
#!/bin/bash
# Skrypt rozwiązywania problemów z zależnościami

# Sprawdź konflikty zależności
pip check

# Sprawdź które pakiety są problematyczne
pip list --outdated

# Zainstaluj zależności w trybie offline
pip install --no-index --find-links /path/to/wheels -r requirements.txt

# Jeśli problem z konkretnym pakietem
pip uninstall problematic-package
pip install problematic-package==specific-version
```

#### 1.3 Problemy z Plikami Statycznymi
```bash
#!/bin/bash
# Skrypt rozwiązywania problemów z plikami statycznymi

# Sprawdź uprawnienia
ls -la /var/www/helpdesk/static/

# Napraw uprawnienia
chown -R www-data:www-data /var/www/helpdesk/static/
chmod -R 755 /var/www/helpdesk/static/

# Wyczyść cache plików statycznych
python manage.py collectstatic --clear --noinput

# Sprawdź konfigurację Apache
apache2ctl configtest
```

### 2. Procedury Naprawcze

#### 2.1 Naprawa Uszkodzonej Aktualizacji
```bash
#!/bin/bash
# Skrypt naprawy uszkodzonej aktualizacji

# Zatrzymaj usługi
systemctl stop apache2

# Przywróć poprzednią wersję kodu
git checkout $PREVIOUS_VERSION

# Przywróć poprzednie zależności
pip install -r requirements_backup.txt

# Przywróć bazę danych
python manage.py restore_database /backups/database/latest.sql.gz

# Uruchom usługi
systemctl start apache2

# Test funkcjonalności
python manage.py check --deploy

# Wyślij raport
mail -s "Naprawa aktualizacji" admin@company.com << EOF
Aktualizacja została naprawiona.

Wersja przywrócona: $PREVIOUS_VERSION
Data: $(date)
Status: Naprawione
EOF
```

#### 2.2 Naprawa Uszkodzonej Bazy Danych
```bash
#!/bin/bash
# Skrypt naprawy uszkodzonej bazy danych

# Zatrzymaj usługi
systemctl stop apache2
systemctl stop mysql

# Sprawdź integralność bazy danych
mysql -u root -p -e "CHECK TABLE crm_ticket;"

# Jeśli tabela jest uszkodzona, napraw ją
mysql -u root -p -e "REPAIR TABLE crm_ticket;"

# Sprawdź wszystkie tabele
mysql -u root -p -e "CHECK TABLE crm_ticket, crm_ticketcomment, crm_ticketattachment, crm_activitylog, crm_userprofile, crm_organization;"

# Jeśli naprawa nie pomoże, przywróć z kopii zapasowej
python manage.py restore_database /backups/database/latest.sql.gz

# Uruchom usługi
systemctl start mysql
systemctl start apache2

# Test funkcjonalności
python manage.py check --deploy
```

### 3. Dokumentacja Problemów

#### 3.1 Rejestr Problemów
```bash
#!/bin/bash
# Skrypt rejestrowania problemów

# Utwórz wpis w rejestrze problemów
cat >> /var/log/update_issues.log << EOF
$(date): Problem z aktualizacją
Wersja: $CURRENT_VERSION
Problem: $PROBLEM_DESCRIPTION
Rozwiązanie: $SOLUTION
Czas naprawy: $REPAIR_TIME
Status: $STATUS
EOF

# Wyślij raport do zespołu
mail -s "Problem z aktualizacją - $(date)" admin@company.com << EOF
Problem: $PROBLEM_DESCRIPTION
Wersja: $CURRENT_VERSION
Rozwiązanie: $SOLUTION
Czas naprawy: $REPAIR_TIME
Status: $STATUS
EOF
```

#### 3.2 Baza Wiedzy
```bash
#!/bin/bash
# Skrypt aktualizacji bazy wiedzy

# Utwórz wpis w bazie wiedzy
cat > /var/www/knowledge_base/update_issues.md << EOF
# Problem: $PROBLEM_DESCRIPTION

## Opis problemu
$PROBLEM_DESCRIPTION

## Przyczyna
$ROOT_CAUSE

## Rozwiązanie
$SOLUTION

## Zapobieganie
$PREVENTION

## Data: $(date)
## Wersja: $CURRENT_VERSION
EOF
```

---

*Ostatnia aktualizacja: Styczeń 2025*
