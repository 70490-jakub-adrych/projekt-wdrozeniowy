# Status projektu Helpdesk

## Stan projektu
Projekt jest w fazie początkowej. Zdefiniowano podstawowe założenia i strukturę bazy danych, ale implementacja jeszcze się nie rozpoczęła.

## Zrealizowane elementy
1. Zdefiniowanie założeń projektu
2. Określenie struktury bazy danych
3. Wybór technologii:
   - Framework Django
   - Baza danych SQLite 3
   - Hosting: mydevil.net

## Planowane funkcjonalności

### System zgłoszeń
- [ ] Tworzenie zgłoszeń przez klientów i agentów
- [ ] Edycja zgłoszeń z historią zmian
- [ ] Formularz zgłoszeniowy (tytuł, kategoria, priorytet, opis, załączniki)
- [ ] System statusów zgłoszeń
- [ ] System potwierdzania rozwiązania
- [ ] Automatyczne powiadomienia e-mail
- [ ] Monitor wyświetlający aktualne zgłoszenia
- [ ] Integracja z bramką SMS (faza końcowa)

### Interfejs użytkownika
- [ ] Panel klienta
  - [ ] Dashboard z listą zgłoszeń
  - [ ] Formularz nowego zgłoszenia
  - [ ] System szyfrowania załączników
  - [ ] System komentarzy
- [ ] Panel agenta
  - [ ] Lista zgłoszeń z filtrami
  - [ ] Zarządzanie użytkownikami
  - [ ] Przypisywanie zgłoszeń
- [ ] Panel administratora
  - [ ] Dostęp do raportów

### System logowania
- [ ] Standardowe logowanie (e-mail + hasło)
- [ ] 2FA przez SMS (faza końcowa)
- [ ] System akceptacji kont
- [ ] Logowanie aktywności
- [ ] System blokady konta
- [ ] Formularz rejestracyjny

### Statystyki i raporty
- [ ] Raporty ilościowe
- [ ] Filtrowanie raportów
- [ ] Wizualizacje danych
- [ ] Raporty miesięczne
- [ ] Statystyki agentów

### Bezpieczeństwo
- [ ] Szyfrowanie haseł
- [ ] Kontrola dostępu
- [ ] Historia zmian
- [ ] Automatyczny backup

## Następne kroki
1. Implementacja podstawowej struktury bazy danych
2. Stworzenie modeli Django
3. Implementacja systemu logowania
4. Rozwój interfejsu użytkownika
5. Implementacja systemu zgłoszeń

## Uwagi
- Projekt będzie rozwijany etapowo
- Integracja z bramką SMS zostanie zaimplementowana w końcowej fazie
- Backup będzie wykonywany automatycznie w godzinach 3:00-5:00 