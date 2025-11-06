# Notatki dotyczące migracji

## Zmiany do wykonania:

1. **CalendarNote.is_private** - Dodano pole `is_private` (BooleanField, default=True)
   - Pozwala użytkownikom oznaczać notatki jako prywatne (tylko dla siebie) lub publiczne (dla wszystkich pracowników)
   
2. **API Updates**:
   - `calendar_notes_api` - pokazuje notatki własne + publiczne od innych (nie dla klientów)
   - `calendar_note_create` - obsługuje pole `is_private`
   - `calendar_note_update` - obsługuje pole `is_private`
   
3. **Frontend Updates**:
   - Dodano checkbox "Tylko dla mnie" w formularzach dodawania i edycji notatek
   - Checkbox domyślnie zaznaczony (prywatna notatka)
   - Notatki publiczne mają ikonę użytkowników, prywatne ikonę kłódki
   - Notatki od innych użytkowników pokazują autora i nie mają przycisków edycji/usuwania
   - Notatki z przypisań ticketów (TicketCalendarAssignment.notes) wyświetlane w popupie po kliknięciu na dzień

## Aby zastosować zmiany:

```bash
# Stwórz migracje
python manage.py makemigrations

# Zastosuj migracje
python manage.py migrate
```

## Testy do wykonania:

1. Sprawdź czy checkbox "Tylko dla mnie" jest domyślnie zaznaczony
2. Stwórz notatkę prywatną i sprawdź czy inni użytkownicy jej nie widzą
3. Stwórz notatkę publiczną i sprawdź czy inni pracownicy ją widzą
4. Sprawdź czy klienci widzą tylko swoje notatki (prywatne i publiczne)
5. Sprawdź czy notatki z przypisań ticketów wyświetlają się w popupie kalendarza
6. Sprawdź czy można edytować tylko własne notatki
