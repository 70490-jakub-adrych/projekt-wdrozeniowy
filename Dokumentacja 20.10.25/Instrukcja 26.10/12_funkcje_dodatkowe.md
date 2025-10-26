# Funkcje Dodatkowe

## 📊 Logi Aktywności

### Dostęp do Logów

**Dostęp:** Admin, Super Agent

Logi aktywności to zapis wszystkich działań w systemie.

### Przeglądanie Logów

1. **Przejdź do Logi aktywności**
   - Kliknij **Logi** w menu nawigacyjnym
2. **Zobaczysz listę akcji:**
   - Logowanie/wylogowanie użytkowników
   - Tworzenie/edycja zgłoszeń
   - Zmiany statusu zgłoszeń
   - Przypisania i reasignacje
   - Dodawanie komentarzy
   - I wiele innych

### Filtrowanie Logów

Możesz filtrować logi według:
- **Typu akcji** - tylko logowania, tylko zgłoszenia itd.
- **Użytkownika** - akcje konkretnego użytkownika
- **Data** - dzisiaj, ten tydzień, ten miesiąc
- **Zgłoszenie** - akcje związane z konkretnym zgłoszeniem

### Szczegóły Logu

Kliknij log aby zobaczyć szczegóły:
- Kto wykonał akcję
- Jaki typ akcji
- Kiedy dokładnie
- Adres IP użytkownika
- Dodatkowe informacje

### Czyszczenie Logów

> ⚠️ **UWAGA:** Czyszczenie logów wymaga weryfikacji 2FA

1. **Przejdź do Logi aktywności**
2. **Kliknij "Wyczyść stare logi"**
3. **Zostaniesz poproszony o kod 2FA**
   - Wprowadź kod z Google Authenticator
4. **Wybierz zakres dat:**
   - Starsze niż X dni
   - Określony zakres dat
5. **Potwierdź czyszczenie**
6. Wybrane logi zostaną usunięte

### Cel Logów

Logi służą do:
- **Śledzenia** działań użytkowników
- **Bezpieczeństwa** - weryfikacja podejrzanych akcji
- **Audytu** - przegląd zgodności z procedurami
- **Rozwiązywania problemów** - analiza błędów

---

## 📈 Statystyki

### Dostęp do Statystyk

**Dostęp:** Admin, Super Agent

### Przegląd Statystyk

1. **Przejdź do Statystyki**
   - Kliknij **Statystyki** w menu
2. **Zobaczysz:**
   - Liczbę otwartych/zamkniętych zgłoszeń
   - Średni czas rozwiązania
   - Wydajność agentów
   - Rozkład po kategoriach
   - Rozkład po priorytetach

### Dostępne Metryki

**Globalne:**
- Całkowita liczba zgłoszeń
- Średni czas rozwiązania
- Wskaźnik sukcesu

**Per Agent:**
- Liczba przypisanych zgłoszeń
- Liczba rozwiązanych zgłoszeń
- Średni czas rozwiązania
- Wydajność

**Per Organizacja:**
- Liczba zgłoszeń
- Średni czas rozwiązania
- Najczęstsze problemy

**Rozkłady:**
- Po kategoriach (sprzęt, oprogramowanie itd.)
- Po priorytetach (krytyczny, wysoki itd.)
- Po statusach (nowe, w trakcie itd.)

### Raporty

System automatycznie generuje raporty:
- **Dzienne** - z dzisiejszego dnia
- **Tygodniowe** - z ostatnich 7 dni
- **Miesięczne** - z ostatniego miesiąca
- **Roczne** - z ostatniego roku

---

## 📧 Powiadomienia Email

### Kiedy Otrzymujesz Powiadomienia

System automatycznie wysyła powiadomienia email o:

**Zgłoszenia:**
- ✅ Utworzenie nowego zgłoszenia
- ✅ Przypisanie zgłoszenia do Ciebie
- ✅ Zmiana statusu zgłoszenia
- ✅ Nowy komentarz w zgłoszeniu
- ✅ Aktualizacja zgłoszenia
- ✅ Zamknięcie zgłoszenia

**Konto:**
- ✅ Zatwierdzenie konta
- ✅ Odrzucenie prośby o dostęp
- ✅ Reset hasła

### Dostosowywanie Powiadomień

Możesz wyłączyć lub dostosować powiadomienia:

1. **Przejdź do ustawień konta** (Panel Django)
2. **Znajdź Email notification settings**
3. **Odznacz** powiadomienia których nie chcesz
4. **Zapisz zmiany**

### Sprawdzanie Powiadomień

- Sprawdzaj email **regularnie**
- Część powiadomień może trafić do **SPAM**
- Ustaw filtry w poczcie aby nie przegapić ważnych emaili

---

## 🤖 Automatyczne Zamykanie Zgłoszeń

### Jak To Działa?

- System **automatycznie zamyka stare zgłoszenia**
- Konfiguracja czasu na zamknięcie jest określana przez administratora
- Zgłoszenia są archiwizowane zamiast usuwane

### Co To Oznacza?

**Po automatycznym zamknięciu:**
- Zgłoszenie zmienia status na "Zamknięte"
- Wszystkie dane są zachowane
- Można je ponownie otworzyć jeśli potrzeba

### Ponowne Otwarcie

Zgłoszenia można ponownie otworzyć:
1. **Otwórz zgłoszenie**
2. **Kliknij "Otwórz ponownie"**
3. **Podaj powód** ponownego otwarcia
4. Zgłoszenie powróci do aktywnych

---

## 🔄 Automatyczne Odświeżanie (Viewer)

### Dla Roli Viewer

Lista zgłoszeń odświeża się **automatycznie co 15 sekund**.

**Korzyści:**
- ✅ Widzisz zawsze aktualny status
- ✅ Nie musisz odświeżać strony ręcznie
- ✅ Real-time monitoring zgłoszeń

### Kontrola

Możesz:
- Włączyć/wyłączyć auto-odświeżanie
- Zmienić interwał (15, 30, 60 sekund)

---

## 📥 Eksport Danych

### Dostępne Eksporty

**Dla Admin/Super Agent:**

**Zgłoszenia:**
- Eksport do CSV
- Eksport do Excel
- Eksport do PDF

**Statystyki:**
- Raporty w formacie PDF
- Wykresy i wykresy
- Dane do dalszej analizy

### Jak Eksportować

1. **Przejdź do Zgłoszenia** lub **Statystyki**
2. **Użyj filtrów** aby zawęzić dane
3. **Kliknij "Eksportuj"**
4. **Wybierz format** (CSV, Excel, PDF)
5. **Pobierz plik**

---

## 🌐 Integracje

### API Systemu

System może oferować API do integracji z innymi systemami.

**Zapytaj administratora** o:
- Dostęp do API
- Dokumentację API
- Klucze dostępowe

---

**Powiązane:**
- [Instrukcje dla Administratora](04_administrator.md)
- [Instrukcje dla Super Agenta](05_superagent.md)
- [Rozwiązywanie Problemów](13_rozwiazywanie_problemow.md)

**Powrót do:** [README.md](README.md)

