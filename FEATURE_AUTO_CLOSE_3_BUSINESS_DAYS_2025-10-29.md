# Zmiana Czasu Auto-zamykania Ticketów: 24h → 3 Dni Robocze - 2025-10-29

## Problem
System automatycznie zamykał rozwiązane tickety po **24 godzinach** od ustawienia statusu "Rozwiązane". To było zbyt krótko dla klientów, którzy potrzebują więcej czasu na weryfikację rozwiązania.

## Rozwiązanie
Zmieniono czas auto-zamykania z **24 godzin** na **3 dni robocze** (pomijając weekendy).

### Jak działa liczenie dni roboczych?

**3 dni robocze** = 3 dni od poniedziałku do piątku, pomijając soboty i niedziele.

#### Przykłady:
- **Ticket rozwiązany w poniedziałek** → zamknięty w czwartek
- **Ticket rozwiązany w piątek** → zamknięty we wtorek (po weekendzie)
- **Ticket rozwiązany w środę** → zamknięty w poniedziałek

### Zmiany w kodzie

#### 1. `crm/management/commands/auto_close_tickets.py`

**Dodano funkcję liczenia dni roboczych:**
```python
def calculate_business_days_ago(num_days):
    """
    Calculate the datetime that was num_days business days ago (excluding weekends)
    """
    current_date = timezone.now()
    business_days_counted = 0
    
    while business_days_counted < num_days:
        current_date -= timedelta(days=1)
        # Check if it's a weekday (Monday=0, Sunday=6)
        if current_date.weekday() < 5:  # Monday to Friday
            business_days_counted += 1
    
    return current_date
```

**Zaktualizowano parametry:**
- Nowy parametr: `--business-days` (domyślnie: 3)
- Zachowano: `--hours` (dla kompatybilności wstecznej)
- Domyślnie używa dni roboczych zamiast godzin

**Zaktualizowano logikę:**
```python
if hours is not None:
    # If hours specified, use that (backwards compatibility)
    cutoff_time = timezone.now() - timedelta(hours=hours)
    time_description = f'{hours} hours'
else:
    # Use business days (default: 3 business days)
    cutoff_time = calculate_business_days_ago(business_days)
    time_description = f'{business_days} business days'
```

**Zaktualizowano komunikaty:**
- Wyświetla "3 business days" zamiast "24 hours"
- Pokazuje wiek ticketa w dniach zamiast godzinach
- Log aktywności: "brak potwierdzenia od klienta przez 3 business days"

#### 2. `crm/scheduler.py`

**Zaktualizowano opis zadania:**
```python
def auto_close_resolved_tickets():
    """
    Job that automatically closes resolved tickets after 3 business days
    """
```

**Zaktualizowano nazwę zadania:**
```python
name="Auto-close resolved tickets after 3 business days"
```

### Jak działa system?

1. **Codziennie o 2:00** rano uruchamia się zadanie automatyczne
2. System **liczy 3 dni robocze wstecz** od dzisiejszej daty
3. **Znajduje tickety** ze statusem "Rozwiązane" starsze niż ta data
4. **Automatycznie zamyka** te tickety
5. **Loguje aktywność** w systemie

### Przykłady działania

#### Przykład 1: Ticket rozwiązany w środę
```
Środa 15:00 - Ticket ustawiony jako "Rozwiązane"
Czwartek      - 1 dzień roboczy
Piątek        - 2 dni robocze
Sobota        - Weekend (nie liczy się)
Niedziela     - Weekend (nie liczy się)
Poniedziałek  - 3 dni robocze
Wtorek 2:00   - System automatycznie zamyka ticket ✅
```

#### Przykład 2: Ticket rozwiązany w piątek
```
Piątek 17:00  - Ticket ustawiony jako "Rozwiązane"
Sobota        - Weekend (nie liczy się)
Niedziela     - Weekend (nie liczy się)
Poniedziałek  - 1 dzień roboczy
Wtorek        - 2 dni robocze
Środa         - 3 dni robocze
Czwartek 2:00 - System automatycznie zamyka ticket ✅
```

### Użycie ręczne (dla testów)

#### Standardowe wywołanie (3 dni robocze):
```bash
python manage.py auto_close_tickets
```

#### Dry-run (test bez zmian):
```bash
python manage.py auto_close_tickets --dry-run
```

#### Niestandardowa liczba dni roboczych:
```bash
python manage.py auto_close_tickets --business-days 5
```

#### Użycie godzin (stary sposób):
```bash
python manage.py auto_close_tickets --hours 24
```

### Kompatybilność wsteczna

✅ **Zachowano parametr `--hours`** - jeśli ktoś używa tego parametru, system nadal będzie działał
✅ **Domyślnie używa dni roboczych** - ale można wrócić do godzin jeśli potrzeba
✅ **Scheduler używa domyślnej wartości** (3 dni robocze)

### Korzyści

1. ✅ **Więcej czasu dla klientów** - 3 dni robocze zamiast 24h
2. ✅ **Pomija weekendy** - klienci mają czas na weryfikację w dni robocze
3. ✅ **Elastyczność** - można zmienić liczbę dni parametrem
4. ✅ **Kompatybilność** - stary sposób (--hours) nadal działa
5. ✅ **Lepsze komunikaty** - pokazuje dni zamiast godzin
6. ✅ **Logika biznesowa** - zgodna z rzeczywistością (3 dni robocze)

### Logika weekendów

System rozpoznaje dni tygodnia:
- **Dni robocze**: Poniedziałek (0) - Piątek (4)
- **Weekend**: Sobota (5) - Niedziela (6)

```python
if current_date.weekday() < 5:  # Monday to Friday
    business_days_counted += 1
```

### Output przykładowy

```
======================================================================
AUTO-CLOSE RESOLVED TICKETS (after 3 business days)
======================================================================

Found 2 ticket(s) to auto-close:

  • Ticket #156: "Problem z drukarką" (resolved 3.2 days ago by Jan Kowalski)
    ✅ Closed
  • Ticket #157: "Wolny komputer" (resolved 4.1 days ago by Anna Nowak)
    ✅ Closed

======================================================================
✅ Successfully closed: 2
======================================================================
```

## Pliki zmodyfikowane
- `crm/management/commands/auto_close_tickets.py` - dodano funkcję liczenia dni roboczych, zmieniono domyślną wartość
- `crm/scheduler.py` - zaktualizowano opisy zadania

## Testowanie

### Test 1: Dry-run
```bash
python manage.py auto_close_tickets --dry-run
```
**Oczekiwany rezultat**: Pokazuje co zostałoby zamknięte, bez faktycznego zamykania

### Test 2: Standardowe wywołanie
```bash
python manage.py auto_close_tickets
```
**Oczekiwany rezultat**: Zamyka tickety starsze niż 3 dni robocze

### Test 3: Niestandardowa liczba dni
```bash
python manage.py auto_close_tickets --business-days 5 --dry-run
```
**Oczekiwany rezultat**: Pokazuje tickety starsze niż 5 dni roboczych

### Test 4: Kompatybilność wsteczna
```bash
python manage.py auto_close_tickets --hours 72 --dry-run
```
**Oczekiwany rezultat**: Pokazuje tickety starsze niż 72 godziny

## Harmonogram automatyczny

Zadanie uruchamia się **codziennie o 2:00** rano dzięki APScheduler:
```python
trigger=CronTrigger(hour=2, minute=0)
```

## Uwagi

- ⚠️ System uruchamia się codziennie, ale liczy **dni robocze**
- ⚠️ Jeśli dzisiaj jest sobota/niedziela, system i tak uruchomi się, ale dni weekendowe nie są liczone
- ⚠️ Ticket rozwiązany w piątek będzie zamknięty najwcześniej w czwartek (pn, wt, śr = 3 dni robocze)
- ⚠️ Po wdrożeniu zmiany, **stare tickety mogą zostać od razu zamknięte** jeśli są starsze niż 3 dni robocze

## Wdrożenie

Zmiany są gotowe! Wystarczy:
```bash
touch passenger_wsgi.py
# lub restart serwera aplikacji
```

Scheduler automatycznie załaduje nową logikę przy następnym uruchomieniu (lub restarcie aplikacji).
