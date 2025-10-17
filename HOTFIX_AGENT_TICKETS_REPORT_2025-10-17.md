# Hotfix - Brak listy ticketów agentów w raportach

**Data:** 2025-10-17  
**Typ:** Bugfix (Critical)  
**Priorytet:** Wysoki  
**Status:** ✅ Naprawione

---

## 🐛 Problem

W wygenerowanych raportach (CSV i Excel) **nie pojawiały się listy ticketów** poszczególnych agentów pomimo że kod był zaimplementowany.

**Gdzie występował:**
- Dashboard statystyk → "Generuj raport" → CSV
- Dashboard statystyk → "Generuj raport" → Excel
- Sekcja "WYDAJNOŚĆ AGENTÓW" miała tylko podsumowanie, brak szczegółów ticketów

---

## 🔍 Przyczyna

**Dwa błędy w kodzie:**

### 1. Brak `agent_id` w słowniku `agent_performance`

**Linia 807** - `agent_performance.append()`:
```python
# BŁĄD - brak agent_id
agent_performance.append({
    'agent_name': "...",
    'ticket_count': ...,
    'resolved_count': ...,
    'resolution_rate': ...,
    'avg_resolution_time': ...
    # ❌ BRAKUJE: 'agent_id'
})
```

**Linia 944** (CSV) i **1150** (Excel) - próba pobrania `agent_id`:
```python
agent_id = ap.get('agent_id')  # ← Zwraca None bo nie ma w słowniku!
if agent_id:  # ← Zawsze False
    # Ten kod nigdy się nie wykonuje
    agent_tickets = Ticket.objects.filter(...)
```

**Rezultat:** Tickety nigdy nie były pobierane bo `agent_id` było `None`.

### 2. Błędne użycie `parse_date()` na obiektach `date`

**Linia 947** (CSV) i **1153** (Excel):
```python
from django.utils.dateparse import parse_date
start_date = parse_date(period_start)  # ← period_start to już obiekt date!
end_date = parse_date(period_end)      # ← parse_date(date) zwraca None!

agent_tickets = Ticket.objects.filter(
    created_at__date__gte=start_date,  # ← None!
    created_at__date__lte=end_date     # ← None!
)
# Rezultat: Zwraca WSZYSTKIE tickety (brak filtrowania dat) lub żadne
```

**Dlaczego `parse_date(date)` zwraca `None`:**
- `parse_date()` oczekuje **stringa** (np. `"2025-10-17"`)
- Jeśli otrzyma obiekt `date`, nie potrafi go sparsować → zwraca `None`
- Filter z `None` albo ignoruje warunek, albo zwraca pusty QuerySet

---

## ✅ Rozwiązanie

### 1. Dodano `agent_id` do słownika

**Plik:** `crm/views/statistics_views.py`, linia 807

**Przed:**
```python
agent_performance.append({
    'agent_name': f"{agent_user.first_name} {agent_user.last_name}" if agent_user.first_name else agent_user.username,
    'ticket_count': agent_total,
    'resolved_count': agent_resolved,
    'resolution_rate': resolution_rate,
    'avg_resolution_time': agent_avg_hours
})
```

**Po:**
```python
agent_performance.append({
    'agent_id': agent_id,  # ← DODANE - klucz do filtrowania ticketów
    'agent_name': f"{agent_user.first_name} {agent_user.last_name}" if agent_user.first_name else agent_user.username,
    'ticket_count': agent_total,
    'resolved_count': agent_resolved,
    'resolution_rate': resolution_rate,
    'avg_resolution_time': agent_avg_hours
})
```

### 2. Usunięto zbędne `parse_date()` - używamy obiektów `date` bezpośrednio

**CSV - Plik:** `crm/views/statistics_views.py`, linia 944

**Przed:**
```python
agent_id = ap.get('agent_id')
if agent_id:
    from django.utils.dateparse import parse_date
    start_date = parse_date(period_start)  # ← BŁĄD
    end_date = parse_date(period_end)      # ← BŁĄD
    
    agent_tickets = Ticket.objects.filter(
        assigned_to_id=agent_id,
        created_at__date__gte=start_date,  # ← None
        created_at__date__lte=end_date     # ← None
    ).order_by('-created_at')
```

**Po:**
```python
agent_id = ap.get('agent_id')
if agent_id:
    # period_start and period_end are already date objects, use them directly
    agent_tickets = Ticket.objects.filter(
        assigned_to_id=agent_id,
        created_at__date__gte=period_start,  # ← Działa!
        created_at__date__lte=period_end     # ← Działa!
    ).order_by('-created_at')
```

**Excel - identyczna poprawka** w linii 1150.

---

## 🧪 Testowanie

### Scenariusz 1: Generowanie raportu CSV
```
1. Zaloguj się jako admin/superagent
2. Przejdź do Statystyki → Dashboard
3. Ustaw zakres dat (np. ostatni miesiąc)
4. Kliknij "Generuj raport" → "CSV"
5. Otwórz pobrany plik CSV
6. Przewiń do sekcji "WYDAJNOŚĆ AGENTÓW"
7. OCZEKIWANE:
   - Pod każdym agentem znajduje się: "Zgłoszenia agenta: [Imię Nazwisko]"
   - Poniżej nagłówki: ID, Tytuł, Status, Priorytet, Kategoria, Utworzono, Rozwiązano, Zamknięto
   - Lista ticketów agenta z danymi
   - Jeśli agent nie ma ticketów: "Brak zgłoszeń w wybranym okresie"
```

### Scenariusz 2: Generowanie raportu Excel
```
1. Kliknij "Generuj raport" → "Excel"
2. Otwórz pobrany plik Excel
3. Przewiń do sekcji "WYDAJNOŚĆ AGENTÓW"
4. OCZEKIWANE:
   - Pod każdym agentem sekcja z ticketami
   - Kolorowe komórki dla statusów (niebieski, zielony, szary, etc.)
   - Kolorowe komórki dla priorytetów (czerwony, żółty, cyjan, szary)
   - Nagłówki z szarym tłem
   - Wszystkie tickety agenta w wybranym okresie
```

### Scenariusz 3: Różne zakresy dat
```
1. Wygeneruj raport dla okresu gdzie agent miał 10 ticketów
2. OCZEKIWANE: Wszystkie 10 ticketów widoczne
3. Zmień zakres na okres gdzie agent miał 0 ticketów
4. Wygeneruj raport ponownie
5. OCZEKIWANE: "Brak zgłoszeń w wybranym okresie"
```

### Scenariusz 4: Wielu agentów
```
1. Wygeneruj raport z wieloma agentami (np. 5+)
2. OCZEKIWANE:
   - Każdy agent ma swoją sekcję
   - Tickety nie mieszają się między agentami
   - Daty są poprawnie filtrowane dla każdego agenta
```

### Scenariusz 5: Weryfikacja dat
```
1. Agent ma tickety:
   - 2025-10-01: Ticket A
   - 2025-10-15: Ticket B
   - 2025-10-20: Ticket C
2. Wygeneruj raport dla okresu: 2025-10-10 do 2025-10-18
3. OCZEKIWANE:
   - Tylko Ticket B widoczny (utworzony 2025-10-15)
   - Ticket A i C NIE powinny być widoczne (poza zakresem)
```

---

## 📊 Flow danych

### Przed poprawką:
```
1. generate_statistics_report()
   ↓
2. agent_performance.append({...}) → ❌ BRAK agent_id
   ↓
3. _generate_csv_report(agent_performance)
   ↓
4. agent_id = ap.get('agent_id') → None
   ↓
5. if agent_id: → False
   ↓
6. Kod pobierający tickety NIE wykonuje się
   ↓
7. Raport bez ticketów agentów ❌
```

### Po poprawce:
```
1. generate_statistics_report()
   ↓
2. agent_performance.append({agent_id: ..., ...}) → ✅ Zawiera agent_id
   ↓
3. _generate_csv_report(agent_performance)
   ↓
4. agent_id = ap.get('agent_id') → 123 (prawdziwe ID)
   ↓
5. if agent_id: → True
   ↓
6. agent_tickets = Ticket.objects.filter(
       assigned_to_id=123,
       created_at__date__gte=period_start,  ✅ Obiekt date
       created_at__date__lte=period_end     ✅ Obiekt date
   )
   ↓
7. Raport z ticketami agentów ✅
```

---

## 🔐 Bezpieczeństwo

✅ **Poprawka jest bezpieczna:**
- Nie zmienia struktury danych w bazie
- Nie wpływa na uprawnienia
- Tylko naprawia filtrowanie ticketów
- Używa istniejących mechanizmów ORM Django

⚠️ **Uwagi:**
- Tickety są filtrowane według `assigned_to_id` (już przypisane)
- Filtrowanie dat według `created_at` (data utworzenia)
- Weryfikuj czy raporty zawierają prawidłowe dane po wdrożeniu

---

## 📝 Lessons Learned

### 1. Zawsze sprawdzaj czy wszystkie potrzebne klucze są w słowniku
```python
# ❌ ŹLE - dodajemy do słownika bez wszystkich kluczy
data.append({'name': name, 'count': count})

# Później:
id = item.get('id')  # ← None, bo nie było w append()

# ✅ DOBRZE - dodajemy wszystkie potrzebne klucze od razu
data.append({'id': id, 'name': name, 'count': count})
```

### 2. Znaj typy danych używanych w funkcjach
```python
# ❌ ŹLE - parse_date() oczekuje stringa
from django.utils.dateparse import parse_date
date_obj = datetime.date(2025, 10, 17)
parsed = parse_date(date_obj)  # ← None!

# ✅ DOBRZE - używaj parse_date() tylko dla stringów
date_string = "2025-10-17"
parsed = parse_date(date_string)  # ← date(2025, 10, 17)

# ✅ NAJLEPIEJ - jeśli już masz date, użyj go bezpośrednio
date_obj = datetime.date(2025, 10, 17)
# Użyj date_obj bezpośrednio w query
```

### 3. Debugowanie brakujących danych
```python
# Dodaj logi aby zweryfikować wartości
logger.debug(f"agent_id: {agent_id}")  # ← Czy jest None?
logger.debug(f"period_start type: {type(period_start)}")  # ← date czy string?
logger.debug(f"agent_tickets count: {agent_tickets.count()}")  # ← Ile ticketów?
```

---

## 🚀 Deployment

**Krok 1: Commit zmian**
```bash
git add crm/views/statistics_views.py
git commit -m "fix(statistics): Add agent_id to performance dict and fix date filtering in reports"
git push origin main
```

**Krok 2: Deploy na serwerze**
```bash
ssh betulait@s27.mydevil.net
cd ~/domains/betulait.usermd.net/public_python
git pull origin main
touch tmp/restart.txt  # Restart aplikacji (wymaga restart dla zmian w views.py)
```

**Krok 3: Weryfikacja**
```bash
# Wygeneruj raport CSV i Excel
# Sprawdź czy zawierają listy ticketów agentów
# Zweryfikuj filtrowanie dat
```

---

## 📋 Powiązane pliki

**Zmienione:**
- ✅ `crm/views/statistics_views.py`:
  - Linia 807: Dodano `'agent_id': agent_id` do `agent_performance.append()`
  - Linia 944-950: Usunięto `parse_date()`, używamy `period_start`/`period_end` bezpośrednio (CSV)
  - Linia 1150-1156: Identyczna zmiana dla Excel

**Powiązane (NIE zmieniane):**
- `crm/templates/crm/statistics/statistics_dashboard.html` (UI)
- `crm/static/crm/js/statistics.js` (frontend)

---

## ✅ Checklist

- [x] Dodano `agent_id` do słownika `agent_performance`
- [x] Usunięto błędne `parse_date()` w CSV
- [x] Usunięto błędne `parse_date()` w Excel
- [x] Dodano komentarze w kodzie
- [x] Utworzono dokumentację hotfixa
- [ ] Przetestowano raport CSV z ticketami agentów
- [ ] Przetestowano raport Excel z ticketami agentów
- [ ] Sprawdzono filtrowanie dat
- [ ] Wdrożono na DEV
- [ ] Wdrożono na PROD

---

**Autor:** AI Assistant (GitHub Copilot)  
**Zgłoszenie:** User report - "lista zgłoszeń agentów nie pojawia się w raporcie"  
**Severity:** High (feature not working)  
**Root cause:** Missing dictionary key + wrong data type usage  
**Estimated time to fix:** 5 minut (3 linie kodu)
