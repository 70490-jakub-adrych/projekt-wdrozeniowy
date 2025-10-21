# 5. Instrukcja administratora

## 5.1 Zarządzanie użytkownikami i rolami

### 5.1.1 Tworzenie nowych użytkowników

#### Metoda 1: Przez panel administracyjny
1. **Zaloguj się jako administrator**
2. **Przejdź do sekcji "Administracja"** w menu głównym
3. **Kliknij "Użytkownicy"** → "Dodaj użytkownika"
4. **Wypełnij formularz**:
   - Nazwa użytkownika
   - Email
   - Hasło (tymczasowe)
   - Imię i nazwisko
   - Rola użytkownika
5. **Przypisz organizacje** (jeśli potrzebne)
6. **Kliknij "Zapisz"**

#### Metoda 2: Zatwierdzanie rejestracji
1. **Przejdź do sekcji "Zatwierdzania"**
2. **Przejrzyj listę oczekujących użytkowników**
3. **Kliknij "Zatwierdź"** przy wybranym użytkowniku
4. **Ustaw odpowiednią rolę** i organizacje
5. **Kliknij "Zatwierdź konto"**

### 5.1.2 Zarządzanie rolami

#### Przypisywanie ról:
1. **Otwórz profil użytkownika**
2. **Przejdź do sekcji "Rola i uprawnienia"**
3. **Wybierz odpowiednią rolę**:
   - **Admin** - pełny dostęp do systemu
   - **Super Agent** - zarządzanie zgłoszeniami i agentami
   - **Agent** - obsługa przypisanych zgłoszeń
   - **Klient** - zgłaszanie problemów
   - **Viewer** - tylko podgląd zgłoszeń
4. **Zapisz zmiany**

#### Uprawnienia szczegółowe:
- **Dostęp do widoków** - kontrola dostępu do poszczególnych sekcji
- **Uprawnienia do zgłoszeń** - możliwość przypisywania, edytowania, zamykania
- **Dostęp do organizacji** - które organizacje może przeglądać
- **Uprawnienia do załączników** - poziom dostępu do plików

### 5.1.3 Zarządzanie organizacjami

#### Tworzenie organizacji:
1. **Przejdź do sekcji "Organizacje"**
2. **Kliknij "Nowa organizacja"**
3. **Wypełnij dane**:
   - Nazwa organizacji
   - Email kontaktowy
   - Telefon
   - Strona internetowa
   - Adres
   - Opis
4. **Kliknij "Zapisz"**

#### Przypisywanie użytkowników do organizacji:
1. **Otwórz profil użytkownika**
2. **Przejdź do sekcji "Organizacje"**
3. **Zaznacz organizacje** do których ma należeć użytkownik
4. **Zapisz zmiany**

## 5.2 Konfiguracja kategorii zgłoszeń i priorytetów

### 5.2.1 Kategorie zgłoszeń

System domyślnie zawiera następujące kategorie:
- **Sprzęt** - problemy z komputerami, drukarkami, urządzeniami
- **Oprogramowanie** - problemy z aplikacjami, systemami
- **Sieć** - problemy z połączeniem internetowym, siecią
- **Konto** - problemy z dostępem do konta, hasłami
- **Inne** - pozostałe problemy

#### Dodawanie nowych kategorii:
1. **Przejdź do sekcji "Konfiguracja"**
2. **Wybierz "Kategorie zgłoszeń"**
3. **Kliknij "Dodaj kategorię"**
4. **Wprowadź nazwę i opis** kategorii
5. **Zapisz zmiany**

### 5.2.2 Priorytety zgłoszeń

System zawiera 4 poziomy priorytetów:
- **Niski** - problem nie wpływa na pracę
- **Średni** - standardowy problem
- **Wysoki** - problem wpływa na pracę
- **Krytyczny** - problem blokuje pracę

#### Konfiguracja SLA:
1. **Przejdź do sekcji "Konfiguracja"**
2. **Wybierz "SLA i czasy odpowiedzi"**
3. **Ustaw czasy odpowiedzi** dla każdego priorytetu:
   - Krytyczny: 1 godzina
   - Wysoki: 4 godziny
   - Średni: 8 godzin
   - Niski: 24 godziny
4. **Zapisz ustawienia**

## 5.3 Konfiguracja powiadomień (email/SMS)

### 5.3.1 Konfiguracja serwera SMTP

#### Ustawienia email:
1. **Przejdź do sekcji "Konfiguracja"** → "Email"
2. **Wprowadź ustawienia SMTP**:
   - Host SMTP (np. smtp.gmail.com)
   - Port (zwykle 587 dla TLS)
   - Użyj TLS/SSL
   - Nazwa użytkownika
   - Hasło
3. **Przetestuj połączenie** klikając "Test email"
4. **Zapisz ustawienia**

#### Przykładowe konfiguracje:

**Gmail:**
```
Host: smtp.gmail.com
Port: 587
TLS: Tak
Użytkownik: twoj-email@gmail.com
Hasło: hasło aplikacji
```

**Outlook:**
```
Host: smtp-mail.outlook.com
Port: 587
TLS: Tak
Użytkownik: twoj-email@outlook.com
Hasło: hasło konta
```

### 5.3.2 Szablony email

#### Dostosowywanie szablonów:
1. **Przejdź do sekcji "Konfiguracja"** → "Szablony email"
2. **Wybierz typ powiadomienia**:
   - Nowe zgłoszenie
   - Przypisanie zgłoszenia
   - Zmiana statusu
   - Nowy komentarz
   - Zamknięcie zgłoszenia
3. **Edytuj treść** szablonu
4. **Użyj zmiennych** dostępnych w systemie:
   - `{{ticket.title}}` - tytuł zgłoszenia
   - `{{ticket.status}}` - status zgłoszenia
   - `{{user.username}}` - nazwa użytkownika
   - `{{organization.name}}` - nazwa organizacji
5. **Zapisz szablon**

### 5.3.3 Ustawienia powiadomień globalnych

#### Konfiguracja domyślnych ustawień:
1. **Przejdź do sekcji "Konfiguracja"** → "Powiadomienia"
2. **Ustaw domyślne preferencje** dla nowych użytkowników:
   - Powiadomienia o nowych zgłoszeniach
   - Powiadomienia o zmianach statusu
   - Powiadomienia o komentarzach
3. **Ustaw częstotliwość** powiadomień
4. **Zapisz ustawienia**

## 5.4 Backup i przywracanie danych

### 5.4.1 Automatyczne kopie zapasowe

#### Konfiguracja automatycznych backupów:
1. **Przejdź do sekcji "Administracja"** → "Backup"
2. **Skonfiguruj harmonogram**:
   - Częstotliwość (codziennie, tygodniowo)
   - Godzina wykonania
   - Liczba przechowywanych kopii
3. **Wybierz typ backupu**:
   - MySQL dump (zalecane)
   - JSON export (uniwersalne)
4. **Ustaw lokalizację** przechowywania
5. **Aktywuj automatyczne kopie**

#### Konfiguracja przez cron (Linux):
```bash
# Codziennie o 2:00
0 2 * * * cd /path/to/project && python manage.py backup_database --format=sql --rotate=7

# Tygodniowo o 2:30 (JSON)
30 2 * * 0 cd /path/to/project && python manage.py backup_database --format=json --rotate=4
```

### 5.4.2 Ręczne tworzenie kopii zapasowych

#### Przez interfejs web:
1. **Przejdź do sekcji "Administracja"** → "Backup"
2. **Kliknij "Utwórz backup teraz"**
3. **Wybierz typ backupu**
4. **Kliknij "Rozpocznij backup"**

#### Przez wiersz poleceń:
```bash
# Backup MySQL
python manage.py backup_database --format=sql

# Backup JSON
python manage.py backup_database --format=json

# Sprawdzenie statusu backupów
python manage.py backup_status
```

### 5.4.3 Przywracanie z kopii zapasowej

#### Przywracanie przez wiersz poleceń:
```bash
# Wyświetl dostępne kopie
python manage.py backup_status

# Przywróć z konkretnej kopii
python manage.py restore_database backups/database/backup_mysql_20250117_020000.sql.gz
```

#### Procedura przywracania:
1. **Zatrzymaj aplikację** (jeśli działa)
2. **Utwórz kopię obecnej bazy** (na wszelki wypadek)
3. **Wykonaj przywracanie** z wybranej kopii
4. **Sprawdź integralność** danych
5. **Uruchom aplikację** ponownie

## 5.5 Monitorowanie logów i bezpieczeństwa

### 5.5.1 Logi aktywności

#### Przeglądanie logów:
1. **Przejdź do sekcji "Logi"**
2. **Użyj filtrów** do zawężenia wyników:
   - Typ akcji
   - Użytkownik
   - Data
   - Adres IP
3. **Eksportuj logi** do CSV (jeśli potrzebne)

#### Typy logowanych akcji:
- Logowanie/wylogowanie
- Nieudane próby logowania
- Blokady kont
- Tworzenie/edycja zgłoszeń
- Zmiany statusu
- Dodawanie komentarzy
- Błędy systemu (404, 403)

### 5.5.2 Monitorowanie bezpieczeństwa

#### Kontrola dostępu:
1. **Przejdź do sekcji "Bezpieczeństwo"**
2. **Przejrzyj statystyki**:
   - Nieudane próby logowania
   - Zablokowane konta
   - Podejrzane aktywności
3. **Skonfiguruj alerty** dla:
   - Wielokrotnych nieudanych logowań
   - Prób dostępu z nowych IP
   - Nieautoryzowanych działań

#### Zarządzanie blokadami:
1. **Przejdź do sekcji "Użytkownicy"**
2. **Znajdź zablokowane konta**
3. **Odblokuj konto** klikając "Odblokuj"
4. **Zresetuj licznik** nieudanych prób

### 5.5.3 Czyszczenie logów

#### Automatyczne czyszczenie:
1. **Przejdź do sekcji "Konfiguracja"** → "Logi"
2. **Ustaw okres retencji** logów (np. 90 dni)
3. **Aktywuj automatyczne czyszczenie**

#### Ręczne czyszczenie:
```bash
# Wyczyść logi starsze niż 30 dni
python manage.py clean_logs --days=30

# Wyczyść wszystkie logi (ostrożnie!)
python manage.py clean_logs --all
```

## 5.6 Zarządzanie systemem

### 5.6.1 Ustawienia systemowe

#### Konfiguracja podstawowa:
1. **Przejdź do sekcji "Konfiguracja"** → "System"
2. **Ustaw parametry**:
   - Nazwa systemu
   - URL systemu
   - Strefa czasowa
   - Język interfejsu
   - Limity plików
3. **Zapisz ustawienia**

### 5.6.2 Zarządzanie sesjami

#### Kontrola sesji użytkowników:
1. **Przejdź do sekcji "Administracja"** → "Sesje"
2. **Przejrzyj aktywne sesje**
3. **Wyloguj użytkowników** (jeśli potrzebne)
4. **Skonfiguruj timeout** sesji

### 5.6.3 Optymalizacja wydajności

#### Czyszczenie cache:
```bash
# Wyczyść cache Django
python manage.py clear_cache

# Wyczyść sesje wygasłe
python manage.py clearsessions
```

#### Optymalizacja bazy danych:
```bash
# Analiza wydajności
python manage.py dbshell
# W MySQL: ANALYZE TABLE crm_ticket;

# Defragmentacja (MySQL)
python manage.py dbshell
# W MySQL: OPTIMIZE TABLE crm_ticket;
```

## 5.7 Rozwiązywanie problemów

### 5.7.1 Najczęstsze problemy

**Problem: Użytkownicy nie mogą się zalogować**
- Sprawdź ustawienia SMTP
- Sprawdź logi błędów
- Zweryfikuj konfigurację 2FA

**Problem: Powiadomienia email nie działają**
- Przetestuj połączenie SMTP
- Sprawdź logi email
- Zweryfikuj ustawienia firewall

**Problem: System działa wolno**
- Sprawdź obciążenie serwera
- Wyczyść cache
- Zoptymalizuj bazę danych

### 5.7.2 Kontakt z pomocą techniczną

W przypadku problemów technicznych:
- **Email:** admin@betulait.usermd.net
- **Logi systemowe:** Sprawdź plik `django.log`
- **Dokumentacja:** Zobacz sekcję "Wdrożenie"
- **GitHub:** Sprawdź issues w repozytorium projektu
