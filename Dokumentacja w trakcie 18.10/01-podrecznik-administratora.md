# 📖 Podręcznik Administratora

## Spis Treści
1. [Wprowadzenie](#wprowadzenie)
2. [Logowanie i Pierwsze Kroki](#logowanie-i-pierwsze-kroki)
3. [Zarządzanie Użytkownikami](#zarządzanie-użytkownikami)
4. [Zarządzanie Rolami i Grupami](#zarządzanie-rolami-i-grupami)
5. [Zarządzanie Organizacjami](#zarządzanie-organizacjami)
6. [Konfiguracja Bezpieczeństwa](#konfiguracja-bezpieczeństwa)
7. [Zarządzanie Zgłoszeniami](#zarządzanie-zgłoszeniami)
8. [Konfiguracja Powiadomień Email](#konfiguracja-powiadomień-email)
9. [Zarządzanie Kopiami Zapasowymi](#zarządzanie-kopiami-zapasowymi)
10. [Monitorowanie i Logi](#monitorowanie-i-logi)
11. [Rozwiązywanie Problemów](#rozwiązywanie-problemów)

---

## Wprowadzenie

Podręcznik Administratora zawiera wszystkie informacje potrzebne do zarządzania systemem helpdesk. Jako administrator masz pełny dostęp do wszystkich funkcji systemu i odpowiedzialność za jego prawidłowe działanie.

### Uprawnienia Administratora
- ✅ Pełny dostęp do wszystkich zgłoszeń
- ✅ Zarządzanie użytkownikami i rolami
- ✅ Konfiguracja systemu
- ✅ Zarządzanie organizacjami
- ✅ Dostęp do logów i statystyk
- ✅ Zarządzanie kopiami zapasowymi
- ✅ Konfiguracja powiadomień email

---

## Logowanie i Pierwsze Kroki

### 1. Logowanie do Systemu

1. Otwórz przeglądarkę i przejdź do adresu systemu
2. Kliknij **"Zaloguj się"**
3. Wprowadź swoje dane:
   - **Nazwa użytkownika:** `admin`
   - **Hasło:** `admin123` (domyślne - ZMIEŃ NATYCHMIAST!)

### 2. Pierwsze Logowanie - Konfiguracja 2FA

**UWAGA:** System wymaga skonfigurowania uwierzytelniania dwuskładnikowego (2FA) dla wszystkich użytkowników, w tym administratorów.

1. Po pierwszym logowaniu zostaniesz przekierowany do konfiguracji 2FA
2. Zainstaluj aplikację **Google Authenticator** na telefonie
3. Zeskanuj kod QR wyświetlony na ekranie
4. Wprowadź kod weryfikacyjny z aplikacji
5. Zapisz kod odzyskiwania w bezpiecznym miejscu

### 3. Zmiana Hasła Administratora

**PRIORYTET:** Zmień domyślne hasło natychmiast po pierwszym logowaniu.

1. Kliknij na swoją nazwę użytkownika w prawym górnym rogu
2. Wybierz **"Zmień hasło"**
3. Wprowadź:
   - Aktualne hasło
   - Nowe hasło (minimum 8 znaków, różne od nazwy użytkownika)
   - Potwierdzenie nowego hasła
4. Kliknij **"Zmień hasło"**

---

## Zarządzanie Użytkownikami

### Tworzenie Nowego Użytkownika

1. Przejdź do **Panelu Administratora** → **Użytkownicy**
2. Kliknij **"Dodaj użytkownika"**
3. Wypełnij formularz:
   - **Nazwa użytkownika:** (unikalna)
   - **Email:** (ważny adres email)
   - **Imię i nazwisko**
   - **Hasło:** (silne hasło)
   - **Potwierdzenie hasła**
4. W sekcji **"Profil"**:
   - Wybierz **Rolę** (Admin, Super Agent, Agent, Klient, Viewer)
   - Dodaj **Telefon** (opcjonalnie)
   - Przypisz do **Organizacji**
5. Kliknij **"Zapisz"**

### Edycja Użytkownika

1. Znajdź użytkownika na liście
2. Kliknij **"Edytuj"**
3. Zmień potrzebne dane
4. Kliknij **"Zapisz"**

### Blokowanie/Odblokowanie Konta

#### Blokowanie Konta
1. Przejdź do profilu użytkownika
2. W sekcji **"Blokada konta"**:
   - Zaznacz **"Konto zablokowane"**
   - Podaj powód blokady
3. Kliknij **"Zapisz"**

#### Odblokowanie Konta
1. Przejdź do profilu użytkownika
2. W sekcji **"Blokada konta"**:
   - Odznacz **"Konto zablokowane"**
   - Ustaw **"Nieudane próby logowania"** na 0
3. Kliknij **"Zapisz"**

### Reset Hasła

1. Przejdź do profilu użytkownika
2. Kliknij **"Resetuj hasło"**
3. System wyśle link resetujący na email użytkownika
4. Użytkownik otrzyma instrukcje resetowania hasła

---

## Zarządzanie Rolami i Grupami

### Dostępne Role

1. **Administrator (Admin)**
   - Pełny dostęp do systemu
   - Zarządzanie wszystkimi zgłoszeniami
   - Dostęp do panelu administracyjnego
   - Zarządzanie użytkownikami

2. **Super Agent**
   - Przypisywanie zgłoszeń innym agentom
   - Zarządzanie zespołem
   - Dostęp do statystyk
   - Nie może zarządzać użytkownikami

3. **Agent**
   - Przyjmowanie zgłoszeń do siebie
   - Rozwiązywanie zgłoszeń
   - Dodawanie komentarzy
   - Ograniczony dostęp do statystyk

4. **Klient**
   - Tworzenie zgłoszeń
   - Śledzenie statusu swoich zgłoszeń
   - Dodawanie komentarzy do swoich zgłoszeń

5. **Viewer**
   - Tylko podgląd zgłoszeń
   - Brak możliwości edycji
   - Automatyczne odświeżanie listy

### Zarządzanie Grupami

1. Przejdź do **Panelu Administratora** → **Grupy**
2. Kliknij **"Dodaj grupę"**
3. Wypełnij:
   - **Nazwa grupy**
   - **Rola użytkowników**
4. W sekcji **"Ustawienia"** skonfiguruj:
   - **Zezwól na wiele organizacji**
   - **Pokaż statystyki**
   - **Zwolnij z 2FA** (niezalecane)
   - **Pokaż pasek nawigacyjny**
   - **Poziom dostępu do załączników**
   - **Uprawnienia przypisywania zgłoszeń**
   - **Uprawnienia zarządzania zgłoszeniami**
5. Kliknij **"Zapisz"**

---

## Zarządzanie Organizacjami

### Tworzenie Organizacji

1. Przejdź do **Organizacje** → **Nowa organizacja**
2. Wypełnij formularz:
   - **Nazwa organizacji**
   - **Email kontaktowy**
   - **Telefon**
   - **Strona internetowa**
   - **Adres**
   - **Opis**
3. Kliknij **"Zapisz"**

### Przypisywanie Użytkowników do Organizacji

1. Przejdź do profilu użytkownika
2. W sekcji **"Organizacje"**:
   - Wybierz organizacje z listy
   - Uwaga: Niektórzy użytkownicy mogą należeć tylko do jednej organizacji (zależy od roli)
3. Kliknij **"Zapisz"**

### Edycja Organizacji

1. Przejdź do listy organizacji
2. Kliknij **"Edytuj"** przy wybranej organizacji
3. Zmień potrzebne dane
4. Kliknij **"Zapisz"**

---

## Konfiguracja Bezpieczeństwa

### Uwierzytelnianie Dwuskładnikowe (2FA)

#### Wymagania 2FA
- **Wszyscy użytkownicy** muszą mieć skonfigurowane 2FA
- **Administratorzy** nie są wyłączeni z tego wymogu
- Użytkownicy bez 2FA nie mogą się zalogować

#### Zarządzanie 2FA dla Użytkowników

**Wyłączenie 2FA dla użytkownika:**
1. Przejdź do profilu użytkownika
2. W sekcji **"Uwierzytelnianie dwuskładnikowe"**:
   - Odznacz **"2FA włączone"**
   - Wyczyść **"Klucz tajny 2FA"**
3. Kliknij **"Zapisz"**

**Wygenerowanie nowego kodu odzyskiwania:**
1. Wybierz użytkowników z listy
2. Kliknij **"Wygeneruj nowy kod odzyskiwania 2FA"**
3. Przekaż kod użytkownikowi bezpiecznym kanałem

### Polityka Haseł

System wymusza następujące zasady haseł:
- Minimum 8 znaków
- Nie może być podobne do nazwy użytkownika
- Nie może być na liście najczęstszych haseł
- Nie może składać się tylko z cyfr

### Blokada Kont po Nieudanych Próbach

- **5 nieudanych prób** = automatyczna blokada konta
- Blokada trwa do momentu odblokowania przez administratora
- Wszystkie próby są logowane

---

## Zarządzanie Zgłoszeniami

### Przeglądanie Zgłoszeń

1. Przejdź do **Zgłoszenia**
2. Użyj filtrów do wyszukiwania:
   - Status (Nowe, W trakcie, Rozwiązane, Zamknięte)
   - Priorytet (Niski, Średni, Wysoki, Krytyczny)
   - Kategoria
   - Organizacja
   - Przypisane do
   - Data utworzenia

### Edycja Zgłoszeń

1. Kliknij **"Szczegóły"** przy zgłoszeniu
2. Kliknij **"Edytuj"**
3. Zmień potrzebne dane:
   - Tytuł i opis
   - Status
   - Priorytet
   - Kategorię
   - Przypisanie
4. Kliknij **"Zapisz"**

### Przypisywanie Zgłoszeń

1. Otwórz zgłoszenie
2. W sekcji **"Przypisanie"**:
   - Wybierz agenta z listy
   - Dodaj notatkę (opcjonalnie)
3. Kliknij **"Przypisz"**

### Zarządzanie Komentarzami

1. Otwórz zgłoszenie
2. Przewiń do sekcji **"Komentarze"**
3. Dodaj nowy komentarz
4. Kliknij **"Dodaj komentarz"**

### Zarządzanie Załącznikami

1. Otwórz zgłoszenie
2. W sekcji **"Załączniki"**:
   - Kliknij **"Dodaj załącznik"**
   - Wybierz plik
   - Zaakceptuj regulamin
3. Kliknij **"Prześlij"**

**Uwaga:** Wszystkie załączniki są automatycznie szyfrowane.

---

## Konfiguracja Powiadomień Email

### Ustawienia SMTP

1. Przejdź do **Panelu Administratora** → **Ustawienia**
2. W sekcji **"Email"** skonfiguruj:
   - **Serwer SMTP**
   - **Port** (zwykle 587)
   - **Użyj TLS** (zalecane)
   - **Nazwa użytkownika SMTP**
   - **Hasło SMTP**
   - **Email nadawcy**

### Testowanie Powiadomień

1. Przejdź do **Panelu Administratora** → **Test Email**
2. Wprowadź adres email testowy
3. Kliknij **"Wyślij test"**
4. Sprawdź czy email dotarł

### Szablony Email

System używa następujących szablonów:
- **Rejestracja:** Powitanie nowego użytkownika
- **Weryfikacja:** Potwierdzenie adresu email
- **Reset hasła:** Instrukcje resetowania
- **Nowe zgłoszenie:** Powiadomienie o utworzeniu
- **Zmiana statusu:** Aktualizacja zgłoszenia
- **Nowy komentarz:** Powiadomienie o komentarzu

---

## Zarządzanie Kopiami Zapasowymi

### Automatyczne Kopie Zapasowe

System obsługuje automatyczne kopie zapasowe:

#### Konfiguracja Cron (Linux/macOS)
```bash
# Codziennie o 2:00
0 2 * * * cd /ścieżka/do/projektu && python manage.py backup_database --format=sql --rotate=7

# Codziennie o 2:30 (JSON)
30 2 * * * cd /ścieżka/do/projektu && python manage.py backup_database --format=json --rotate=7 --prefix=json_backup
```

### Ręczne Tworzenie Kopii Zapasowych

```bash
# Kopia SQL (zalecana)
python manage.py backup_database --format=sql

# Kopia JSON (uniwersalna)
python manage.py backup_database --format=json

# Sprawdzenie statusu kopii
python manage.py backup_status
```

### Przywracanie z Kopii Zapasowej

**UWAGA:** Przywracanie zastąpi wszystkie obecne dane!

```bash
# Wyświetl dostępne kopie
python manage.py backup_status

# Przywróć z kopii SQL
python manage.py restore_database backups/database/backup_mysql_YYYYMMDD_HHMMSS.sql.gz

# Przywróć z kopii JSON
python manage.py restore_database backups/database/backup_django_YYYYMMDD_HHMMSS.json.gz
```

---

## Monitorowanie i Logi

### Logi Aktywności

1. Przejdź do **Logi** → **Logi aktywności**
2. Przeglądaj logi według:
   - Typu akcji
   - Użytkownika
   - Daty
   - Adresu IP

### Typy Logowanych Akcji

- **Logowanie/Wylogowanie**
- **Nieudane próby logowania**
- **Blokada/Odblokowanie kont**
- **Tworzenie/edycja zgłoszeń**
- **Zmiana statusów**
- **Dodawanie komentarzy**
- **Zmiana preferencji**
- **Błędy 404/403**

### Czyszczenie Logów

**UWAGA:** Ta operacja jest nieodwracalna!

1. Przejdź do **Logi** → **Wyczyść logi**
2. Wprowadź kod bezpieczeństwa
3. Potwierdź operację

### Monitorowanie Wydajności

1. Przejdź do **Statystyki**
2. Przeglądaj:
   - Liczbę zgłoszeń według statusu
   - Średni czas rozwiązywania
   - Wydajność agentów
   - Rozkład kategorii i priorytetów

---

## Rozwiązywanie Problemów

### Najczęstsze Problemy

#### Problem: Użytkownik nie może się zalogować
**Rozwiązanie:**
1. Sprawdź czy konto nie jest zablokowane
2. Sprawdź logi nieudanych prób logowania
3. Zresetuj hasło użytkownika
4. Sprawdź czy 2FA jest skonfigurowane

#### Problem: Powiadomienia email nie działają
**Rozwiązanie:**
1. Sprawdź konfigurację SMTP
2. Przetestuj połączenie
3. Sprawdź logi serwera
4. Zweryfikuj ustawienia firewall

#### Problem: Załączniki nie są dostępne
**Rozwiązanie:**
1. Sprawdź uprawnienia do plików
2. Zweryfikuj konfigurację MEDIA_ROOT
3. Sprawdź czy szyfrowanie działa poprawnie

#### Problem: System działa wolno
**Rozwiązanie:**
1. Sprawdź wykorzystanie zasobów serwera
2. Zoptymalizuj zapytania do bazy danych
3. Sprawdź logi błędów
4. Rozważ zwiększenie zasobów

### Kontakt z Wsparciem

W przypadku problemów, które nie są opisane w tym przewodniku:
1. Sprawdź logi systemu
2. Zbierz informacje o błędzie
3. Skontaktuj się z zespołem wsparcia technicznego

---

## Najlepsze Praktyki

### Bezpieczeństwo
- ✅ Regularnie zmieniaj hasła administratorów
- ✅ Monitoruj logi aktywności
- ✅ Twórz regularne kopie zapasowe
- ✅ Aktualizuj system regularnie
- ✅ Używaj silnych haseł

### Zarządzanie
- ✅ Regularnie przeglądaj zgłoszenia
- ✅ Monitoruj wydajność agentów
- ✅ Aktualizuj dokumentację
- ✅ Szkol nowych użytkowników
- ✅ Zbieraj feedback od użytkowników

### Konserwacja
- ✅ Regularnie czyść stare logi
- ✅ Monitoruj wykorzystanie dysku
- ✅ Sprawdzaj integralność bazy danych
- ✅ Testuj procedury przywracania
- ✅ Dokumentuj zmiany w systemie

---

*Ostatnia aktualizacja: Styczeń 2025*
