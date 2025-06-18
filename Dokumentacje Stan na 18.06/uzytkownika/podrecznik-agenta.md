# 👨‍💻 Podręcznik Agenta - System Helpdesk

## Wprowadzenie

Agent to kluczowa rola w systemie helpdesk, odpowiedzialna za obsługę zgłoszeń klientów i zarządzanie procesem wsparcia technicznego. Ten podręcznik zawiera wszystkie niezbędne informacje do efektywnej pracy.

## Panel Agenta

### Dostęp do Systemu
- **URL:** `https://twoja-domena.pl/`
- **Uprawnienia:** Zarządzanie zgłoszeniami, użytkownikami, raporty
- **Bezpieczeństwo:** Wymagane uwierzytelnienie

### Główne Sekcje Panelu

#### 1. Dashboard
- **Przegląd zgłoszeń** - otwarte, w trakcie, zamknięte
- **Statystyki dzienne** - liczba zgłoszeń, czas odpowiedzi
- **Powiadomienia** - nowe zgłoszenia, aktualizacje
- **Szybkie akcje** - tworzenie zgłoszeń, przypisywanie

#### 2. Zarządzanie Zgłoszeniami
- **Lista wszystkich zgłoszeń** z filtrami
- **Tworzenie nowych zgłoszeń**
- **Edycja i aktualizacja** istniejących
- **Przypisywanie** do innych agentów

#### 3. Zarządzanie Użytkownikami
- **Lista użytkowników** w organizacjach
- **Zatwierdzanie rejestracji**
- **Resetowanie haseł**
- **Edycja profili**

## Zarządzanie Zgłoszeniami

### Tworzenie Nowego Zgłoszenia

1. **Przejdź do:** Dashboard → "Nowe zgłoszenie"
2. **Wypełnij dane:**
   - **Tytuł** - krótki opis problemu
   - **Kategoria** - wybierz odpowiednią kategorię
   - **Priorytet** - Low/Medium/High/Critical
   - **Opis** - szczegółowy opis problemu
   - **Klient** - wybierz zgłaszającego
   - **Załączniki** - dodaj pliki (opcjonalnie)
3. **Zapisz:** Kliknij "Utwórz zgłoszenie"

### Edycja Zgłoszenia

1. **Znajdź zgłoszenie:** Użyj filtrów lub wyszukiwania
2. **Otwórz zgłoszenie:** Kliknij na tytuł
3. **Edytuj dane:**
   - Zmień status (Open → In Progress → Closed)
   - Zaktualizuj opis
   - Dodaj komentarze
   - Przypisz do innego agenta
4. **Zapisz zmiany:** Kliknij "Aktualizuj"

### Workflow Zgłoszenia

#### Status: Open (Otwarte)
- **Akcje:** Przypisz do siebie, rozpoczn pracę
- **Czas:** Maksymalnie 2 godziny na rozpoczęcie

#### Status: In Progress (W trakcie)
- **Akcje:** Pracuj nad rozwiązaniem, aktualizuj postęp
- **Komentarze:** Informuj klienta o postępach
- **Czas:** Regularne aktualizacje co 4-8 godzin

#### Status: Closed (Zamknięte)
- **Akcje:** Potwierdź rozwiązanie z klientem
- **Wymagane:** Klient musi potwierdzić rozwiązanie
- **Dokumentacja:** Opisz rozwiązanie w komentarzu

### Komentarze i Komunikacja

#### Dodawanie Komentarzy
1. **Otwórz zgłoszenie**
2. **Przejdź do sekcji:** "Komentarze"
3. **Dodaj komentarz:**
   - **Treść** - opis postępów/rozwiązania
   - **Typ** - Publiczny (widoczny dla klienta) / Wewnętrzny
4. **Wyślij:** Kliknij "Dodaj komentarz"

#### Powiadomienia Email
- **Automatyczne** - przy każdej aktualizacji
- **Szablony** - gotowe wiadomości
- **Personalizacja** - możliwość edycji treści

### Załączniki i Pliki

#### Dodawanie Załączników
1. **W zgłoszeniu:** Kliknij "Dodaj załącznik"
2. **Wybierz plik:** Maksymalny rozmiar 10MB
3. **Oznacz jako wrażliwe:** Jeśli zawiera dane poufne
4. **Dodaj opis:** Krótkie wyjaśnienie zawartości

#### Szyfrowanie Plików
- **Automatyczne** - dla plików oznaczonych jako wrażliwe
- **Bezpieczeństwo** - AES-256 szyfrowanie
- **Dostęp** - tylko uprawnieni użytkownicy

## Zarządzanie Użytkownikami

### Zatwierdzanie Rejestracji

1. **Sprawdź listę:** Dashboard → "Oczekujące rejestracje"
2. **Przejrzyj dane:**
   - Poprawność email
   - Dane organizacji
   - Informacje kontaktowe
3. **Zatwierdź lub odrzuć:** Wybierz akcję
4. **Powiadom użytkownika:** System wyśle email

### Resetowanie Haseł

1. **Znajdź użytkownika:** Lista użytkowników
2. **Wybierz akcję:** "Resetuj hasło"
3. **Potwierdź:** Kliknij "Tak"
4. **Powiadom:** Użytkownik otrzyma email z nowym hasłem

### Edycja Profili

1. **Otwórz profil:** Kliknij na nazwę użytkownika
2. **Edytuj dane:**
   - Informacje kontaktowe
   - Rola w organizacji
   - Status konta
3. **Zapisz zmiany:** Kliknij "Aktualizuj"

## Raporty i Statystyki

### Raporty Dziennicze

1. **Przejdź do:** Dashboard → "Raporty"
2. **Wybierz typ:**
   - **Zgłoszenia dzienne** - liczba i status
   - **Czas odpowiedzi** - średni czas reakcji
   - **Kategorie** - podział według typów problemów
3. **Generuj raport:** Kliknij "Generuj"
4. **Eksportuj:** Pobierz w PDF/CSV

### Statystyki Wydajności

#### Metryki Kluczowe
- **Liczba zgłoszeń** - dzienna/miesięczna
- **Czas rozwiązania** - średni czas
- **Satysfakcja klienta** - oceny rozwiązań
- **Obłożenie** - liczba aktywnych zgłoszeń

#### Analiza Trendów
- **Wzorce** - popularne kategorie problemów
- **Sezonowość** - okresy zwiększonego ruchu
- **Wydajność** - porównanie z poprzednimi okresami

## Najlepsze Praktyki

### Komunikacja z Klientami

#### Zasady Komunikacji
- **Szybka odpowiedź** - maksymalnie 2 godziny
- **Jasny język** - unikaj żargonu technicznego
- **Regularne aktualizacje** - informuj o postępach
- **Profesjonalizm** - zawsze uprzejmy i pomocny

#### Szablony Odpowiedzi
- **Powitanie** - potwierdzenie otrzymania zgłoszenia
- **Postęp** - informacja o aktualnym statusie
- **Rozwiązanie** - opis zastosowanego rozwiązania
- **Zamknięcie** - potwierdzenie zakończenia

### Organizacja Pracy

#### Priorytetyzacja
1. **Critical** - natychmiastowa reakcja
2. **High** - w ciągu 4 godzin
3. **Medium** - w ciągu 8 godzin
4. **Low** - w ciągu 24 godzin

#### Zarządzanie Czasem
- **Bloki czasowe** - dedykowany czas na zgłoszenia
- **Przerwy** - regularne przerwy w pracy
- **Planowanie** - plan na następny dzień

### Dokumentacja

#### Wiedza w Systemie
- **Baza wiedzy** - dokumentuj często występujące problemy
- **Szablony** - gotowe rozwiązania
- **Szkolenia** - dziel się wiedzą z zespołem

#### Rozwiązania
- **Szczegółowe opisy** - jak problem został rozwiązany
- **Kroki** - krok po kroku instrukcje
- **Prewencja** - jak uniknąć problemu w przyszłości

## Rozwiązywanie Problemów

### Częste Problemy

#### Zgłoszenie się nie ładuje
1. **Odśwież stronę** - F5
2. **Sprawdź połączenie** - internet
3. **Wyczyść cache** - Ctrl+F5
4. **Skontaktuj się z adminem** - jeśli problem trwa

#### Email nie wysyłany
1. **Sprawdź adres** - poprawność email
2. **Sprawdź spam** - folder spam
3. **Testuj szablon** - wyślij test
4. **Zgłoś problem** - do administratora

#### Załącznik nie dodaje się
1. **Sprawdź rozmiar** - maksymalnie 10MB
2. **Sprawdź format** - dozwolone typy plików
3. **Spróbuj ponownie** - po kilku minutach
4. **Skontaktuj się z adminem** - jeśli problem trwa

### Escalation (Eskalacja)

#### Kiedy Eskalować
- **Złożone problemy** - wymagające specjalistycznej wiedzy
- **Krytyczne zgłoszenia** - wpływające na biznes
- **Brak postępów** - po 24 godzinach pracy
- **Konflikt z klientem** - problemy komunikacyjne

#### Procedura Eskalacji
1. **Dokumentuj** - szczegółowy opis problemu
2. **Kontaktuj** - przełożonego lub specjalistę
3. **Przekaż** - wszystkie informacje
4. **Śledź** - postęp w rozwiązaniu

---

**Ostatnia aktualizacja:** 18.06.2025 