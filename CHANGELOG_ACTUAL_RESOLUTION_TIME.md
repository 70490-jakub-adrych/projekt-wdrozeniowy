# Rzeczywisty czas wykonania zgłoszeń - Dokumentacja zmian

## Przegląd

Dodano funkcjonalność śledzenia **rzeczywistego czasu wykonania zgłoszeń** (actual resolution time). Agent/Admin/Superagent podczas zamykania zgłoszenia może podać ile godzin faktycznie poświęcił na realizację zadania. Te dane są następnie wykorzystywane do generowania statystyk wydajności.

## Zmiany w bazie danych

### Model Ticket (crm/models.py)

Dodano nowe pole:

```python
actual_resolution_time = models.DecimalField(
    max_digits=6, 
    decimal_places=2, 
    null=True, 
    blank=True, 
    verbose_name="Rzeczywisty czas wykonania (godziny)",
    help_text="Podaj rzeczywisty czas poświęcony na wykonanie zgłoszenia w godzinach"
)
```

**Właściwości:**
- `null=True, blank=True` - pole opcjonalne, stare zgłoszenia będą miały NULL
- `max_digits=6, decimal_places=2` - maksymalnie 9999.99 godziny
- Wartość w godzinach (np. 2.5 = 2 godziny 30 minut)

### Migracja bazy danych

**WAŻNE:** Musisz wykonać migrację na serwerze produkcyjnym:

```bash
python manage.py makemigrations
python manage.py migrate
```

Migracja jest bezpieczna - dodaje nowe pole z `null=True`, więc nie wpłynie na istniejące dane.

## Zmiany w kodzie

### 1. Widok zamykania zgłoszenia (crm/views/tickets/action_views.py)

**Dodano:**
- Import `Decimal` i `InvalidOperation` do walidacji
- Pobieranie wartości `actual_resolution_time` z POST
- Walidacja czasu wykonania:
  - Minimum: 0.25 godziny (15 minut)
  - Maximum: 1000 godzin
  - Tylko liczby (format: 2.5)
- Logowanie czasu wykonania w ActivityLog
- Przekazanie `show_time_field` do template (tylko dla agentów/adminów/superagentów)

**Walidacja:**
```python
if actual_time_decimal < Decimal('0.25'):
    messages.error(request, 'Rzeczywisty czas wykonania musi być co najmniej 0.25 godziny (15 minut)')
if actual_time_decimal > Decimal('1000'):
    messages.error(request, 'Rzeczywisty czas wykonania nie może przekraczać 1000 godzin')
```

### 2. Template zamykania zgłoszenia (ticket_confirm_close.html)

**Dodano pole formularza:**
```html
<input 
    type="number" 
    class="form-control" 
    id="actual_resolution_time" 
    name="actual_resolution_time" 
    step="0.25" 
    min="0.25"
    max="1000"
    placeholder="np. 2.5"
    required>
```

**Funkcjonalność:**
- Pole wyświetlane tylko dla agentów/adminów/superagentów
- Walidacja HTML5 (min/max/step)
- Wymagane pole (required)
- Podpowiedź dla użytkownika

### 3. Statystyki (crm/views/statistics_views.py)

**Dodano nowe kalkulacje:**

**Statystyki globalne:**
```python
avg_actual_resolution_time = tickets.exclude(
    actual_resolution_time__isnull=True
).aggregate(
    avg_actual_time=Avg('actual_resolution_time')
)['avg_actual_time']

tickets_with_actual_time = tickets.exclude(actual_resolution_time__isnull=True).count()
tickets_with_actual_time_percentage = (tickets_with_actual_time / total_tickets * 100)
```

**Statystyki per agent:**
```python
agent_actual_avg_time = agent_tickets.exclude(
    actual_resolution_time__isnull=True
).aggregate(
    avg_actual_time=Avg('actual_resolution_time')
)['avg_actual_time']

agent_tickets_with_actual_time = agent_tickets.exclude(actual_resolution_time__isnull=True).count()
```

**Dodano do kontekstu:**
- `avg_actual_hours` - średni rzeczywisty czas dla wszystkich zgłoszeń
- `tickets_with_actual_time` - liczba zgłoszeń z podanym czasem
- `tickets_with_actual_time_percentage` - procent zgłoszeń z podanym czasem
- W `agent_performance`:
  - `avg_actual_resolution_time` - średni rzeczywisty czas per agent
  - `tickets_with_actual_time` - liczba zgłoszeń z czasem per agent

### 4. Template statystyk (statistics_dashboard.html)

**Dodano nową kartę statystyk:**
```html
<div class="col-md-4 mb-3">
    <div class="stats-card bg-light p-3 rounded text-center h-100">
        <h5 class="text-muted">Średni rzeczywisty czas wykonania</h5>
        <h2>{{ avg_actual_hours|floatformat:2 }} godz.</h2>
        <small class="text-muted">
            {{ tickets_with_actual_time }} zgłoszeń ({{ tickets_with_actual_time_percentage|floatformat:0 }}%)
        </small>
    </div>
</div>
```

**Wskaźniki kolorów:**
- 🟢 Zielony: < 2 godziny (dobrze)
- 🟡 Żółty: 2-5 godzin (średnio)
- 🔴 Czerwony: > 5 godzin (słabo)

**Dodano kolumnę w tabeli wydajności agentów:**
```html
<th>Śr. rzeczywisty czas</th>
...
<td>
    {{ ap.avg_actual_resolution_time|floatformat:1 }} godz.
    <small>({{ ap.tickets_with_actual_time }} zgł.)</small>
</td>
```

### 5. Widok szczegółów zgłoszenia (ticket_detail.html)

**Dodano wyświetlanie:**
```html
{% if ticket.actual_resolution_time %}
<div class="row mb-3">
    <div class="col-md-3 fw-bold">Rzeczywisty czas wykonania:</div>
    <div class="col-md-9">
        <span class="badge bg-info">
            <i class="fas fa-clock"></i> {{ ticket.actual_resolution_time }} godzin
        </span>
    </div>
</div>
{% endif %}
```

### 6. Admin Django (crm/admin.py)

**Dodano pole do TicketAdmin:**
- Dodano `actual_resolution_time` do `list_display`
- Dodano grupę pól "Daty i czas" w `fieldsets`
- Pole edytowalne w adminie

## Jak używać

### Dla agentów/adminów/superagentów:

1. **Zamykanie zgłoszenia:**
   - Kliknij "Zamknij zgłoszenie"
   - Wyświetli się formularz z polem "Rzeczywisty czas wykonania"
   - Wpisz czas w godzinach (np. `2.5` dla 2h 30min, `0.5` dla 30 minut)
   - Kliknij "Zamknij zgłoszenie"

2. **Walidacja:**
   - Minimum: 0.25 godziny (15 minut)
   - Maximum: 1000 godzin
   - Krok: 0.25 godziny
   - Pole wymagane

3. **Jeśli nie podano czasu:**
   - Wyświetli się ostrzeżenie: "Zaleca się podanie rzeczywistego czasu wykonania zgłoszenia"
   - Zgłoszenie zostanie zamknięte, ale bez czasu wykonania

### Dla klientów:

- Klienci **nie widzą** pola czasu wykonania podczas zamykania
- Mogą zobaczyć czas wykonania w szczegółach zamkniętego zgłoszenia (jeśli został podany)

### Statystyki:

1. **Dashboard statystyk:**
   - Karta "Średni rzeczywisty czas wykonania" - pokazuje średnią dla wszystkich zgłoszeń z podanym czasem
   - Procent zgłoszeń z podanym czasem
   
2. **Tabela wydajności agentów:**
   - Kolumna "Śr. rzeczywisty czas" dla każdego agenta
   - Liczba zgłoszeń z podanym czasem w nawiasie

3. **Filtrowanie:**
   - Statystyki uwzględniają tylko zgłoszenia z podanym czasem (NULL są pomijane)
   - Stare zgłoszenia nie wpływają na statystyki

## Różnica między czasami

System teraz śledzi **dwa różne czasy**:

### 1. Średni czas rozwiązania (avg_resolution_time)
- **Automatyczny** - obliczany z dat: `resolved_at - created_at`
- Pokazuje całkowity czas od zgłoszenia do rozwiązania
- Zawiera czas oczekiwania, komunikacji, etc.
- **Przykład:** Zgłoszenie utworzono 1.01 o 10:00, rozwiązano 3.01 o 14:00 = 52 godziny

### 2. Średni rzeczywisty czas wykonania (avg_actual_resolution_time)
- **Ręczny** - podawany przez agenta
- Pokazuje faktyczny czas pracy agenta nad zgłoszeniem
- Nie zawiera czasu oczekiwania na klienta, czasu bezczynności
- **Przykład:** Agent przepracował 2.5 godziny (mimo że zgłoszenie było otwarte 52 godziny)

## Migracja danych

### Stare zgłoszenia:
- Będą miały `actual_resolution_time = NULL`
- **Nie będą** uwzględniane w statystykach rzeczywistego czasu
- To jest zamierzone - chcemy statystyki tylko z nowych, dokładnych danych

### Nowe zgłoszenia:
- Agent powinien zawsze podawać rzeczywisty czas
- System wyświetla ostrzeżenie jeśli czas nie został podany
- Ale nie blokuje zamknięcia zgłoszenia

## Testy

Przed wdrożeniem na produkcję, przetestuj:

1. **Zamykanie zgłoszenia:**
   - [ ] Agent może zamknąć zgłoszenie z czasem
   - [ ] Walidacja min/max działa
   - [ ] Ostrzeżenie przy braku czasu
   - [ ] Klient nie widzi pola czasu

2. **Statystyki:**
   - [ ] Karta "Średni rzeczywisty czas" wyświetla się
   - [ ] Tabela agentów ma nową kolumnę
   - [ ] Stare zgłoszenia nie psują statystyk

3. **Widok szczegółów:**
   - [ ] Czas wykonania wyświetla się dla zamkniętych zgłoszeń
   - [ ] Nie wyświetla się dla zgłoszeń bez czasu

4. **Admin:**
   - [ ] Pole jest edytowalne
   - [ ] Wyświetla się w liście

## Rozszerzenia w przyszłości

Możliwe ulepszenia:

1. **Wykres czasów wykonania** - rozkład czasów w czasie
2. **Porównanie czasów** - rzeczywisty vs. oczekiwany
3. **Cele czasowe** - SLA dla czasu wykonania
4. **Export do CSV** - danych o czasach
5. **Automatyczne sugestie** - ML do przewidywania czasu
6. **Powiadomienia** - gdy czas przekracza normy

## Problemy i rozwiązania

### Problem: Stare zgłoszenia mają NULL
**Rozwiązanie:** To zamierzone. Statystyki ignorują NULL wartości.

### Problem: Agent zapomniał podać czas
**Rozwiązanie:** System wyświetla ostrzeżenie, ale nie blokuje. Można później edytować w adminie.

### Problem: Nieprawidłowy format czasu
**Rozwiązanie:** Walidacja HTML5 + walidacja backendu pokazuje błąd.

### Problem: Bardzo długi czas (>1000h)
**Rozwiązanie:** Walidacja blokuje wartości > 1000 godzin.

## Commit message

```
feat: Dodaj rzeczywisty czas wykonania zgłoszeń

- Dodano pole actual_resolution_time do modelu Ticket
- Agent może podać rzeczywisty czas przy zamykaniu zgłoszenia
- Walidacja 0.25-1000 godzin
- Statystyki średniego czasu per agent i globalnie
- Wyświetlanie czasu w szczegółach zgłoszenia
- Edycja w Django admin
- Stare zgłoszenia (NULL) nie wpływają na statystyki
```

## Autorzy

- Implementacja: GitHub Copilot
- Data: 2025-10-15