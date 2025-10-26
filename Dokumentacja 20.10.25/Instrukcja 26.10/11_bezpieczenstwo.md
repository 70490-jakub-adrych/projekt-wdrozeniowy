# Bezpieczeństwo

## 🔐 Uwierzytelnianie Dwuskładnikowe (2FA)

### Co to Jest 2FA?

2FA to dodatkowa warstwa bezpieczeństwa dla Twojego konta. Oprócz hasła, logowanie wymaga specjalnego kodu wygenerowanego przez aplikację na telefonie.

### Dlaczego Jest Ważne?

- ✅ Zabezpiecza przed kradzieżą konta
- ✅ Chroni dane nawet jeśli ktoś pozna Twoje hasło
- ✅ Zalecane dla wszystkich użytkowników
- ✅ Standard branżowy

---

## 📱 Włączanie 2FA

### Krok 1: Przygotowanie

1. **Zainstaluj aplikację** na telefonie:
   - **Google Authenticator** (zalecane)
   - Lub **Microsoft Authenticator**
   
2. **Android:** Google Play Store
   - Wyszukaj "Google Authenticator"
   - Zainstaluj aplikację

3. **iPhone:** App Store
   - Wyszukaj "Google Authenticator"
   - Zainstaluj aplikację

### Krok 2: Włączenie w Systemie

1. **Po zalogowaniu** zobaczysz komunikat o włączeniu 2FA
2. **Kliknij "Włącz 2FA"** lub przejdź do ustawień
3. Zobaczysz **kod QR** do zeskanowania

### Krok 3: Skanowanie Kodu QR

1. **Otwórz aplikację** Google Authenticator
2. **Kliknij "+"** aby dodać konto
3. **Wybierz "Skanuj kod QR"**
4. **Skanuj kod QR** wyświetlony w systemie
5. Aplikacja automatycznie doda konto

### Krok 4: Kod Weryfikacyjny

1. **System poprosi o kod** z aplikacji
2. **Otwórz Google Authenticator**
3. **Znajdź odpowiedni kod** (6 cyfr)
4. **Wprowadź kod**
5. **Kliknij "Potwierdź"**

### Krok 5: Kod Odzyskiwania

> ⚠️ **WAŻNE:** ZAPISZ KOD ODZYSKIWANIA W BEZPIECZNYM MIEJSCU!

1. **System wygeneruje kod odzyskiwania**
2. **Skopiuj kod** i zapisz w bezpiecznym miejscu
3. **Nie udostępniaj** kodu nikomu
4. Kod odzyskiwania pozwala odzyskać dostęp bez aplikacji

---

## 🔑 Logowanie z 2FA

### Standardowy Proces

1. **Wprowadź login i hasło**
2. **Zostaniesz poproszony o kod 2FA**
3. **Otwórz Google Authenticator**
4. **Wprowadź kod** (6 cyfr)
5. **Kliknij "Zaloguj"**

### Zapamiętywanie Urządzenia

- Możesz zaznaczyć **"Zapamiętaj to urządzenie na 30 dni"**
- Przez 30 dni nie będziesz musiał wprowadzać kodu 2FA
- Po 30 dniach ponownie poproszony o kod
- **Zalecane** dla zaufanych urządzeń (dom, biuro)

---

## 🔓 Odzyskiwanie Konta

### Jeśli Utracisz Dostęp Do Aplikacji

Jeśli nie masz dostępu do telefonu z Google Authenticator:

1. **Kliknij "Odzyskaj konto"** na stronie logowania
2. **Wprowadź kod odzyskiwania**
3. **System wyłączy 2FA**
4. Możesz zalogować się normalnie
5. **Włącz 2FA ponownie** po zalogowaniu

### Jeśli Nie Masz Kodu Odzyskiwania

Jeśli nie masz kodu odzyskiwania:
1. **Skontaktuj się z administratorem**
2. Administrator może wyłączyć 2FA dla Twojego konta
3. **Włącz 2FA ponownie** po zalogowaniu

---

## 🔒 Blokada Konta

### Automatyczna Blokada

- Po **5 nieudanych próbach** logowania konto zostaje automatycznie zablokowane
- Chroni przed atakami typu "brute force"
- Zabezpiecza Twoje dane

### Co Po Blokadzie?

1. **Konto jest zablokowane** - nie możesz się zalogować
2. **Skontaktuj się z administratorem**
3. **Administrator może odblokować** Twoje konto
4. **Spróbuj ponownie** po odblokowaniu

### Ręczna Blokada

Administrator może również zablokować Twoje konto ręcznie:
- Ze względów bezpieczeństwa
- W przypadku podejrzeń o nieuprawniony dostęp
- Z innych przyczyn administracyjnych

---

## 🔐 Szyfrowane Załączniki

### Jak Działa Szyfrowanie

- **Wszystkie załączniki są automatycznie szyfrowane**
- Podczas pobierania plik jest automatycznie odszyfrowany
- Tylko uprawnieni użytkownicy mogą je odczytać

### Poziomy Dostępu

**Admin / Super Agent:**
- ✅ Wszystkie załączniki ze wszystkich organizacji
- ✅ Pełny dostęp

**Agent:**
- ✅ Załączniki z jego organizacji
- ✅ Załączniki do przypisanych zgłoszeń

**Klient:**
- ✅ Tylko własne załączniki

### Bezpieczeństwo

- **Nie można** obejść szyfrowania
- **Nie można** pobrać załączników bez uprawnień
- **Wszystkie pliki** są chronione

---

## 👁️ Prywatność Danych

### Co Jest Przechowywane?

System przechowuje:
- ✅ Dane użytkowników (imię, nazwisko, email)
- ✅ Zgłoszenia i ich historie
- ✅ Komentarze i załączniki
- ✅ Logi aktywności

### Dostęp do Danych

- **Tylko uprawnieni** użytkownicy mają dostęp do danych
- **Administratorzy** mogą przeglądać wszystkie dane
- **Logi aktywności** rejestrują wszystkie akcje

### Usuwanie Danych

- Administrator może usunąć dane zgodnie z przepisami
- Zgłoszenia mogą być archiwizowane
- Stare logi mogą być czyszczone (tylko z 2FA)

---

## 🚨 Najlepsze Praktyki

### Bezpieczne Hasła

1. **Minimum 8 znaków**
2. **Używaj wielkich i małych liter**
3. **Dodaj cyfry**
4. **Użyj znaków specjalnych**
5. **Nie używaj** tego samego hasła w różnych miejscach

### Bezpieczne Logowanie

1. **Zawsze wyloguj się** gdy kończysz pracę
2. **Nie zapisuj hasła** w przeglądarce na publicznych komputerach
3. **Używaj zaufanych urządzeń**
4. **Włącz 2FA** jeśli możesz

### Przechowywanie Kodów

1. **Kod odzyskiwania** zapisz w bezpiecznym miejscu
2. **Nie zapisuj** w plikach tekstowych na komputerze
3. **Rozważ** zapisanie w menadżerze haseł
4. **Nigdy nie udostępniaj** kodów innym

---

**Powiązane:**
- [Logowanie](03_logowanie.md)
- [Instrukcje dla Administratora](04_administrator.md)
- [Rozwiązywanie Problemów](13_rozwiazywanie_problemow.md)

**Powrót do:** [README.md](README.md)

