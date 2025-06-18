# 👨‍💼 Podręcznik Administratora - System Helpdesk

## Wprowadzenie

Administrator ma pełny dostęp do systemu i odpowiedzialność za jego prawidłowe funkcjonowanie. Ten podręcznik zawiera wszystkie niezbędne informacje do zarządzania systemem.

## Panel Administracyjny

### Dostęp do Panelu
- **URL:** `https://twoja-domena.pl/admin/`
- **Uprawnienia:** Tylko użytkownicy z rolą Administrator
- **Bezpieczeństwo:** Wymagane uwierzytelnienie dwuskładnikowe

### Główne Sekcje Panelu

#### 1. Zarządzanie Użytkownikami
- **Dodawanie nowych użytkowników**
- **Edycja istniejących kont**
- **Zatwierdzanie rejestracji**
- **Resetowanie haseł**
- **Blokowanie/odblokowywanie kont**

#### 2. Zarządzanie Organizacjami
- **Tworzenie nowych organizacji**
- **Edycja danych firm**
- **Przypisywanie użytkowników do organizacji**
- **Zarządzanie uprawnieniami**

#### 3. Konfiguracja Systemu
- **Kategorie zgłoszeń**
- **Priorytety**
- **Szablony email**
- **Ustawienia bezpieczeństwa**

## Zarządzanie Użytkownikami

### Dodawanie Nowego Użytkownika

1. **Przejdź do:** Panel Admin → Użytkownicy → Dodaj użytkownika
2. **Wypełnij dane:**
   - Imię i nazwisko
   - Email (będzie używany jako login)
   - Hasło (minimum 8 znaków)
   - Organizacja
   - Rola (Admin/Agent/Client/Viewer)
3. **Zatwierdź:** Kliknij "Zapisz"

### Zatwierdzanie Rejestracji

1. **Sprawdź listę oczekujących:** Panel Admin → Użytkownicy → Oczekujący
2. **Przejrzyj dane:** Sprawdź poprawność informacji
3. **Zatwierdź lub odrzuć:** Wybierz odpowiednią akcję
4. **Powiadom użytkownika:** System automatycznie wyśle email

### Resetowanie Hasła

1. **Znajdź użytkownika:** Panel Admin → Użytkownicy → Lista
2. **Wybierz użytkownika:** Kliknij na nazwę
3. **Resetuj hasło:** Kliknij "Resetuj hasło"
4. **Wyślij email:** System wyśle tymczasowe hasło

### Blokowanie Konta

1. **Identyfikuj problem:** Sprawdź logi aktywności
2. **Zablokuj konto:** Panel Admin → Użytkownicy → Zablokuj
3. **Powiadom użytkownika:** Wyślij informację o blokadzie
4. **Ustal przyczynę:** Skontaktuj się z użytkownikiem

## Zarządzanie Organizacjami

### Tworzenie Nowej Organizacji

1. **Przejdź do:** Panel Admin → Organizacje → Dodaj organizację
2. **Wypełnij dane:**
   - Nazwa firmy
   - Adres
   - Telefon kontaktowy
   - Email kontaktowy
3. **Zapisz:** Kliknij "Zapisz"

### Przypisywanie Użytkowników

1. **Wybierz organizację:** Panel Admin → Organizacje → Lista
2. **Dodaj użytkowników:** Kliknij "Dodaj użytkownika"
3. **Wybierz użytkowników:** Z listy dostępnych
4. **Przypisz role:** Określ uprawnienia w organizacji

## Konfiguracja Systemu

### Kategorie Zgłoszeń

1. **Przejdź do:** Panel Admin → Kategorie → Dodaj kategorię
2. **Wypełnij dane:**
   - Nazwa kategorii
   - Opis
   - Kolor (dla interfejsu)
   - Czy aktywna
3. **Zapisz:** Kliknij "Zapisz"

### Szablony Email

1. **Przejdź do:** Panel Admin → Szablony → Lista
2. **Edytuj szablon:** Wybierz odpowiedni szablon
3. **Modyfikuj treść:** Dostosuj wiadomość
4. **Testuj:** Wyślij test do siebie

## Monitoring i Logi

### Logi Aktywności

1. **Przejdź do:** Panel Admin → Logi → Aktywność użytkowników
2. **Filtruj:** Według użytkownika, daty, akcji
3. **Eksportuj:** Pobierz raport w CSV/PDF

### Logi Systemowe

1. **Przejdź do:** Panel Admin → Logi → System
2. **Sprawdź błędy:** Filtruj według poziomu (ERROR/CRITICAL)
3. **Analizuj:** Znajdź przyczyny problemów

### Raporty Wydajności

1. **Przejdź do:** Panel Admin → Raporty → Wydajność
2. **Wybierz okres:** Określ zakres dat
3. **Generuj raport:** Kliknij "Generuj"
4. **Eksportuj:** Pobierz w wybranym formacie

## Bezpieczeństwo

### Ustawienia Bezpieczeństwa

1. **Przejdź do:** Panel Admin → Ustawienia → Bezpieczeństwo
2. **Konfiguruj:**
   - Minimalna długość hasła
   - Liczba nieudanych prób logowania
   - Czas blokady konta
   - Wymagane znaki w haśle

### Backup i Odzyskiwanie

1. **Przejdź do:** Panel Admin → System → Backup
2. **Utwórz backup:** Kliknij "Utwórz backup"
3. **Pobierz plik:** Zapisz lokalnie
4. **Sprawdź integralność:** Zweryfikuj backup

### Audyt Bezpieczeństwa

1. **Przejdź do:** Panel Admin → Bezpieczeństwo → Audyt
2. **Sprawdź:**
   - Nieudane logowania
   - Podejrzane aktywności
   - Zmiany uprawnień
3. **Zgłoś incydenty:** Jeśli wykryto problemy

## Procedury Awaryjne

### Awaria Systemu

1. **Sprawdź logi:** Panel Admin → Logi → System
2. **Zidentyfikuj problem:** Znajdź błąd krytyczny
3. **Zatrzymaj usługi:** Jeśli konieczne
4. **Napraw problem:** Zgodnie z dokumentacją
5. **Uruchom ponownie:** Sprawdź funkcjonalność

### Utrata Danych

1. **Sprawdź backup:** Panel Admin → System → Backup
2. **Przywróć dane:** Z najnowszego backup
3. **Zweryfikuj:** Sprawdź integralność
4. **Powiadom użytkowników:** O problemie i rozwiązaniu

### Atak Bezpieczeństwa

1. **Zablokuj dostęp:** Tymczasowo zablokuj system
2. **Analizuj logi:** Znajdź źródło ataku
3. **Napraw luki:** Usuń podatności
4. **Zmień hasła:** Wymuś zmianę wszystkich haseł
5. **Powiadom:** Zespół bezpieczeństwa

## Najlepsze Praktyki

### Codzienne Operacje
- **Sprawdzaj logi** codziennie rano
- **Monitoruj wydajność** systemu
- **Twórz backup** przed większymi zmianami
- **Testuj funkcjonalność** po aktualizacjach

### Bezpieczeństwo
- **Używaj silnych haseł** i zmieniaj je regularnie
- **Włącz 2FA** dla wszystkich kont admin
- **Monitoruj aktywność** użytkowników
- **Aktualizuj system** regularnie

### Komunikacja
- **Powiadamiaj użytkowników** o planowanych przerwach
- **Dokumentuj zmiany** w systemie
- **Szkol użytkowników** w nowych funkcjach
- **Zbieraj feedback** od użytkowników

---

**Ostatnia aktualizacja:** 18.06.2025 