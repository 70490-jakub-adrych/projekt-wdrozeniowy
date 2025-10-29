# Asynchroniczne Wysyłanie Powiadomień Email - 2025-10-29

## Problem
Podczas tworzenia ticketów system wysyłał maile synchronicznie z opóźnieniem 5 sekund między każdym mailem. To powodowało, że im więcej użytkowników (agentów) było w systemie, tym dłużej użytkownik musiał czekać na utworzenie ticketa. Na przykład:
- 8 użytkowników × 5 sekund = 40 sekund oczekiwania na utworzenie ticketa

## Rozwiązanie
Zmodyfikowano system wysyłania powiadomień email, aby działał asynchronicznie:

### Zmiany w `crm/services/email/ticket.py`

1. **Dodano import `threading`**
   ```python
   import threading
   ```

2. **Utworzono nową funkcję pomocniczą `_send_notifications_to_stakeholders`**
   - Funkcja ta wykonuje faktyczne wysyłanie maili
   - Działa w osobnym wątku w tle
   - Pobiera obiekty z bazy danych w kontekście własnego wątku
   - Zachowuje 5-sekundowe opóźnienia między mailami (aby uniknąć spam detection)

3. **Zmodyfikowano funkcję `notify_ticket_stakeholders`**
   - Funkcja teraz zwraca kontrolę natychmiast po określeniu listy odbiorców
   - Uruchamia wątek demon (daemon thread) do wysyłania maili w tle
   - Przekazuje do wątku tylko ID obiektów, nie same obiekty (bezpieczniejsze w kontekście wielowątkowym)

## Korzyści

1. **Natychmiastowa odpowiedź** - ticket tworzy się od razu, użytkownik nie musi czekać
2. **Lepsza wydajność** - frontend dostaje odpowiedź natychmiast
3. **Zachowana funkcjonalność** - maile nadal wysyłane są z 5-sekundowym opóźnieniem, aby uniknąć spam detection
4. **Bezpieczna implementacja**:
   - Używamy daemon threads (automatycznie kończą się gdy główny proces się kończy)
   - Przekazujemy tylko ID do wątków, nie obiekty Django ORM
   - Każdy wątek pobiera swoje dane z bazy danych
   - Pełne logowanie błędów w wątkach

## Techniczne szczegóły

### Wątek demon (daemon thread)
- Wątek jest oznaczony jako `daemon=True`
- Nie blokuje zakończenia procesu Django
- Idealny do zadań typu "fire and forget"

### Thread-safety
- Przekazujemy tylko ID (integers) między wątkami
- Każdy wątek pobiera obiekty z bazy danych niezależnie
- Django ORM jest thread-safe na poziomie połączeń do bazy danych

## Testy

Po wdrożeniu należy zweryfikować:
1. ✅ Ticket tworzy się natychmiast na frontendzie
2. ✅ Maile nadal są wysyłane do wszystkich stakeholders
3. ✅ Opóźnienia między mailami są zachowane
4. ✅ Logi pokazują informacje o wysyłaniu w tle

## Logi

Przed zmianami:
```
INFO Starting notification for created on ticket #156
INFO Sending created notifications to 8 stakeholders
ERROR Failed to send email to superagent@example.com
INFO Ticket created notification sent to pawel.biskupski@betulait.pl
... (każde wywołanie blokuje przez 5 sekund)
INFO Successfully sent 6 notifications out of 8
```

Po zmianach:
```
INFO Starting notification for created on ticket #156
INFO Started background thread to send created notifications to 8 stakeholders
(ticket się już utworzył - użytkownik widzi efekt)

-- w tle --
INFO Sending created notifications to 8 stakeholders
ERROR Failed to send email to superagent@example.com
INFO Ticket created notification sent to pawel.biskupski@betulait.pl
...
INFO Successfully sent 6 notifications out of 8
```

## Pliki zmodyfikowane
- `crm/services/email/ticket.py` - główne zmiany w logice wysyłania maili
