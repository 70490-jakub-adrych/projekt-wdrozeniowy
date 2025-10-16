# Auto-Close Resolved Tickets - Instrukcje

## Opis
Ta komenda automatycznie zamyka zgłoszenia, które są w statusie "Rozwiązane" przez 24 godziny lub dłużej.

**Dlaczego?** Klienci często zapominają potwierdzić rozwiązanie ticketa. Po 24h system automatycznie zamyka ticket.

## Użycie

### Testowanie (Dry Run)
```bash
python manage.py auto_close_tickets --dry-run
```
Pokaże które tickety zostałyby zamknięte, ale ich nie zamknie.

### Normalne uruchomienie
```bash
python manage.py auto_close_tickets
```

### Zmiana czasu (np. 48 godzin zamiast 24)
```bash
python manage.py auto_close_tickets --hours=48
```

## Ustawienie Cron (mydevil.net)

### Dla hosta produkcyjnego:

**Czas cron:** `0 2 * * *` (codziennie o 2:00)

**Komenda do wpisania w cron:**
```bash
cd ~/domains/betulait.usermd.net/public_python && python manage.py auto_close_tickets >> logs/auto_close.log 2>&1
```

### Dla hosta dev:

**Czas cron:** `0 3 * * *` (codziennie o 3:00)

**Komenda do wpisania w cron:**
```bash
cd ~/domains/dev.betulait.usermd.net/public_python && python manage.py auto_close_tickets >> logs/auto_close.log 2>&1
```

## Przykład działania

```
======================================================================
AUTO-CLOSE RESOLVED TICKETS (after 24 hours)
======================================================================

Found 3 ticket(s) to auto-close:

  • Ticket #123: "Problem z drukarką" (resolved 26.5h ago by agent_piotr)
    ✅ Closed
  • Ticket #124: "Błąd systemu" (resolved 48.2h ago by agent_anna)
    ✅ Closed
  • Ticket #125: "Prośba o dostęp" (resolved 25.0h ago by unassigned)
    ✅ Closed

======================================================================
✅ Successfully closed: 3
======================================================================
```

## Logi

Komenda automatycznie loguje zamknięcia w:
- `ActivityLog` (widoczne w panelu admin)
- Plik `logs/auto_close.log` (jeśli przekierujesz output)

## Powiadomienia Email

Obecnie komenda **NIE wysyła** emaili o automatycznym zamknięciu. 

Jeśli chcesz dodać powiadomienia, możesz zmodyfikować kod w `auto_close_tickets.py` dodając:
```python
from crm.services.email_service import EmailNotificationService
EmailNotificationService.notify_ticket_stakeholders('closed', ticket, triggered_by=None)
```

## Testowanie przed wdrożeniem

1. **Przygotuj testowe dane:**
   ```python
   python manage.py shell
   ```
   
   Następnie w konsoli Python:
   ```python
   from django.utils import timezone
   from datetime import timedelta
   from crm.models import Ticket
   
   # Znajdź ticket do testu
   ticket = Ticket.objects.filter(status='resolved').first()
   
   # Ustaw resolved_at na 25 godzin temu
   ticket.resolved_at = timezone.now() - timedelta(hours=25)
   ticket.save()
   ```

2. **Uruchom dry-run:**
   ```bash
   python manage.py auto_close_tickets --dry-run
   ```

3. **Jeśli wygląda dobrze, uruchom normalnie:**
   ```bash
   python manage.py auto_close_tickets
   ```

4. **Sprawdź logi aktywności w admin panelu**

## Bezpieczeństwo

- ✅ Komenda działa tylko na ticketach w statusie 'resolved'
- ✅ Sprawdza `resolved_at` przed zamknięciem
- ✅ Loguje każde zamknięcie w `ActivityLog`
- ✅ Tryb dry-run pozwala przetestować bez zmian
- ✅ Obsługa błędów - jeśli jeden ticket się nie zamknie, pozostałe będą kontynuowane
