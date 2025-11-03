# Instrukcje dla Administratora

## 🎯 Panel Główny

Po zalogowaniu zobaczysz panel główny z przeglądem:

- **Wszystkich zgłoszeń** w systemie
- **Statystyk zgłoszeń** według statusów
- **Oczekujących na zatwierdzenie** użytkowników
- **Logów aktywności**

---

## 👥 Zarządzanie Użytkownikami

### Dodawanie i Edycja Użytkowników

1. Przejdź do **Panel Admina** (ikonka kół zębatych w górnym menu)
2. Wybierz **Użytkownicy**
3. Możesz:
   - **Dodawać** nowych użytkowników
   - **Edytować** istniejących
   - **Zarządzać rolami**
   - **Aktywować/dezaktywować** konta

### Edycja Profilu Użytkownika

1. Otwórz profil użytkownika
2. Zmień dane:
   - login
   - Email
   - Imię i nazwisko
   - Telefon
   - Rola
   - Organizacje
4. Kliknij **Zapisz**

---

## ✅ Zatwierdzanie Kont

### Lista Oczekujących

1. Przejdź do **Oczekujące zatwierdzenia** (link w menu lub powiadomienie)
2. Zobaczysz listę użytkowników oczekujących na aprobatę
3. Dla każdego użytkownika zobaczysz:
   - Imię i nazwisko
   - Email
   - Data rejestracji
   - Przyciski: **Zatwierdź** i **Odrzuć**

### Zatwierdzanie

1. Kliknij **Zatwierdź** obok użytkownika
2. Wybierz **Rolę** dla użytkownika
3. Wybierz **Organizację** użytkownika
4. Potwierdź zatwierdzenie
5. Użytkownik otrzyma email z powiadomieniem

### Odrzucanie

1. Kliknij **Odrzuć** obok użytkownika
2. Uzupełnij powód odrzucenia (opcjonalnie)
3. Potwierdź odrzucenie
4. Użytkownik otrzyma email z informacją

---

## 🔒 Blokowanie/Odblokowanie Kont

### Odblokowanie Konta

1. Przejdź do **Panel Django** → **User profiles**
2. Znajdź użytkownika
3. Edytuj profil
4. Odznacz **Konto zablokowane**
5. W razie potrzeby zresetuj licznik prób logowania

### Ręczne Blokowanie

1. Otwórz profil użytkownika
2. Zaznacz **Konto zablokowane**
3. Możesz podać powód blokady
4. Zapisz zmiany

---

## 🏢 Zarządzanie Organizacjami

### Dodawanie Organizacji

1. Przejdź do **Organizacje**
2. Kliknij **Nowa organizacja**
3. Wypełnij dane:
   - **Nazwa** - wymagane
   - **Email** - opcjonalne
   - **Telefon** - opcjonalne
   - **Strona internetowa** - opcjonalne
   - **Adres** - opcjonalne
   - **Opis** - opcjonalne
4. Kliknij **Zapisz**

### Edycja i Usuwanie

1. Otwórz organizację
2. Kliknij **Edytuj** lub **Usuń**
3. Potwierdź akcję

### Przypisywanie Użytkowników do Organizacji

1. Otwórz organizację lub profil użytkownika
2. W sekcji **Organizacje** zaznacz odpowiednie organizacje
3. Kliknij **Zapisz**

---

## 📊 Dostęp do Logów

### Przeglądanie Logów

1. Przejdź do **Logi aktywności**
2. Zobaczysz listę wszystkich akcji:
   - Logowanie/wylogowanie
   - Tworzenie/edycja zgłoszeń
   - Zmiany statusu
   - I wiele innych
3. **Filtruj** według:
   - Typu akcji
   - Użytkownika
   - Daty
   - Zgłoszenia

### Szczegóły Logu

1. Kliknij log aby zobaczyć szczegóły
2. Zobaczysz:
   - Użytkownika
   - Typ akcji
   - Szczegóły
   - Adres IP
   - Datę i godzinę

### Czyszczenie Logów

> ⚠️ **UWAGA:** Ta akcja wymaga weryfikacji 2FA

1. Przejdź do **Logi aktywności**
2. Kliknij **Wyczyść stare logi**
3. Zostaniesz poproszony o kod 2FA
4. Wybierz zakres dat do czyszczenia
5. Potwierdź akcję

---

## 📧 Zarządzanie Powiadomieniami Email

### Testowanie Wysyłki Email

1. W Panel Django przejdź do **CRM** → **Test email**
2. Wybierz typ emaila do testu
3. Wprowadź adres email odbiorcy
4. Kliknij **Wyślij testowy email**

### Sprawdzanie Konfiguracji

- Przejdź do ustawień systemu w Panel Django
- Sprawdź konfigurację serwera email
- Upewnij się że serwer SMTP działa poprawnie

---

## 🎨 Panel Django (Admin Panel)

Panel Django to główne narzędzie administracyjne.

### Dostępne Sekcje:

- **Users** - zarządzanie użytkownikami
- **User profiles** - profile użytkowników
- **Organizations** - organizacje
- **Tickets** - zgłoszenia
- **Ticket comments** - komentarze
- **Activity logs** - logi aktywności
- **Email verification** - weryfikacja email
- **And more...**

### Filtrowanie i Wyszukiwanie

Użyj filtrów aby szybko znaleźć:
- Konkretnego użytkownika
- Zgłoszenia w określonym statusie
- Logi z określonego dnia

---

**Powiązane:**
- [Zarządzanie Zgłoszeniami](09_zgloszenia.md)
- [Organizacje](10_organizacje.md)
- [Bezpieczeństwo](11_bezpieczenstwo.md)
- [Funkcje Dodatkowe](12_funkcje_dodatkowe.md)

**Powrót do:** [README.md](README.md)


