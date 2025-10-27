# Organizacje i Kontakty

## 🏢 Zarządzanie Organizacjami (Admin)

Tylko Administratorzy mogą zarządzać organizacjami.

### Dodawanie Organizacji

1. **Przejdź do Organizacje**
   - Kliknij **Organizacje** w menu
   - Kliknij **Nowa organizacja**

2. **Wypełnij Dane**

   **Nazwa** (wymagane)
   - Nazwa organizacji
   - Przykład: "ABC Sp. z o.o."
   
   **Email** (opcjonalne)
   - Email kontaktowy organizacji
   - Używany do powiadomień zbiorczych
   
   **Telefon** (opcjonalne)
   - Numer telefonu organizacji
   - Format: +48 XXX XXX XXX
   
   **Strona internetowa** (opcjonalne)
   - URL strony www organizacji
   
   **Adres** (opcjonalne)
   - Pełny adres organizacji
   - Ulica, miasto, kod pocztowy
   
   **Opis** (opcjonalne)
   - Dodatkowe informacje o organizacji

3. **Zapisz organizację**
   - Kliknij **Zapisz**
   - Organizacja zostanie dodana

### Edycja Organizacji

1. **Znajdź organizację**
   - Przejdź do listy organizacji
   - Otwórz organizację do edycji

2. **Edytuj dane**
   - Zmień potrzebne informacje
   - Zaktualizuj dane kontaktowe

3. **Zapisz zmiany**
   - Kliknij **Zapisz**
   - Zmiany zostaną zapisane

### Usuwanie Organizacji

> ⚠️ **UWAGA:** Usunięcie organizacji usunie również wszystkie zgłoszenia tej organizacji

1. **Otwórz organizację**
2. **Kliknij Usuń**
3. **Potwierdź usunięcie**
4. Organizacja i jej dane zostaną usunięte

---

## 👥 Przypisywanie Użytkowników do Organizacji

### Z Poziomu Organizacji

1. **Otwórz organizację**
   - Przejdź do listy organizacji
   - Otwórz organizację

2. **Przejdź do sekcji Użytkownicy**
   - Zobaczysz listę aktualnych użytkowników

3. **Dodaj użytkownika**
   - Kliknij **Dodaj użytkownika**
   - Wybierz użytkownika z listy
   - Potwierdź przypisanie

### Z Poziomu Użytkownika

1. **Otwórz profil użytkownika**
   - Przejdź do **Panel Django** → **Users**
   - Otwórz profil użytkownika

2. **Przejdź do sekcji Organizacje**
   - Zobaczysz listę organizacji użytkownika

3. **Dodaj organizację**
   - Zaznacz organizację
   - Zapisz zmiany

### Usuwanie z Organizacji

1. **Otwórz organizację lub profil użytkownika**
2. **Usuń zaznaczenie** przy organizacji
3. **Zapisz zmiany**

---

## 🔗 Wielokrotne Organizacje

### Jak To Działa

Niektóre role mogą należeć do **więcej niż jednej organizacji**:

- **Admin, Super Agent, Agent** - mogą należeć do wielu organizacji i widzieć zgłoszenia ze wszystkich swoich organizacji
- **Klient** - należy do jednej organizacji i widzi zgłoszenia tylko swojej organizacji

---

## 📋 Lista Organizacji

### Przeglądanie Listy

1. **Przejdź do Organizacje**
   - Zobaczysz listę wszystkich organizacji
   - Każda organizacja pokazuje:
     - Nazwę
     - Email
     - Liczbę użytkowników
     - Liczbę zgłoszeń

### Filtrowanie

- **Po nazwie** - wyszukaj organizację
- **Po członkach** - organizacje z najwięcej użytkowników
- **Po zgłoszeniach** - organizacje z najwięcej zgłoszeniami

---

## 👤 Kontakty

> ℹ️ **Uwaga:** Funkcja zarządzania kontaktami może być dostępna w niektórych instalacjach systemu

### Jeśli Dostępne

Funkcja **Kontakty** pozwala na:
- Zarządzanie listą kontaktów
- Szybkie dodawanie kontaktów do zgłoszeń
- Centralną bazę kontaktów organizacji

### Jak Sprawdzić Czy Mam Dostęp?

1. Sprawdź menu nawigacyjne
2. Jeśli widzisz **Kontakty** - masz dostęp
3. Skontaktuj się z administratorem jeśli nie widzisz opcji

---

## 📊 Organizacje i Zgłoszenia

### Statystyki na Organizację

Jako Admin lub Super Agent możesz zobaczyć:
- Ile zgłoszeń ma organizacja
- Jakie są statusy zgłoszeń organizacji
- Jaka jest średnia liczba zgłoszeń na agenta

### Przypisanie Zgłoszeń

Przy tworzeniu zgłoszenia:
- Wybierz organizację z listy
- Każdy klient może tworzyć zgłoszenia tylko dla swojej organizacji
- Agenci widzą zgłoszenia swojej organizacji

---

## 🌟 Najlepsze Praktyki

### Dla Administratorów

**Organizacja Struktury:**
1. Twórz organizacje logicznie
2. Nazywaj organizacje czytelnie
3. Wypełniaj wszystkie dane kontaktowe

**Przypisywanie Użytkowników:**
1. Przypisuj użytkowników do odpowiednich organizacji
2. Sprawdzaj czy użytkownik należy do właściwej org.
3. Regularnie aktualizuj członkostwo

### Dla Użytkowników

**Sprawdzanie Własnej Organizacji:**
1. Sprawdź do której organizacji należysz
2. Twórz zgłoszenia tylko dla swojej organizacji
3. Skontaktuj się z adminem jeśli coś nie gra

---

**Powiązane:**
- [Instrukcje dla Administratora](04_administrator.md)
- [Zarządzanie Zgłoszeniami](09_zgloszenia.md)

**Powrót do:** [README.md](README.md)

