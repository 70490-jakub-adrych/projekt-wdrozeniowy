# 🎫 System Zarządzania Zgłoszeniami - System Helpdesk

## Przegląd Systemu

System zarządzania zgłoszeniami to serce platformy helpdesk, umożliwiające kompleksowe zarządzanie procesem obsługi zgłoszeń technicznych od momentu utworzenia do finalnego rozwiązania.

## Workflow Zgłoszenia

### 1. Tworzenie Zgłoszenia

#### Kto Może Utworzyć Zgłoszenie
- **Klienci** - zgłaszają problemy techniczne
- **Agenci** - tworzą zgłoszenia telefoniczne lub w imieniu klientów
- **Administratorzy** - pełny dostęp do tworzenia zgłoszeń

#### Proces Tworzenia
1. **Wypełnienie formularza:**
   - Tytuł zgłoszenia (obowiązkowe)
   - Kategoria problemu (obowiązkowe)
   - Priorytet (obowiązkowe)
   - Opis problemu (obowiązkowe)
   - Załączniki (opcjonalne)

2. **Walidacja danych:**
   - Sprawdzenie poprawności email
   - Weryfikacja rozmiaru załączników
   - Walidacja kategorii i priorytetu

3. **Zapisanie zgłoszenia:**
   - Automatyczne przypisanie numeru
   - Ustawienie statusu "Otwarte"
   - Przypisanie do organizacji klienta

### 2. Statusy Zgłoszeń

#### 🔴 Open (Otwarte)
- **Opis:** Zgłoszenie zostało utworzone i czeka na obsługę
- **Akcje dostępne:**
  - Przypisanie do agenta
  - Zmiana priorytetu
  - Dodanie komentarzy
  - Dodanie załączników
- **Czas reakcji:** Maksymalnie 2 godziny

#### 🟡 In Progress (W trakcie)
- **Opis:** Agent pracuje nad rozwiązaniem problemu
- **Akcje dostępne:**
  - Aktualizacja postępów
  - Dodanie komentarzy
  - Zmiana statusu
  - Przypisanie do innego agenta
- **Wymagania:** Regularne aktualizacje co 4-8 godzin

#### 🟢 Closed (Zamknięte)
- **Opis:** Problem został rozwiązany
- **Wymagania:**
  - Potwierdzenie klienta
  - Opis rozwiązania
  - Dokumentacja kroków
- **Możliwość ponownego otwarcia:** Jeśli klient odrzuci rozwiązanie

### 3. Priorytety Zgłoszeń

#### 🚨 Critical (Krytyczny)
- **Czas reakcji:** Natychmiast (maksymalnie 1 godzina)
- **Przykłady:** System nie działa, utrata danych, bezpieczeństwo
- **Eskalacja:** Automatyczna po 30 minutach

#### 🔴 High (Wysoki)
- **Czas reakcji:** 4 godziny
- **Przykłady:** Problemy z logowaniem, błędy aplikacji
- **Eskalacja:** Po 2 godzinach

#### 🟡 Medium (Średni)
- **Czas reakcji:** 8 godzin
- **Przykłady:** Problemy z konfiguracją, pytania użytkowników
- **Eskalacja:** Po 6 godzinach

#### 🟢 Low (Niski)
- **Czas reakcji:** 24 godziny
- **Przykłady:** Sugestie, drobne problemy
- **Eskalacja:** Po 18 godzinach

## Kategorie Problemów

### Predefiniowane Kategorie

#### 🖥️ Hardware (Sprzęt)
- Problemy z komputerami
- Problemy z drukarkami
- Problemy z siecią
- Problemy z urządzeniami peryferyjnymi

#### 💻 Software (Oprogramowanie)
- Problemy z aplikacjami
- Problemy z systemem operacyjnym
- Problemy z licencjami
- Problemy z aktualizacjami

#### 🌐 Network (Sieć)
- Problemy z połączeniem internetowym
- Problemy z VPN
- Problemy z serwerami
- Problemy z bezpieczeństwem sieci

#### 👤 Access (Dostęp)
- Problemy z logowaniem
- Problemy z hasłami
- Problemy z uprawnieniami
- Problemy z kontami użytkowników

#### 📧 Email (Poczta)
- Problemy z wysyłaniem emaili
- Problemy z odbieraniem emaili
- Problemy z kalendarzem
- Problemy z kontaktami

### Zarządzanie Kategoriami

#### Dodawanie Nowej Kategorii
1. **Panel Admin** → Kategorie → Dodaj kategorię
2. **Wypełnij dane:**
   - Nazwa kategorii
   - Opis
   - Kolor (dla interfejsu)
   - Czy aktywna
3. **Zapisz:** Kliknij "Zapisz"

#### Edycja Kategorii
- Zmiana nazwy i opisu
- Zmiana koloru
- Aktywacja/deaktywacja
- Przypisanie agentów specjalistów

## System Komentarzy

### Typy Komentarzy

#### Publiczne (Widoczne dla klienta)
- **Użycie:** Komunikacja z klientem
- **Zawartość:** Postępy, pytania, rozwiązania
- **Powiadomienia:** Email do klienta

#### Wewnętrzne (Tylko dla agentów)
- **Użycie:** Komunikacja między agentami
- **Zawartość:** Notatki, sugestie, eskalacja
- **Powiadomienia:** Tylko dla agentów

### Funkcje Komentarzy

#### Formatowanie
- **Tekst podstawowy** - zwykły tekst
- **Pogrubienie** - **ważne informacje**
- **Kursywa** - *nazwy plików, komendy*
- **Listy** - numerowane i punktowane

#### Załączniki w Komentarzach
- **Obrazy** - zrzuty ekranu
- **Pliki** - dokumenty, logi
- **Linki** - odnośniki do zasobów

#### Powiadomienia
- **Email** - automatyczne powiadomienia
- **W systemie** - licznik nieprzeczytanych
- **SMS** - dla krytycznych zgłoszeń (planowane)

## System Załączników

### Obsługiwane Typy Plików

#### Obrazy
- **Formaty:** JPG, PNG, GIF, BMP
- **Maksymalny rozmiar:** 5MB
- **Użycie:** Zrzuty ekranu, zdjęcia problemów

#### Dokumenty
- **Formaty:** PDF, DOC, DOCX, TXT, RTF
- **Maksymalny rozmiar:** 10MB
- **Użycie:** Dokumentacja, instrukcje, logi

#### Archiwa
- **Formaty:** ZIP, RAR, 7Z
- **Maksymalny rozmiar:** 10MB
- **Użycie:** Zestawy plików, backup

#### Inne
- **Formaty:** CSV, XLS, XLSX
- **Maksymalny rozmiar:** 5MB
- **Użycie:** Raporty, dane

### Bezpieczeństwo Załączników

#### Szyfrowanie Automatyczne
- **Dane wrażliwe** - automatyczne szyfrowanie AES-256
- **Oznaczenie** - checkbox "Dane wrażliwe"
- **Dostęp** - tylko uprawnieni użytkownicy

#### Kontrola Dostępu
- **Organizacje** - klienci widzą tylko swoje pliki
- **Role** - różne poziomy dostępu
- **Audyt** - śledzenie dostępu do plików

#### Walidacja
- **Rozmiar** - sprawdzenie limitów
- **Typ** - weryfikacja dozwolonych formatów
- **Zawartość** - skanowanie wirusów (planowane)

## Automatyzacja

### Automatyczne Powiadomienia

#### Email
- **Nowe zgłoszenie** - potwierdzenie otrzymania
- **Zmiana statusu** - informacja o postępach
- **Nowy komentarz** - powiadomienie o aktualizacji
- **Zamknięcie** - prośba o potwierdzenie

#### Szablony Wiadomości
- **Personalizacja** - imię klienta, numer zgłoszenia
- **Zmienne** - status, kategoria, priorytet
- **Języki** - obsługa wielu języków (planowane)

### Automatyczne Przypisania

#### Inteligentne Przypisanie
- **Kategoria** - przypisanie do specjalisty
- **Obłożenie** - równoważenie obciążenia
- **Umiejętności** - przypisanie według kompetencji

#### Eskalacja Automatyczna
- **Czas** - po przekroczeniu SLA
- **Priorytet** - dla krytycznych zgłoszeń
- **Brak odpowiedzi** - gdy agent nie odpowiada

### Automatyczne Akcje

#### Zamknięcie Zgłoszeń
- **Potwierdzenie klienta** - automatyczne zamknięcie
- **Brak aktywności** - po 7 dniach bez komentarzy
- **Duplikaty** - wykrywanie podobnych zgłoszeń

#### Archiwizacja
- **Stare zgłoszenia** - po 90 dniach
- **Backup** - automatyczne tworzenie kopii
- **Czyszczenie** - usuwanie niepotrzebnych danych

## Raportowanie

### Raporty Standardowe

#### Raporty Dziennicze
- **Liczba zgłoszeń** - utworzonych, zamkniętych
- **Czas odpowiedzi** - średni czas reakcji
- **Kategorie** - podział według typów problemów
- **Agenty** - wydajność poszczególnych agentów

#### Raporty Miesięczne
- **Trendy** - porównanie z poprzednimi miesiącami
- **SLA** - zgodność z umowami o poziomie usług
- **Satysfakcja** - oceny klientów
- **Koszty** - analiza kosztów obsługi

### Metryki Kluczowe (KPI)

#### Czas Reakcji
- **Pierwsza odpowiedź** - czas do pierwszego komentarza
- **Rozwiązanie** - czas do zamknięcia zgłoszenia
- **Eskalacja** - czas do eskalacji

#### Jakość Obsługi
- **Satysfakcja klienta** - oceny rozwiązań
- **Ponowne otwarcie** - liczba ponownie otwartych zgłoszeń
- **Rozwiązanie za pierwszym razem** - FCR (First Call Resolution)

#### Wydajność
- **Zgłoszenia na agenta** - obciążenie pracą
- **Czas pracy** - efektywność agentów
- **Koszty** - koszt obsługi zgłoszenia

### Eksport i Integracja

#### Formaty Eksportu
- **PDF** - raporty do druku
- **Excel** - dane do analizy
- **CSV** - dane do systemów zewnętrznych
- **API** - integracja z innymi systemami

#### Automatyczne Raporty
- **Codzienne** - podsumowanie dnia
- **Tygodniowe** - analiza tygodnia
- **Miesięczne** - raport miesięczny
- **Kwartalne** - analiza kwartału

## Integracje

### Systemy Zewnętrzne

#### Email
- **SMTP** - wysyłanie powiadomień
- **IMAP/POP3** - odbieranie zgłoszeń email
- **Kalendarz** - integracja z kalendarzami

#### Komunikacja
- **SMS** - powiadomienia SMS (planowane)
- **Slack** - integracja z komunikatorami (planowane)
- **Teams** - integracja z Microsoft Teams (planowane)

#### Monitoring
- **Nagios** - integracja z systemami monitoringu
- **Zabbix** - automatyczne zgłoszenia
- **Prometheus** - metryki wydajności

---

**Ostatnia aktualizacja:** 18.06.2025 