# Hotfix - Kolory badge'ów w rozwijanych listach ticketów

**Data:** 2025-10-17  
**Typ:** Bugfix (UI)  
**Priorytet:** Średni  
**Status:** ✅ Naprawione

---

## 🐛 Problem

W rozwijanych listach ticketów agentów (dashboard statystyk) badge'y statusów i priorytetów miały **białe kolory** zamiast kolorowych:
- Wszystkie badge'y wyglądały identycznie (białe tło, biały tekst)
- Niemożliwe było odróżnienie priorytetów i statusów na pierwszy rzut oka
- Niespójna stylizacja z resztą aplikacji (np. `ticket_list.html`)

**Przyczyna:**
Używano **starych klas Bootstrap 4** (`badge-primary`, `badge-success`, etc.) zamiast **Bootstrap 5** (`bg-primary`, `bg-success`, etc.)

---

## ✅ Rozwiązanie

Zaktualizowano klasy CSS w JavaScript generującym HTML dla rozwijanych list ticketów.

### Zmiany w kodzie

**Plik:** `crm/templates/crm/statistics/statistics_dashboard.html`

**Przed (Bootstrap 4 - NIE DZIAŁA):**
```javascript
let statusClass = '';
if (ticket.status_raw === 'closed') statusClass = 'badge-secondary';
else if (ticket.status_raw === 'resolved') statusClass = 'badge-success';
else if (ticket.status_raw === 'in_progress') statusClass = 'badge-info';
else if (ticket.status_raw === 'new') statusClass = 'badge-primary';
else statusClass = 'badge-warning';

let priorityClass = '';
if (ticket.priority_raw === 'critical') priorityClass = 'badge-danger';
else if (ticket.priority_raw === 'high') priorityClass = 'badge-warning';
else if (ticket.priority_raw === 'medium') priorityClass = 'badge-info';
else priorityClass = 'badge-secondary';
```

**Po (Bootstrap 5 - DZIAŁA):**
```javascript
// Bootstrap 5 badge classes with proper colors
let statusClass = '';
if (ticket.status_raw === 'new') statusClass = 'bg-primary';
else if (ticket.status_raw === 'in_progress') statusClass = 'bg-info';
else if (ticket.status_raw === 'unresolved') statusClass = 'bg-warning text-dark';
else if (ticket.status_raw === 'resolved') statusClass = 'bg-success';
else if (ticket.status_raw === 'closed') statusClass = 'bg-secondary';
else statusClass = 'bg-secondary';

let priorityClass = '';
if (ticket.priority_raw === 'low') priorityClass = 'bg-secondary';
else if (ticket.priority_raw === 'medium') priorityClass = 'bg-info';
else if (ticket.priority_raw === 'high') priorityClass = 'bg-warning text-dark';
else if (ticket.priority_raw === 'critical') priorityClass = 'bg-danger';
else priorityClass = 'bg-secondary';
```

---

## 🎨 Kolory badge'ów

### Statusy (zgodne z `ticket_list.html`)

| Status | Klasa Bootstrap 5 | Kolor | Tekst |
|--------|------------------|-------|-------|
| **Nowy** (`new`) | `bg-primary` | 🔵 Niebieski | Biały |
| **W trakcie** (`in_progress`) | `bg-info` | 🔵 Cyjan | Biały |
| **Nierozwiązany** (`unresolved`) | `bg-warning text-dark` | 🟡 Żółty | **Czarny** |
| **Rozwiązany** (`resolved`) | `bg-success` | 🟢 Zielony | Biały |
| **Zamknięty** (`closed`) | `bg-secondary` | ⚫ Szary | Biały |

### Priorytety (zgodne z `ticket_list.html`)

| Priorytet | Klasa Bootstrap 5 | Kolor | Tekst |
|-----------|------------------|-------|-------|
| **Niski** (`low`) | `bg-secondary` | ⚫ Szary | Biały |
| **Średni** (`medium`) | `bg-info` | 🔵 Cyjan | Biały |
| **Wysoki** (`high`) | `bg-warning text-dark` | 🟡 Żółty | **Czarny** |
| **Krytyczny** (`critical`) | `bg-danger` | 🔴 Czerwony | Biały |

---

## 🔍 Kluczowe zmiany

### 1. Bootstrap 4 → Bootstrap 5
- ❌ `badge-primary` → ✅ `bg-primary`
- ❌ `badge-success` → ✅ `bg-success`
- ❌ `badge-warning` → ✅ `bg-warning`
- ❌ `badge-danger` → ✅ `bg-danger`
- ❌ `badge-secondary` → ✅ `bg-secondary`
- ❌ `badge-info` → ✅ `bg-info`

### 2. Dodano `text-dark` dla żółtych badge'ów
- `bg-warning` **SAM** = żółte tło + biały tekst (nieczytelne)
- `bg-warning text-dark` = żółte tło + **czarny tekst** (czytelne)

Dotyczy:
- Status: **Nierozwiązany** (`unresolved`)
- Priorytet: **Wysoki** (`high`)

### 3. Dodano obsługę `unresolved` status
Wcześniej brakował przypadek dla statusu `unresolved` - teraz ma żółty badge z czarnym tekstem.

### 4. Uporządkowano kolejność warunków
Kolejność if-else zgodna z logicznym przepływem statusów:
- `new` → `in_progress` → `unresolved` → `resolved` → `closed`

Kolejność priorytetów od najniższego do najwyższego:
- `low` → `medium` → `high` → `critical`

---

## 🧪 Testowanie

### Scenariusz 1: Sprawdzenie kolorów statusów
```
1. Zaloguj się jako admin/superagent
2. Przejdź do Statystyki → Dashboard
3. Rozwiń listę ticketów dowolnego agenta
4. OCZEKIWANE kolory badge'ów statusów:
   - Nowy: NIEBIESKI (bg-primary)
   - W trakcie: CYJAN (bg-info)
   - Nierozwiązany: ŻÓŁTY z CZARNYM tekstem (bg-warning text-dark)
   - Rozwiązany: ZIELONY (bg-success)
   - Zamknięty: SZARY (bg-secondary)
```

### Scenariusz 2: Sprawdzenie kolorów priorytetów
```
1. W rozwiniętej liście ticketów sprawdź badge'y priorytetów
2. OCZEKIWANE kolory:
   - Niski: SZARY (bg-secondary)
   - Średni: CYJAN (bg-info)
   - Wysoki: ŻÓŁTY z CZARNYM tekstem (bg-warning text-dark)
   - Krytyczny: CZERWONY (bg-danger)
```

### Scenariusz 3: Porównanie z ticket_list
```
1. Otwórz Zgłoszenia → Lista zgłoszeń
2. Porównaj kolory badge'ów w tabeli ticketów
3. Otwórz Statystyki → Dashboard → rozwiń agenta
4. OCZEKIWANE: Identyczne kolory w obu miejscach
```

### Scenariusz 4: Czytelność tekstu na żółtym tle
```
1. Znajdź ticket z priorytetem "Wysoki" lub statusem "Nierozwiązany"
2. Sprawdź czy tekst jest wyraźnie widoczny
3. OCZEKIWANE: Czarny tekst na żółtym tle (dobry kontrast)
```

---

## 📋 Zgodność z resztą aplikacji

### Miejsca używające tych samych kolorów:

✅ **`ticket_list.html`** (lista ticketów):
```django
<span class="badge 
    {% if ticket.priority == 'low' %}bg-secondary
    {% elif ticket.priority == 'medium' %}bg-info
    {% elif ticket.priority == 'high' %}bg-warning text-dark
    {% elif ticket.priority == 'critical' %}bg-danger
    {% endif %}">
```

✅ **`statistics_dashboard.html`** (rozwijane listy - NAPRAWIONE):
```javascript
if (ticket.priority_raw === 'high') priorityClass = 'bg-warning text-dark';
```

✅ **`_generate_excel_report()`** (raporty Excel):
Kolory hex zgodne z badge'ami:
- `007bff` (niebieski) = `bg-primary`
- `17a2b8` (cyjan) = `bg-info`
- `ffc107` (żółty) = `bg-warning`
- `28a745` (zielony) = `bg-success`
- `dc3545` (czerwony) = `bg-danger`
- `6c757d` (szary) = `bg-secondary`

---

## 🚀 Deployment

**Krok 1: Commit zmian**
```bash
git add crm/templates/crm/statistics/statistics_dashboard.html
git commit -m "fix(statistics): Fix badge colors in expandable agent ticket lists (Bootstrap 5)"
git push origin main
```

**Krok 2: Deploy na serwerze**
```bash
# Zaloguj się na serwer
ssh betulait@s27.mydevil.net

# Przejdź do katalogu
cd ~/domains/betulait.usermd.net/public_python

# Pobierz zmiany
git pull origin main

# Nie wymaga restartu - zmiana tylko w template
```

**Krok 3: Weryfikacja**
```bash
# Otwórz stronę w przeglądarce
# Wyczyść cache (Ctrl+F5)
# Rozwiń listę agenta na dashboardzie statystyk
# Sprawdź kolory badge'ów
```

---

## 📊 Impact Analysis

**Dotknięte komponenty:**
- ✅ Dashboard statystyk - rozwijane listy ticketów agentów
- ✅ AJAX endpoint `/api/agent-tickets/<agent_id>/`
- ❌ Inne części aplikacji NIE są dotknięte (tylko ta jedna funkcja JS)

**Ryzyka:**
- ✅ **Niskie ryzyko** - zmiana tylko klas CSS
- ✅ Nie wpływa na logikę backend
- ✅ Nie wpływa na zapytania do bazy danych
- ✅ Nie zmienia API response

**Kompatybilność:**
- ✅ Bootstrap 5 (aktualnie używana wersja w projekcie)
- ✅ Wszystkie nowoczesne przeglądarki
- ✅ Responsywne (mobile/tablet/desktop)

---

## 📝 Uwagi dodatkowe

### Dlaczego `text-dark` dla żółtych badge'ów?

Bootstrap 5 domyślnie używa **białego tekstu** na wszystkich kolorowych badge'ach, ale:
- Żółte tło (`bg-warning` = `#ffc107`) + biały tekst = **słaby kontrast** (WCAG fail)
- Żółte tło + czarny tekst = **dobry kontrast** (WCAG AAA)

Dlatego dodajemy `text-dark` do `bg-warning`.

### Różnice Bootstrap 4 vs Bootstrap 5

| Element | Bootstrap 4 | Bootstrap 5 |
|---------|-------------|-------------|
| Badge primary | `badge badge-primary` | `badge bg-primary` |
| Badge success | `badge badge-success` | `badge bg-success` |
| Badge warning | `badge badge-warning` | `badge bg-warning` |
| Ciemny tekst | `text-dark` | `text-dark` (bez zmian) |

**Projekt używa Bootstrap 5**, więc musimy używać `bg-*` zamiast `badge-*`.

---

## ✅ Checklist

- [x] Zmieniono klasy Bootstrap 4 na Bootstrap 5
- [x] Dodano `text-dark` dla żółtych badge'ów
- [x] Uporządkowano kolejność warunków if-else
- [x] Dodano komentarze w kodzie
- [x] Sprawdzono zgodność z `ticket_list.html`
- [x] Utworzono dokumentację hotfixa
- [ ] Przetestowano na DEV
- [ ] Przetestowano na PROD
- [ ] Zweryfikowano wszystkie kombinacje status/priorytet

---

**Autor:** AI Assistant (GitHub Copilot)  
**Zgłoszenie:** User feedback - białe badge'y w rozwijanych listach  
**Powiązane pliki:** `statistics_dashboard.html`, `ticket_list.html`  
**Priorytet wdrożenia:** Razem z innymi poprawkami UI
