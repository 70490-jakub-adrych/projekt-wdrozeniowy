# 7. Wymagania systemowe

## 7.1 Wymagania sprzętowe

### 7.1.1 Serwer (produkcja)

#### Minimalne wymagania:
- **Procesor:** 2 rdzenie CPU, 2.0 GHz
- **RAM:** 4 GB
- **Dysk:** 20 GB wolnego miejsca
- **Sieć:** Połączenie internetowe (min. 10 Mbps)

#### Zalecane wymagania:
- **Procesor:** 4 rdzenie CPU, 2.5 GHz
- **RAM:** 8 GB
- **Dysk:** 50 GB SSD
- **Sieć:** Połączenie internetowe (min. 100 Mbps)

#### Wymagania dla dużych organizacji:
- **Procesor:** 8 rdzeni CPU, 3.0 GHz
- **RAM:** 16 GB
- **Dysk:** 100 GB SSD
- **Sieć:** Połączenie internetowe (min. 1 Gbps)

### 7.1.2 Stacja robocza (rozwój)

#### Minimalne wymagania:
- **Procesor:** 2 rdzenie CPU, 2.0 GHz
- **RAM:** 4 GB
- **Dysk:** 10 GB wolnego miejsca
- **System operacyjny:** Windows 10, macOS 10.14+, Ubuntu 18.04+

#### Zalecane wymagania:
- **Procesor:** 4 rdzenie CPU, 2.5 GHz
- **RAM:** 8 GB
- **Dysk:** 20 GB SSD
- **System operacyjny:** Windows 11, macOS 12+, Ubuntu 20.04+

## 7.2 Wymagania programowe

### 7.2.1 System operacyjny serwera

#### Linux (zalecane):
- **Ubuntu:** 20.04 LTS lub nowszy
- **CentOS:** 8 lub nowszy
- **Debian:** 10 lub nowszy
- **RHEL:** 8 lub nowszy

#### Windows Server:
- **Windows Server:** 2019 lub nowszy
- **IIS:** 10.0 lub nowszy
- **PowerShell:** 5.1 lub nowszy

### 7.2.2 Oprogramowanie serwera

#### Python:
- **Wersja:** Python 3.8 - 3.12
- **Zalecana:** Python 3.10
- **pip:** Najnowsza wersja

#### Baza danych:
- **MySQL:** 8.0 lub nowszy (zalecane dla produkcji)
- **SQLite:** 3.8+ (dla rozwoju i testowania)
- **PostgreSQL:** 12+ (alternatywa)

#### Serwer web:
- **Apache:** 2.4+ z mod_wsgi
- **Nginx:** 1.18+ z uwsgi
- **Gunicorn:** 20.0+ (dla Python)

### 7.2.3 Zależności Python

#### Główne pakiety:
```
Django==4.2.22
django-crispy-forms>=1.14.0
crispy-bootstrap4>=2022.1
pillow>=9.0.0
python-decouple>=3.6
cryptography>=41.0.0
pyotp>=2.8.0
qrcode>=7.3.1
APScheduler>=3.10.0
django-apscheduler>=0.6.2
```

#### Pakiety do testowania:
```
selenium==4.15.0
pytest==7.4.3
pytest-django==4.7.0
pytest-xvfb==3.0.0
webdriver-manager==4.0.1
pytest-html==4.1.1
pytest-cov==4.1.0
factory-boy==3.3.0
faker==20.1.0
```

#### Pakiety dla produkcji:
```
mysqlclient>=2.1.0  # dla MySQL
psycopg2-binary>=2.9.0  # dla PostgreSQL
gunicorn>=20.0.0  # serwer WSGI
whitenoise>=6.0.0  # obsługa plików statycznych
```

## 7.3 Przeglądarki i platformy obsługiwane

### 7.3.1 Przeglądarki internetowe

#### Pełne wsparcie:
- **Chrome:** 90+ (zalecane)
- **Firefox:** 88+
- **Safari:** 14+
- **Edge:** 90+

#### Ograniczone wsparcie:
- **Internet Explorer:** 11 (nie zalecane)
- **Opera:** 76+

### 7.3.2 Urządzenia mobilne

#### Smartfony:
- **iOS:** 14+ (Safari)
- **Android:** 8+ (Chrome)

#### Tablety:
- **iPad:** iOS 14+
- **Android:** 8+

### 7.3.3 Funkcje wymagane w przeglądarce

#### JavaScript:
- **ES6+** - nowoczesny JavaScript
- **Fetch API** - komunikacja AJAX
- **Local Storage** - przechowywanie preferencji
- **File API** - upload plików

#### CSS:
- **CSS3** - nowoczesne style
- **Flexbox** - układ responsywny
- **Grid** - zaawansowane układy

#### HTML5:
- **Semantic HTML** - struktura strony
- **Form validation** - walidacja formularzy
- **File upload** - przesyłanie plików

## 7.4 Wymagania sieciowe

### 7.4.1 Połączenie internetowe

#### Minimalne:
- **Download:** 5 Mbps
- **Upload:** 2 Mbps
- **Latencja:** < 200ms

#### Zalecane:
- **Download:** 25 Mbps
- **Upload:** 10 Mbps
- **Latencja:** < 100ms

### 7.4.2 Porty sieciowe

#### Porty wymagane:
- **80** - HTTP (przekierowanie na HTTPS)
- **443** - HTTPS (główny port)
- **22** - SSH (zarządzanie serwerem)

#### Porty opcjonalne:
- **8000** - Django development server
- **3306** - MySQL (jeśli zdalny dostęp)

### 7.4.3 Firewall

#### Reguły wymagane:
```bash
# Zezwól na HTTP/HTTPS
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Zezwól na SSH (ograniczone IP)
iptables -A INPUT -p tcp --dport 22 -s TRUSTED_IP -j ACCEPT

# Odrzuć pozostałe połączenia
iptables -A INPUT -j DROP
```

## 7.5 Wymagania bezpieczeństwa

### 7.5.1 Certyfikaty SSL

#### Typ certyfikatu:
- **Let's Encrypt** - darmowy (zalecane)
- **Comodo** - komercyjny
- **DigiCert** - enterprise

#### Wymagania:
- **SHA-256** - algorytm hash
- **2048+ bit** - długość klucza
- **Wildcard** - dla subdomen (opcjonalnie)

### 7.5.2 Kontrola dostępu

#### Uwierzytelnianie:
- **2FA** - uwierzytelnianie dwuskładnikowe
- **Strong passwords** - silne hasła
- **Session timeout** - automatyczne wylogowanie

#### Autoryzacja:
- **Role-based** - kontrola dostępu według ról
- **IP whitelist** - ograniczenie dostępu do IP
- **Rate limiting** - ograniczenie prób logowania

## 7.6 Wymagania wydajnościowe

### 7.6.1 Czas odpowiedzi

#### Cele wydajnościowe:
- **Strona główna:** < 2 sekundy
- **Lista zgłoszeń:** < 3 sekundy
- **Tworzenie zgłoszenia:** < 5 sekund
- **Upload pliku:** < 10 sekund (10MB)

### 7.6.2 Obciążenie

#### Obsługiwane obciążenie:
- **Użytkownicy jednocześnie:** 100+
- **Zgłoszenia dziennie:** 1000+
- **Pliki:** 10MB max na plik
- **Baza danych:** 1GB+ danych

### 7.6.3 Dostępność

#### Cel SLA:
- **Uptime:** 99.5%
- **MTTR:** < 4 godziny
- **Backup:** Codziennie
- **Monitoring:** 24/7

## 7.7 Wymagania zgodności

### 7.7.1 Standardy bezpieczeństwa

#### OWASP Top 10:
- **A01** - Broken Access Control
- **A02** - Cryptographic Failures
- **A03** - Injection
- **A04** - Insecure Design
- **A05** - Security Misconfiguration

#### GDPR (jeśli dotyczy):
- **Anonimizacja danych** - usuwanie danych osobowych
- **Audit trail** - śledzenie dostępu do danych
- **Encryption** - szyfrowanie wrażliwych danych

### 7.7.2 Dostępność

#### WCAG 2.1:
- **Level AA** - podstawowy poziom dostępności
- **Keyboard navigation** - nawigacja klawiaturą
- **Screen readers** - wsparcie dla czytników ekranu
- **Color contrast** - odpowiedni kontrast kolorów
