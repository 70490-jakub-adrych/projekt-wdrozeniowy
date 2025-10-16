# APScheduler - Automatyczne zadania bez CRON

## 🎯 Co to jest?

**APScheduler** to biblioteka Python, która pozwala uruchamiać zadania periodyczne **bez konfiguracji CRON**.

Zamiast ustawiać cron na serwerze, zadania działają **wewnątrz Django** jako część aplikacji.

## ✅ Zalety nad CRON:

| Cecha | CRON | APScheduler |
|-------|------|-------------|
| Wymaga konfiguracji serwera | ✅ Tak | ❌ Nie |
| Działa na Windows | ❌ Nie | ✅ Tak |
| Zarządzanie z Django | ❌ Nie | ✅ Tak |
| Historia wykonań w bazie | ❌ Nie | ✅ Tak |
| Prosty deployment | ❌ Nie | ✅ Tak |

## 📦 Co zostało dodane:

### 1. Nowe zależności
```
APScheduler>=3.10.0
django-apscheduler>=0.6.2
```

### 2. Nowy plik: `crm/scheduler.py`
Zawiera konfigurację zadań periodycznych:
- `auto_close_resolved_tickets()` - zamyka tickety po 24h (codziennie o 2:00)
- `delete_old_job_executions()` - czyści stare logi (w niedziele o 3:00)

### 3. Modyfikacja: `crm/apps.py`
Scheduler startuje automatycznie gdy Django się uruchamia.

### 4. Modyfikacja: `settings.py`
Dodano `django_apscheduler` do `INSTALLED_APPS`.

## 🚀 Instalacja

### Krok 1: Zainstaluj zależności
```bash
pip install -r requirements.txt
```

### Krok 2: Uruchom migracje
```bash
python manage.py migrate
```

To utworzy tabele dla `django_apscheduler`:
- `django_apscheduler_djangojob` - definicje zadań
- `django_apscheduler_djangojobexecution` - historia wykonań

### Krok 3: Restart aplikacji
```bash
# Na mydevil.net:
touch tmp/restart.txt

# Lokalnie:
python manage.py runserver
```

## ✅ Jak to działa?

1. **Django startuje** (przez Passenger, runserver, gunicorn, etc.)
2. **`CrmConfig.ready()` wywołuje** `start_scheduler()`
3. **Scheduler dodaje zadania:**
   - Auto-close tickets: codziennie o 2:00
   - Cleanup: w niedziele o 3:00
4. **Scheduler działa w tle** tak długo jak Django jest uruchomione
5. **O 2:00 każdego dnia** automatycznie wywołuje `python manage.py auto_close_tickets`

## 📊 Monitorowanie

### Django Admin
Przejdź do: **Django Admin → Django Apscheduler → Django job executions**

Zobaczysz:
- Kiedy zadanie było uruchomione
- Czy się powiodło
- Logi błędów (jeśli były)
- Czas wykonania

### Logi aplikacji
```bash
# Zobacz logi schedulera
grep "scheduler" logs/django.log

# Zobacz logi auto-close
grep "auto_close" logs/django.log
```

## ⚙️ Konfiguracja zadań

### Zmiana czasu wykonania

Edytuj `crm/scheduler.py`:

```python
# PRZED: Runs at 2:00 AM
scheduler.add_job(
    auto_close_resolved_tickets,
    trigger=CronTrigger(hour=2, minute=0),
    ...
)

# PO: Runs at 3:30 AM
scheduler.add_job(
    auto_close_resolved_tickets,
    trigger=CronTrigger(hour=3, minute=30),
    ...
)
```

### Dodanie nowego zadania

```python
def my_custom_task():
    """My custom periodic task"""
    logger.info("Running my custom task...")
    # Your code here

# W start_scheduler():
scheduler.add_job(
    my_custom_task,
    trigger=CronTrigger(hour=4, minute=0),  # Run at 4 AM
    id="my_custom_task",
    max_instances=1,
    replace_existing=True,
    name="My custom task description"
)
```

### Inne triggery

```python
# Co godzinę
CronTrigger(minute=0)

# Co 30 minut
CronTrigger(minute='*/30')

# W określone dni tygodnia
CronTrigger(day_of_week='mon,wed,fri', hour=9, minute=0)

# Pierwszy dzień miesiąca
CronTrigger(day=1, hour=8, minute=0)
```

## 🐛 Troubleshooting

### Problem: Scheduler nie startuje

**Sprawdź logi:**
```bash
python manage.py runserver
# Szukaj: "Periodic task scheduler started successfully"
```

**Możliwe przyczyny:**
- Brak zainstalowanych pakietów: `pip install APScheduler django-apscheduler`
- Brak migracji: `python manage.py migrate`
- Błąd w `scheduler.py` - sprawdź logi błędów

### Problem: Zadania nie wykonują się

**Sprawdź w Django Admin:**
1. Przejdź do **Django Apscheduler → Django job executions**
2. Zobacz ostatnie wykonania
3. Sprawdź czy są błędy

**Sprawdź czy Django działa:**
- Scheduler działa tylko gdy Django jest uruchomione
- Passenger: sprawdź czy aplikacja nie crashuje
- Lokalnie: musi być uruchomiony `runserver`

### Problem: Zadania wykonują się dwa razy

To może się zdarzyć gdy:
- Runserver z auto-reloadem (uruchamia się dwa razy)
- Masz dwie instancje Django (np. dwa Passengery)

**Rozwiązanie:**
- Kod już to zabezpiecza: `max_instances=1`
- Upewnij się że masz tylko jedną instancję Django

### Problem: Chcę wyłączyć scheduler tymczasowo

**Opcja 1: Zmień settings.py**
```python
# Dodaj do settings.py:
ENABLE_SCHEDULER = config('ENABLE_SCHEDULER', default=True, cast=bool)

# W apps.py:
if not skip_scheduler and settings.ENABLE_SCHEDULER:
    ...
```

**Opcja 2: Usuń z INSTALLED_APPS**
```python
# Zakomentuj w settings.py:
# 'django_apscheduler',
```

## 📝 Porównanie: CRON vs APScheduler

### CRON (jak wcześniej):
```bash
# Konfiguracja w crontab na serwerze
0 2 * * * cd ~/domains/betulait.usermd.net/public_python && python manage.py auto_close_tickets

✅ Działa nawet gdy Django nie działa
❌ Wymaga dostępu do crona
❌ Trudniejszy debugging
❌ Każdy serwer wymaga konfiguracji
```

### APScheduler (teraz):
```python
# Konfiguracja w crm/scheduler.py
scheduler.add_job(auto_close_resolved_tickets, trigger=CronTrigger(hour=2, minute=0))

✅ Nie wymaga konfiguracji serwera
✅ Historia w Django Admin
✅ Łatwy debugging
✅ Automatycznie działa po deploymencie
❌ Wymaga działającego Django
```

## 🎯 Rekomendacja

**Dla większości przypadków:** Użyj **APScheduler** (prostsze, mniej konfiguracji)

**Użyj CRON gdy:**
- Potrzebujesz zadań które działają nawet gdy Django nie działa
- Masz bardzo krytyczne zadania (np. backupy bazy)
- Chcesz niezależność od aplikacji

**Możesz użyć OBIE:**
- APScheduler: Auto-close tickets (co 24h)
- CRON: Backupy bazy danych (raz dziennie, niezależnie od Django)

## 📚 Więcej informacji

- APScheduler docs: https://apscheduler.readthedocs.io/
- Django APScheduler: https://github.com/jcass77/django-apscheduler

---

**Data:** 2025-10-16  
**Wersja:** 1.0
