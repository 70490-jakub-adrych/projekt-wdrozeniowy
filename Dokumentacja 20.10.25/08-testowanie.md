# 8. Testowanie i jakość

## 8.1 Testy funkcjonalne

### 8.1.1 Scenariusze działania

#### Test 1: Tworzenie zgłoszenia przez klienta
**Cel:** Weryfikacja poprawnego tworzenia zgłoszenia przez użytkownika z rolą klienta

**Kroki testowe:**
1. Zaloguj się jako klient
2. Przejdź do sekcji "Nowe zgłoszenie"
3. Wypełnij formularz:
   - Tytuł: "Problem z drukarką"
   - Opis: "Drukarka nie drukuje dokumentów"
   - Kategoria: "Sprzęt"
   - Priorytet: "Średni"
4. Dodaj załącznik (zrzut ekranu)
5. Zaakceptuj regulamin
6. Kliknij "Wyślij zgłoszenie"

**Oczekiwany rezultat:**
- Zgłoszenie zostaje utworzone
- Status: "Nowe"
- Powiadomienie email zostaje wysłane
- Zgłoszenie pojawia się w liście zgłoszeń

#### Test 2: Przypisanie zgłoszenia przez agenta
**Cel:** Weryfikacja możliwości przypisania zgłoszenia przez agenta

**Kroki testowe:**
1. Zaloguj się jako agent
2. Przejdź do listy zgłoszeń
3. Znajdź zgłoszenie ze statusem "Nowe"
4. Kliknij "Przypisz do siebie"
5. Dodaj komentarz: "Rozpoczynam pracę nad problemem"
6. Zmień status na "W trakcie"

**Oczekiwany rezultat:**
- Zgłoszenie zostaje przypisane do agenta
- Status zmienia się na "W trakcie"
- Powiadomienie email zostaje wysłane do klienta
- Komentarz zostaje dodany

#### Test 3: Rozwiązywanie zgłoszenia
**Cel:** Weryfikacja procesu rozwiązywania zgłoszenia

**Kroki testowe:**
1. Jako agent, otwórz przypisane zgłoszenie
2. Dodaj komentarz z opisem rozwiązania
3. Zmień status na "Rozwiązane"
4. Dodaj informację o czasie rozwiązania
5. Zaloguj się jako klient
6. Sprawdź status zgłoszenia
7. Dodaj komentarz potwierdzający rozwiązanie

**Oczekiwany rezultat:**
- Status zmienia się na "Rozwiązane"
- Powiadomienie email zostaje wysłane
- Klient może dodać komentarz potwierdzający
- Statystyki zostają zaktualizowane

### 8.1.2 Testy integracji

#### Test 4: Integracja z systemem email
**Cel:** Weryfikacja wysyłania powiadomień email

**Kroki testowe:**
1. Skonfiguruj serwer SMTP w ustawieniach
2. Utwórz nowe zgłoszenie
3. Przypisz zgłoszenie do agenta
4. Dodaj komentarz
5. Zmień status zgłoszenia
6. Sprawdź skrzynki email wszystkich zaangażowanych użytkowników

**Oczekiwany rezultat:**
- Wszystkie powiadomienia email zostają wysłane
- Treść emaili jest poprawna
- Linki w emailach działają
- Szablony email są renderowane poprawnie

#### Test 5: Integracja z Google Authenticator
**Cel:** Weryfikacja działania uwierzytelniania dwuskładnikowego

**Kroki testowe:**
1. Zaloguj się jako administrator
2. Włącz 2FA dla użytkownika testowego
3. Wygeneruj kod QR
4. Zeskanuj kod w aplikacji Google Authenticator
5. Wprowadź kod weryfikacyjny
6. Przetestuj logowanie z 2FA
7. Przetestuj kod odzyskiwania

**Oczekiwany rezultat:**
- Kod QR zostaje wygenerowany
- Aplikacja Google Authenticator akceptuje kod
- Logowanie z 2FA działa poprawnie
- Kod odzyskiwania działa w przypadku utraty dostępu

## 8.2 Testy użytkownika

### 8.2.1 Scenariusze typowych zgłoszeń

#### Scenariusz 1: Problem z dostępem do konta
**Użytkownik:** Pracownik biurowy
**Problem:** Nie może się zalogować do systemu

**Kroki użytkownika:**
1. Próbuje się zalogować - nie udaje się
2. Kliknij "Zapomniałem hasła"
3. Wprowadza email
4. Sprawdza skrzynkę email
5. Kliknij link resetowania w emailu
6. Ustawia nowe hasło
7. Loguje się z nowym hasłem

**Oczekiwany rezultat:**
- Reset hasła działa poprawnie
- Email z linkiem zostaje wysłany
- Nowe hasło zostaje ustawione
- Użytkownik może się zalogować

#### Scenariusz 2: Problem z drukarką
**Użytkownik:** Pracownik biurowy
**Problem:** Drukarka nie drukuje dokumentów

**Kroki użytkownika:**
1. Tworzy zgłoszenie w kategorii "Sprzęt"
2. Opisuje problem szczegółowo
3. Dodaje zrzut ekranu błędu
4. Ustawia priorytet "Wysoki"
5. Czeka na odpowiedź agenta
6. Odpowiada na pytania agenta
7. Potwierdza rozwiązanie problemu

**Oczekiwany rezultat:**
- Zgłoszenie zostaje utworzone
- Agent odpowiada w odpowiednim czasie
- Problem zostaje rozwiązany
- Użytkownik potwierdza rozwiązanie

#### Scenariusz 3: Problem z oprogramowaniem
**Użytkownik:** Pracownik IT
**Problem:** Aplikacja nie uruchamia się poprawnie

**Kroki użytkownika:**
1. Tworzy zgłoszenie w kategorii "Oprogramowanie"
2. Opisuje kroki reprodukcji problemu
3. Dodaje logi aplikacji jako załącznik
4. Ustawia priorytet "Krytyczny"
5. Monitoruje postęp zgłoszenia
6. Testuje rozwiązanie zaproponowane przez agenta

**Oczekiwany rezultat:**
- Zgłoszenie zostaje utworzone z wysokim priorytetem
- Agent szybko odpowiada na krytyczny problem
- Rozwiązanie zostaje przetestowane
- Problem zostaje rozwiązany

### 8.2.2 Testy użyteczności

#### Test 6: Nawigacja w systemie
**Cel:** Weryfikacja intuicyjności interfejsu

**Kroki testowe:**
1. Poproś użytkownika o wykonanie podstawowych zadań bez instrukcji
2. Obserwuj jak użytkownik nawiguje po systemie
3. Zapisz problemy z użytecznością
4. Poproś o feedback dotyczący interfejsu

**Oczekiwane rezultaty:**
- Użytkownik może łatwo znaleźć potrzebne funkcje
- Interfejs jest intuicyjny
- Minimalna liczba kliknięć do wykonania zadań
- Pozytywny feedback od użytkowników

#### Test 7: Responsywność na urządzeniach mobilnych
**Cel:** Weryfikacja działania na urządzeniach mobilnych

**Kroki testowe:**
1. Otwórz system na smartfonie
2. Przetestuj wszystkie główne funkcje
3. Sprawdź czy elementy są odpowiednio skalowane
4. Przetestuj na tablecie
5. Sprawdź różne orientacje ekranu

**Oczekiwane rezultaty:**
- Wszystkie funkcje działają na urządzeniach mobilnych
- Interfejs jest responsywny
- Elementy są łatwe do kliknięcia
- Tekst jest czytelny

## 8.3 Testy bezpieczeństwa

### 8.3.1 Testy autoryzacji

#### Test 8: Kontrola dostępu do zgłoszeń
**Cel:** Weryfikacja że użytkownicy widzą tylko odpowiednie zgłoszenia

**Kroki testowe:**
1. Zaloguj się jako klient
2. Sprawdź czy widzisz tylko swoje zgłoszenia
3. Spróbuj otworzyć zgłoszenie innego użytkownika (przez URL)
4. Zaloguj się jako agent
5. Sprawdź czy widzisz zgłoszenia swojej organizacji
6. Spróbuj otworzyć zgłoszenie z innej organizacji

**Oczekiwany rezultat:**
- Użytkownicy widzą tylko odpowiednie zgłoszenia
- Próby dostępu do nieautoryzowanych danych są blokowane
- Zwracany jest błąd 403 (Forbidden)

#### Test 9: Ochrona przed atakami SQL Injection
**Cel:** Weryfikacja ochrony przed atakami SQL injection

**Kroki testowe:**
1. Spróbuj wprowadzić kod SQL w polach tekstowych
2. Przetestuj różne wektory ataku:
   - `'; DROP TABLE tickets; --`
   - `' OR '1'='1`
   - `' UNION SELECT * FROM users --`
3. Sprawdź czy ataki są blokowane
4. Sprawdź logi systemowe

**Oczekiwany rezultat:**
- Ataki SQL injection są blokowane
- System zwraca błędy walidacji
- Dane nie zostają uszkodzone
- Ataki są logowane

### 8.3.2 Testy szyfrowania

#### Test 10: Szyfrowanie załączników
**Cel:** Weryfikacja że załączniki są odpowiednio szyfrowane

**Kroki testowe:**
1. Dodaj załącznik do zgłoszenia
2. Sprawdź czy plik jest szyfrowany na dysku
3. Spróbuj otworzyć plik bezpośrednio z dysku
4. Sprawdź czy plik można odszyfrować przez system
5. Przetestuj z różnymi typami plików

**Oczekiwany rezultat:**
- Pliki są szyfrowane na dysku
- Nie można otworzyć plików bezpośrednio
- System może odszyfrować pliki
- Szyfrowanie działa dla wszystkich typów plików

## 8.4 Testy wydajnościowe

### 8.4.1 Testy obciążenia

#### Test 11: Obciążenie systemu
**Cel:** Weryfikacja wydajności pod obciążeniem

**Kroki testowe:**
1. Utwórz 1000 zgłoszeń testowych
2. Symuluj 50 użytkowników jednocześnie
3. Monitoruj czas odpowiedzi
4. Sprawdź wykorzystanie zasobów serwera
5. Przetestuj różne scenariusze obciążenia

**Oczekiwane rezultaty:**
- Czas odpowiedzi < 3 sekundy
- Wykorzystanie CPU < 80%
- Wykorzystanie RAM < 80%
- Brak błędów pod obciążeniem

#### Test 12: Testy skalowania
**Cel:** Weryfikacja możliwości skalowania systemu

**Kroki testowe:**
1. Przetestuj z różnymi rozmiarami bazy danych
2. Sprawdź wydajność z różną liczbą użytkowników
3. Przetestuj z różnymi rozmiarami plików
4. Sprawdź wydajność zapytań do bazy danych

**Oczekiwane rezultaty:**
- System skaluje się liniowo
- Wydajność pozostaje akceptowalna
- Optymalizacje działają poprawnie

## 8.5 Raportowanie błędów

### 8.5.1 Znane ograniczenia

#### Ograniczenia funkcjonalne:
1. **Brak integracji z zewnętrznymi systemami** - system nie integruje się z Active Directory, LDAP
2. **Ograniczone powiadomienia** - brak powiadomień SMS, push notifications
3. **Brak bazy wiedzy** - system nie zawiera modułu FAQ/bazy wiedzy
4. **Ograniczone raporty** - brak zaawansowanych raportów analitycznych

#### Ograniczenia techniczne:
1. **Rozmiar plików** - maksymalny rozmiar załącznika to 10MB
2. **Liczba użytkowników** - system testowany dla maksymalnie 100 użytkowników jednocześnie
3. **Baza danych** - brak wsparcia dla NoSQL, tylko relacyjne bazy danych
4. **Mobilność** - aplikacja webowa, brak natywnych aplikacji mobilnych

### 8.5.2 Proces raportowania błędów

#### Jak zgłaszać błędy:
1. **Utwórz zgłoszenie** w kategorii "Inne"
2. **Opisz problem** szczegółowo:
   - Co się stało
   - Kiedy się stało
   - Jakie kroki prowadziły do błędu
   - Oczekiwane zachowanie
3. **Dodaj zrzuty ekranu** lub logi błędów
4. **Ustaw odpowiedni priorytet**

#### Priorytety błędów:
- **Krytyczny** - system nie działa, błąd bezpieczeństwa
- **Wysoki** - główna funkcjonalność nie działa
- **Średni** - funkcjonalność działa częściowo
- **Niski** - kosmetyczne problemy, sugestie ulepszeń

### 8.5.3 Proces naprawy błędów

#### Cykl życia błędu:
1. **Zgłoszenie** - błąd zostaje zgłoszony
2. **Weryfikacja** - błąd zostaje zweryfikowany przez zespół
3. **Priorytetyzacja** - błąd zostaje przypisany do odpowiedniej kolejki
4. **Naprawa** - błąd zostaje naprawiony przez deweloperów
5. **Testowanie** - naprawa zostaje przetestowana
6. **Wdrożenie** - naprawa zostaje wdrożona do produkcji
7. **Zamknięcie** - błąd zostaje zamknięty

#### Czas naprawy (SLA):
- **Krytyczny:** 4 godziny
- **Wysoki:** 24 godziny
- **Średni:** 72 godziny
- **Niski:** 7 dni
