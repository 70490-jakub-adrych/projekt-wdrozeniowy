# Automatyczna Zmiana Statusu na "W trakcie" przy Tworzeniu Przypisanego Ticketa - 2025-10-29

## Problem
Gdy Agent, Superagent lub Admin tworzył ticket i od razu go do kogoś przypisywał:
- Status ticketa pozostawał jako **"Nowe"**
- Przypisana osoba musiała ręcznie zmienić status na "W trakcie" lub użyć przycisku "Przydziel do mnie"
- To było niepotrzebnym krokiem, ponieważ ticket był już przypisany

## Rozwiązanie
Dodano automatyczną zmianę statusu podczas tworzenia ticketa:

### Logika
- **Klient** tworzy ticket bez przypisania → status: **"Nowe"** ✅ (bez zmian)
- **Agent/Superagent/Admin** tworzy ticket bez przypisania → status: **"Nowe"** ✅ (bez zmian)
- **Agent/Superagent/Admin** tworzy ticket Z przypisaniem → status: **"W trakcie"** ✨ (NOWE!)

### Zmiany w kodzie

#### `crm/views/tickets/create_views.py`

Dodano sprawdzenie po zapisaniu ticketa:

```python
# If agent/superagent/admin creates ticket and assigns it immediately, set status to 'in_progress'
if user.profile.role in ['admin', 'superagent', 'agent'] and form.cleaned_data.get('assigned_to'):
    ticket.status = 'in_progress'
```

## Korzyści

1. ✅ **Mniej kliknięć** - przypisana osoba nie musi już ręcznie zmieniać statusu
2. ✅ **Lepszy workflow** - ticket od razu jest w statusie "W trakcie", co odzwierciedla rzeczywistość
3. ✅ **Zachowana elastyczność** - tickety nieprzypisane nadal mają status "Nowe"
4. ✅ **Zgodność z logiką biznesową** - przypisany ticket = ktoś nad nim pracuje

## Przypadki użycia

### Scenariusz 1: Klient tworzy ticket
- Klient wypełnia formularz (bez możliwości przypisania)
- Status: **"Nowe"**
- Assigned to: **Nieprzypisane**
- ✅ Bez zmian - działa jak wcześniej

### Scenariusz 2: Agent tworzy ticket bez przypisania
- Agent wypełnia formularz
- Pole "Przypisany do" pozostaje puste
- Status: **"Nowe"**
- Assigned to: **Nieprzypisane**
- ✅ Bez zmian - działa jak wcześniej

### Scenariusz 3: Agent tworzy ticket Z przypisaniem (NOWE!)
- Agent wypełnia formularz
- Agent wybiera osobę w polu "Przypisany do"
- Status: **"W trakcie"** ✨
- Assigned to: **[wybrana osoba]**
- ✅ Nowe zachowanie - oszczędza krok!

## Techniczne szczegóły

### Moment ustawienia statusu
Status jest ustawiany **przed** `ticket.save()`, więc:
- Jest częścią pierwotnego zapisu ticketa
- Jest widoczny w logach aktywności
- Jest uwzględniony w powiadomieniach email

### Walidacja
- Sprawdzenie roli użytkownika: `user.profile.role in ['admin', 'superagent', 'agent']`
- Sprawdzenie czy ticket jest przypisany: `form.cleaned_data.get('assigned_to')`
- Tylko gdy OBA warunki są spełnione, status zmienia się na `'in_progress'`

## Pliki zmodyfikowane
- `crm/views/tickets/create_views.py` - dodano automatyczne ustawianie statusu

## Testowanie

Po wdrożeniu należy przetestować:
1. ✅ Klient tworzy ticket → status "Nowe"
2. ✅ Agent tworzy ticket bez przypisania → status "Nowe"
3. ✅ Agent tworzy ticket z przypisaniem → status "W trakcie" ✨
4. ✅ Superagent tworzy ticket z przypisaniem → status "W trakcie" ✨
5. ✅ Admin tworzy ticket z przypisaniem → status "W trakcie" ✨
