# Changelog - Zmiany funkcjonalne (2025-10-15)

## 🎯 Podsumowanie zmian

Dodano 3 nowe funkcjonalności związane z rzeczywistym czasem realizacji ticketów oraz automatycznym zamykaniem.

---

## 1️⃣ Pole "Rzeczywisty czas" przy oznaczaniu jako "Rozwiązane"

### ✅ Co się zmieniło:
- Agent/Admin/Superagent musi teraz podać rzeczywisty czas wykonania przy oznaczaniu ticketa jako "Rozwiązane"
- Wcześniej pole to było tylko przy "Zamknij zgłoszenie"
- Teraz jest w obu miejscach: **Rozwiąż** i **Zamknij**

### 📄 Zmodyfikowane pliki:
- `crm/templates/crm/tickets/ticket_confirm_resolve.html` - dodano formularz z polem czasu
- `crm/views/tickets/action_views.py` - dodano walidację i zapisywanie czasu w funkcji `ticket_mark_resolved()`

### 🎯 Walidacja:
- Minimum: **0.25 godziny** (15 minut)
- Maximum: **1000 godzin**
- Krok: **0.25** (można wpisywać: 0.25, 0.5, 0.75, 1.0, itd.)
- Pole jest **wymagane** (required) dla agentów/adminów/superagentów
- Klienci nie widzą tego pola (nie mogą oznaczać jako rozwiązane)

### 💡 Przykład użycia:
```
Agent otwiera ticket → pracuje nad nim 2.5 godziny → klika "Rozwiąż zgłoszenie" 
→ wpisuje "2.5" w polu "Rzeczywisty czas wykonania" → zapisuje
```

### 📊 Gdzie się pojawia ten czas:
- W szczegółach ticketa (badge z ikoną zegara)
- W statystykach (średni rzeczywisty czas)
- W raportach CSV/Excel (nowa kolumna)
- W logach aktywności

---

## 2️⃣ Automatyczne zamykanie ticketów po 24h

### ✅ Co się zmieniło:
- Tickety w statusie "Rozwiązane" są automatycznie zamykane po 24 godzinach
- **Dlaczego?** Klienci często zapominają potwierdzić rozwiązanie
- System teraz robi to za nich po upływie czasu

### 📄 Nowe pliki:
- `crm/management/commands/auto_close_tickets.py` - komenda do zamykania ticketów
- `AUTO_CLOSE_README.md` - dokumentacja użycia

### ⚙️ Użycie komendy:

#### Testowanie (dry-run):
```bash
python manage.py auto_close_tickets --dry-run
```
Pokaże które tickety zostałyby zamknięte, ale ich nie zamknie.

#### Normalne uruchomienie:
```bash
python manage.py auto_close_tickets
```

#### Zmiana czasu (np. 48h zamiast 24h):
```bash
python manage.py auto_close_tickets --hours=48
```

### 🕒 Konfiguracja CRON (mydevil.net):

**Dla produkcji:**
- **Czas:** `0 2 * * *` (codziennie o 2:00)
- **Komenda:**
  ```bash
  cd ~/domains/betulait.usermd.net/public_python && python manage.py auto_close_tickets >> logs/auto_close.log 2>&1
  ```

**Dla dev:**
- **Czas:** `0 3 * * *` (codziennie o 3:00)
- **Komenda:**
  ```bash
  cd ~/domains/dev.betulait.usermd.net/public_python && python manage.py auto_close_tickets >> logs/auto_close.log 2>&1
  ```

### 📝 Co się dzieje podczas auto-zamknięcia:
1. Komenda znajduje tickety: status="resolved" + resolved_at starsze niż 24h
2. Zmienia status na "closed"
3. Ustawia `closed_at = teraz`
4. Loguje w `ActivityLog` z opisem: "Automatycznie zamknięto zgłoszenie ... (brak potwierdzenia od klienta przez 24h)"
5. **NIE wysyła** emaila (można dodać w przyszłości)

### 💡 Przykład działania:
```
Poniedziałek 10:00 - Agent oznacza ticket jako "Rozwiązane"
Wtorek 02:00 - Cron uruchamia auto_close_tickets
Wtorek 02:00 - Ticket automatycznie zamknięty (minęło 16h, ale < 24h) ❌
Środa 02:00 - Cron uruchamia auto_close_tickets
Środa 02:00 - Ticket automatycznie zamknięty (minęło >24h) ✅
```

### 🔍 Logi:
```
======================================================================
AUTO-CLOSE RESOLVED TICKETS (after 24 hours)
======================================================================

Found 3 ticket(s) to auto-close:

  • Ticket #123: "Problem z drukarką" (resolved 26.5h ago by agent_piotr)
    ✅ Closed
  • Ticket #124: "Błąd systemu" (resolved 48.2h ago by agent_anna)
    ✅ Closed

======================================================================
✅ Successfully closed: 2
======================================================================
```

---

## 3️⃣ Rzeczywiste godziny w raportach CSV/Excel

### ✅ Co się zmieniło:
- W sekcji "WYDAJNOŚĆ AGENTÓW" raportów dodano 2 nowe kolumny:
  - **Śr. rzeczywisty czas (godz.)** - średni rzeczywisty czas wykonania dla tego agenta
  - **Zgł. z rzecz. czasem** - liczba zgłoszeń, w których agent podał rzeczywisty czas

### 📄 Zmodyfikowane pliki:
- `crm/views/statistics_views.py` - funkcje `_generate_csv_report()` i `_generate_excel_report()`

### 📊 Przed i po:

**PRZED:**
```
Agent               | Liczba zgłoszeń | Rozwiązanych | % rozwiązanych | Śr. czas rozwiązania
Jan Kowalski        | 45              | 40           | 88.9%          | 12.50
Anna Nowak          | 38              | 35           | 92.1%          | 8.30
```

**PO:**
```
Agent               | Liczba zgłoszeń | Rozwiązanych | % rozwiązanych | Śr. czas rozwiązania | Śr. rzeczywisty czas | Zgł. z rzecz. czasem
Jan Kowalski        | 45              | 40           | 88.9%          | 12.50                | 2.30                 | 38
Anna Nowak          | 38              | 35           | 92.1%          | 8.30                 | 1.80                 | 32
Piotr Wiśniewski    | 52              | 48           | 92.3%          | 15.20                | Brak danych          | 0
```

### 💡 Co oznaczają dane:
- **Śr. czas rozwiązania** - czas od utworzenia do rozwiązania ticketa (automatyczny)
- **Śr. rzeczywisty czas** - średni czas który agent wpisuje ręcznie (faktyczny czas pracy)
- **Zgł. z rzecz. czasem** - ile ticketów ma wypełnione pole `actual_resolution_time`

### 🔍 Przypadki brzegowe:
- Jeśli agent **nigdy nie wpisał** rzeczywistego czasu → pokazuje "Brak danych" / 0 zgłoszeń
- Jeśli agent wpisał tylko w **niektórych** ticketach → średnia z tych które mają
- Jeśli ticket został **zamknięty bez podania czasu** → nie jest brany do średniej

---

## 🧪 Testowanie

### Test 1: Pole czasu przy "Rozwiąż"
1. Zaloguj się jako agent
2. Otwórz przypisany ticket
3. Kliknij "Rozwiąż zgłoszenie"
4. ✅ Powinno pokazać pole "Rzeczywisty czas wykonania"
5. Wpisz "2.5"
6. Kliknij "Oznacz jako rozwiązane"
7. ✅ Ticket powinien mieć status "Rozwiązane" i actual_resolution_time = 2.5

### Test 2: Walidacja czasu
1. Spróbuj wpisać "0.1" → ❌ Powinien pokazać błąd "min 0.25"
2. Spróbuj wpisać "1001" → ❌ Powinien pokazać błąd "max 1000"
3. Spróbuj wpisać "abc" → ❌ Powinien pokazać błąd "nieprawidłowy format"
4. Zostaw puste → ❌ HTML5 validation powinien wymusić wypełnienie

### Test 3: Auto-close (dry-run)
1. Na serwerze produkcyjnym/dev uruchom:
   ```bash
   python manage.py auto_close_tickets --dry-run
   ```
2. ✅ Powinno pokazać listę ticketów które zostałyby zamknięte
3. ✅ Tickety NIE powinny być zamknięte (to tylko podgląd)

### Test 4: Auto-close (rzeczywiste)
1. Stwórz testowy ticket
2. Oznacz jako "Rozwiązane"
3. W Django shell:
   ```python
   from django.utils import timezone
   from datetime import timedelta
   from crm.models import Ticket
   
   ticket = Ticket.objects.get(id=123)  # Twój testowy ticket
   ticket.resolved_at = timezone.now() - timedelta(hours=25)
   ticket.save()
   ```
4. Uruchom: `python manage.py auto_close_tickets`
5. ✅ Ticket powinien być zamknięty
6. ✅ ActivityLog powinien mieć wpis o auto-zamknięciu

### Test 5: Raport CSV/Excel
1. Przejdź do Statystyki
2. Kliknij "Wygeneruj raport"
3. Wybierz format CSV lub Excel
4. Pobierz plik
5. ✅ W sekcji "WYDAJNOŚĆ AGENTÓW" powinny być kolumny:
   - Śr. rzeczywisty czas (godz.)
   - Zgł. z rzecz. czasem
6. ✅ Dane powinny być prawidłowe

---

## 📋 Checklist wdrożenia

### Na serwerze DEV:
- [ ] Sprawdź czy formularz "Rozwiąż" ma pole czasu
- [ ] Przetestuj walidację (0.1, 1001, abc, puste)
- [ ] Uruchom `auto_close_tickets --dry-run`
- [ ] Wygeneruj raport CSV - sprawdź nowe kolumny
- [ ] Wygeneruj raport Excel - sprawdź nowe kolumny

### Na serwerze PRODUKCJA:
- [ ] Deploy kodu
- [ ] Restart aplikacji: `touch tmp/restart.txt`
- [ ] Sprawdź czy formularz "Rozwiąż" działa
- [ ] Ustaw CRON dla `auto_close_tickets`:
  - Czas: `0 2 * * *`
  - Komenda: `cd ~/domains/betulait.usermd.net/public_python && python manage.py auto_close_tickets >> logs/auto_close.log 2>&1`
- [ ] Stwórz folder `logs` jeśli nie istnieje: `mkdir -p logs`
- [ ] Przetestuj ręcznie: `python manage.py auto_close_tickets --dry-run`
- [ ] Sprawdź raporty CSV/Excel

---

## 🐛 Znane problemy / Ograniczenia

1. **Auto-close NIE wysyła emaili** - jeśli chcesz dodać powiadomienia, zobacz kod w `auto_close_tickets.py`
2. **Pole czasu nie jest wymuszane dla adminów** przy zamykaniu przez panel admin - tylko przez widoki
3. **Statystyki pokazują średnią tylko z ticketów które mają czas** - tickety bez czasu są pomijane

---

## 📚 Dokumentacja

- `AUTO_CLOSE_README.md` - szczegółowa dokumentacja auto-close
- `EMAIL_NOTIFICATIONS_SUMMARY.md` - system powiadomień email
- `CHANGELOG_ACTUAL_RESOLUTION_TIME.md` - poprzednia dokumentacja rzeczywistego czasu

---

**Data:** 2025-10-15  
**Autor:** GitHub Copilot  
**Wersja:** 1.0
