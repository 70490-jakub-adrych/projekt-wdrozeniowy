# 🧪 Testy - System Helpdesk

## Przegląd Testów

System Helpdesk posiada kompleksowy plan testów zapewniający wysoką jakość i bezpieczeństwo aplikacji. Testy obejmują funkcjonalność, bezpieczeństwo oraz automatyzację kluczowych procesów.

## 📋 Rodzaje Testów

### 1. Testy Funkcjonalne
- **Testy formularzy** - walidacja danych wejściowych
- **Testy ścieżek użytkowników** - pełne scenariusze dla każdej roli
- **Testy zarządzania zgłoszeniami** - tworzenie, edycja, zamykanie
- **Testy panelu administratora** - zarządzanie użytkownikami i systemem

### 2. Testy Bezpieczeństwa
- **Uwierzytelnianie i autoryzacja** - kontrola dostępu
- **Ochrona przed atakami** - XSS, CSRF, SQL Injection
- **Testy penetracyjne** - z wykorzystaniem Kali Linux
- **Skanowanie podatności** - automatyczne wykrywanie luk

### 3. Testy Automatyczne
- **Selenium WebDriver** - automatyzacja interfejsu użytkownika
- **Testy end-to-end** - pełne scenariusze biznesowe
- **Integracja CI/CD** - automatyczne uruchamianie testów
- **Monitoring wydajności** - testy obciążeniowe

## 🔗 Szczegółowa Dokumentacja

**Pełna dokumentacja testów znajduje się w pliku:** [Testy.md](../../Testy.md)

### Zawartość głównej dokumentacji testów:

#### Testy Funkcjonalne (TC-F-001 do TC-F-017)
- Formularz zgłoszenia
- Panel administratora
- Ścieżka użytkownika: Klient
- Ścieżka użytkownika: Agent/Superagent
- Ścieżka administratora

#### Testy Bezpieczeństwa (TC-S-001 do TC-S-010)
- Uwierzytelnianie i autoryzacja
- Ochrona przed XSS
- Ochrona CSRF
- Ochrona przed wstrzykiwaniem danych
- Skanowanie bezpieczeństwa (Kali Linux)

#### Testy Automatyczne (TA-001 do TA-011)
- Automatyzacja z Selenium
- Testy logowania i rejestracji
- Testy zarządzania zgłoszeniami
- Testy panelu administratora

## 🛠️ Środowisko Testowe

### Konfiguracja
- **URL testowy:** http://betulait.usermd.net/
- **Przeglądarka:** Chrome WebDriver
- **Framework:** Selenium WebDriver
- **System bezpieczeństwa:** Kali Linux 2023.x

### Dane Testowe
- **Administrator:** admin / u9rKvvtfN(VtxjcHfFor
- **Agent:** agent1 / agent123
- **Klient:** client1 / client123
- **Superagent:** superagent / [hasło]

## 📊 Metryki Testowe

### Pokrycie Testami
- **Testy funkcjonalne:** 100% głównych funkcji
- **Testy bezpieczeństwa:** OWASP Top 10
- **Testy automatyczne:** Kluczowe ścieżki użytkowników

### Kryteria Akceptacji
- ✅ Wszystkie testy funkcjonalne przechodzą
- ✅ Brak krytycznych podatności bezpieczeństwa
- ✅ Testy automatyczne działają stabilnie
- ✅ System spełnia wymagania wydajnościowe

## 🚀 Uruchamianie Testów

### Testy Funkcjonalne
```bash
# Ręczne uruchomienie testów
python manage.py test crm.tests
```

### Testy Automatyczne (Selenium)
```bash
# Uruchomienie testów Selenium
python test_automation.py
```

### Testy Bezpieczeństwa (Kali Linux)
```bash
# Skanowanie portów
nmap -sV -Pn target_ip

# Skanowanie podatności
nikto -h target_url

# Testowanie SQL Injection
sqlmap -u "target_url" --batch
```

## 📈 Raportowanie

### Struktura Raportu
1. **Executive Summary** - podsumowanie dla kierownictwa
2. **Metodologia** - użyte narzędzia i techniki
3. **Znalezione podatności** - szczegółowy opis z CVSS
4. **Rekomendacje** - sposoby naprawy
5. **Załączniki** - logi, screenshoty, PoC

### Narzędzia Raportowania
- **Nmap:** XML output dla skanowania portów
- **Nikto:** HTML raporty dla podatności web
- **SQLmap:** Automatyczne raporty SQLi
- **ZAP:** HTML raporty bezpieczeństwa

## 🔄 Cykl Testowy

### 1. Planowanie
- Określenie zakresu testów
- Wybór metodologii
- Przygotowanie środowiska

### 2. Projektowanie
- Tworzenie przypadków testowych
- Przygotowanie danych testowych
- Konfiguracja narzędzi

### 3. Wykonanie
- Uruchomienie testów
- Dokumentacja wyników
- Identyfikacja problemów

### 4. Raportowanie
- Analiza wyników
- Priorytetyzacja problemów
- Rekomendacje napraw

### 5. Retesty
- Weryfikacja poprawek
- Potwierdzenie rozwiązań
- Finalne testy akceptacyjne

## 📚 Dodatkowe Zasoby

### Dokumentacja Testów
- [Testy.md](../../Testy.md) - Pełna dokumentacja testów
- [Troubleshooting](../operacyjna/troubleshooting.md) - Rozwiązywanie problemów
- [Deployment](../wdrozeniowa/deployment.md) - Wdrożenie i konfiguracja

### Narzędzia Testowe
- **Selenium WebDriver** - Automatyzacja testów
- **Kali Linux** - Testy bezpieczeństwa
- **Nmap** - Skanowanie sieci
- **Nikto** - Skanowanie aplikacji web
- **SQLmap** - Testowanie SQL Injection
- **Burp Suite** - Proxy i analiza aplikacji

---

**Ostatnia aktualizacja:** 18.06.2025  
**Link do pełnej dokumentacji:** [Testy.md](../../Testy.md) 