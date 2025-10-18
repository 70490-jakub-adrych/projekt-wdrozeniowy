# 🧪 Dokumentacja Testów

## Spis Treści
1. [Wprowadzenie](#wprowadzenie)
2. [Testy Funkcjonalne](#testy-funkcjonalne)
3. [Testy Bezpieczeństwa](#testy-bezpieczeństwa)
4. [Testy Automatyczne](#testy-automatyczne)
5. [Środowisko Testowe](#środowisko-testowe)
6. [Metodologia Testów](#metodologia-testów)
7. [Testy Wydajności](#testy-wydajności)
8. [Testy Integracyjne](#testy-integracyjne)
9. [Testy Regresji](#testy-regresji)
10. [Raportowanie i Metryki](#raportowanie-i-metryki)
11. [Narzędzia Testowe](#narzędzia-testowe)
12. [Procedury Testowe](#procedury-testowe)

---

## Wprowadzenie

Niniejsza dokumentacja opisuje kompleksowy plan testów dla systemu helpdesk obejmujący testy funkcjonalne, bezpieczeństwa, automatyczne oraz wydajnościowe. System składa się z trzech głównych ról użytkowników: **klient**, **agent/superagent** oraz **administrator**.

### Cel Dokumentacji
- **Weryfikacja poprawności** funkcjonalności systemu
- **Zapewnienie bezpieczeństwa** danych i dostępu
- **Automatyzacja** kluczowych scenariuszy testowych
- **Walidacja ścieżek** użytkowników
- **Zapewnienie jakości** oprogramowania

### Zakres Testów
- **Testy funkcjonalne** - wszystkie funkcje systemu
- **Testy bezpieczeństwa** - ochrona przed atakami
- **Testy automatyczne** - automatyzacja scenariuszy
- **Testy wydajności** - obciążenie i skalowalność
- **Testy integracyjne** - współdziałanie komponentów
- **Testy regresji** - weryfikacja po zmianach

### Odbiorcy
- **Testerzy** - wykonawcy testów
- **Deweloperzy** - implementacja poprawek
- **Administratorzy** - zarządzanie środowiskiem testowym
- **Kierownictwo** - ocena jakości systemu

---

## Testy Funkcjonalne

### 1. Formularz Zgłoszenia

#### TC-F-001: Poprawne ustawienie wartości pól formularza
**Cel:** Weryfikacja poprawnego wypełnienia i walidacji pól formularza zgłoszenia

**Kroki testowe:**
1. Otwórz formularz tworzenia zgłoszenia
2. Wypełnij wszystkie wymagane pola poprawnymi danymi:
   - Tytuł zgłoszenia
   - Opis problemu
   - Kategoria
   - Akceptacja regulaminu
3. Sprawdź walidację pól wymaganych
4. Zweryfikuj ograniczenia formatów danych

**Oczekiwany rezultat:** Formularz akceptuje poprawne dane i wyświetla błędy walidacji dla niepoprawnych

**Priorytet:** Wysoki  
**Typ:** Pozytywny/Negatywny

#### TC-F-002: Wywołanie funkcji onSubmit
**Cel:** Sprawdzenie czy po zatwierdzeniu poprawnego formularza wywoływana jest właściwa funkcja

**Kroki testowe:**
1. Wypełnij formularz poprawnymi danymi
2. Kliknij przycisk "Wyślij"
3. Zweryfikuj czy zgłoszenie zostało utworzone
4. Sprawdź czy użytkownik został przekierowany na właściwą stronę

**Oczekiwany rezultat:** Zgłoszenie zostaje utworzone i zapisane w systemie

**Priorytet:** Wysoki  
**Typ:** Pozytywny

#### TC-F-003: Filtracja zgłoszeń wg kategorii/statusu
**Cel:** Weryfikacja działania filtrów w liście zgłoszeń

**Kroki testowe:**
1. Przejdź do listy zgłoszeń
2. Zastosuj filtr według kategorii
3. Zastosuj filtr według statusu
4. Zweryfikuj wyniki filtrowania

**Oczekiwany rezultat:** Lista wyświetla tylko zgłoszenia spełniające kryteria filtra

**Priorytet:** Średni  
**Typ:** Pozytywny

#### TC-F-004: Reducer zmienia status zgłoszenia
**Cel:** Sprawdzenie mechanizmu zmiany statusu zgłoszenia

**Kroki testowe:**
1. Otwórz zgłoszenie o statusie "open"
2. Zmień status na "closed"
3. Zapisz zmiany
4. Zweryfikuj aktualizację statusu w systemie

**Oczekiwany rezultat:** Status zgłoszenia zostaje poprawnie zaktualizowany

**Priorytet:** Wysoki  
**Typ:** Pozytywny

### 2. Panel Administratora

#### TC-F-005: Dodawanie użytkowników
**Cel:** Weryfikacja funkcjonalności dodawania nowych użytkowników przez administratora

**Kroki testowe:**
1. Zaloguj się jako administrator
2. Przejdź do panelu zarządzania użytkownikami
3. Kliknij "Dodaj użytkownika"
4. Wypełnij formularz danych użytkownika
5. Zapisz nowego użytkownika

**Oczekiwany rezultat:** Nowy użytkownik zostaje utworzony w systemie

**Priorytet:** Wysoki  
**Typ:** Pozytywny

#### TC-F-006: Nadawanie ról
**Cel:** Sprawdzenie możliwości przypisywania ról użytkownikom

**Kroki testowe:**
1. Otwórz panel użytkowników
2. Wybierz użytkownika
3. Przypisz rolę (admin, agent, klient)
4. Zapisz zmiany
5. Zweryfikuj uprawnienia użytkownika

**Oczekiwany rezultat:** Rola zostaje przypisana i uprawnienia są aktywne

**Priorytet:** Wysoki  
**Typ:** Pozytywny

#### TC-F-007: Blokowanie/odblokowywanie konta
**Cel:** Weryfikacja funkcjonalności blokowania dostępu do kont użytkowników

**Kroki testowe:**
1. Wybierz aktywne konto użytkownika
2. Zablokuj konto
3. Spróbuj zalogować się na zablokowane konto
4. Odblokuj konto
5. Ponownie sprawdź możliwość logowania

**Oczekiwany rezultat:** Zablokowane konto nie może się zalogować, odblokowane może

**Priorytet:** Wysoki  
**Typ:** Pozytywny/Negatywny

### 3. Ścieżka Użytkownika Klient

#### TC-F-008: Rejestracja nowego użytkownika
**Cel:** Weryfikacja procesu rejestracji nowego klienta

**Kroki testowe:**
1. Otwórz formularz rejestracji
2. Wypełnij wszystkie wymagane pola
3. Zaakceptuj regulamin
4. Wyślij formularz rejestracji
5. Sprawdź potwierdzenie rejestracji

**Oczekiwany rezultat:** Konto zostaje utworzone i oczekuje na aktywację

**Priorytet:** Wysoki  
**Typ:** Pozytywny

#### TC-F-009: Zalogowanie i dodanie zgłoszenia
**Cel:** Sprawdzenie pełnej ścieżki od logowania do utworzenia zgłoszenia

**Kroki testowe:**
1. Zaloguj się jako klient
2. Przejdź do sekcji zgłoszeń
3. Utwórz nowe zgłoszenie
4. Wypełnij wszystkie pola
5. Wyślij zgłoszenie

**Oczekiwany rezultat:** Zgłoszenie zostaje utworzone i jest widoczne w panelu

**Priorytet:** Wysoki  
**Typ:** Pozytywny

#### TC-F-010: Przeglądanie zgłoszeń w panelu klienta
**Cel:** Weryfikacja widoku zgłoszeń dla klienta

**Kroki testowe:**
1. Zaloguj się jako klient
2. Przejdź do "Moje zgłoszenia"
3. Sprawdź listę zgłoszeń
4. Otwórz szczegóły zgłoszenia

**Oczekiwany rezultat:** Klient widzi tylko swoje zgłoszenia z pełnymi szczegółami

**Priorytet:** Średni  
**Typ:** Pozytywny

#### TC-F-011: Odpowiedź do zgłoszenia przez formularz komentarzy
**Cel:** Sprawdzenie możliwości dodawania komentarzy do zgłoszeń

**Kroki testowe:**
1. Otwórz szczegóły zgłoszenia
2. Przejdź do sekcji komentarzy
3. Dodaj komentarz
4. Wyślij komentarz
5. Zweryfikuj wyświetlenie komentarza

**Oczekiwany rezultat:** Komentarz zostaje dodany i jest widoczny w historii

**Priorytet:** Średni  
**Typ:** Pozytywny

#### TC-F-012: Wylogowanie
**Cel:** Weryfikacja procesu wylogowania

**Kroki testowe:**
1. Będąc zalogowanym, kliknij opcję wylogowania
2. Spróbuj uzyskać dostęp do chronionej strony
3. Sprawdź przekierowanie na stronę logowania

**Oczekiwany rezultat:** Sesja zostaje zakończona, dostęp do panelu zablokowany

**Priorytet:** Średni  
**Typ:** Pozytywny

### 4. Ścieżka Użytkownika Agent/Superagent

#### TC-F-013: Przeglądanie zgłoszeń przypisanych do siebie
**Cel:** Weryfikacja widoku zgłoszeń przypisanych do agenta

**Kroki testowe:**
1. Zaloguj się jako agent
2. Przejdź do listy zgłoszeń
3. Sprawdź filtr "Przypisane do mnie"
4. Zweryfikuj czy wyświetlane są tylko właściwe zgłoszenia

**Oczekiwany rezultat:** Agent widzi tylko zgłoszenia przypisane do siebie

**Priorytet:** Wysoki  
**Typ:** Pozytywny

#### TC-F-014: Zmiana statusu zgłoszenia
**Cel:** Sprawdzenie możliwości zmiany statusu przez agenta

**Kroki testowe:**
1. Otwórz przypisane zgłoszenie
2. Zmień status na "przyjęte"
3. Następnie zmień na "rozwiązane"
4. Zapisz zmiany

**Oczekiwany rezultat:** Status zostaje zaktualizowany w systemie

**Priorytet:** Wysoki  
**Typ:** Pozytywny

#### TC-F-015: Przypisanie zgłoszenia innemu agentowi
**Cel:** Weryfikacja możliwości przekazywania zgłoszeń między agentami

**Kroki testowe:**
1. Otwórz zgłoszenie przypisane do siebie
2. Wybierz opcję "Przypisz do innego agenta"
3. Wybierz docelowego agenta
4. Potwierdź zmianę
5. Sprawdź aktualizację przypisania

**Oczekiwany rezultat:** Zgłoszenie zostaje przypisane do wybranego agenta

**Priorytet:** Średni  
**Typ:** Pozytywny

### 5. Ścieżka Administratora

#### TC-F-016: Zarządzanie zgłoszeniami
**Cel:** Weryfikacja uprawnień administratora do zarządzania zgłoszeniami

**Kroki testowe:**
1. Zaloguj się jako administrator
2. Otwórz dowolne zgłoszenie
3. Edytuj szczegóły zgłoszenia
4. Usuń wybrane zgłoszenie
5. Sprawdź zmiany w systemie

**Oczekiwany rezultat:** Administrator może modyfikować i usuwać zgłoszenia

**Priorytet:** Wysoki  
**Typ:** Pozytywny

#### TC-F-017: Przypisywanie ról
**Cel:** Sprawdzenie zarządzania rolami użytkowników

**Kroki testowe:**
1. Przejdź do zarządzania użytkownikami
2. Wybierz użytkownika
3. Zmień jego rolę
4. Zapisz zmiany
5. Zweryfikuj nowe uprawnienia

**Oczekiwany rezultat:** Rola zostaje zmieniona i uprawnienia są aktywne

**Priorytet:** Wysoki  
**Typ:** Pozytywny

---

## Testy Bezpieczeństwa

### 1. Uwierzytelnianie i Autoryzacja

#### TC-S-001: Próba wysłania formularza bez uprawnień (401)
**Cel:** Weryfikacja ochrony przed nieautoryzowanym dostępem

**Kroki testowe:**
1. Wyloguj się z systemu
2. Spróbuj wysłać żądanie POST do chronionego endpointu
3. Sprawdź kod odpowiedzi HTTP

**Oczekiwany rezultat:** System zwraca błąd 401 Unauthorized

**Priorytet:** Krytyczny  
**Typ:** Negatywny

#### TC-S-002: Próba dostępu do panelu admina bez uprawnień
**Cel:** Sprawdzenie ochrony panelu administratora

**Kroki testowe:**
1. Zaloguj się jako zwykły użytkownik
2. Spróbuj uzyskać dostęp do panelu admina
3. Sprawdź czy następuje przekierowanie lub błąd

**Oczekiwany rezultat:** Dostęp zostaje zablokowany

**Priorytet:** Krytyczny  
**Typ:** Negatywny

#### TC-S-003: Brak dostępu do danych innego użytkownika (IDOR)
**Cel:** Weryfikacja ochrony przed Insecure Direct Object Reference

**Kroki testowe:**
1. Zaloguj się jako użytkownik A
2. Zanotuj ID zgłoszenia użytkownika A
3. Zmień ID w URL na ID należące do użytkownika B
4. Sprawdź czy dane są dostępne

**Oczekiwany rezultat:** System blokuje dostęp do cudzych danych

**Priorytet:** Krytyczny  
**Typ:** Negatywny

#### TC-S-004: Wymuszenie silnego hasła
**Cel:** Sprawdzenie polityki haseł

**Kroki testowe:**
1. Spróbuj utworzyć konto ze słabym hasłem
2. Testuj różne kombinacje:
   - Krócej niż 8 znaków
   - Bez wielkich liter
   - Bez cyfr
   - Bez znaków specjalnych

**Oczekiwany rezultat:** Słabe hasła są odrzucane z odpowiednim komunikatem

**Priorytet:** Wysoki  
**Typ:** Negatywny

#### TC-S-005: Wygasanie tokenu JWT
**Cel:** Weryfikacja mechanizmu wygasania sesji

**Kroki testowe:**
1. Zaloguj się do systemu
2. Poczekaj na wygaśnięcie tokena
3. Spróbuj wykonać chronioną operację
4. Sprawdź czy następuje przekierowanie na logowanie

**Oczekiwany rezultat:** Po wygaśnięciu tokena wymagane jest ponowne logowanie

**Priorytet:** Wysoki  
**Typ:** Negatywny

### 2. Ochrona przed XSS

#### TC-S-006: Wprowadzenie skryptu w formularzu
**Cel:** Weryfikacja ochrony przed Cross-Site Scripting

**Kroki testowe:**
1. W polu opisu zgłoszenia wprowadź `<script>alert(1)</script>`
2. Wyślij formularz
3. Otwórz zgłoszenie i sprawdź czy skrypt się wykonuje

**Oczekiwany rezultat:** Skrypt nie zostaje wykonany, dane są filtrowane

**Priorytet:** Wysoki  
**Typ:** Negatywny

### 3. Ochrona CSRF

#### TC-S-007: Żądania wymagają tokenu CSRF
**Cel:** Sprawdzenie ochrony przed Cross-Site Request Forgery

**Kroki testowe:**
1. Przygotuj żądanie POST/PUT/DELETE bez tokenu CSRF
2. Wyślij żądanie
3. Sprawdź odpowiedź serwera

**Oczekiwany rezultat:** Żądanie zostaje odrzucone

**Priorytet:** Wysoki  
**Typ:** Negatywny

#### TC-S-008: Blokada żądań z innego originu
**Cel:** Weryfikacja polityki CORS

**Kroki testowe:**
1. Z innej domeny wyślij żądanie AJAX
2. Sprawdź nagłówki CORS w odpowiedzi
3. Zweryfikuj czy żądanie zostaje zablokowane

**Oczekiwany rezultat:** Żądania z niepożądanych originów są blokowane

**Priorytet:** Średni  
**Typ:** Negatywny

### 4. Ochrona przed wstrzykiwaniem danych

#### TC-S-009: Próba SQL Injection
**Cel:** Weryfikacja ochrony przed wstrzykiwaniem SQL

**Kroki testowe:**
1. W polu formularza wprowadź `'; DROP TABLE users;--`
2. Wyślij formularz
3. Sprawdź czy dane w bazie pozostają nienaruszone

**Oczekiwany rezultat:** Próba wstrzykiwania SQL nie wpływa na bazę danych

**Priorytet:** Krytyczny  
**Typ:** Negatywny

### 5. Testy Penetracyjne (Kali Linux)

#### TC-S-010: Skanowanie portów - Nmap
**Cel:** Identyfikacja otwartych portów i usług

**Narzędzie:** Nmap (Kali Linux)

**Polecenia:**
```bash
# Podstawowe skanowanie
nmap -sV -Pn target_ip

# Skanowanie agresywne
nmap -A -T4 target_ip

# Skanowanie podatności
nmap --script vuln target_ip

# Skanowanie ukrytych portów
nmap -p- target_ip
```

**Oczekiwany rezultat:** Tylko niezbędne porty są otwarte (80, 443), brak niepotrzebnych usług

**Priorytet:** Wysoki  
**Typ:** Penetracyjny

#### TC-S-011: Wykrywanie podatności - Nikto
**Cel:** Identyfikacja podatności aplikacji webowych

**Narzędzie:** Nikto (Kali Linux)

**Polecenia:**
```bash
# Podstawowe skanowanie
nikto -h http://betulait.usermd.net

# Skanowanie z zapisem do pliku
nikto -h http://betulait.usermd.net -o nikto_report.html -Format htm

# Skanowanie przez proxy
nikto -h http://betulait.usermd.net -useproxy http://127.0.0.1:8080
```

**Oczekiwany rezultat:** Brak krytycznych podatności aplikacji webowej

**Priorytet:** Wysoki  
**Typ:** Penetracyjny

#### TC-S-012: Ochrona plików konfiguracyjnych
**Cel:** Sprawdzenie dostępności wrażliwych plików

**Kroki testowe:**
1. Spróbuj uzyskać dostęp do `.env`, `.git`, `package-lock.json`
2. Sprawdź odpowiedź serwera

**Oczekiwany rezultat:** Pliki konfiguracyjne nie są dostępne przez HTTP

**Priorytet:** Wysoki  
**Typ:** Negatywny

#### TC-S-013: Ograniczenie uploadu plików
**Cel:** Weryfikacja kontroli przesyłanych plików

**Kroki testowe:**
1. Spróbuj przesłać plik o niedozwolonym rozszerzeniu
2. Spróbuj przesłać plik przekraczający limit rozmiaru
3. Sprawdź walidację typu MIME

**Oczekiwany rezultat:** Nieprawidłowe pliki są odrzucane

**Priorytet:** Wysoki  
**Typ:** Negatywny

### 6. Testy Rate Limiting i Brute Force

#### TC-S-014: Ograniczenie prób logowania - Hydra
**Cel:** Weryfikacja ochrony przed atakami brute-force

**Narzędzie:** Hydra (Kali Linux)

**Polecenia:**
```bash
# Atak słownikowy na login
hydra -l admin -P /usr/share/wordlists/rockyou.txt betulait.usermd.net http-post-form "/login:username=^USER^&password=^PASS^:Invalid"

# Test z listą użytkowników
hydra -L users.txt -P passwords.txt betulait.usermd.net http-post-form "/login:username=^USER^&password=^PASS^:Invalid"

# Ograniczony atak czasowy
hydra -l admin -P /usr/share/wordlists/rockyou.txt -t 1 -W 30 betulait.usermd.net http-post-form "/login:username=^USER^&password=^PASS^:Invalid"
```

**Oczekiwany rezultat:** Po określonej liczbie prób (np. 5) dostęp zostaje tymczasowo zablokowany

**Priorytet:** Wysoki  
**Typ:** Penetracyjny

#### TC-S-015: Fuzzing aplikacji - WFUZZ
**Cel:** Testowanie odporności aplikacji na nieprawidłowe dane

**Narzędzie:** WFUZZ (Kali Linux)

**Polecenia:**
```bash
# Fuzzing parametrów GET
wfuzz -c -z file,/usr/share/wfuzz/wordlist/general/common.txt --hc 404 http://betulait.usermd.net/tickets?FUZZ=test

# Fuzzing hidden directories
wfuzz -c --hc 404 -z file,/usr/share/dirb/wordlists/common.txt http://betulait.usermd.net/FUZZ

# POST parameter fuzzing
wfuzz -c -z file,payloads.txt -d "username=admin&password=FUZZ" http://betulait.usermd.net/login
```

**Oczekiwany rezultat:** Aplikacja obsługuje nieprawidłowe dane bez crashowania

**Priorytet:** Średni  
**Typ:** Penetracyjny

#### TC-S-016: Skanowanie katalogów - Dirb/Gobuster
**Cel:** Wykrywanie ukrytych katalogów i plików

**Narzędzie:** Dirb/Gobuster (Kali Linux)

**Polecenia:**
```bash
# Skanowanie podstawowe - Dirb
dirb http://betulait.usermd.net /usr/share/dirb/wordlists/common.txt

# Skanowanie zaawansowane - Gobuster
gobuster dir -u http://betulait.usermd.net -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt

# Skanowanie plików
gobuster dir -u http://betulait.usermd.net -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,html,txt,js
```

**Oczekiwany rezultat:** Brak dostępu do wrażliwych katalogów i plików

**Priorytet:** Średni  
**Typ:** Penetracyjny

### 7. Testowanie Aplikacji Webowych

#### TC-S-017: Skanowanie podatności OWASP - ZAP
**Cel:** Automatyczne wykrywanie podatności aplikacji webowych

**Narzędzie:** OWASP ZAP (Kali Linux)

**Procedura:**
1. Uruchom ZAP: `zaproxy`
2. Skonfiguruj proxy przeglądarki (127.0.0.1:8080)
3. Przeglądaj aplikację manualnie (spider)
4. Uruchom Active Scan
5. Przeanalizuj wyniki

**Polecenia CLI:**
```bash
# Skanowanie automatyczne
zap-cli quick-scan --self-contained http://betulait.usermd.net

# Skanowanie z raportem
zap-cli quick-scan --self-contained --reportPath zap_report.html http://betulait.usermd.net
```

**Oczekiwany rezultat:** Brak podatności o wysokim i średnim ryzyku

**Priorytet:** Wysoki  
**Typ:** Penetracyjny

#### TC-S-018: Testowanie Burp Suite
**Cel:** Manualne testowanie bezpieczeństwa aplikacji

**Narzędzie:** Burp Suite Community (Kali Linux)

**Procedura testowa:**
1. Skonfiguruj proxy Burp (127.0.0.1:8080)
2. Przechwytuj ruch HTTP/HTTPS
3. Testuj:
   - Parameter manipulation
   - Session management
   - Authentication bypass
   - Input validation

**Oczekiwany rezultat:** Aplikacja odporna na podstawowe ataki

**Priorytet:** Wysoki  
**Typ:** Penetracyjny

#### TC-S-019: Analiza SSL/TLS - SSLyze
**Cel:** Weryfikacja konfiguracji SSL/TLS

**Narzędzie:** SSLyze (Kali Linux)

**Polecenia:**
```bash
# Podstawowa analiza SSL
sslyze betulait.usermd.net

# Szczegółowa analiza
sslyze --regular betulait.usermd.net

# Sprawdzenie podatności
sslyze --heartbleed --openssl_ccs --robot betulait.usermd.net
```

**Oczekiwany rezultat:** Bezpieczna konfiguracja SSL/TLS, brak znanych podatności

**Priorytet:** Średni  
**Typ:** Penetracyjny

#### TC-S-020: Testowanie SQLi - SQLmap
**Cel:** Automatyczne wykrywanie podatności SQL Injection

**Narzędzie:** SQLmap (Kali Linux)

**Polecenia:**
```bash
# Test podstawowy
sqlmap -u "http://betulait.usermd.net/tickets?id=1" --batch

# Test POST parameters
sqlmap -u "http://betulait.usermd.net/login" --data="username=test&password=test" --batch

# Test z cookies
sqlmap -u "http://betulait.usermd.net/profile" --cookie="sessionid=abc123" --batch

# Test z custom headers
sqlmap -u "http://betulait.usermd.net/api/tickets" --headers="Authorization: Bearer token123" --batch
```

**Oczekiwany rezultat:** Brak podatności SQL Injection

**Priorytet:** Krytyczny  
**Typ:** Penetracyjny

### 8. Testowanie Sieci i Infrastruktury

#### TC-S-021: Skanowanie sieci - Netdiscover
**Cel:** Mapowanie sieci i aktywnych hostów

**Narzędzie:** Netdiscover (Kali Linux)

**Polecenia:**
```bash
# Skanowanie pasywne
netdiscover -r 192.168.1.0/24 -P

# Skanowanie aktywne
netdiscover -r 192.168.1.0/24
```

**Oczekiwany rezultat:** Identyfikacja wszystkich hostów w sieci

**Priorytet:** Średni  
**Typ:** Penetracyjny

#### TC-S-022: Analiza ruchu sieciowego - Wireshark
**Cel:** Monitorowanie i analiza komunikacji sieciowej

**Narzędzie:** Wireshark (Kali Linux)

**Procedura:**
1. Uruchom przechwytywanie pakietów
2. Wykonaj operacje w aplikacji
3. Analizuj przechwyconą komunikację:
   - Czy dane są szyfrowane
   - Czy występują niezabezpieczone protokoły
   - Czy hasła są przesyłane w plain text

**Oczekiwany rezultat:** Cała komunikacja zabezpieczona, brak wrażliwych danych w plain text

**Priorytet:** Wysoki  
**Typ:** Penetracyjny

#### TC-S-023: Test Man-in-the-Middle - Ettercap
**Cel:** Weryfikacja odporności na ataki MITM

**Narzędzie:** Ettercap (Kali Linux)

**Polecenia:**
```bash
# ARP Spoofing
ettercap -T -M arp:remote /192.168.1.1/ /192.168.1.100/

# DNS Spoofing
ettercap -T -M arp:remote -P dns_spoof /192.168.1.1/ /192.168.1.100/
```

**Oczekiwany rezultat:** Aplikacja wykrywa lub jest odporna na ataki MITM

**Priorytet:** Średni  
**Typ:** Penetracyjny

### 9. Testowanie Wireless

#### TC-S-024: Audit WiFi - Aircrack-ng Suite
**Cel:** Testowanie bezpieczeństwa sieci bezprzewodowej

**Narzędzia:** Aircrack-ng Suite (Kali Linux)

**Polecenia:**
```bash
# Monitor mode
airmon-ng start wlan0

# Skanowanie sieci
airodump-ng wlan0mon

# Przechwytywanie handshake
airodump-ng -c 6 --bssid AABBCCDDEEFF -w capture wlan0mon

# Testowanie hasła
aircrack-ng -w /usr/share/wordlists/rockyou.txt capture.cap
```

**Oczekiwany rezultat:** WiFi używa silnego szyfrowania i bezpiecznych haseł

**Priorytet:** Niski  
**Typ:** Penetracyjny

---

## Testy Automatyczne

### Framework Testów Automatycznych

Testy automatyczne zostały zaimplementowane przy użyciu **Selenium WebDriver** w języku **Python**. Framework zapewnia automatyzację kluczowych scenariuszy użytkownika.

### Struktura Testów Automatycznych

#### TA-001: test_login()
**Cel:** Automatyczna weryfikacja procesu logowania administratora

**Implementacja:**
- Otwiera stronę logowania
- Wprowadza dane administratora
- Weryfikuje przekierowanie na panel główny

**Kod:**
```python
def test_login():
    driver.get("http://betulait.usermd.net/login")
    driver.find_element(By.NAME, "username").send_keys("admin")
    driver.find_element(By.NAME, "password").send_keys("u9rKvvtfN(VtxjcHfFor")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    assert "dashboard" in driver.current_url
```

#### TA-002: test_create_organization()
**Cel:** Automatyczne tworzenie nowej organizacji

**Implementacja:**
- Logowanie jako administrator
- Wypełnienie formularza organizacji losowymi danymi
- Zatwierdzenie utworzenia

**Kod:**
```python
def test_create_organization():
    login_as_admin()
    driver.find_element(By.LINK_TEXT, "Organizacje").click()
    driver.find_element(By.LINK_TEXT, "Dodaj organizację").click()
    
    org_name = random_string(10)
    driver.find_element(By.NAME, "name").send_keys(org_name)
    driver.find_element(By.NAME, "email").send_keys(f"{org_name}@test.com")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    
    assert org_name in driver.page_source
```

#### TA-003: test_edit_organization()
**Cel:** Automatyczna edycja istniejącej organizacji

**Implementacja:**
- Wybór losowej organizacji z listy
- Edycja danych organizacji
- Zapisanie zmian

**Kod:**
```python
def test_edit_organization():
    login_as_admin()
    driver.find_element(By.LINK_TEXT, "Organizacje").click()
    
    # Wybierz pierwszą organizację
    driver.find_element(By.XPATH, "//table//tr[2]//a").click()
    
    # Edytuj nazwę
    name_field = driver.find_element(By.NAME, "name")
    name_field.clear()
    new_name = random_string(8)
    name_field.send_keys(new_name)
    
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    assert new_name in driver.page_source
```

#### TA-004: test_create_user()
**Cel:** Automatyczna rejestracja nowego użytkownika

**Implementacja:**
- Wypełnienie formularza rejestracji
- Generowanie losowych danych użytkownika
- Przesłanie formularza

**Kod:**
```python
def test_create_user():
    driver.get("http://betulait.usermd.net/register")
    
    username = random_login(8)
    email = f"{username}@test.com"
    
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.NAME, "password1").send_keys("Test123!")
    driver.find_element(By.NAME, "password2").send_keys("Test123!")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    
    assert "rejestracja" in driver.page_source.lower()
```

#### TA-005: accept_user()
**Cel:** Automatyczne zatwierdzanie oczekujących użytkowników

**Implementacja:**
- Przejście do listy oczekujących zatwierdzeń
- Zatwierdzenie nowego użytkownika

**Kod:**
```python
def accept_user():
    login_as_admin()
    driver.find_element(By.LINK_TEXT, "Oczekujące zatwierdzenia").click()
    
    if driver.find_elements(By.XPATH, "//table//tr"):
        driver.find_element(By.XPATH, "//table//tr[2]//a[contains(@href, 'approve')]").click()
        assert "zatwierdzony" in driver.page_source.lower()
```

#### TA-006: login_and_ticket()
**Cel:** Automatyczne tworzenie zgłoszenia przez klienta

**Implementacja:**
- Logowanie jako klient
- Utworzenie nowego zgłoszenia z losowymi danymi
- Wybór kategorii i zatwierdzenie

**Kod:**
```python
def login_and_ticket():
    driver.get("http://betulait.usermd.net/login")
    driver.find_element(By.NAME, "username").send_keys("client1")
    driver.find_element(By.NAME, "password").send_keys("client123")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    
    driver.find_element(By.LINK_TEXT, "Nowe zgłoszenie").click()
    
    title = f"Test zgłoszenie {random_string(5)}"
    driver.find_element(By.NAME, "title").send_keys(title)
    driver.find_element(By.NAME, "description").send_keys("Automatyczne zgłoszenie testowe")
    
    # Wybierz kategorię
    Select(driver.find_element(By.NAME, "category")).select_by_value("technical")
    
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    assert title in driver.page_source
```

#### TA-007: login_agent_and_przypisanie_ticket()
**Cel:** Automatyczne przypisanie zgłoszenia przez agenta

**Implementacja:**
- Logowanie jako agent
- Znalezienie nieprzypisanego zgłoszenia
- Przypisanie zgłoszenia do siebie

**Kod:**
```python
def login_agent_and_przypisanie_ticket():
    driver.get("http://betulait.usermd.net/login")
    driver.find_element(By.NAME, "username").send_keys("agent1")
    driver.find_element(By.NAME, "password").send_keys("agent123")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    
    driver.find_element(By.LINK_TEXT, "Zgłoszenia").click()
    
    # Znajdź nieprzypisane zgłoszenie
    unassigned_tickets = driver.find_elements(By.XPATH, "//tr[td[contains(text(), 'Nieprzypisane')]]")
    if unassigned_tickets:
        unassigned_tickets[0].find_element(By.LINK_TEXT, "Przypisz").click()
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        assert "przypisane" in driver.page_source.lower()
```

#### TA-008: login_admin_and_przypisanie_ticket()
**Cel:** Automatyczne przypisanie zgłoszenia przez administratora

**Implementacja:**
- Logowanie jako administrator
- Znajdowanie zgłoszenia oczekującego na akcję
- Przypisanie do wybranego agenta

**Kod:**
```python
def login_admin_and_przypisanie_ticket():
    login_as_admin()
    driver.find_element(By.LINK_TEXT, "Zgłoszenia").click()
    
    # Znajdź zgłoszenie do przypisania
    tickets = driver.find_elements(By.XPATH, "//tr[td[contains(text(), 'Nowe')]]")
    if tickets:
        tickets[0].find_element(By.LINK_TEXT, "Przypisz").click()
        
        # Wybierz agenta
        Select(driver.find_element(By.NAME, "assigned_to")).select_by_visible_text("agent1")
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        assert "przypisane" in driver.page_source.lower()
```

#### TA-009: login_admin_change_status_ticket()
**Cel:** Automatyczna zmiana statusu zgłoszenia

**Implementacja:**
- Znajdowanie zgłoszenia do zamknięcia
- Zmiana statusu na zamknięte

**Kod:**
```python
def login_admin_change_status_ticket():
    login_as_admin()
    driver.find_element(By.LINK_TEXT, "Zgłoszenia").click()
    
    # Znajdź zgłoszenie do zamknięcia
    tickets = driver.find_elements(By.XPATH, "//tr[td[contains(text(), 'Rozwiązane')]]")
    if tickets:
        tickets[0].find_element(By.LINK_TEXT, "Zamknij").click()
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        assert "zamknięte" in driver.page_source.lower()
```

#### TA-010: login_admin_panel()
**Cel:** Automatyczne zarządzanie panelem administratora

**Implementacja:**
- Dostęp do panelu Django Admin
- Zarządzanie komentarzami i użytkownikami
- Blokowanie/odblokowanie kont

**Kod:**
```python
def login_admin_panel():
    login_as_admin()
    driver.get("http://betulait.usermd.net/admin/")
    
    # Sprawdź dostęp do panelu admin
    assert "Django administration" in driver.page_source
    
    # Przejdź do zarządzania użytkownikami
    driver.find_element(By.LINK_TEXT, "Users").click()
    
    # Sprawdź czy można zarządzać użytkownikami
    assert driver.find_elements(By.XPATH, "//table//tr")
```

#### TA-011: login_client_and_comment_to_random_ticket_and_logout()
**Cel:** Automatyczne dodawanie komentarzy i wylogowanie

**Implementacja:**
- Logowanie jako klient
- Wybór losowego zgłoszenia
- Dodanie komentarza
- Wylogowanie z systemu

**Kod:**
```python
def login_client_and_comment_to_random_ticket_and_logout():
    driver.get("http://betulait.usermd.net/login")
    driver.find_element(By.NAME, "username").send_keys("client1")
    driver.find_element(By.NAME, "password").send_keys("client123")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    
    driver.find_element(By.LINK_TEXT, "Moje zgłoszenia").click()
    
    # Wybierz pierwsze zgłoszenie
    tickets = driver.find_elements(By.XPATH, "//table//tr[position()>1]//a")
    if tickets:
        tickets[0].click()
        
        # Dodaj komentarz
        comment = f"Automatyczny komentarz {random_string(5)}"
        driver.find_element(By.NAME, "content").send_keys(comment)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        
        assert comment in driver.page_source
    
    # Wyloguj się
    driver.find_element(By.LINK_TEXT, "Wyloguj").click()
    assert "login" in driver.current_url
```

### Funkcje Pomocnicze

#### random_string(length=8)
**Cel:** Generuje losowy ciąg znaków o określonej długości

```python
def random_string(length=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))
```

#### random_login(length=8)
**Cel:** Generuje losową nazwę użytkownika

```python
def random_login(length=8):
    return f"user_{random_string(length)}"
```

#### random_phone()
**Cel:** Generuje losowy numer telefonu w formacie polskim

```python
def random_phone():
    return f"+48{random.randint(100000000, 999999999)}"
```

### Uruchamianie Testów Automatycznych

```python
if __name__ == "__main__":
    test_login()
    test_create_organization()
    test_edit_organization()
    test_create_user()
    # accept_user()  # Odkomentować w razie potrzeby
    login_and_ticket()
    login_agent_and_przypisanie_ticket()
    login_and_ticket()
    login_admin_and_przypisanie_ticket()
    login_and_ticket()
    login_admin_change_status_ticket()
    login_admin_panel()
    login_client_and_comment_to_random_ticket_and_logout()
```

---

## Środowisko Testowe

### Konfiguracja Środowiska

#### Środowisko Testowe
- **URL testowy:** `http://betulait.usermd.net`
- **Przeglądarka:** Chrome WebDriver
- **Framework:** Python Selenium WebDriver
- **System operacyjny:** Kali Linux 2023.x (dla testów bezpieczeństwa)
- **Narzędzia penetracyjne:** Pełna kolekcja Kali Linux

#### Dane Testowe
- **Administrator:** `admin` / `u9rKvvtfN(VtxjcHfFor`
- **Agent:** `agent1` / `agent123`
- **Klient:** `client1` / `client123`
- **Superagent:** `superagent` / `[hasło]`

### Wymagania Środowiska

#### Dla testów automatycznych
- **Selenium WebDriver** - automatyzacja przeglądarki
- **ChromeDriver** - sterownik przeglądarki Chrome
- **Python 3.x** - język programowania
- **Stabilne połączenie internetowe** - dostęp do środowiska testowego

#### Dla testów bezpieczeństwa (Kali Linux)
- **Skanowanie portów:** nmap, masscan
- **Testowanie aplikacji web:** nikto, dirb, gobuster, wfuzz
- **Ataki brute-force:** hydra, medusa
- **Analiza SSL/TLS:** sslyze, testssl.sh
- **Testowanie SQLi:** sqlmap
- **Proxy/Intercepting:** Burp Suite, OWASP ZAP
- **Analiza sieci:** wireshark, ettercap, netdiscover
- **Testowanie WiFi:** aircrack-ng suite
- **Słowniki:** rockyou.txt, dirb wordlists, seclists

### Konfiguracja Kali Linux

```bash
# Aktualizacja systemu
sudo apt update && sudo apt upgrade -y

# Instalacja dodatkowych narzędzi
sudo apt install -y zaproxy burpsuite sqlmap

# Przygotowanie słowników
sudo gunzip /usr/share/wordlists/rockyou.txt.gz
```

---

## Metodologia Testów

### Podejście do Testowania

#### 1. Testy Funkcjonalne
- **Weryfikacja wszystkich funkcjonalności** systemu
- **Testowanie ścieżek użytkowników** dla każdej roli
- **Walidacja formularzy** i walidacji danych
- **Testowanie filtrów** i wyszukiwania

#### 2. Testy Bezpieczeństwa
- **Sprawdzenie odporności na ataki** z wykorzystaniem Kali Linux
- **Testowanie uwierzytelniania** i autoryzacji
- **Ochrona przed atakami** XSS, CSRF, SQL Injection
- **Testy penetracyjne** - symulacja rzeczywistych ataków

#### 3. Testy Automatyczne
- **Automatyzacja kluczowych scenariuszy** użytkownika
- **Testy regresji** po każdej zmianie
- **Integracja z CI/CD** - automatyczne uruchamianie
- **Raportowanie wyników** testów

#### 4. Testy Penetracyjne
- **Symulacja rzeczywistych ataków** na system
- **Identyfikacja podatności** bezpieczeństwa
- **Ocena ryzyka** i rekomendacje naprawcze
- **Weryfikacja zgodności** ze standardami bezpieczeństwa

### Metodologia Testów Bezpieczeństwa (Kali Linux)

#### Faza 1: Reconnaissance (Rozpoznanie)
- **Skanowanie portów** (nmap)
- **Mapowanie sieci** (netdiscover)
- **Zbieranie informacji o domenie** (whois, dig)

#### Faza 2: Scanning (Skanowanie)
- **Skanowanie podatności** (nikto, nmap scripts)
- **Fuzzing aplikacji** (wfuzz, gobuster)
- **Analiza SSL/TLS** (sslyze)

#### Faza 3: Enumeration (Wyliczanie)
- **Identyfikacja technologii** (whatweb)
- **Skanowanie katalogów** (dirb, gobuster)
- **Analiza aplikacji** (Burp Suite, ZAP)

#### Faza 4: Exploitation (Eksploitacja)
- **Testowanie SQL Injection** (sqlmap)
- **Ataki brute-force** (hydra)
- **Testowanie XSS i CSRF**

#### Faza 5: Post-Exploitation (Po eksploitacji)
- **Analiza logów bezpieczeństwa**
- **Sprawdzenie eskalacji uprawnień**
- **Testowanie trwałości dostępu**

### Harmonogram Testów

#### Tydzień 1: Testy Funkcjonalne
- **Dni 1-3:** Testy modułów podstawowych
- **Dni 4-5:** Testy ścieżek użytkowników

#### Tydzień 2: Testy Bezpieczeństwa (Kali Linux)
- **Dzień 1:** Skanowanie i reconnaissance
- **Dzień 2:** Testowanie aplikacji webowych
- **Dzień 3:** Ataki brute-force i SQLi
- **Dzień 4:** Analiza SSL/TLS i sieci
- **Dzień 5:** Raportowanie i weryfikacja

#### Tydzień 3: Testy Automatyczne
- **Dni 1-2:** Implementacja testów Selenium
- **Dni 3-4:** Integracja z CI/CD
- **Dzień 5:** Optymalizacja i dokumentacja

### Kryteria Akceptacji

- **Wszystkie testy funkcjonalne** muszą przejść pomyślnie
- **Brak krytycznych podatności** bezpieczeństwa
- **Testy automatyczne** działają stabilnie
- **System spełnia wymagania** wydajnościowe

### Raportowanie Błędów

#### Format Raportu Błędu
1. **Identyfikacja błędu** - opis problemu
2. **Kroki reprodukcji** - jak odtworzyć błąd
3. **Oczekiwany vs rzeczywisty rezultat** - porównanie
4. **Priorytet i wpływ na system** - ocena ważności
5. **Środowisko testowe** - gdzie wystąpił błąd
6. **Załączniki** - screenshoty, logi

#### Przykład Raportu
```
Tytuł: Błąd walidacji w formularzu zgłoszenia
Priorytet: Wysoki
Środowisko: Test
Kroki:
1. Otwórz formularz zgłoszenia
2. Wprowadź tytuł z 200+ znakami
3. Kliknij "Wyślij"
Oczekiwany rezultat: Błąd walidacji długości tytułu
Rzeczywisty rezultat: Formularz zostaje przesłany bez walidacji
```

### Cykl Testowy

#### 1. Planowanie
- **Określenie zakresu** testów
- **Przygotowanie środowiska** testowego
- **Przydział zasobów** i czasu

#### 2. Projektowanie
- **Tworzenie przypadków** testowych
- **Przygotowanie danych** testowych
- **Konfiguracja narzędzi** testowych

#### 3. Wykonanie
- **Uruchomienie testów** zgodnie z planem
- **Dokumentowanie wyników** testów
- **Identyfikacja błędów** i problemów

#### 4. Raportowanie
- **Dokumentacja wyników** testów
- **Raportowanie błędów** do deweloperów
- **Przygotowanie raportu** końcowego

#### 5. Retesty
- **Weryfikacja poprawek** błędów
- **Testy regresji** po zmianach
- **Potwierdzenie naprawy** problemów

---

## Testy Wydajności

### Testy Obciążeniowe

#### TC-P-001: Test równoczesnych użytkowników
**Cel:** Sprawdzenie wydajności systemu przy wielu równoczesnych użytkownikach

**Narzędzie:** JMeter / LoadRunner

**Scenariusz:**
- **Liczba użytkowników:** 100 równoczesnych
- **Czas trwania:** 30 minut
- **Operacje:** Logowanie, tworzenie zgłoszeń, przeglądanie list

**Metryki:**
- **Czas odpowiedzi:** < 2 sekundy
- **Przepustowość:** > 50 żądań/sekundę
- **Wskaźnik błędów:** < 1%

#### TC-P-002: Test obciążenia bazy danych
**Cel:** Sprawdzenie wydajności bazy danych przy dużym obciążeniu

**Scenariusz:**
- **Liczba rekordów:** 100,000 zgłoszeń
- **Operacje:** Wyszukiwanie, filtrowanie, sortowanie
- **Równoczesne zapytania:** 50

**Metryki:**
- **Czas zapytania:** < 500ms
- **Użycie CPU:** < 80%
- **Użycie pamięci:** < 90%

### Testy Skalowalności

#### TC-P-003: Test skalowalności poziomej
**Cel:** Sprawdzenie możliwości skalowania systemu

**Scenariusz:**
- **Dodawanie serwerów** aplikacyjnych
- **Testowanie load balancera**
- **Weryfikacja dystrybucji obciążenia**

#### TC-P-004: Test skalowalności pionowej
**Cel:** Sprawdzenie możliwości zwiększenia zasobów serwera

**Scenariusz:**
- **Zwiększenie RAM** serwera
- **Zwiększenie CPU** serwera
- **Testowanie wydajności** po zmianach

---

## Testy Integracyjne

### Testy API

#### TC-I-001: Test endpointów API
**Cel:** Weryfikacja działania interfejsów API

**Endpointy do testowania:**
- `GET /api/tickets/` - lista zgłoszeń
- `POST /api/tickets/` - tworzenie zgłoszenia
- `PUT /api/tickets/{id}/` - aktualizacja zgłoszenia
- `DELETE /api/tickets/{id}/` - usuwanie zgłoszenia

**Testy:**
- **Walidacja danych** wejściowych
- **Kody odpowiedzi** HTTP
- **Format danych** JSON
- **Autoryzacja** i uwierzytelnianie

#### TC-I-002: Test integracji z bazą danych
**Cel:** Sprawdzenie integracji aplikacji z bazą danych

**Scenariusze:**
- **Tworzenie rekordów** w bazie danych
- **Aktualizacja danych** w bazie danych
- **Usuwanie rekordów** z bazy danych
- **Transakcje** i spójność danych

### Testy Komponentów

#### TC-I-003: Test integracji modułów
**Cel:** Sprawdzenie współdziałania modułów systemu

**Moduły:**
- **Moduł uwierzytelniania** z modułem użytkowników
- **Moduł zgłoszeń** z modułem powiadomień
- **Moduł statystyk** z modułem raportów

---

## Testy Regresji

### Strategia Testów Regresji

#### Automatyczne testy regresji
- **Uruchamianie po każdej zmianie** kodu
- **Testowanie kluczowych funkcjonalności**
- **Weryfikacja nie wprowadzenia** nowych błędów

#### Manualne testy regresji
- **Testowanie zmienionych funkcjonalności**
- **Weryfikacja wpływów** zmian na inne moduły
- **Testowanie integracji** po zmianach

### Kryteria Testów Regresji

#### Wysoki priorytet
- **Funkcjonalności krytyczne** dla biznesu
- **Ścieżki użytkowników** najczęściej używane
- **Funkcjonalności związane** z bezpieczeństwem

#### Średni priorytet
- **Funkcjonalności pomocnicze**
- **Funkcjonalności rzadko używane**
- **Funkcjonalności kosmetyczne**

---

## Raportowanie i Metryki

### Metryki Testowe

#### Pokrycie Testami
- **Pokrycie kodu** - procent linii kodu pokrytych testami
- **Pokrycie funkcjonalności** - procent funkcji przetestowanych
- **Pokrycie ścieżek** - procent ścieżek użytkowników przetestowanych

#### Jakość Testów
- **Liczba znalezionych błędów** (krytyczne, wysokie, średnie, niskie)
- **Czas wykonania testów** - czas potrzebny na wykonanie wszystkich testów
- **Wskaźnik powodzenia testów** - procent testów przechodzących pomyślnie
- **Liczba przypadków testowych** - całkowita liczba przypadków testowych

#### Metryki Bezpieczeństwa (Kali Linux)
- **Liczba zidentyfikowanych podatności** - całkowita liczba znalezionych podatności
- **Poziom ryzyka podatności** (CVSS score) - ocena ryzyka podatności
- **Skuteczność ataków brute-force** - procent udanych ataków brute-force
- **Czas potrzebny na kompromitację** - czas potrzebny na przełamanie zabezpieczeń
- **Pokrycie testami penetracyjnymi** - procent systemu przetestowanego

### Raportowanie z Kali Linux

#### Narzędzia do generowania raportów
```bash
# Nmap XML output
nmap -sV -oX nmap_scan.xml target

# Nikto HTML report
nikto -h target -o nikto_report.html -Format htm

# SQLmap raport
sqlmap --flush-session --batch --report

# ZAP HTML report
zap-cli report -o zap_report.html -f html
```

#### Struktura raportu bezpieczeństwa
1. **Executive Summary** - podsumowanie dla kierownictwa
2. **Metodologia** - użyte narzędzia i techniki
3. **Znalezione podatności** - szczegółowy opis z CVSS
4. **Rekomendacje** - sposoby naprawy
5. **Załączniki** - logi, screenshoty, PoC

### Przykładowy Raport Testowy

#### Podsumowanie Wykonawcze
```
System Helpdesk - Raport Testów
Data: 2024-01-15
Wersja: 1.0.0

Wykonane testy:
- Testy funkcjonalne: 17 przypadków testowych
- Testy bezpieczeństwa: 24 przypadki testowe
- Testy automatyczne: 11 scenariuszy
- Testy penetracyjne: Kali Linux

Wyniki:
- Testy funkcjonalne: 16/17 przeszły (94%)
- Testy bezpieczeństwa: 22/24 przeszły (92%)
- Testy automatyczne: 11/11 przeszły (100%)
- Podatności bezpieczeństwa: 2 średnie, 0 krytycznych

Rekomendacje:
- Naprawić błąd walidacji w formularzu zgłoszenia
- Zaktualizować konfigurację SSL/TLS
- Zaimplementować dodatkowe zabezpieczenia przed XSS
```

---

## Narzędzia Testowe

### Narzędzia do Testów Funkcjonalnych

#### Selenium WebDriver
- **Cel:** Automatyzacja testów przeglądarki
- **Języki:** Python, Java, C#, JavaScript
- **Funkcje:** Automatyzacja UI, testy end-to-end

#### TestNG / JUnit
- **Cel:** Framework testów jednostkowych
- **Funkcje:** Organizacja testów, raportowanie, assertions

#### Postman
- **Cel:** Testowanie API
- **Funkcje:** Testy REST API, automatyzacja, dokumentacja

### Narzędzia do Testów Bezpieczeństwa

#### Kali Linux Suite
- **Nmap** - skanowanie portów i sieci
- **Nikto** - skanowanie aplikacji webowych
- **SQLmap** - testowanie SQL Injection
- **Burp Suite** - testowanie aplikacji webowych
- **OWASP ZAP** - skanowanie podatności
- **Hydra** - ataki brute-force
- **Wireshark** - analiza ruchu sieciowego

#### Narzędzia Specjalistyczne
- **SSLyze** - analiza SSL/TLS
- **Aircrack-ng** - testowanie WiFi
- **Ettercap** - testy MITM
- **Dirb/Gobuster** - skanowanie katalogów

### Narzędzia do Testów Wydajności

#### Apache JMeter
- **Cel:** Testy obciążeniowe
- **Funkcje:** Symulacja użytkowników, testy wydajności

#### LoadRunner
- **Cel:** Testy wydajności enterprise
- **Funkcje:** Zaawansowane testy obciążeniowe

#### Gatling
- **Cel:** Testy wydajności aplikacji webowych
- **Funkcje:** Testy obciążeniowe, raportowanie

---

## Procedury Testowe

### Procedura Uruchamiania Testów

#### 1. Przygotowanie Środowiska
```bash
# Instalacja zależności
pip install selenium pytest

# Konfiguracja ChromeDriver
export PATH=$PATH:/path/to/chromedriver

# Sprawdzenie połączenia
curl -I http://betulait.usermd.net
```

#### 2. Uruchamianie Testów Funkcjonalnych
```bash
# Uruchomienie wszystkich testów funkcjonalnych
python -m pytest tests/functional/ -v

# Uruchomienie konkretnego testu
python -m pytest tests/functional/test_ticket_creation.py -v

# Uruchomienie z raportem
python -m pytest tests/functional/ --html=report.html
```

#### 3. Uruchamianie Testów Bezpieczeństwa
```bash
# Skanowanie portów
nmap -sV -Pn betulait.usermd.net

# Skanowanie aplikacji webowej
nikto -h http://betulait.usermd.net

# Test SQL Injection
sqlmap -u "http://betulait.usermd.net/tickets?id=1" --batch
```

#### 4. Uruchamianie Testów Automatycznych
```bash
# Uruchomienie testów Selenium
python selenium_tests.py

# Uruchomienie z headless mode
python selenium_tests.py --headless

# Uruchomienie konkretnego testu
python selenium_tests.py --test=test_login
```

### Procedura Raportowania Błędów

#### 1. Identyfikacja Błędu
- **Opis problemu** - szczegółowy opis błędu
- **Środowisko** - gdzie wystąpił błąd
- **Wersja** - wersja systemu/testowana

#### 2. Kroki Reprodukcji
- **Kroki krok po kroku** - jak odtworzyć błąd
- **Dane testowe** - jakie dane użyto
- **Warunki wstępne** - co musi być spełnione

#### 3. Oczekiwany vs Rzeczywisty Rezultat
- **Oczekiwany rezultat** - co powinno się stać
- **Rzeczywisty rezultat** - co się faktycznie stało
- **Różnica** - opis różnicy

#### 4. Priorytet i Wpływ
- **Priorytet** - krytyczny, wysoki, średni, niski
- **Wpływ na system** - jak błąd wpływa na system
- **Wpływ na użytkowników** - jak błąd wpływa na użytkowników

#### 5. Załączniki
- **Screenshoty** - obrazy pokazujące błąd
- **Logi** - logi systemowe i aplikacji
- **Pliki** - pliki konfiguracyjne, dane testowe

### Procedura Weryfikacji Poprawek

#### 1. Retest Błędu
- **Wykonanie kroków** reprodukcji błędu
- **Weryfikacja naprawy** - czy błąd został naprawiony
- **Testowanie funkcjonalności** - czy nie wprowadzono nowych błędów

#### 2. Testy Regresji
- **Testowanie powiązanych** funkcjonalności
- **Weryfikacja nie wprowadzenia** nowych błędów
- **Testowanie całego** modułu/systemu

#### 3. Potwierdzenie Naprawy
- **Zamknięcie błędu** w systemie śledzenia
- **Dokumentacja naprawy** - co zostało naprawione
- **Aktualizacja testów** - czy potrzebne są nowe testy

---

*Ostatnia aktualizacja: Styczeń 2025*
