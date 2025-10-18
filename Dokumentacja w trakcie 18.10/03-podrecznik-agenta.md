# 🔧 Podręcznik Agenta

## Spis Treści
1. [Wprowadzenie](#wprowadzenie)
2. [Logowanie i Pierwsze Kroki](#logowanie-i-pierwsze-kroki)
3. [Dashboard Agenta](#dashboard-agenta)
4. [Zarządzanie Zgłoszeniami](#zarządzanie-zgłoszeniami)
5. [Przypisywanie Zgłoszeń](#przypisywanie-zgłoszeń)
6. [Rozwiązywanie Zgłoszeń](#rozwiązywanie-zgłoszeń)
7. [Komunikacja z Klientami](#komunikacja-z-klientami)
8. [Zarządzanie Załącznikami](#zarządzanie-załącznikami)
9. [Statystyki i Raporty](#statystyki-i-raporty)
10. [Najlepsze Praktyki](#najlepsze-praktyki)
11. [Rozwiązywanie Problemów](#rozwiązywanie-problemów)

---

## Wprowadzenie

Podręcznik Agenta zawiera wszystkie informacje potrzebne do efektywnej obsługi zgłoszeń w systemie helpdesk. Jako agent jesteś odpowiedzialny za przyjmowanie, rozwiązywanie i komunikację z klientami w sprawie ich zgłoszeń.

### Uprawnienia Agenta
- ✅ Przyjmowanie zgłoszeń do siebie
- ✅ Rozwiązywanie przypisanych zgłoszeń
- ✅ Dodawanie komentarzy i załączników
- ✅ Zmiana statusów zgłoszeń
- ✅ Komunikacja z klientami
- ✅ Podgląd statystyk wydajności
- ✅ Cofanie przypisania własnych zgłoszeń

### Ograniczenia Agenta
- ❌ Nie może przypisywać zgłoszeń innym agentom
- ❌ Nie może edytować zgłoszeń innych agentów
- ❌ Nie może zarządzać użytkownikami
- ❌ Nie ma dostępu do panelu administracyjnego

---

## Logowanie i Pierwsze Kroki

### 1. Logowanie do Systemu

1. **Otwórz przeglądarkę** i przejdź do adresu systemu
2. **Kliknij "Zaloguj się"**
3. **Wprowadź swoje dane logowania:**
   - Nazwa użytkownika
   - Hasło
4. **Jeśli masz skonfigurowane 2FA:**
   - Otwórz aplikację Google Authenticator
   - Wprowadź kod weryfikacyjny

### 2. Pierwsze Logowanie - Konfiguracja 2FA

**UWAGA:** System wymaga skonfigurowania uwierzytelniania dwuskładnikowego!

1. **Zainstaluj Google Authenticator** na telefonie
2. **Zeskanuj kod QR** wyświetlony na ekranie
3. **Wprowadź kod weryfikacyjny** z aplikacji
4. **Zapisz kod odzyskiwania** w bezpiecznym miejscu

### 3. Sprawdzenie Profilu

1. **Kliknij na swoją nazwę użytkownika** w prawym górnym rogu
2. **Sprawdź swoje dane:**
   - Rola: Agent
   - Organizacje
   - Status zatwierdzenia
3. **Zmień hasło** jeśli to konieczne

---

## Dashboard Agenta

### Przegląd Dashboard

Po zalogowaniu zobaczysz dashboard zawierający:

#### Statystyki Zgłoszeń
- **Nowe** - zgłoszenia oczekujące na obsługę
- **W trakcie** - zgłoszenia aktualnie obsługiwane
- **Nierozwiązane** - zgłoszenia wymagające uwagi
- **Rozwiązane** - zgłoszenia oczekujące na potwierdzenie
- **Zamknięte** - zgłoszenia zakończone

#### Szybkie Akcje
- **Nowe zgłoszenie** - utworzenie zgłoszenia dla klienta
- **Zgłoszenia do potwierdzenia** - jeśli masz rozwiązane zgłoszenia

#### Panele Specjalne dla Agenta

##### Panel 1: Zgłoszenia Przypisane do Mnie
- Lista zgłoszeń przypisanych bezpośrednio do Ciebie
- Status, priorytet i data utworzenia
- Szybki dostęp do szczegółów

##### Panel 2: Zgłoszenia Oczekujące na Akceptację
- Zgłoszenia nieprzypisane do żadnego agenta
- Możliwość przypisania do siebie
- Priorytet i organizacja

### Nawigacja

**Główny pasek nawigacyjny:**
- **Dashboard** - panel główny
- **Zgłoszenia** - lista wszystkich zgłoszeń
- **Organizacje** - przegląd organizacji klientów
- **Zatwierdzanie** - zatwierdzanie nowych użytkowników

---

## Zarządzanie Zgłoszeniami

### Przeglądanie Listy Zgłoszeń

1. **Przejdź do "Zgłoszenia"**
2. **Użyj filtrów** do wyszukiwania:
   - **Status:** Nowe, W trakcie, Rozwiązane, Zamknięte
   - **Priorytet:** Niski, Średni, Wysoki, Krytyczny
   - **Kategoria:** Sprzęt, Oprogramowanie, Sieć, Konto, Inne
   - **Przypisane:** Do mnie, Nieprzypisane
   - **Organizacja:** Wybierz organizację
   - **Data:** Od - do

### Szczegóły Zgłoszenia

Kliknij **"Szczegóły"** przy zgłoszeniu, aby zobaczyć:

#### Informacje Podstawowe
- **Tytuł i opis** zgłoszenia
- **Status** (Nowe, W trakcie, Rozwiązane, Zamknięte)
- **Priorytet** (Niski, Średni, Wysoki, Krytyczny)
- **Kategoria** (Sprzęt, Oprogramowanie, Sieć, Konto, Inne)
- **Organizacja** klienta
- **Data utworzenia** i ostatniej aktualizacji

#### Informacje o Przypisaniu
- **Utworzone przez** - kto zgłosił problem
- **Przypisane do** - aktualny agent odpowiedzialny
- **Data przypisania**

#### Historia Zgłoszenia
- **Komentarze** - wszystkie komentarze w chronologicznej kolejności
- **Zmiany statusu** - historia zmian
- **Załączniki** - pliki dodane przez klientów i agentów

---

## Przypisywanie Zgłoszeń

### Przypisanie Zgłoszenia do Siebie

1. **Znajdź nieprzypisane zgłoszenie** na liście
2. **Kliknij "Szczegóły"**
3. **Kliknij "Przypisz do mnie"**
4. **Potwierdź przypisanie**

**Alternatywnie:**
1. **Użyj filtra "Nieprzypisane"**
2. **Kliknij "Przypisz"** bezpośrednio z listy
3. **Potwierdź akcję**

### Cofanie Przypisania

Jeśli zgłoszenie zostało przypisane do Ciebie przez pomyłkę:

1. **Otwórz zgłoszenie**
2. **Kliknij "Cofnij przypisanie"**
3. **Potwierdź akcję**

**Uwaga:** Możesz cofnąć przypisanie tylko własnych zgłoszeń.

### Przypisywanie Zgłoszeń Innym Agentom

**Ograniczenie:** Jako Agent nie możesz przypisywać zgłoszeń innym agentom. Ta funkcja jest dostępna tylko dla Super Agentów i Administratorów.

---

## Rozwiązywanie Zgłoszeń

### Workflow Rozwiązywania

#### 1. Przyjęcie Zgłoszenia
1. **Przypisz zgłoszenie do siebie**
2. **Zmień status na "W trakcie"**
3. **Przeczytaj dokładnie opis problemu**

#### 2. Analiza Problemu
1. **Sprawdź wszystkie załączniki** od klienta
2. **Przeczytaj historię komentarzy**
3. **Zidentyfikuj przyczynę problemu**
4. **Określ plan rozwiązania**

#### 3. Komunikacja z Klientem
1. **Dodaj komentarz** z informacją o rozpoczęciu pracy
2. **Zadaj dodatkowe pytania** jeśli potrzebujesz więcej informacji
3. **Informuj o postępach** regularnie

#### 4. Implementacja Rozwiązania
1. **Wykonaj niezbędne działania**
2. **Przetestuj rozwiązanie**
3. **Dokumentuj wykonane kroki**

#### 5. Oznaczenie jako Rozwiązane
1. **Dodaj komentarz** z opisem rozwiązania
2. **Zmień status na "Rozwiązane"**
3. **Poczekaj na potwierdzenie** od klienta

#### 6. Zamknięcie Zgłoszenia
1. **Po potwierdzeniu** przez klienta
2. **Zmień status na "Zamknięte"**
3. **Dodaj podsumowanie** jeśli potrzebne

### Zmiana Statusów Zgłoszeń

#### Statusy Dostępne dla Agenta

**Nowe → W trakcie**
- Kliknij **"Rozpocznij pracę"**
- Dodaj komentarz o rozpoczęciu

**W trakcie → Rozwiązane**
- Kliknij **"Oznacz jako rozwiązane"**
- Dodaj szczegółowy opis rozwiązania

**Rozwiązane → Zamknięte**
- Dostępne tylko po potwierdzeniu przez klienta
- Kliknij **"Zamknij zgłoszenie"**

**Zamknięte → W trakcie**
- Jeśli klient zgłosił problem ponownie
- Kliknij **"Otwórz ponownie"**

### Dodawanie Komentarzy

#### Kiedy Dodawać Komentarze

- **Na początku pracy** - informacja o rozpoczęciu
- **Podczas analizy** - pytania do klienta
- **W trakcie rozwiązywania** - informacje o postępach
- **Po rozwiązaniu** - szczegółowy opis rozwiązania
- **W odpowiedzi** na komentarze klienta

#### Jak Dodawać Komentarze

1. **Otwórz zgłoszenie**
2. **Przewiń do sekcji "Komentarze"**
3. **Wpisz treść komentarza**
4. **Kliknij "Dodaj komentarz"**

#### Najlepsze Praktyki Komentarzy

- **Bądź profesjonalny** i uprzejmy
- **Używaj jasnego języka** - unikaj żargonu technicznego
- **Informuj o postępach** regularnie
- **Zadawaj konkretne pytania** jeśli potrzebujesz więcej informacji
- **Podawaj dokładne instrukcje** rozwiązania

---

## Komunikacja z Klientami

### Zasady Komunikacji

#### Ton i Styl
- **Profesjonalny** ale przyjazny
- **Jasny** i zrozumiały
- **Konkretny** - unikaj ogólników
- **Terminowy** - odpowiadaj szybko

#### Struktura Odpowiedzi
1. **Powitanie** i potwierdzenie problemu
2. **Analiza** sytuacji
3. **Plan działania** lub rozwiązanie
4. **Następne kroki**
5. **Zakończenie** z pytaniem czy potrzebna pomoc

### Przykłady Komunikacji

#### Rozpoczęcie Pracy
```
Dzień dobry,

Dziękuję za zgłoszenie problemu z drukarką. Rozpoczynam analizę tego problemu.

Czy mogę prosić o dodatkowe informacje:
- Jakie konkretnie błędy wyświetla drukarka?
- Czy problem występuje przy wszystkich dokumentach?

Będę informować o postępach w pracy.

Pozdrawiam,
[Twoje imię]
```

#### Informacja o Postępach
```
Witam,

Postęp w sprawie zgłoszenia #123:

✅ Sprawdziłem konfigurację drukarki
✅ Zaktualizowałem sterowniki
🔄 Testuję drukowanie różnych dokumentów

Oczekuję wyniku testów w ciągu 30 minut. Poinformuję o rezultatach.

Pozdrawiam,
[Twoje imię]
```

#### Rozwiązanie Problemu
```
Dzień dobry,

Problem został rozwiązany! 

✅ Przyczyna: Przestarzałe sterowniki drukarki
✅ Rozwiązanie: Zaktualizowałem sterowniki do najnowszej wersji
✅ Test: Drukarka działa poprawnie

Proszę przetestować drukowanie i potwierdzić, czy wszystko działa jak należy.

Pozdrawiam,
[Twoje imię]
```

### Obsługa Trudnych Klientów

#### Strategie
- **Słuchaj aktywnie** - pozwól klientowi się wypowiedzieć
- **Potwierdź emocje** - "Rozumiem, że to frustrujące"
- **Skup się na rozwiązaniu** - nie na problemie
- **Bądź cierpliwy** - nie odpowiadaj emocjonalnie
- **Eskaluj jeśli potrzeba** - poproś o pomoc przełożonego

#### Przykład Odpowiedzi
```
Rozumiem Pańską frustrację związaną z tym problemem. Przepraszam za niedogodności.

Zrobię wszystko, co w mojej mocy, aby rozwiązać ten problem jak najszybciej. 
Rozpoczynam natychmiastową analizę i będę informować o każdym kroku.

Czy mogę prosić o dodatkowe informacje, które pomogą mi szybciej zdiagnozować problem?

Pozdrawiam,
[Twoje imię]
```

---

## Zarządzanie Załącznikami

### Dodawanie Załączników

#### Kiedy Dodawać Załączniki
- **Screenshoty** błędów lub problemów
- **Pliki konfiguracyjne** po zmianach
- **Instrukcje** dla klienta
- **Dokumentacja** rozwiązania
- **Logi systemowe** jeśli potrzebne

#### Jak Dodawać Załączniki

1. **Otwórz zgłoszenie**
2. **Przewiń do sekcji "Załączniki"**
3. **Kliknij "Dodaj załącznik"**
4. **Wybierz plik** z komputera
5. **Zaakceptuj regulamin** (zaznacz checkbox)
6. **Kliknij "Prześlij"**

#### Ograniczenia Plików
- **Maksymalny rozmiar:** 10MB
- **Dozwolone typy:** Dokumenty, obrazy, archiwa
- **Szyfrowanie:** Wszystkie pliki są automatycznie szyfrowane

### Pobieranie Załączników Klientów

1. **Znajdź załącznik** w sekcji "Załączniki"
2. **Kliknij nazwę pliku**
3. **Plik zostanie pobrany** i automatycznie odszyfrowany

### Najlepsze Praktyki Załączników

- **Nazywaj pliki opisowo** - "screenshot_bledu_drukarki.png"
- **Kompresuj duże pliki** przed wysłaniem
- **Usuwaj niepotrzebne pliki** po rozwiązaniu
- **Zachowaj kopie** ważnych dokumentów

---

## Statystyki i Raporty

### Dostępne Statystyki

#### Dashboard Statystyk
- **Liczba zgłoszeń** według statusu
- **Średni czas rozwiązywania**
- **Najczęstsze kategorie** problemów
- **Rozkład priorytetów**

#### Statystyki Osobiste
- **Twoje zgłoszenia** - przypisane do Ciebie
- **Rozwiązane w tym miesiącu**
- **Średni czas** rozwiązywania
- **Ocena wydajności**

### Jak Przeglądać Statystyki

1. **Przejdź do "Statystyki"** w menu głównym
2. **Wybierz okres** (dzień, tydzień, miesiąc)
3. **Filtruj według** organizacji lub kategorii
4. **Eksportuj raport** jeśli potrzebny

### Interpretacja Statystyk

#### Wskaźniki Wydajności
- **Czas reakcji** - jak szybko rozpoczynasz pracę
- **Czas rozwiązywania** - jak długo trwa rozwiązanie
- **Wskaźnik sukcesu** - ile zgłoszeń rozwiązujesz bez eskalacji
- **Satysfakcja klientów** - oceny otrzymane od klientów

#### Celowanie w Cele
- **Czas reakcji:** < 2 godziny
- **Czas rozwiązywania:** < 24 godziny (średnio)
- **Wskaźnik sukcesu:** > 90%
- **Satysfakcja:** > 4.5/5

---

## Najlepsze Praktyki

### Organizacja Pracy

#### Priorytetyzacja Zgłoszeń
1. **Krytyczne** - systemy nie działają
2. **Wysokie** - znaczące utrudnienia w pracy
3. **Średnie** - drobne problemy
4. **Niskie** - ulepszenia i prośby

#### Zarządzanie Czasem
- **Sprawdzaj nowe zgłoszenia** co 30 minut
- **Reaguj szybko** na krytyczne problemy
- **Planuj czas** na każde zgłoszenie
- **Informuj o opóźnieniach** z wyprzedzeniem

#### Dokumentacja Pracy
- **Zapisuj wszystkie kroki** w komentarzach
- **Dokumentuj rozwiązania** dla przyszłych podobnych problemów
- **Aktualizuj statusy** regularnie
- **Zamykaj zgłoszenia** po potwierdzeniu

### Komunikacja

#### Z Klientami
- **Odpowiadaj szybko** - najlepiej w ciągu 2 godzin
- **Informuj o postępach** regularnie
- **Używaj jasnego języka** - unikaj żargonu
- **Bądź uprzejmy** i profesjonalny

#### Z Zespołem
- **Komunikuj się** z innymi agentami
- **Proś o pomoc** gdy potrzebujesz
- **Dziel się wiedzą** o rozwiązaniach
- **Eskaluj** trudne przypadki

### Rozwiązywanie Problemów

#### Metodologia
1. **Zrozum problem** - przeczytaj dokładnie opis
2. **Zbierz informacje** - zadaj pytania klientowi
3. **Zdiagnozuj przyczynę** - sprawdź wszystkie możliwości
4. **Zaimplementuj rozwiązanie** - wykonaj niezbędne kroki
5. **Przetestuj** - upewnij się, że działa
6. **Dokumentuj** - zapisz rozwiązanie

#### Narzędzia Diagnostyczne
- **Screenshoty** błędów
- **Logi systemowe**
- **Testy połączeń**
- **Sprawdzanie konfiguracji**
- **Konsultacje z ekspertami**

### Rozwój Zawodowy

#### Ciągłe Uczenie
- **Czytaj dokumentację** techniczną
- **Ucz się nowych technologii**
- **Szkol się** na kursach
- **Obserwuj** doświadczonych agentów

#### Budowanie Wiedzy
- **Twórz bazę wiedzy** z rozwiązaniami
- **Dokumentuj** typowe problemy
- **Dziel się** doświadczeniami z zespołem
- **Proś o feedback** od przełożonych

---

## Rozwiązywanie Problemów

### Najczęstsze Problemy

#### Problem: Nie mogę przypisać zgłoszenia do siebie
**Przyczyna:** Zgłoszenie jest już przypisane do innego agenta.

**Rozwiązanie:**
1. Sprawdź czy zgłoszenie nie jest już przypisane
2. Skontaktuj się z Super Agentem lub Administratorem
3. Poproś o przepisanie zgłoszenia

#### Problem: Nie mogę zmienić statusu zgłoszenia
**Przyczyna:** Brak uprawnień lub błędny workflow.

**Rozwiązanie:**
1. Sprawdź czy zgłoszenie jest przypisane do Ciebie
2. Sprawdź aktualny status zgłoszenia
3. Upewnij się, że wykonujesz prawidłową sekwencję zmian

#### Problem: Klient nie odpowiada na moje pytania
**Przyczyna:** Klient może być niedostępny lub nie sprawdza emaili.

**Rozwiązanie:**
1. Spróbuj skontaktować się telefonicznie
2. Poproś Super Agenta o pomoc w kontakcie
3. Dodaj notatkę o próbach kontaktu
4. Rozważ eskalację do przełożonego

#### Problem: Załącznik nie można pobrać
**Przyczyna:** Problem z szyfrowaniem lub uszkodzony plik.

**Rozwiązanie:**
1. Sprawdź czy masz uprawnienia do załącznika
2. Spróbuj pobrać ponownie
3. Skontaktuj się z Administratorem jeśli problem się powtarza

#### Problem: System działa wolno
**Przyczyna:** Problemy z serwerem lub siecią.

**Rozwiązanie:**
1. Sprawdź połączenie internetowe
2. Odśwież stronę (F5)
3. Wyczyść cache przeglądarki
4. Skontaktuj się z Administratorem

### Kontakt z Wsparciem

#### Kiedy Szukać Pomocy
- **Problemy techniczne** z systemem
- **Trudne przypadki** wymagające ekspertyzy
- **Eskalacja** konfliktów z klientami
- **Problemy z uprawnieniami**

#### Jak Szukać Pomocy
1. **Sprawdź dokumentację** i FAQ
2. **Skontaktuj się z Super Agentem**
3. **Poproś o pomoc** w zespole
4. **Eskaluj do Administratora** w razie potrzeby

#### Informacje do Przekazania
- **Numer zgłoszenia**
- **Opis problemu**
- **Kroki już wykonane**
- **Błędy** lub komunikaty
- **Screenshoty** jeśli potrzebne

---

## Checklist Dzienny

### Na Początek Dnia
- [ ] Sprawdź nowe zgłoszenia
- [ ] Przejrzyj zgłoszenia przypisane do Ciebie
- [ ] Sprawdź czy są pilne sprawy do załatwienia
- [ ] Zaplanuj priorytety na dzień

### W Trakcie Dnia
- [ ] Regularnie sprawdzaj nowe zgłoszenia (co 30 min)
- [ ] Aktualizuj statusy zgłoszeń
- [ ] Odpowiadaj na komentarze klientów
- [ ] Informuj o postępach w pracy
- [ ] Dokumentuj wykonane kroki

### Na Koniec Dnia
- [ ] Sprawdź czy wszystkie zgłoszenia są aktualne
- [ ] Zakończ pracę nad zgłoszeniami jeśli możliwe
- [ ] Przekaż informacje o niedokończonych sprawach
- [ ] Zaktualizuj statusy przed wyjściem

### Tygodniowy Przegląd
- [ ] Przejrzyj statystyki wydajności
- [ ] Sprawdź czy osiągasz cele czasowe
- [ ] Zidentyfikuj obszary do poprawy
- [ ] Zaplanuj rozwój umiejętności

---

*Ostatnia aktualizacja: Styczeń 2025*
