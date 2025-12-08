# Dokumentacja Wdrożeniowa - System Helpdesk

## Spis Treści

### 1. Dokumentacja Funkcjonalna
- 1.1. Cel Systemu i Zakres Działania
- 1.2. Lista Funkcji i Modułów
  - Moduł Zgłoszeń (Tickets)
  - Moduł Komentarzy
  - Moduł Załączników
  - Moduł Organizacji
  - Moduł Użytkowników i Ról
  - Moduł Uwierzytelniania Dwuskładnikowego (2FA)
  - Moduł Powiadomień Email
  - Moduł Kalendarza i Dyżurów
  - Moduł Statystyk
  - Moduł Logów Aktywności
  - Panel Administracyjny
- 1.3. Workflow Zgłoszenia (Krok po Kroku)
  - Scenariusz 1: Klient tworzy zgłoszenie
  - Scenariusz 2: Agent tworzy zgłoszenie dla klienta
  - Scenariusz 3: Viewer przegląda zgłoszenia
- 1.4. Role i Uprawnienia Użytkowników
  - Administrator (Admin)
  - Super Agent
  - Agent
  - Klient
  - Viewer (Przeglądający)
- 1.5. Uprawnienia do Załączników

### 2. Dokumentacja Operacyjna
- 2.1. Ogólne Informacje o Użytkowaniu Systemu w Firmie

### 3. Dokumentacja Rozwojowa
- 3.1. Możliwe Kierunki Rozwoju

### 4. Dokumentacja Techniczna
- 4.1. Struktura Repozytorium
- 4.2. Architektura Backendu i Frontendu
- 4.3. Opis Bazy Danych
- 4.4. Lista Najważniejszych Endpointów API

### 5. Dokumentacja Użytkownika
- 5.1. Instrukcja dla Klienta
  - 5.1.1. Logowanie do Systemu
  - 5.1.2. Tworzenie Nowego Zgłoszenia
  - 5.1.3. Przeglądanie i Filtrowanie Zgłoszeń
  - 5.1.4. Przeglądanie Szczegółów Zgłoszenia
  - 5.1.5. Dodawanie Komentarzy do Zgłoszenia
  - 5.1.6. Potwierdzanie Rozwiązania Zgłoszenia
  - 5.1.7. Zmiana Hasła
  - 5.1.8. Reset Hasła (Gdy Zapomnisz)
- 5.2. Instrukcja dla Agenta i Super Agenta
  - 5.2.1. Logowanie i Panel Główny
  - 5.2.2. Przypisywanie Zgłoszenia do Siebie
  - 5.2.3. Przypisywanie Zgłoszenia do Innego Użytkownika (Tylko Super Agent)
  - 5.2.4. Cofanie Przypisania Zgłoszenia (Agent)
  - 5.2.5. Dodawanie Komentarzy do Zgłoszenia
  - 5.2.6. Oznaczanie Zgłoszenia jako Rozwiązane
  - 5.2.7. Zamykanie Zgłoszenia (Super Agent)
  - 5.2.8. Filtrowanie i Wyszukiwanie Zgłoszeń
  - 5.2.9. Tworzenie Zgłoszenia dla Klienta
  - 5.2.10. Przypisywanie Zgłoszenia do Kalendarza
  - 5.2.11. Zarządzanie Dyżurami (Super Agent)
  - 5.2.12. Przeglądanie Statystyk (Jeśli dostępne)
  - 5.2.13. Aktualizacja Logu Pracy
- 5.3. Instrukcja dla Administratora
  - 5.3.1. Panel Główny Administratora
  - 5.3.2. Edycja Zgłoszeń
  - 5.3.3. Zatwierdzanie Kont Użytkowników
  - 5.3.4. Odblokowywanie Kont Użytkowników
  - 5.3.5. Zarządzanie Użytkownikami przez Panel Admina Django
  - 5.3.6. Zarządzanie Organizacjami
  - 5.3.7. Przeglądanie Logów Aktywności
  - 5.3.8. Zarządzanie 2FA dla Użytkowników
  - 5.3.9. Generowanie Raportów Statystycznych
  - 5.3.10. Zarządzanie Grupami i Uprawnieniami
- 5.4. Instrukcja dla Viewera (Przeglądającego)
  - 5.4.1. Logowanie i Dostęp
  - 5.4.2. Przeglądanie Listy Zgłoszeń
  - 5.4.3. Ograniczenia Viewera
  - 5.4.4. Wylogowanie

### 6. Dokumentacja Wdrożeniowa
- 6.1. Stan Obecny Systemu w Firmie
- 6.2. Najważniejsze Funkcje Działające w Produkcji
- 6.3. Ewentualne Problemy Napotkane Podczas Wdrożenia

### 7. Testy
- 7.1. Lista Testowanych Funkcji
- 7.2. Scenariusze Testowe
- 7.3. Wyniki Testów

### 8. Podsumowanie
- 8.1. Najważniejsze Wnioski Dotyczące Funkcjonowania Systemu
- 8.2. Stabilność Działania
- 8.3. Możliwe Kierunki Rozwoju i Ulepszeń

---

## 1. Dokumentacja Funkcjonalna

### 1.1. Cel Systemu i Zakres Działania

System Helpdesk jest kompleksowym narzędziem do zarządzania zgłoszeniami IT w firmie. Głównym celem systemu jest:

- Centralizacja obsługi zgłoszeń technicznych od klientów i pracowników
- Automatyzacja przepływu pracy związanej z rozwiązywaniem problemów IT
- Śledzenie statusu zgłoszeń od momentu utworzenia do zamknięcia
- Zarządzanie zasobami ludzkimi poprzez przypisywanie zgłoszeń do odpowiednich agentów
- Generowanie statystyk i raportów dotyczących efektywności obsługi zgłoszeń
- Zapewnienie bezpieczeństwa danych poprzez szyfrowanie załączników i uwierzytelnianie dwuskładnikowe

System działa w środowisku produkcyjnym i obsługuje wszystkich użytkowników firmy, w tym klientów zewnętrznych, agentów wsparcia technicznego, superagentów oraz administratorów.

### 1.2. Lista Funkcji i Modułów

#### Moduł Zgłoszeń (Tickets)
- **Tworzenie zgłoszeń**: Użytkownicy mogą tworzyć nowe zgłoszenia z opisem problemu, priorytetem, kategorią i załącznikami
- **Przeglądanie zgłoszeń**: Lista zgłoszeń z możliwością filtrowania po statusie, priorytecie, kategorii, organizacji, dacie
- **Szczegóły zgłoszenia**: Pełne informacje o zgłoszeniu, historia zmian, komentarze, załączniki
- **Edycja zgłoszeń**: Modyfikacja tytułu, opisu, statusu, priorytetu, kategorii, przypisania
- **Zamykanie i rozwiązywanie**: Zmiana statusu na "Rozwiązane" lub "Zamknięte"
- **Przypisywanie**: Przypisywanie zgłoszeń do siebie lub innych użytkowników
- **Automatyczne sugerowanie kategorii**: System analizuje treść zgłoszenia i sugeruje odpowiednią kategorię

#### Moduł Komentarzy
- **Dodawanie komentarzy**: Użytkownicy mogą dodawać komentarze do zgłoszeń
- **Historia komentarzy**: Chronologiczna lista wszystkich komentarzy z informacją o autorze i dacie
- **Powiadomienia**: Automatyczne powiadomienia email o nowych komentarzach

#### Moduł Załączników
- **Dodawanie załączników**: Możliwość dołączania plików do zgłoszeń
- **Szyfrowanie**: Wszystkie załączniki są automatycznie szyfrowane przed zapisem
- **Bezpieczny dostęp**: Kontrola dostępu do załączników na podstawie roli użytkownika i organizacji
- **Regulamin**: Wymagana akceptacja regulaminu przed dodaniem załącznika

#### Moduł Organizacji
- **Zarządzanie organizacjami**: Tworzenie, edycja i przeglądanie organizacji klientów
- **Przypisywanie członków**: Dodawanie użytkowników do organizacji podczas tworzenia lub edycji
- **Informacje kontaktowe**: Przechowywanie danych kontaktowych organizacji (email, telefon, adres)

#### Moduł Użytkowników i Ról
- **Rejestracja**: Nowi użytkownicy mogą się rejestrować w systemie
- **Weryfikacja email**: Wymagana weryfikacja adresu email poprzez kod weryfikacyjny
- **Zatwierdzanie kont**: Administratorzy zatwierdzają nowe konta użytkowników
- **Zarządzanie rolami**: Przypisywanie użytkowników do odpowiednich grup (Admin, Super Agent, Agent, Klient, Viewer)
- **Blokada kont**: Automatyczna blokada po 5 nieudanych próbach logowania
- **Odblokowywanie**: Administratorzy mogą odblokowywać konta użytkowników

#### Moduł Uwierzytelniania Dwuskładnikowego (2FA)
- **Konfiguracja 2FA**: Wymagana konfiguracja Google Authenticator dla wszystkich użytkowników
- **Zaufane urządzenia**: Możliwość zapisania do 3 zaufanych urządzeń (na podstawie IP i User-Agent)
- **Kody odzyskiwania**: Generowanie kodów odzyskiwania w przypadku utraty dostępu do aplikacji 2FA
- **Weryfikacja**: Wymagana weryfikacja kodem 2FA przy logowaniu z nowych urządzeń

#### Moduł Powiadomień Email
- **Asynchroniczne wysyłanie**: Powiadomienia wysyłane w tle, nie blokują tworzenia zgłoszeń
- **Typy powiadomień**: 
  - Utworzenie zgłoszenia
  - Przypisanie zgłoszenia
  - Zmiana statusu
  - Nowy komentarz
  - Aktualizacja zgłoszenia
  - Zamknięcie zgłoszenia
  - Zatwierdzenie konta
  - Reset hasła
- **Personalizacja**: Każdy użytkownik może włączyć/wyłączyć poszczególne typy powiadomień

#### Moduł Kalendarza i Dyżurów
- **Przypisywanie do dat**: Możliwość przypisania zgłoszeń do konkretnych dat w kalendarzu
- **Zarządzanie dyżurami**: Automatyczne generowanie i ręczna zmiana dyżurów agentów
- **Notatki kalendarzowe**: Prywatne i publiczne notatki przypisane do dat
- **Widok kalendarza**: Miesięczny widok z przypisaniami i dyżurami

#### Moduł Statystyk
- **Dashboard statystyk**: Przegląd kluczowych metryk dotyczących zgłoszeń
- **Raporty agentów**: Statystyki pracy poszczególnych agentów
- **Raporty organizacji**: Statystyki zgłoszeń dla organizacji
- **Logi pracy**: Śledzenie czasu pracy agentów nad zgłoszeniami
- **Metryki czasu**: Średni czas rozwiązania, średni czas pierwszej odpowiedzi

#### Moduł Logów Aktywności
- **Rejestrowanie działań**: Wszystkie istotne działania użytkowników są logowane
- **Typy akcji**: Logowanie, wylogowanie, tworzenie/edycja/zamykanie zgłoszeń, dodawanie komentarzy, zmiany hasła
- **Informacje o IP**: Każdy log zawiera adres IP użytkownika
- **Przeglądanie logów**: Administratorzy mogą przeglądać historię aktywności
- **Czyszczenie logów**: Możliwość wyczyszczenia starych logów (wymaga kodu bezpieczeństwa)

#### Panel Administracyjny
- **Zarządzanie użytkownikami**: Pełna kontrola nad kontami użytkowników
- **Zarządzanie zgłoszeniami**: Edycja wszystkich zgłoszeń
- **Zarządzanie organizacjami**: Tworzenie i modyfikacja organizacji
- **Zarządzanie grupami**: Konfiguracja uprawnień grup użytkowników
- **Zarządzanie 2FA**: Regenerowanie kodów odzyskiwania, wyłączanie 2FA dla użytkowników
- **Zarządzanie zaufanymi urządzeniami**: Przeglądanie i usuwanie zaufanych urządzeń

### 1.3. Workflow Zgłoszenia (Krok po Kroku)

#### Scenariusz 1: Klient tworzy zgłoszenie

1. **Logowanie**: Klient loguje się do systemu (wymagana weryfikacja email i zatwierdzenie konta)
2. **Weryfikacja 2FA**: Jeśli 2FA jest włączone, klient wprowadza kod z aplikacji Google Authenticator
3. **Utworzenie zgłoszenia**: 
   - Klient wybiera opcję "Utwórz zgłoszenie"
   - Wypełnia formularz: tytuł, opis problemu, kategoria (system może zasugerować kategorię)
   - Opcjonalnie dodaje załączniki (wymagana akceptacja regulaminu)
   - Wybiera priorytet (domyślnie: średni)
4. **Zapisanie**: Zgłoszenie zostaje zapisane ze statusem "Nowe"
5. **Powiadomienia**: System wysyła asynchronicznie powiadomienia email do:
   - Agentów przypisanych do organizacji klienta
   - Superagentów z dostępem do organizacji
   - Administratorów
6. **Przypisanie**: Agent lub superagent przypisuje zgłoszenie do siebie lub innego agenta
7. **Zmiana statusu**: Po przypisaniu, jeśli zgłoszenie zostało utworzone przez agenta z przypisaniem, status automatycznie zmienia się na "W trakcie"
8. **Praca nad zgłoszeniem**: 
   - Agent dodaje komentarze z informacjami o postępach
   - Może aktualizować status, priorytet, kategorię
   - Może dodawać załączniki
9. **Rozwiązanie**: Agent oznacza zgłoszenie jako "Rozwiązane"
10. **Potwierdzenie**: Klient może potwierdzić rozwiązanie lub zgłosić, że problem nadal występuje
11. **Auto-zamknięcie**: Jeśli klient nie zareaguje w ciągu 3 dni roboczych, system automatycznie zamyka zgłoszenie
12. **Zamknięcie**: Zgłoszenie otrzymuje status "Zamknięte" i jest archiwizowane

#### Scenariusz 2: Agent tworzy zgłoszenie dla klienta

1. **Logowanie**: Agent loguje się do systemu
2. **Utworzenie zgłoszenia**: 
   - Agent wybiera organizację klienta
   - Wypełnia formularz zgłoszenia
   - Może od razu przypisać zgłoszenie do siebie lub innego agenta
   - Jeśli przypisze zgłoszenie, status automatycznie ustawia się na "W trakcie"
3. **Powiadomienia**: System wysyła powiadomienia do:
   - Twórcy zgłoszenia (jeśli inny niż agent)
   - Przypisanego agenta
   - Innych agentów w organizacji
4. **Dalszy proces**: Analogicznie jak w scenariuszu 1, od kroku 8

#### Scenariusz 3: Viewer przegląda zgłoszenia

1. **Logowanie**: Viewer loguje się do systemu
2. **Ograniczony dostęp**: Viewer ma dostęp tylko do widoku listy zgłoszeń
3. **Automatyczne odświeżanie**: Lista zgłoszeń odświeża się automatycznie co 15 sekund (AJAX polling)
4. **Tylko do odczytu**: Viewer nie może tworzyć, edytować ani komentować zgłoszeń

### 1.4. Role i Uprawnienia Użytkowników

#### Administrator (Admin)
- **Pełny dostęp**: Wszystkie funkcje systemu
- **Zarządzanie użytkownikami**: Tworzenie, edycja, zatwierdzanie, odblokowywanie kont
- **Zarządzanie organizacjami**: Pełna kontrola nad organizacjami
- **Zarządzanie zgłoszeniami**: Może edytować wszystkie zgłoszenia
- **Przeglądanie logów**: Dostęp do wszystkich logów aktywności
- **Zarządzanie grupami**: Konfiguracja uprawnień grup
- **Statystyki**: Dostęp do wszystkich statystyk
- **Panel administracyjny Django**: Pełny dostęp do panelu admina
- **Ograniczenia**: Nie może przypisywać zgłoszeń do siebie ani innych (tylko edycja)

#### Super Agent
- **Zarządzanie zgłoszeniami**: Może edytować zgłoszenia w swoich organizacjach
- **Przypisywanie**: Może przypisywać zgłoszenia innym użytkownikom w organizacji
- **Przepisywanie**: Może zmieniać przypisanie już przypisanych zgłoszeń
- **Zamykanie**: Może zamykać dowolne zgłoszenia w swoich organizacjach
- **Zarządzanie organizacjami**: Może tworzyć i edytować organizacje
- **Zatwierdzanie kont**: Może zatwierdzać konta użytkowników
- **Statystyki**: Dostęp do statystyk swoich organizacji
- **Ograniczenia**: Nie może przypisywać zgłoszeń do siebie, nie ma dostępu do panelu admina

#### Agent
- **Przypisywanie do siebie**: Może przypisywać nieprzydzielone zgłoszenia do siebie
- **Cofanie przypisania**: Może cofać przypisanie swoich zgłoszeń
- **Zamykanie przypisanych**: Może oznaczać jako rozwiązane zgłoszenia przypisane do siebie
- **Komentowanie**: Może dodawać komentarze do zgłoszeń w swoich organizacjach
- **Dodawanie załączników**: Może dodawać załączniki do zgłoszeń
- **Ograniczenia**: 
  - Nie może przypisywać zgłoszeń innym użytkownikom
  - Nie może edytować zgłoszeń
  - Nie może zamykać zgłoszeń nieprzypisanych do siebie
  - Widzi tylko zgłoszenia ze swoich organizacji

#### Klient
- **Tworzenie zgłoszeń**: Może tworzyć nowe zgłoszenia w swoich organizacjach
- **Przeglądanie**: Może przeglądać swoje zgłoszenia i zgłoszenia ze swoich organizacji
- **Komentowanie**: Może dodawać komentarze do swoich zgłoszeń
- **Dodawanie załączników**: Może dodawać załączniki do swoich zgłoszeń
- **Potwierdzanie rozwiązania**: Może potwierdzać lub odrzucać rozwiązania
- **Ograniczenia**: 
  - Nie może edytować zgłoszeń
  - Nie może zmieniać statusu
  - Nie może przypisywać zgłoszeń
  - Widzi tylko swoje zgłoszenia i zgłoszenia ze swoich organizacji

#### Viewer (Przeglądający)
- **Tylko odczyt**: Może tylko przeglądać listę zgłoszeń
- **Automatyczne odświeżanie**: Lista odświeża się co 15 sekund
- **Ograniczenia**: 
  - Nie może tworzyć, edytować ani komentować zgłoszeń
  - Nie ma dostępu do innych modułów systemu
  - Dostęp tylko do widoku listy zgłoszeń

### 1.5. Uprawnienia do Załączników

System kontroluje dostęp do załączników na podstawie roli użytkownika:

- **Własne załączniki**: Użytkownicy widzą tylko załączniki, które sami dodali
- **Załączniki organizacji**: Agenci widzą załączniki dodane przez innych użytkowników w tej samej organizacji
- **Wszystkie załączniki**: Administratorzy i Super Agenci widzą wszystkie załączniki

## 2. Dokumentacja Operacyjna

### 2.1. Ogólne Informacje o Użytkowaniu Systemu w Firmie

System Helpdesk jest głównym narzędziem obsługi zgłoszeń IT w firmie. Wszystkie problemy techniczne, prośby o wsparcie oraz zgłoszenia dotyczące infrastruktury IT są obsługiwane przez ten system.

**Codzienne użytkowanie:**
- Klienci i pracownicy tworzą zgłoszenia poprzez interfejs webowy
- Agenci wsparcia technicznego monitorują nowe zgłoszenia i przypisują je do siebie
- Super Agenci zarządzają przepływem pracy i przypisują zgłoszenia do odpowiednich agentów
- Administratorzy nadzorują cały system i zarządzają użytkownikami

**Procedury utrzymania:**
- System automatycznie zamyka rozwiązane zgłoszenia po 3 dniach roboczych bez odpowiedzi klienta
- Codziennie o godzinie 2:00 rano uruchamia się automatyczne zadanie zamykania zgłoszeń
- Kopie zapasowe bazy danych są tworzone automatycznie zgodnie z harmonogramem
- Logi aktywności są przechowywane w systemie i mogą być przeglądane przez administratorów

**Wsparcie IT:**
- W przypadku problemów technicznych z systemem, należy skontaktować się z działem IT
- Administratorzy systemu mogą odblokowywać konta użytkowników i resetować hasła
- W przypadku utraty dostępu do 2FA, administrator może wygenerować nowy kod odzyskiwania

## 3. Dokumentacja Rozwojowa

### 3.1. Możliwe Kierunki Rozwoju

System został zaprojektowany z myślą o możliwości rozbudowy. Poniżej przedstawiono potencjalne kierunki rozwoju:

**Integracje zewnętrzne:**
- Integracja z systemami monitoringu infrastruktury IT
- Integracja z systemami zarządzania zasobami (CMDB)
- Integracja z systemami komunikacji (Slack, Microsoft Teams)
- API REST dla integracji z innymi systemami

**Rozszerzenie funkcjonalności:**
- System oceny satysfakcji klientów po zamknięciu zgłoszenia
- Szablony zgłoszeń dla często występujących problemów
- Automatyczne kategoryzowanie zgłoszeń z wykorzystaniem uczenia maszynowego
- Rozbudowany system SLA z alertami
- Integracja z systemami ticketingowymi zewnętrznymi

**Ulepszenia interfejsu:**
- Aplikacja mobilna dla agentów
- Powiadomienia push
- Zaawansowane filtry i wyszukiwanie
- Eksport raportów do różnych formatów (PDF, Excel, CSV)

**Bezpieczeństwo:**
- Integracja z systemami SSO (Single Sign-On)
- Rozszerzenie logowania dwuskładnikowego o dodatkowe metody
- Zaawansowane audyty bezpieczeństwa

## 4. Dokumentacja Techniczna

### 4.1. Struktura Repozytorium

Główne foldery i ich funkcje:

**projekt_wdrozeniowy/**
- Główny folder projektu Django zawierający konfigurację aplikacji
- `settings.py`: Główne ustawienia aplikacji (baza danych, email, bezpieczeństwo)
- `urls.py`: Główny plik routingu URL
- `wsgi.py`: Konfiguracja WSGI dla serwera produkcyjnego

**crm/**
- Główna aplikacja Django zawierająca całą logikę biznesową
- `models.py`: Modele danych (UserProfile, Ticket, Organization, itp.)
- `views/`: Moduł widoków podzielony na podmoduły:
  - `tickets/`: Widoki związane ze zgłoszeniami
  - `auth_views.py`: Widoki autentykacji
  - `dashboard_views.py`: Widoki panelu głównego
  - `organization_views.py`: Widoki organizacji
  - `statistics_views.py`: Widoki statystyk
  - `two_factor_views.py`: Widoki 2FA
  - `api_views.py`: Endpointy API
- `forms.py`: Formularze Django
- `admin.py`: Konfiguracja panelu administracyjnego
- `middleware.py`: Middleware Django (kontrola dostępu, weryfikacja email, 2FA)
- `services/email/`: Serwisy email podzielone na moduły:
  - `ticket.py`: Powiadomienia o zgłoszeniach
  - `account.py`: Powiadomienia o kontach
  - `password.py`: Powiadomienia o resetowaniu hasła
  - `verification.py`: Powiadomienia weryfikacyjne
- `management/commands/`: Komendy zarządzania Django:
  - `auto_close_tickets.py`: Automatyczne zamykanie zgłoszeń
  - `backup_database.py`: Tworzenie kopii zapasowych
  - `restore_database.py`: Przywracanie z kopii zapasowej
- `migrations/`: Migracje bazy danych
- `templates/`: Szablony HTML
- `static/`: Pliki statyczne (CSS, JavaScript)
- `utils/`: Narzędzia pomocnicze (np. sugerowanie kategorii)
- `validators.py`: Walidatory formularzy
- `scheduler.py`: Konfiguracja zadań okresowych (APScheduler)

**static/**
- Globalne pliki statyczne (logo, skrypty JavaScript)

**backups/**
- Katalog przechowujący kopie zapasowe bazy danych

### 4.2. Architektura Backendu i Frontendu

**Backend:**
- Framework: Django 4.2.22
- Architektura: Model-View-Template (MVT)
- Baza danych: MySQL w produkcji, SQLite w rozwoju
- Scheduler: APScheduler do zadań okresowych
- Email: Asynchroniczne wysyłanie poprzez threading
- Szyfrowanie: Biblioteka cryptography (Fernet) do szyfrowania załączników
- Uwierzytelnianie: Django Authentication + django-otp dla 2FA

**Frontend:**
- Framework: Django Templates
- CSS Framework: Bootstrap 4
- JavaScript: Vanilla JavaScript z AJAX
- Formularze: django-crispy-forms z crispy-bootstrap4
- Responsywność: Bootstrap zapewnia responsywny design
- Automatyczne odświeżanie: AJAX polling dla widoku Viewer (co 15 sekund)

**Komunikacja:**
- Synchronous: Standardowe żądania HTTP dla operacji CRUD
- Asynchronous: Threading dla powiadomień email
- AJAX: Endpointy API dla dynamicznych aktualizacji (lista zgłoszeń, informacje kontaktowe)

### 4.3. Opis Bazy Danych

Główne tabele i ich pola:

**auth_user** (standardowa tabela Django)
- `id`: Identyfikator użytkownika
- `username`: Nazwa użytkownika
- `email`: Adres email
- `first_name`, `last_name`: Imię i nazwisko
- `is_active`, `is_staff`, `is_superuser`: Flagi uprawnień
- `date_joined`, `last_login`: Daty rejestracji i ostatniego logowania

**crm_userprofile**
- `id`: Identyfikator profilu
- `user_id`: Klucz obcy do auth_user
- `role`: Rola użytkownika (admin, superagent, agent, client, viewer)
- `phone`: Numer telefonu
- `is_approved`: Czy konto jest zatwierdzone
- `email_verified`: Czy email jest zweryfikowany
- `approved_by_id`: Kto zatwierdził konto
- `approved_at`: Data zatwierdzenia
- `failed_login_attempts`: Liczba nieudanych prób logowania
- `is_locked`: Czy konto jest zablokowane
- `locked_at`: Data blokady
- `ga_enabled`: Czy 2FA jest włączone
- `ga_secret_key`: Klucz tajny 2FA
- `ga_recovery_hash`: Hash kodu odzyskiwania 2FA

**crm_organization**
- `id`: Identyfikator organizacji
- `name`: Nazwa organizacji
- `email`: Email kontaktowy
- `phone`: Telefon kontaktowy
- `website`: Strona internetowa
- `address`: Adres
- `description`: Opis
- `created_at`, `updated_at`: Daty utworzenia i aktualizacji

**crm_ticket**
- `id`: Identyfikator zgłoszenia
- `title`: Tytuł zgłoszenia
- `description`: Opis problemu
- `status`: Status (new, in_progress, unresolved, resolved, closed)
- `priority`: Priorytet (low, medium, high, critical)
- `category`: Kategoria (hardware, software, network, account, other)
- `created_by_id`: Kto utworzył zgłoszenie
- `assigned_to_id`: Do kogo jest przypisane
- `organization_id`: Organizacja zgłoszenia
- `created_at`, `updated_at`: Daty utworzenia i aktualizacji
- `resolved_at`, `closed_at`: Daty rozwiązania i zamknięcia
- `actual_resolution_time`: Rzeczywisty czas wykonania w godzinach
- `on_duty`: Czy zgłoszenie jest związane z dyżurem
- `has_contact_person`: Czy jest osoba do kontaktu
- `contact_person_first_name`, `contact_person_last_name`: Dane osoby do kontaktu
- `contact_person_phone`: Telefon osoby do kontaktu

**crm_ticketcomment**
- `id`: Identyfikator komentarza
- `ticket_id`: Klucz obcy do zgłoszenia
- `author_id`: Autor komentarza
- `content`: Treść komentarza
- `created_at`: Data utworzenia

**crm_ticketattachment**
- `id`: Identyfikator załącznika
- `ticket_id`: Klucz obcy do zgłoszenia
- `file`: Ścieżka do pliku (szyfrowanego)
- `filename`: Nazwa pliku
- `uploaded_by_id`: Kto dodał załącznik
- `uploaded_at`: Data dodania
- `encryption_key`: Klucz szyfrowania (binarny)
- `accepted_policy`: Czy zaakceptowano regulamin

**crm_activitylog**
- `id`: Identyfikator logu
- `user_id`: Użytkownik (może być NULL)
- `action_type`: Typ akcji (login, ticket_created, ticket_updated, itp.)
- `ticket_id`: Zgłoszenie (może być NULL)
- `description`: Opis akcji
- `ip_address`: Adres IP użytkownika
- `created_at`: Data i czas akcji

**crm_trusteddevice**
- `id`: Identyfikator urządzenia
- `user_id`: Użytkownik
- `ip_address`: Adres IP urządzenia
- `device_fingerprint`: Odcisk urządzenia (User-Agent)
- `trusted_until`: Data wygaśnięcia zaufania
- `created_at`, `last_used`: Daty utworzenia i ostatniego użycia

**crm_ticketcalendarassignment**
- `id`: Identyfikator przypisania
- `ticket_id`: Zgłoszenie
- `assigned_to_id`: Do kogo przypisane
- `assigned_date`: Data przypisania
- `assigned_by_id`: Kto przypisał
- `notes`: Notatki
- `created_at`: Data utworzenia

**crm_calendarduty**
- `id`: Identyfikator dyżuru
- `assigned_to_id`: Kto jest na dyżurze
- `duty_date`: Data dyżuru (unikalna)
- `created_by_id`: Kto utworzył dyżur
- `notes`: Notatki
- `created_at`, `updated_at`: Daty

**crm_calendarnote**
- `id`: Identyfikator notatki
- `user_id`: Właściciel notatki
- `date`: Data notatki
- `title`: Tytuł
- `content`: Treść
- `is_private`: Czy notatka jest prywatna
- `created_at`, `updated_at`: Daty

**crm_emailverification**
- `id`: Identyfikator weryfikacji
- `user_id`: Użytkownik (unikalny)
- `verification_code`: Kod weryfikacyjny (6 cyfr)
- `is_verified`: Czy zweryfikowany
- `created_at`, `verified_at`: Daty

**crm_emailnotificationsettings**
- `id`: Identyfikator ustawień
- `user_id`: Użytkownik (unikalny)
- Flagi powiadomień dla różnych typów zdarzeń (notify_ticket_created, notify_ticket_assigned, itp.)
- `created_at`, `updated_at`: Daty

**crm_ticketstatistics**
- `id`: Identyfikator statystyki
- `period_type`: Typ okresu (day, week, month, year)
- `period_start`, `period_end`: Daty okresu
- `organization_id`, `agent_id`: Opcjonalne filtry
- `tickets_opened`, `tickets_closed`, `tickets_resolved`: Liczniki
- `avg_resolution_time`, `avg_first_response_time`, `avg_agent_work_time`: Średnie czasy
- `priority_distribution`, `category_distribution`: Rozkłady (JSON)
- `satisfaction_score`, `sla_compliance`: Wskaźniki wydajności

**crm_agentworklog**
- `id`: Identyfikator logu pracy
- `agent_id`: Agent
- `ticket_id`: Zgłoszenie
- `start_time`, `end_time`: Czas rozpoczęcia i zakończenia pracy
- `work_time_minutes`: Obliczony czas pracy w minutach
- `notes`: Notatki

**crm_groupsettings**
- `id`: Identyfikator ustawień
- `group_id`: Grupa (unikalna)
- `allow_multiple_organizations`: Czy pozwolić na wiele organizacji
- `show_statistics`: Czy pokazywać statystyki
- `exempt_from_2fa`: Czy zwolnić z 2FA
- `show_navbar`: Czy pokazywać pasek nawigacyjny
- `attachments_access_level`: Poziom dostępu do załączników
- Flagi uprawnień do przypisywania i zarządzania zgłoszeniami

### 4.4. Lista Najważniejszych Endpointów API

**Endpointy autentykacji:**
- `POST /login/` - Logowanie użytkownika
- `POST /logout/` - Wylogowanie
- `POST /register/` - Rejestracja nowego użytkownika
- `POST /verify-email/` - Weryfikacja adresu email
- `POST /password_reset/` - Reset hasła
- `POST /2fa/verify/` - Weryfikacja kodu 2FA
- `POST /2fa/setup/` - Konfiguracja 2FA

**Endpointy zgłoszeń:**
- `GET /tickets/` - Lista zgłoszeń (z filtrowaniem)
- `POST /tickets/create/` - Utworzenie nowego zgłoszenia
- `GET /tickets/<id>/` - Szczegóły zgłoszenia
- `POST /tickets/<id>/update/` - Aktualizacja zgłoszenia
- `POST /tickets/<id>/assign/` - Przypisanie zgłoszenia do siebie
- `POST /tickets/<id>/assign-to-other/` - Przypisanie do innego użytkownika
- `POST /tickets/<id>/unassign/` - Cofnięcie przypisania
- `POST /tickets/<id>/close/` - Zamknięcie zgłoszenia
- `POST /tickets/<id>/reopen/` - Ponowne otwarcie zgłoszenia
- `POST /tickets/<id>/mark-resolved/` - Oznaczenie jako rozwiązane
- `POST /tickets/<id>/confirm-solution/` - Potwierdzenie rozwiązania przez klienta

**Endpointy komentarzy:**
- Komentarze są dodawane poprzez formularz w szczegółach zgłoszenia (POST do `/tickets/<id>/`)

**Endpointy załączników:**
- `GET /secure-file/<attachment_id>/` - Pobranie załącznika (z deszyfrowaniem)
- Załączniki są dodawane podczas tworzenia/edycji zgłoszenia

**Endpointy organizacji:**
- `GET /organizations/` - Lista organizacji
- `POST /organizations/create/` - Utworzenie organizacji
- `GET /organizations/<id>/` - Szczegóły organizacji
- `POST /organizations/<id>/update/` - Aktualizacja organizacji

**Endpointy API (AJAX):**
- `GET /api/user-contact/<user_id>/` - Informacje kontaktowe użytkownika
  - Zwraca: `{username, full_name, email, phone, role, organizations}`
- `GET /api/agent-tickets/<agent_id>/` - Lista zgłoszeń agenta
- `POST /api/toggle-theme/` - Przełączenie motywu (jasny/ciemny)
- `GET /api/calendar-notes/` - Lista notatek kalendarzowych
- `POST /api/calendar-notes/create/` - Utworzenie notatki
- `POST /api/calendar-notes/<id>/update/` - Aktualizacja notatki
- `DELETE /api/calendar-notes/<id>/delete/` - Usunięcie notatki
- `GET /get_tickets_update/` - Aktualizacja listy zgłoszeń (dla Viewer)

**Endpointy kalendarza:**
- `POST /tickets/<ticket_id>/assign-to-calendar/` - Przypisanie zgłoszenia do daty
- `GET /calendar/assignments/` - Lista przypisań kalendarzowych
- `POST /calendar/generate-duties/` - Generowanie dyżurów
- `POST /calendar/change-duty/` - Zmiana dyżuru

**Endpointy statystyk:**
- `GET /statistics/` - Dashboard statystyk
- `POST /statistics/update-work-log/` - Aktualizacja logu pracy
- `GET /statistics/generate-report/` - Generowanie raportu
- `GET /statistics/organization-report/` - Raport organizacji

**Endpointy administracyjne:**
- `GET /approvals/` - Lista oczekujących zatwierdzeń
- `POST /approvals/<user_id>/approve/` - Zatwierdzenie użytkownika
- `POST /approvals/<user_id>/reject/` - Odrzucenie użytkownika
- `POST /approvals/<user_id>/unlock/` - Odblokowanie konta
- `GET /logs/` - Lista logów aktywności
- `GET /logs/<log_id>/` - Szczegóły logu
- `POST /logs/wipe/` - Wyczyszczenie logów (wymaga kodu bezpieczeństwa)

**Przykładowe odpowiedzi API:**

`GET /api/user-contact/123/`:
```json
{
  "success": true,
  "username": "jan_kowalski",
  "full_name": "Jan Kowalski",
  "email": "jan.kowalski@example.com",
  "phone": "+48 12 345 67 89",
  "role": "Agent",
  "organizations": ["Firma ABC Sp. z o.o."]
}
```

`GET /get_tickets_update/` (dla Viewer):
```json
{
  "tickets": [
    {
      "id": 456,
      "title": "Problem z drukarką",
      "status": "in_progress",
      "priority": "high",
      "created_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

## 5. Dokumentacja Użytkownika

### 5.1. Instrukcja dla Klienta

#### 5.1.1. Logowanie do Systemu

1. Otwórz przeglądarkę internetową i przejdź na adres systemu helpdesk
2. Na stronie logowania wprowadź:
   - **Nazwa użytkownika**: Twój login przypisany przez administratora
   - **Hasło**: Twoje hasło do systemu
3. Kliknij przycisk "Zaloguj"
4. Jeśli masz włączone uwierzytelnianie dwuskładnikowe (2FA):
   - Otwórz aplikację Google Authenticator na telefonie
   - Wprowadź 6-cyfrowy kod wyświetlany w aplikacji
   - Kliknij "Weryfikuj"
5. Po pomyślnym zalogowaniu zostaniesz przekierowany do panelu głównego

#### 5.1.2. Tworzenie Nowego Zgłoszenia

1. Z panelu głównego kliknij przycisk "Utwórz zgłoszenie" w menu lub na karcie dashboardu
2. Wypełnij formularz zgłoszenia:
   - **Tytuł zgłoszenia**: Wprowadź krótki, opisowy tytuł problemu (np. "Nie działa drukarka w biurze na pierwszym piętrze")
   - **Opis problemu**: Szczegółowo opisz:
     - Co dokładnie nie działa
     - Kiedy problem wystąpił
     - Jakie kroki wykonałeś przed zgłoszeniem
     - Jakie komunikaty błędów widzisz (jeśli występują)
     - Oczekiwany rezultat
   - **Kategoria**: Wybierz z listy rozwijanej:
     - Sprzęt (problemy z drukarkami, komputerami, monitorami)
     - Oprogramowanie (problemy z aplikacjami, systemem operacyjnym)
     - Sieć (problemy z połączeniem internetowym, dostępem do sieci)
     - Konto (problemy z logowaniem, uprawnieniami)
     - Inne (problemy niepasujące do powyższych kategorii)
     - *Uwaga: System może automatycznie zasugerować kategorię na podstawie treści tytułu i opisu*
   - **Priorytet**: Wybierz priorytet zgłoszenia:
     - Niski (problem nie wpływa na pracę)
     - Średni (problem wpływa częściowo na pracę)
     - Wysoki (problem znacząco utrudnia pracę)
     - Krytyczny (problem uniemożliwia pracę)
3. **Dodawanie załączników** (opcjonalnie):
   - Kliknij przycisk "Wybierz pliki" lub przeciągnij pliki do obszaru załączników
   - Zaakceptuj regulamin dotyczący przetwarzania danych (zaznacz checkbox)
   - Możesz dodać wiele plików jednocześnie
4. Kliknij przycisk "Utwórz zgłoszenie"
5. System wyświetli komunikat potwierdzający utworzenie zgłoszenia
6. Otrzymasz powiadomienie email na adres przypisany do konta

#### 5.1.3. Przeglądanie i Filtrowanie Zgłoszeń

1. Z menu głównego wybierz "Zgłoszenia"
2. Zobaczysz listę wszystkich swoich zgłoszeń oraz zgłoszeń z organizacji, do której należysz
3. **Filtrowanie zgłoszeń:**
   - **Status**: Wybierz jeden lub więcej statusów (Nowe, W trakcie, Nierozwiązany, Rozwiązane, Zamknięte)
   - **Priorytet**: Wybierz priorytety do wyświetlenia
   - **Kategoria**: Filtruj po kategoriach
   - **Data utworzenia**: Wprowadź zakres dat (od-do) w kalendarzu
   - **Tytuł**: Wprowadź fragment tytułu do wyszukania
   - **Organizacja**: Wybierz organizację (jeśli należysz do wielu)
   - Kliknij "Filtruj" aby zastosować filtry
4. **Sortowanie:**
   - Wybierz kryterium sortowania z listy rozwijanej:
     - Data utworzenia (najnowsze/najstarsze)
     - Data aktualizacji
     - Priorytet (od najwyższego)
     - Status
5. **Domyślnie zamknięte zgłoszenia są ukryte** - możesz je pokazać odznaczając opcję "Ukryj zamknięte"

#### 5.1.4. Przeglądanie Szczegółów Zgłoszenia

1. Z listy zgłoszeń kliknij na tytuł wybranego zgłoszenia
2. Zobaczysz pełne informacje o zgłoszeniu:
   - Tytuł i szczegółowy opis
   - Aktualny status z kolorowym oznaczeniem
   - Priorytet
   - Kategoria
   - Data utworzenia i ostatniej aktualizacji
   - Informacja o tym, kto utworzył zgłoszenie
   - Informacja o agencie przypisanym do zgłoszenia (jeśli przypisane)
   - Organizacja zgłoszenia
3. **Sekcja komentarzy:**
   - Zobaczysz wszystkie komentarze w kolejności chronologicznej (najstarsze na górze)
   - Każdy komentarz zawiera:
     - Autora komentarza
     - Datę i godzinę dodania
     - Treść komentarza
   - Aby dodać nowy komentarz:
     - Wprowadź treść komentarza w polu tekstowym na dole sekcji
     - Kliknij przycisk "Dodaj komentarz"
4. **Sekcja załączników:**
   - Zobaczysz listę wszystkich załączników z nazwami plików
   - Aby pobrać załącznik, kliknij na jego nazwę
   - Aby dodać nowy załącznik:
     - Kliknij "Wybierz pliki" lub przeciągnij plik
     - Zaakceptuj regulamin
     - Kliknij "Dodaj załącznik"

#### 5.1.5. Dodawanie Komentarzy do Zgłoszenia

1. Otwórz szczegóły zgłoszenia
2. Przewiń do sekcji "Komentarze"
3. W polu tekstowym na dole sekcji wprowadź treść komentarza
4. Możesz dodać:
   - Dodatkowe informacje o problemie
   - Pytania do agenta
   - Potwierdzenie otrzymania odpowiedzi
   - Informacje o zmianach w sytuacji
5. Kliknij przycisk "Dodaj komentarz"
6. Komentarz zostanie dodany i widoczny dla wszystkich uprawnionych użytkowników
7. Otrzymasz powiadomienie email o odpowiedzi agenta (jeśli włączone w ustawieniach)

#### 5.1.6. Potwierdzanie Rozwiązania Zgłoszenia

1. Gdy zgłoszenie ma status "Rozwiązane", zobaczysz przycisk "Potwierdź rozwiązanie"
2. Kliknij na przycisk
3. Wybierz jedną z opcji:
   - **Problem rozwiązany**: Potwierdź, że problem został rozwiązany i możesz zamknąć zgłoszenie
   - **Problem nadal występuje**: Zgłoś, że problem nie został rozwiązany - zgłoszenie wróci do statusu "W trakcie"
4. Po potwierdzeniu rozwiązania zgłoszenie zostanie automatycznie zamknięte po 3 dniach roboczych, jeśli nie dodasz nowych komentarzy

#### 5.1.7. Zmiana Hasła

1. Z menu użytkownika (ikonka w prawym górnym rogu) wybierz "Zmiana hasła"
2. Wprowadź:
   - **Aktualne hasło**: Twoje obecne hasło
   - **Nowe hasło**: Nowe hasło (minimum 8 znaków)
   - **Potwierdź nowe hasło**: Powtórz nowe hasło
3. Kliknij "Zmień hasło"
4. Otrzymasz powiadomienie email o zmianie hasła

#### 5.1.8. Reset Hasła (Gdy Zapomnisz)

1. Na stronie logowania kliknij "Nie pamiętasz hasła?"
2. Wprowadź adres email przypisany do Twojego konta
3. Kliknij "Wyślij link resetujący"
4. Sprawdź skrzynkę email i kliknij w link resetujący hasło
5. Wprowadź nowe hasło i potwierdź je
6. Zaloguj się używając nowego hasła

### 5.2. Instrukcja dla Agenta i Super Agenta

#### 5.2.1. Logowanie i Panel Główny

1. Zaloguj się do systemu używając swoich danych dostępowych
2. Po zalogowaniu zobaczysz panel główny z:
   - **Statystykami zgłoszeń**: Liczba zgłoszeń w poszczególnych statusach (Nowe, W trakcie, Rozwiązane, Zamknięte)
   - **Moje przypisane zgłoszenia**: Lista 5 najnowszych zgłoszeń przypisanych do Ciebie
   - **Nieprzydzielone zgłoszenia**: Lista 5 najnowszych zgłoszeń bez przypisanego agenta z Twoich organizacji
   - **Ostatnio zamknięte**: Lista ostatnio zamkniętych zgłoszeń
   - **Ostatnie aktywności**: Ostatnie działania w systemie

#### 5.2.2. Przypisywanie Zgłoszenia do Siebie

1. Przejdź do sekcji "Zgłoszenia"
2. Znajdź nieprzydzielone zgłoszenie z listy (oznaczone jako "Nieprzydzielone")
3. Kliknij na tytuł zgłoszenia, aby otworzyć szczegóły
4. Kliknij przycisk "Przypisz do mnie" w sekcji akcji
5. Zgłoszenie zostanie przypisane do Ciebie, a status automatycznie zmieni się na "W trakcie" (jeśli było "Nowe")
6. Otrzymasz powiadomienie email o przypisaniu

**Uwaga dla Super Agenta**: Możesz przypisywać zgłoszenia również innym użytkownikom (patrz sekcja 5.2.3)

#### 5.2.3. Przypisywanie Zgłoszenia do Innego Użytkownika (Tylko Super Agent)

1. Otwórz szczegóły zgłoszenia
2. Kliknij przycisk "Przypisz do innego użytkownika"
3. W oknie dialogowym wybierz użytkownika z listy rozwijanej (widzisz tylko użytkowników z Twoich organizacji)
4. Opcjonalnie dodaj notatkę dotyczącą przypisania
5. Kliknij "Przypisz"
6. Wybrany użytkownik otrzyma powiadomienie email o przypisaniu

#### 5.2.4. Cofanie Przypisania Zgłoszenia (Agent)

1. Otwórz szczegóły zgłoszenia przypisanego do Ciebie
2. Kliknij przycisk "Cofnij przypisanie"
3. Potwierdź akcję
4. Zgłoszenie wróci do statusu "Nieprzydzielone"
5. Inni agenci z organizacji będą mogli je przypisać do siebie

#### 5.2.5. Dodawanie Komentarzy do Zgłoszenia

1. Otwórz szczegóły zgłoszenia
2. Przewiń do sekcji "Komentarze"
3. Wprowadź treść komentarza zawierającą:
   - Informacje o podjętych działaniach
   - Postępy w rozwiązaniu problemu
   - Pytania do klienta
   - Instrukcje dla klienta
   - Informacje o potrzebie dodatkowych danych
4. Kliknij "Dodaj komentarz"
5. Komentarz zostanie wysłany, a klient i inni zainteresowani otrzymają powiadomienie email

#### 5.2.6. Oznaczanie Zgłoszenia jako Rozwiązane

1. Po rozwiązaniu problemu otwórz szczegóły zgłoszenia
2. Kliknij przycisk "Oznacz jako rozwiązane"
3. Opcjonalnie dodaj komentarz z informacją o rozwiązaniu
4. Status zgłoszenia zmieni się na "Rozwiązane"
5. Klient otrzyma powiadomienie i będzie mógł potwierdzić rozwiązanie
6. Jeśli klient nie zareaguje w ciągu 3 dni roboczych, zgłoszenie zostanie automatycznie zamknięte

#### 5.2.7. Zamykanie Zgłoszenia (Super Agent)

1. Otwórz szczegóły zgłoszenia
2. Kliknij przycisk "Zamknij zgłoszenie"
3. Potwierdź akcję
4. Zgłoszenie otrzyma status "Zamknięte" i zostanie zarchiwizowane
5. Klient otrzyma powiadomienie email o zamknięciu

#### 5.2.8. Filtrowanie i Wyszukiwanie Zgłoszeń

1. Przejdź do sekcji "Zgłoszenia"
2. Użyj zaawansowanych filtrów:
   - **Status**: Możesz wybrać wiele statusów jednocześnie (Ctrl+klik)
   - **Priorytet**: Filtruj po priorytetach
   - **Kategoria**: Wybierz kategorie
   - **Organizacja**: Wybierz organizację (jeśli masz dostęp do wielu)
   - **Przypisane**: Wybierz "Do mnie" lub "Nieprzydzielone"
   - **Dyżur**: Filtruj zgłoszenia związane z dyżurem
   - **Data utworzenia**: Zakres dat
   - **Tytuł**: Wyszukiwanie po tytule
3. Wybierz sortowanie (data utworzenia, aktualizacji, priorytet)
4. Kliknij "Filtruj" aby zastosować filtry
5. Możesz zapisać preferencje filtrowania - system zapamięta Twoje ustawienia

#### 5.2.9. Tworzenie Zgłoszenia dla Klienta

1. Kliknij "Utwórz zgłoszenie"
2. Wypełnij formularz:
   - **Organizacja**: Wybierz organizację klienta z listy rozwijanej
   - **Tytuł**: Wprowadź tytuł zgłoszenia
   - **Opis**: Szczegółowy opis problemu
   - **Kategoria**: Wybierz kategorię
   - **Priorytet**: Ustaw priorytet
   - **Przypisane do**: Możesz od razu przypisać do siebie lub innego agenta
     - *Uwaga: Jeśli przypiszesz zgłoszenie podczas tworzenia, status automatycznie ustawi się na "W trakcie"*
   - **Data w kalendarzu** (opcjonalnie): Przypisz zgłoszenie do konkretnej daty w kalendarzu
   - **Notatki kalendarzowe** (opcjonalnie): Dodaj notatki do przypisania kalendarzowego
3. Dodaj załączniki jeśli potrzebne
4. Kliknij "Utwórz zgłoszenie"
5. Klient i inni zainteresowani otrzymają powiadomienie email

#### 5.2.10. Przypisywanie Zgłoszenia do Kalendarza

1. Otwórz szczegóły zgłoszenia
2. Kliknij przycisk "Przypisz do kalendarza"
3. W oknie dialogowym:
   - Wybierz datę z kalendarza (tylko dni robocze - weekendy są zablokowane)
   - Wybierz użytkownika, do którego przypisać (domyślnie Ty)
   - Dodaj opcjonalne notatki
4. Kliknij "Przypisz"
5. Zgłoszenie pojawi się w kalendarzu w wybranym dniu

#### 5.2.11. Zarządzanie Dyżurami (Super Agent)

1. Przejdź do sekcji "Kalendarz" (jeśli dostępna)
2. Aby wygenerować dyżury automatycznie:
   - Kliknij "Generuj dyżury"
   - Wybierz zakres dat
   - Wybierz użytkowników do rotacji
   - Kliknij "Generuj"
3. Aby zmienić dyżur ręcznie:
   - Kliknij na datę w kalendarzu
   - Wybierz "Zmień dyżur"
   - Wybierz nowego użytkownika
   - Kliknij "Zapisz"

#### 5.2.12. Przeglądanie Statystyk (Jeśli dostępne)

1. Z menu głównego wybierz "Statystyki"
2. Zobaczysz dashboard z:
   - Liczbą obsłużonych zgłoszeń
   - Średnim czasem rozwiązania
   - Średnim czasem pierwszej odpowiedzi
   - Rozkładem zgłoszeń po kategoriach i priorytetach
3. Możesz filtrować statystyki po:
   - Okresie (dzień, tydzień, miesiąc, rok)
   - Organizacji
   - Dacie
4. Możesz wygenerować raport klikając "Generuj raport"

#### 5.2.13. Aktualizacja Logu Pracy

1. W szczegółach zgłoszenia znajdź sekcję "Log pracy"
2. Kliknij "Rozpocznij pracę" aby rozpocząć śledzenie czasu
3. Po zakończeniu pracy kliknij "Zakończ pracę"
4. System automatycznie obliczy czas poświęcony na zgłoszenie
5. Opcjonalnie dodaj notatki o wykonanej pracy

### 5.3. Instrukcja dla Administratora

#### 5.3.1. Panel Główny Administratora

1. Po zalogowaniu zobaczysz rozszerzony dashboard z:
   - **Statystyki systemowe**: Liczba zgłoszeń we wszystkich statusach
   - **Moje przypisane zgłoszenia**: Zgłoszenia przypisane do Ciebie
   - **Nieprzydzielone zgłoszenia**: Wszystkie nieprzydzielone zgłoszenia w systemie
   - **Zgłoszenia w trakcie**: Lista aktywnych zgłoszeń
   - **Ostatnio zamknięte**: Ostatnio zamknięte zgłoszenia
   - **Ostatnie aktywności**: Wszystkie ostatnie działania w systemie
   - **Oczekujące zatwierdzenia**: Liczba użytkowników oczekujących na zatwierdzenie konta

#### 5.3.2. Edycja Zgłoszeń

1. Przejdź do sekcji "Zgłoszenia"
2. Kliknij na tytuł zgłoszenia, które chcesz edytować
3. Kliknij przycisk "Edytuj" w prawym górnym rogu
4. W formularzu edycji możesz zmienić:
   - **Tytuł**: Zmień tytuł zgłoszenia
   - **Opis**: Zaktualizuj opis problemu
   - **Status**: Zmień status (Nowe, W trakcie, Nierozwiązany, Rozwiązane, Zamknięte)
   - **Priorytet**: Zmień priorytet
   - **Kategoria**: Zmień kategorię
   - **Przypisane do**: Przypisz lub zmień przypisanie do agenta
   - **Organizacja**: Zmień organizację (jeśli potrzebne)
5. Kliknij "Zapisz zmiany"
6. Wszyscy zainteresowani otrzymają powiadomienie email o zmianach

#### 5.3.3. Zatwierdzanie Kont Użytkowników

1. Z menu głównego wybierz "Zatwierdzenia"
2. Zobaczysz listę użytkowników oczekujących na zatwierdzenie
3. Dla każdego użytkownika zobaczysz:
   - Nazwę użytkownika
   - Email
   - Datę rejestracji
   - Status weryfikacji email
   - Organizację (jeśli przypisana)
4. Aby zatwierdzić konto:
   - Kliknij przycisk "Zatwierdź" przy użytkowniku
   - Opcjonalnie wybierz organizację, do której ma być przypisany
   - Kliknij "Potwierdź zatwierdzenie"
5. Aby odrzucić konto:
   - Kliknij przycisk "Odrzuć"
   - Wprowadź powód odrzucenia (opcjonalnie)
   - Kliknij "Potwierdź odrzucenie"
6. Użytkownik otrzyma powiadomienie email o decyzji

#### 5.3.4. Odblokowywanie Kont Użytkowników

1. Przejdź do sekcji "Zatwierdzenia"
2. Znajdź użytkownika z zablokowanym kontem (oznaczone jako "Zablokowane")
3. Kliknij przycisk "Odblokuj" przy użytkowniku
4. Potwierdź akcję
5. Konto zostanie odblokowane, a liczba nieudanych prób logowania zostanie zresetowana
6. Użytkownik otrzyma powiadomienie email o odblokowaniu

#### 5.3.5. Zarządzanie Użytkownikami przez Panel Admina Django

1. Z menu głównego wybierz "Panel Admina" (lub przejdź bezpośrednio do `/admin/`)
2. W sekcji "Użytkownicy" znajdziesz listę wszystkich użytkowników
3. Kliknij na użytkownika, aby edytować:
   - **Podstawowe dane**: Imię, nazwisko, email, status konta
   - **Grupy**: Przypisz użytkownika do grupy (Admin, Superagent, Agent, Klient, Viewer)
   - **Profil użytkownika**: 
     - Rola
     - Telefon
     - Status zatwierdzenia
     - Status weryfikacji email
     - Organizacje (możesz przypisać wiele organizacji)
     - Status 2FA
   - **Zaufane urządzenia**: Przeglądanie i usuwanie zaufanych urządzeń 2FA
4. Kliknij "Zapisz" aby zapisać zmiany

#### 5.3.6. Zarządzanie Organizacjami

1. Z menu głównego wybierz "Organizacje"
2. Zobaczysz listę wszystkich organizacji w systemie
3. **Tworzenie nowej organizacji:**
   - Kliknij przycisk "Utwórz organizację"
   - Wypełnij formularz:
     - Nazwa organizacji
     - Email kontaktowy
     - Telefon kontaktowy (z automatycznym formatowaniem)
     - Strona internetowa
     - Adres
     - Opis
   - **Członkowie organizacji**: Zaznacz checkboxy przy użytkownikach, którzy mają być członkami
   - Kliknij "Utwórz organizację"
4. **Edycja organizacji:**
   - Kliknij na nazwę organizacji
   - Kliknij przycisk "Edytuj"
   - Zmień potrzebne dane
   - Dodaj lub usuń członków organizacji
   - Kliknij "Zapisz zmiany"
5. **Szczegóły organizacji:**
   - Zobaczysz listę wszystkich zgłoszeń organizacji
   - Listę członków organizacji
   - Statystyki zgłoszeń organizacji

#### 5.3.7. Przeglądanie Logów Aktywności

1. Z menu głównego wybierz "Logi"
2. Zobaczysz listę wszystkich działań w systemie z:
   - Typem akcji (logowanie, tworzenie zgłoszenia, itp.)
   - Użytkownikiem, który wykonał akcję
   - Zgłoszeniem (jeśli dotyczy)
   - Opisem akcji
   - Adresem IP
   - Datą i godziną
3. **Filtrowanie logów:**
   - Po użytkowniku: Wybierz użytkownika z listy
   - Po typie akcji: Wybierz typ akcji
   - Po dacie: Wybierz zakres dat
   - Kliknij "Filtruj"
4. **Szczegóły logu:**
   - Kliknij na log, aby zobaczyć szczegółowe informacje
5. **Czyszczenie logów:**
   - Kliknij przycisk "Wyczyść logi"
   - Wprowadź kod bezpieczeństwa (ustawiony w konfiguracji systemu)
   - Wybierz zakres dat do wyczyszczenia
   - Kliknij "Wyczyść"
   - *Uwaga: Ta operacja jest nieodwracalna*

#### 5.3.8. Zarządzanie 2FA dla Użytkowników

1. Przejdź do Panelu Admina Django
2. Wybierz użytkownika
3. W sekcji "Profil użytkownika" zobaczysz:
   - Status 2FA (włączone/wyłączone)
   - Datę włączenia 2FA
   - Datę ostatniego uwierzytelnienia
   - Datę ostatniej generacji kodu odzyskiwania
4. **Regenerowanie kodu odzyskiwania:**
   - W liście użytkowników zaznacz użytkownika
   - Z listy akcji wybierz "Wygeneruj nowy kod odzyskiwania 2FA"
   - Kliknij "Wykonaj"
   - System wyświetli nowy kod odzyskiwania - przekaż go użytkownikowi bezpiecznym kanałem
5. **Wyłączanie 2FA:**
   - Zaznacz użytkownika
   - Z listy akcji wybierz "Wyłącz uwierzytelnianie dwuskładnikowe (2FA)"
   - Kliknij "Wykonaj"
   - 2FA zostanie wyłączone dla użytkownika
6. **Czyszczenie statusu uwierzytelnienia:**
   - Zaznacz użytkownika
   - Z listy akcji wybierz "Wyczyść status uwierzytelnienia 2FA"
   - Użytkownik będzie musiał ponownie wprowadzić kod 2FA przy następnym logowaniu

#### 5.3.9. Generowanie Raportów Statystycznych

1. Przejdź do sekcji "Statystyki"
2. Zobaczysz dashboard z metrykami systemowymi:
   - Liczba zgłoszeń w poszczególnych statusach
   - Średni czas rozwiązania
   - Średni czas pierwszej odpowiedzi
   - Rozkład po kategoriach i priorytetach
   - Statystyki agentów
3. **Filtrowanie statystyk:**
   - Wybierz okres (dzień, tydzień, miesiąc, rok)
   - Wybierz organizację (lub wszystkie)
   - Wybierz agenta (lub wszystkich)
   - Wybierz zakres dat
   - Kliknij "Filtruj"
4. **Generowanie raportu:**
   - Kliknij "Generuj raport"
   - Wybierz format (jeśli dostępny)
   - Raport zostanie wygenerowany i możesz go pobrać
5. **Raport organizacji:**
   - Kliknij "Raport organizacji"
   - Wybierz organizację
   - Wybierz okres
   - Kliknij "Generuj"
   - Zobaczysz szczegółowe statystyki dla wybranej organizacji

#### 5.3.10. Zarządzanie Grupami i Uprawnieniami

1. Przejdź do Panelu Admina Django
2. W sekcji "Grupy" znajdziesz wszystkie grupy użytkowników
3. Kliknij na grupę, aby edytować:
   - **Nazwa grupy**: Nazwa grupy (Admin, Superagent, Agent, Klient, Viewer)
   - **Rola użytkowników**: Rola przypisywana użytkownikom w tej grupie
   - **Ustawienia grupy**:
     - Zezwól na wiele organizacji
     - Pokaż statystyki
     - Zwolnij z 2FA
     - Pokaż pasek nawigacyjny
     - Poziom dostępu do załączników
     - Uprawnienia do przypisywania zgłoszeń
     - Uprawnienia do zarządzania zgłoszeniami
   - **Uprawnienia do widoków**: Wybierz, które widoki są dostępne dla grupy
   - **Uprawnienia Django**: Standardowe uprawnienia Django
4. Kliknij "Zapisz" aby zapisać zmiany

### 5.4. Instrukcja dla Viewera (Przeglądającego)

#### 5.4.1. Logowanie i Dostęp

1. Zaloguj się do systemu używając swoich danych dostępowych
2. Po zalogowaniu zostaniesz automatycznie przekierowany do widoku listy zgłoszeń
3. Viewer ma dostęp **tylko** do widoku listy zgłoszeń - inne sekcje systemu są niedostępne

#### 5.4.2. Przeglądanie Listy Zgłoszeń

1. Zobaczysz listę wszystkich zgłoszeń w systemie z podstawowymi informacjami:
   - Numer zgłoszenia
   - Tytuł
   - Status (z kolorowym oznaczeniem)
   - Priorytet
   - Kategoria
   - Data utworzenia
   - Przypisany agent (jeśli przypisane)
   - Organizacja
2. **Lista odświeża się automatycznie** co 15 sekund - nie musisz ręcznie odświeżać strony
3. Nowe zgłoszenia pojawią się automatycznie na liście

#### 5.4.3. Ograniczenia Viewera

Viewer **nie może**:
- Tworzyć nowych zgłoszeń
- Edytować zgłoszeń
- Dodawać komentarzy
- Przypisywać zgłoszeń
- Zmieniać statusu zgłoszeń
- Dodawać załączników
- Przeglądać szczegółów zgłoszeń (tylko lista)
- Dostępować do innych sekcji systemu (Dashboard, Organizacje, Statystyki, itp.)

Viewer **może tylko**:
- Przeglądać listę zgłoszeń
- Widzieć podstawowe informacje o zgłoszeniach
- Wylogować się z systemu

#### 5.4.4. Wylogowanie

1. Kliknij przycisk "Wyloguj" w prawym górnym rogu
2. Zostaniesz wylogowany z systemu i przekierowany do strony logowania

## 6. Dokumentacja Wdrożeniowa

### 6.1. Stan Obecny Systemu w Firmie

System Helpdesk jest w pełni wdrożony i działa w środowisku produkcyjnym. System obsługuje wszystkich użytkowników firmy, w tym:

- Klientów zewnętrznych korzystających z usług IT
- Pracowników firmy zgłaszających problemy techniczne
- Agentów wsparcia technicznego obsługujących zgłoszenia
- Superagentów zarządzających przepływem pracy
- Administratorów zarządzających systemem

System jest dostępny 24/7 poprzez interfejs webowy. Wszystkie dane są przechowywane w bezpiecznej bazie danych MySQL z regularnymi kopiami zapasowymi.

### 6.2. Najważniejsze Funkcje Działające w Produkcji

**Funkcje podstawowe:**
- ✅ Tworzenie, edycja i zamykanie zgłoszeń
- ✅ System komentarzy i załączników
- ✅ Przypisywanie zgłoszeń do agentów
- ✅ Filtrowanie i sortowanie zgłoszeń
- ✅ Powiadomienia email (asynchroniczne)
- ✅ Automatyczne zamykanie rozwiązanych zgłoszeń po 3 dniach roboczych

**Funkcje bezpieczeństwa:**
- ✅ Weryfikacja email przy rejestracji
- ✅ Zatwierdzanie kont przez administratorów
- ✅ Blokada kont po 5 nieudanych próbach logowania
- ✅ Uwierzytelnianie dwuskładnikowe (2FA) wymagane dla wszystkich użytkowników
- ✅ Zaufane urządzenia (do 3 urządzeń)
- ✅ Szyfrowanie załączników

**Funkcje zaawansowane:**
- ✅ Automatyczne sugerowanie kategorii zgłoszeń
- ✅ Automatyczna zmiana statusu na "W trakcie" przy przypisaniu
- ✅ Kalendarz z przypisaniami i dyżurami
- ✅ Notatki kalendarzowe (prywatne i publiczne)
- ✅ Statystyki i raporty
- ✅ Logi aktywności

**Funkcje operacyjne:**
- ✅ Automatyczne zadania okresowe (zamykanie zgłoszeń)
- ✅ Kopie zapasowe bazy danych
- ✅ Panel administracyjny Django

### 6.3. Ewentualne Problemy Napotkane Podczas Wdrożenia

**Problem 1: Wydajność powiadomień email**
- **Opis**: Podczas tworzenia zgłoszeń system blokował się na długi czas z powodu synchronicznego wysyłania powiadomień email
- **Rozwiązanie**: Zaimplementowano asynchroniczne wysyłanie powiadomień poprzez threading. Powiadomienia są teraz wysyłane w tle, a tworzenie zgłoszenia jest natychmiastowe
- **Status**: Rozwiązane

**Problem 2: Automatyczne zamykanie zgłoszeń**
- **Opis**: Początkowo system zamykał rozwiązane zgłoszenia po 24 godzinach, co było zbyt krótko dla klientów
- **Rozwiązanie**: Zmieniono logikę na 3 dni robocze (pomijając weekendy). System teraz liczy tylko dni robocze od poniedziałku do piątku
- **Status**: Rozwiązane

**Problem 3: Przypisywanie użytkowników do organizacji**
- **Opis**: Przy tworzeniu organizacji nie można było od razu przypisać użytkowników, co wymagało dodatkowych kroków
- **Rozwiązanie**: Dodano pole "Członkowie organizacji" w formularzu tworzenia/edycji organizacji z możliwością wyboru wielu użytkowników
- **Status**: Rozwiązane

**Problem 4: Formatowanie numerów telefonów**
- **Opis**: Użytkownicy wpisywali numery telefonów w różnych formatach, co utrudniało ich weryfikację
- **Rozwiązanie**: Zaimplementowano automatyczną maskę telefonu dla numerów polskich z formatowaniem w czasie rzeczywistym
- **Status**: Rozwiązane

**Problem 5: Viewer nie widział aktualizacji**
- **Opis**: Użytkownicy z rolą Viewer musieli ręcznie odświeżać stronę, aby zobaczyć nowe zgłoszenia
- **Rozwiązanie**: Zaimplementowano automatyczne odświeżanie listy zgłoszeń co 15 sekund poprzez AJAX polling
- **Status**: Rozwiązane

## 7. Testy

### 7.1. Lista Testowanych Funkcji

**Funkcje podstawowe:**
- Tworzenie zgłoszeń przez różnych użytkowników
- Edycja zgłoszeń
- Przypisywanie zgłoszeń
- Zamykanie i ponowne otwieranie zgłoszeń
- Dodawanie komentarzy
- Dodawanie i pobieranie załączników

**Funkcje autentykacji:**
- Rejestracja nowych użytkowników
- Weryfikacja email
- Logowanie i wylogowanie
- Reset hasła
- Konfiguracja 2FA
- Weryfikacja 2FA
- Zaufane urządzenia

**Funkcje zarządzania:**
- Zatwierdzanie kont użytkowników
- Odblokowywanie kont
- Zarządzanie organizacjami
- Zarządzanie użytkownikami
- Przypisywanie użytkowników do organizacji

**Funkcje zaawansowane:**
- Automatyczne sugerowanie kategorii
- Automatyczna zmiana statusu
- Automatyczne zamykanie zgłoszeń
- Kalendarz i dyżury
- Notatki kalendarzowe
- Statystyki i raporty

**Funkcje bezpieczeństwa:**
- Szyfrowanie załączników
- Kontrola dostępu do załączników
- Logi aktywności
- Blokada kont

### 7.2. Scenariusze Testowe

**Scenariusz 1: Klient tworzy zgłoszenie**
1. Klient loguje się do systemu
2. Klient weryfikuje kod 2FA
3. Klient tworzy nowe zgłoszenie z tytułem, opisem, kategorią
4. Klient dodaje załącznik (akceptuje regulamin)
5. Klient zapisuje zgłoszenie
6. **Oczekiwany rezultat**: Zgłoszenie zostaje utworzone ze statusem "Nowe", powiadomienia email są wysyłane asynchronicznie, zgłoszenie pojawia się na liście

**Scenariusz 2: Agent przypisuje zgłoszenie do siebie**
1. Agent loguje się do systemu
2. Agent weryfikuje kod 2FA
3. Agent przegląda listę nieprzydzielonych zgłoszeń
4. Agent klika "Przypisz do mnie" na wybranym zgłoszeniu
5. **Oczekiwany rezultat**: Zgłoszenie zostaje przypisane do agenta, status zmienia się na "W trakcie" (jeśli było "Nowe"), agent otrzymuje powiadomienie email

**Scenariusz 3: Agent dodaje komentarz do zgłoszenia**
1. Agent otwiera szczegóły zgłoszenia
2. Agent dodaje komentarz z informacją o postępach
3. Agent zapisuje komentarz
4. **Oczekiwany rezultat**: Komentarz pojawia się w historii, klient i inni zainteresowani otrzymują powiadomienie email

**Scenariusz 4: Automatyczne zamykanie rozwiązanych zgłoszeń**
1. Agent oznacza zgłoszenie jako "Rozwiązane"
2. System czeka 3 dni robocze (pomijając weekendy)
3. System automatycznie zamyka zgłoszenie
4. **Oczekiwany rezultat**: Zgłoszenie otrzymuje status "Zamknięte", data zamknięcia jest zapisana, log aktywności jest utworzony

**Scenariusz 5: Administrator zatwierdza konto użytkownika**
1. Nowy użytkownik rejestruje się w systemie
2. Użytkownik weryfikuje email
3. Administrator loguje się do systemu
4. Administrator przechodzi do sekcji "Zatwierdzenia"
5. Administrator zatwierdza konto użytkownika
6. **Oczekiwany rezultat**: Konto użytkownika zostaje zatwierdzone, użytkownik otrzymuje powiadomienie email, użytkownik może teraz logować się do systemu

**Scenariusz 6: Konfiguracja 2FA**
1. Nowy użytkownik loguje się po raz pierwszy
2. System przekierowuje użytkownika do konfiguracji 2FA
3. Użytkownik skanuje kod QR w aplikacji Google Authenticator
4. Użytkownik wprowadza kod weryfikacyjny
5. Użytkownik zapisuje kod odzyskiwania
6. **Oczekiwany rezultat**: 2FA jest włączone, użytkownik może logować się z weryfikacją 2FA, kod odzyskiwania jest wyświetlony

**Scenariusz 7: Blokada konta po nieudanych próbach logowania**
1. Użytkownik wprowadza błędne hasło 5 razy
2. **Oczekiwany rezultat**: Konto zostaje zablokowane, użytkownik nie może się zalogować, administrator może odblokować konto

**Scenariusz 8: Automatyczne sugerowanie kategorii**
1. Użytkownik tworzy zgłoszenie z tytułem zawierającym słowo "drukarka"
2. Użytkownik wypełnia opis problemu z drukarką
3. **Oczekiwany rezultat**: System sugeruje kategorię "Sprzęt" z odpowiednim poziomem pewności

**Scenariusz 9: Viewer przegląda zgłoszenia**
1. Viewer loguje się do systemu
2. Viewer widzi listę zgłoszeń
3. System automatycznie odświeża listę co 15 sekund
4. **Oczekiwany rezultat**: Lista zgłoszeń jest zawsze aktualna, Viewer nie może tworzyć ani edytować zgłoszeń

**Scenariusz 10: Administrator zarządza organizacją**
1. Administrator tworzy nową organizację
2. Administrator wybiera członków organizacji z listy użytkowników
3. Administrator zapisuje organizację
4. **Oczekiwany rezultat**: Organizacja zostaje utworzona, wybrani użytkownicy są przypisani do organizacji, twórca jest automatycznie dodany

### 7.3. Wyniki Testów

**Funkcje podstawowe:**
- ✅ Tworzenie zgłoszeń: **OK**
- ✅ Edycja zgłoszeń: **OK**
- ✅ Przypisywanie zgłoszeń: **OK**
- ✅ Zamykanie zgłoszeń: **OK**
- ✅ Dodawanie komentarzy: **OK**
- ✅ Załączniki: **OK**

**Funkcje autentykacji:**
- ✅ Rejestracja: **OK**
- ✅ Weryfikacja email: **OK**
- ✅ Logowanie: **OK**
- ✅ Reset hasła: **OK**
- ✅ 2FA: **OK**
- ✅ Zaufane urządzenia: **OK**

**Funkcje zarządzania:**
- ✅ Zatwierdzanie kont: **OK**
- ✅ Odblokowywanie kont: **OK**
- ✅ Zarządzanie organizacjami: **OK**
- ✅ Przypisywanie użytkowników: **OK**

**Funkcje zaawansowane:**
- ✅ Sugerowanie kategorii: **OK**
- ✅ Auto-status: **OK**
- ✅ Auto-zamykanie: **OK**
- ✅ Kalendarz: **OK**
- ✅ Statystyki: **OK**

**Funkcje bezpieczeństwa:**
- ✅ Szyfrowanie załączników: **OK**
- ✅ Kontrola dostępu: **OK**
- ✅ Logi: **OK**
- ✅ Blokada kont: **OK**

**Wszystkie testowane funkcje działają poprawnie w środowisku produkcyjnym.**

## 8. Podsumowanie

### 8.1. Najważniejsze Wnioski Dotyczące Funkcjonowania Systemu

System Helpdesk jest w pełni funkcjonalnym narzędziem do zarządzania zgłoszeniami IT, które spełnia wszystkie wymagania biznesowe firmy. System został pomyślnie wdrożony i jest używany przez wszystkich użytkowników na co dzień.

**Mocne strony systemu:**
- Kompleksowa funkcjonalność pokrywająca wszystkie aspekty zarządzania zgłoszeniami
- Wysoki poziom bezpieczeństwa dzięki 2FA, szyfrowaniu załączników i kontroli dostępu
- Intuicyjny interfejs użytkownika ułatwiający pracę
- Automatyzacja wielu procesów (zamykanie zgłoszeń, powiadomienia, sugerowanie kategorii)
- Elastyczny system ról i uprawnień dostosowany do potrzeb firmy
- Skalowalna architektura umożliwiająca rozbudowę

**Obszary wymagające uwagi:**
- System wymaga regularnych kopii zapasowych bazy danych (zaimplementowane)
- Monitorowanie wydajności przy dużej liczbie użytkowników
- Regularne aktualizacje bezpieczeństwa Django i zależności

### 8.2. Stabilność Działania

System działa stabilnie w środowisku produkcyjnym. Wszystkie kluczowe funkcje są przetestowane i działają poprawnie. Automatyczne zadania okresowe (zamykanie zgłoszeń) działają niezawodnie. Powiadomienia email są wysyłane asynchronicznie, co zapewnia szybką odpowiedź systemu.

Nie odnotowano poważnych awarii ani problemów z dostępnością systemu. Wszystkie napotkane problemy zostały rozwiązane podczas wdrożenia.

### 8.3. Możliwe Kierunki Rozwoju i Ulepszeń

**Krótkoterminowe ulepszenia:**
- Rozbudowa systemu statystyk o dodatkowe metryki
- Ulepszenie interfejsu użytkownika na podstawie feedbacku
- Optymalizacja wydajności przy dużej liczbie zgłoszeń
- Dodanie eksportu raportów do różnych formatów

**Średnioterminowe rozszerzenia:**
- Integracja z systemami zewnętrznymi (monitoring, CMDB)
- Rozbudowa systemu SLA z alertami
- System oceny satysfakcji klientów
- Szablony zgłoszeń dla często występujących problemów

**Długoterminowe wizje:**
- Aplikacja mobilna dla agentów
- Integracja z systemami SSO
- Wykorzystanie uczenia maszynowego do automatycznej kategoryzacji
- Rozbudowany system analityki i raportowania

System został zaprojektowany z myślą o możliwości rozbudowy, więc wszystkie te kierunki rozwoju są możliwe do zaimplementowania bez większych zmian w architekturze.

---

**Dokumentacja zaktualizowano:** 2025-12-XX  
**Wersja systemu:** Produkcyjna  
**Status:** W pełni funkcjonalny i stabilny
**Dołączono oddzielnie Załącznik A


