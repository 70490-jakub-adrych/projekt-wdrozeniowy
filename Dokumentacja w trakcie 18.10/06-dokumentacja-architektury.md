# 🏗️ Dokumentacja Architektury Systemu

## Spis Treści
1. [Wprowadzenie](#wprowadzenie)
2. [Przegląd Architektury](#przegląd-architektury)
3. [Komponenty Systemu](#komponenty-systemu)
4. [Model Bazy Danych](#model-bazy-danych)
5. [Architektura Frontend](#architektura-frontend)
6. [Architektura Backend](#architektura-backend)
7. [Bezpieczeństwo](#bezpieczeństwo)
8. [Integracje](#integracje)
9. [Wydajność i Skalowalność](#wydajność-i-skalowalność)
10. [Deployment i DevOps](#deployment-i-devops)

---

## Wprowadzenie

Dokumentacja architektury systemu helpdesk opisuje strukturę techniczną, komponenty, wzorce projektowe i decyzje architektoniczne zastosowane w systemie. Dokument ten jest przeznaczony dla deweloperów, administratorów systemu i architektów technicznych.

### Cel Dokumentacji
- **Zrozumienie struktury** systemu
- **Planowanie rozwoju** i rozszerzeń
- **Rozwiązywanie problemów** technicznych
- **Onboarding** nowych deweloperów
- **Audyty bezpieczeństwa** i wydajności

### Odbiorcy
- **Deweloperzy** - zrozumienie kodu i architektury
- **Administratorzy** - zarządzanie infrastrukturą
- **Architekci** - planowanie rozszerzeń
- **Audytorzy** - ocena bezpieczeństwa i zgodności

---

## Przegląd Architektury

### Architektura Ogólna

System helpdesk jest zbudowany w oparciu o architekturę **MVC (Model-View-Controller)** z wykorzystaniem frameworka Django, co zapewnia:

- **Separację logiki** biznesowej od prezentacji
- **Modularność** i łatwość rozszerzania
- **Bezpieczeństwo** wbudowane w framework
- **Skalowalność** i wydajność

### Diagram Architektury Ogólnej

```
┌─────────────────────────────────────────────────────────────┐
│                    WARSTWA PREZENTACJI                      │
├─────────────────────────────────────────────────────────────┤
│  Frontend (HTML/CSS/JS)  │  Mobile Responsive  │  Admin   │
├─────────────────────────────────────────────────────────────┤
│                    WARSTWA APLIKACJI                        │
├─────────────────────────────────────────────────────────────┤
│  Django Views  │  Forms  │  Middleware  │  Templates      │
├─────────────────────────────────────────────────────────────┤
│                    WARSTWA LOGIKI BIZNESOWEJ               │
├─────────────────────────────────────────────────────────────┤
│  Models  │  Services  │  Utils  │  Validators  │  Signals  │
├─────────────────────────────────────────────────────────────┤
│                    WARSTWA DANYCH                          │
├─────────────────────────────────────────────────────────────┤
│  Database (SQLite/MySQL)  │  File Storage  │  Cache       │
└─────────────────────────────────────────────────────────────┘
```

### Technologie

#### Backend
- **Python 3.8-3.12** - język programowania
- **Django 4.2.22** - framework webowy
- **SQLite/MySQL** - baza danych
- **APScheduler** - planowanie zadań
- **Cryptography** - szyfrowanie

#### Frontend
- **HTML5/CSS3** - struktura i stylowanie
- **Bootstrap 4** - framework CSS
- **JavaScript** - interaktywność
- **Font Awesome** - ikony
- **Crispy Forms** - formularze

#### Infrastruktura
- **Apache/Nginx** - serwer web
- **mod_wsgi/uWSGI** - interfejs WSGI
- **MySQL** - baza danych produkcyjna
- **SSL/TLS** - szyfrowanie komunikacji

---

## Komponenty Systemu

### 1. Aplikacja CRM (Główna)

#### Struktura Katalogów
```
crm/
├── __init__.py              # Inicjalizacja aplikacji
├── admin.py                 # Konfiguracja panelu administracyjnego
├── apps.py                  # Konfiguracja aplikacji
├── models.py                # Modele danych
├── views.py                 # Główny plik widoków
├── urls.py                  # Routing URL
├── forms.py                 # Formularze Django
├── middleware.py            # Middleware niestandardowe
├── signals.py               # Sygnały Django
├── validators.py            # Walidatory
├── decorators.py            # Dekoratory
├── context_processors.py   # Procesory kontekstu
├── auth_backends.py         # Backend uwierzytelniania
├── scheduler.py             # Planowanie zadań
├── services/                # Usługi biznesowe
│   ├── email/              # Usługi email
│   └── email_service.py    # Główny serwis email
├── views/                   # Widoki podzielone na moduły
│   ├── auth_views.py       # Uwierzytelnianie
│   ├── dashboard_views.py  # Dashboard
│   ├── tickets/            # Zarządzanie zgłoszeniami
│   ├── organization_views.py # Organizacje
│   └── ...
├── templates/              # Szablony HTML
├── static/                 # Pliki statyczne
├── utils/                  # Narzędzia pomocnicze
└── management/             # Komendy Django
```

#### Kluczowe Komponenty

**Models (models.py)**
- `UserProfile` - rozszerzenie użytkownika Django
- `Organization` - organizacje klientów
- `Ticket` - zgłoszenia
- `TicketComment` - komentarze
- `TicketAttachment` - załączniki
- `ActivityLog` - logi aktywności
- `GroupSettings` - ustawienia grup

**Views (views/)**
- Modularna struktura widoków
- Separacja logiki według funkcjonalności
- Wykorzystanie klas i funkcji
- Obsługa AJAX i API

**Services (services/)**
- Logika biznesowa wydzielona z widoków
- Usługi email
- Przetwarzanie danych
- Integracje zewnętrzne

### 2. Projekt Główny (projekt_wdrozeniowy)

#### Struktura
```
projekt_wdrozeniowy/
├── __init__.py
├── settings.py              # Konfiguracja Django
├── urls.py                  # Główny routing
├── wsgi.py                  # WSGI interface
├── asgi.py                  # ASGI interface (przyszłość)
└── manage.py                # Narzędzia zarządzania
```

#### Kluczowe Ustawienia

**settings.py**
- Konfiguracja bazy danych
- Ustawienia bezpieczeństwa
- Konfiguracja email
- Ustawienia statycznych plików
- Middleware i aplikacje
- Logowanie i monitoring

### 3. Komponenty Pomocnicze

#### Middleware
- `ViewerRestrictMiddleware` - ograniczenia dla viewer
- `EmailVerificationMiddleware` - weryfikacja email
- `TwoFactorMiddleware` - obsługa 2FA

#### Signals
- Automatyczne tworzenie profili użytkowników
- Synchronizacja ról z grupami
- Logowanie aktywności

#### Management Commands
- `backup_database` - kopie zapasowe
- `restore_database` - przywracanie
- `auto_close_tickets` - automatyczne zamykanie
- `create_random_tickets` - dane testowe

---

## Model Bazy Danych

### Diagram ERD (Entity Relationship Diagram)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     User        │    │   UserProfile   │    │   Organization │
│ (Django Auth)   │◄──►│                 │◄──►│                 │
│                 │    │ - role          │    │ - name          │
│ - username      │    │ - phone         │    │ - email         │
│ - email         │    │ - is_approved   │    │ - address       │
│ - password      │    │ - 2FA fields    │    │ - description   │
│ - is_active     │    │ - lock fields   │    │ - created_at    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Ticket      │    │ TicketComment   │    │TicketAttachment │
│                 │    │                 │    │                 │
│ - title         │◄──►│ - content       │    │ - file          │
│ - description   │    │ - author        │    │ - filename      │
│ - status        │    │ - created_at    │    │ - uploaded_by   │
│ - priority      │    │ - ticket        │    │ - encryption_key│
│ - category      │    └─────────────────┘    │ - uploaded_at   │
│ - created_by    │                           └─────────────────┘
│ - assigned_to   │
│ - organization  │
│ - created_at    │
│ - resolved_at   │
│ - closed_at     │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  ActivityLog    │
│                 │
│ - user          │
│ - action_type   │
│ - ticket        │
│ - description   │
│ - ip_address    │
│ - created_at    │
└─────────────────┘
```

### Relacje i Ograniczenia

#### Relacje Główne
- **User ↔ UserProfile** - OneToOne (1:1)
- **User ↔ Organization** - ManyToMany (M:N) przez UserProfile
- **Ticket → User** - ForeignKey (N:1) dla created_by i assigned_to
- **Ticket → Organization** - ForeignKey (N:1)
- **TicketComment → Ticket** - ForeignKey (N:1)
- **TicketAttachment → Ticket** - ForeignKey (N:1)

#### Indeksy i Optymalizacje
```python
# Indeksy dla wydajności
class UserProfile(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['trusted_until'], name='idx_trusted_until'),
            models.Index(fields=['ga_enabled'], name='idx_ga_enabled'),
        ]

class TicketStatistics(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['period_type', 'period_start']),
            models.Index(fields=['organization']),
            models.Index(fields=['agent']),
        ]
```

#### Polityki Bezpieczeństwa
- **Soft Delete** - brak usuwania danych
- **Audit Trail** - wszystkie zmiany logowane
- **Szyfrowanie** - załączniki szyfrowane
- **Integralność** - ograniczenia kluczy obcych

### Migracje i Wersjonowanie

#### Struktura Migracji
```
crm/migrations/
├── __init__.py
├── 0001_initial.py
├── 0002_auto_*.py
├── 0003_auto_*.py
└── 0004_set_resolved_at_for_existing.py
```

#### Zarządzanie Migracjami
```bash
# Tworzenie migracji
python manage.py makemigrations

# Zastosowanie migracji
python manage.py migrate

# Sprawdzenie statusu
python manage.py showmigrations

# Wycofanie migracji
python manage.py migrate crm 0003
```

---

## Architektura Frontend

### Struktura Szablonów

```
crm/templates/
├── crm/
│   ├── base.html              # Szablon bazowy
│   ├── dashboard.html         # Dashboard główny
│   ├── login.html             # Logowanie
│   ├── register.html          # Rejestracja
│   ├── tickets/               # Szablony zgłoszeń
│   │   ├── ticket_list.html
│   │   ├── ticket_detail.html
│   │   ├── ticket_form.html
│   │   └── ...
│   ├── organizations/         # Szablony organizacji
│   ├── logs/                  # Szablony logów
│   ├── 2fa/                   # Szablony 2FA
│   └── emails/                # Szablony email
└── admin/                     # Szablony admina
    └── base_site.html
```

### Hierarchia Szablonów

```
base.html (szablon bazowy)
├── {% block title %} - tytuł strony
├── {% block extra_css %} - dodatkowe CSS
├── {% block content %} - główna zawartość
├── {% block extra_js %} - dodatkowe JavaScript
└── {% include %} - komponenty wspólne

└── extends base.html
    ├── dashboard.html
    ├── ticket_list.html
    ├── ticket_detail.html
    └── ...
```

### Responsywność

#### Breakpoints Bootstrap 4
```css
/* Extra small devices (portrait phones) */
@media (max-width: 575.98px) { ... }

/* Small devices (landscape phones) */
@media (min-width: 576px) and (max-width: 767.98px) { ... }

/* Medium devices (tablets) */
@media (min-width: 768px) and (max-width: 991.98px) { ... }

/* Large devices (desktops) */
@media (min-width: 992px) and (max-width: 1199.98px) { ... }

/* Extra large devices (large desktops) */
@media (min-width: 1200px) { ... }
```

#### Strategia Mobile-First
- **Desktop** - pełne tabele z wszystkimi funkcjami
- **Mobile** - karty z kompaktowym układem
- **Adaptacyjne filtry** - desktop vs mobile
- **Touch-friendly** - większe przyciski na mobile

### JavaScript i AJAX

#### Struktura Plików JS
```
crm/static/crm/js/
├── ui-enhancements.js        # Ulepszenia UI
├── password-validation.js    # Walidacja haseł
├── statistics.js            # Statystyki
└── cookie-consent.js        # Zgoda na cookies
```

#### Funkcjonalności AJAX
- **Automatyczne odświeżanie** listy zgłoszeń (viewer)
- **Walidacja formularzy** w czasie rzeczywistym
- **Lazy loading** komponentów
- **Dynamiczne filtry** bez przeładowania strony

### CSS i Stylowanie

#### Struktura CSS
```
crm/static/crm/css/
├── custom-bs5.css           # Niestandardowe style Bootstrap
└── admin/
    └── custom_admin.css     # Style panelu admina
```

#### Metodologia CSS
- **Bootstrap 4** jako framework bazowy
- **Custom CSS** dla specyficznych komponentów
- **CSS Variables** dla spójności kolorów
- **Mobile-first** approach

---

## Architektura Backend

### Wzorce Projektowe

#### MVC Pattern (Django MVT)
```
Model (models.py)     ←→     View (views.py)     ←→     Template (templates/)
     ↓                           ↓                           ↓
  Dane/Biznes                Logika kontrolera            Prezentacja
```

#### Service Layer Pattern
```python
# services/email_service.py
class EmailService:
    def send_notification(self, user, ticket, notification_type):
        # Logika wysyłania emaili
        pass

# views/ticket_views.py
def ticket_create(request):
    # Widok używa serwisu
    email_service = EmailService()
    email_service.send_notification(user, ticket, 'created')
```

#### Repository Pattern (przez Django ORM)
```python
# models.py
class TicketRepository:
    @staticmethod
    def get_user_tickets(user):
        return Ticket.objects.filter(created_by=user)
    
    @staticmethod
    def get_unassigned_tickets():
        return Ticket.objects.filter(assigned_to__isnull=True)
```

### Struktura Widoków

#### Organizacja Widoków
```
views/
├── auth_views.py              # Uwierzytelnianie
├── dashboard_views.py         # Dashboard
├── ticket_views.py           # Główny plik zgłoszeń
├── tickets/                  # Moduł zgłoszeń
│   ├── create_views.py       # Tworzenie
│   ├── detail_views.py       # Szczegóły
│   ├── list_views.py         # Lista
│   ├── update_views.py       # Aktualizacja
│   ├── action_views.py       # Akcje (zamknij, otwórz)
│   ├── assignment_views.py    # Przypisywanie
│   └── unassignment_views.py # Cofanie przypisania
├── organization_views.py     # Organizacje
├── log_views.py              # Logi
├── statistics_views.py       # Statystyki
└── api_views.py             # API endpoints
```

#### Typy Widoków
- **Function-based Views** - proste operacje
- **Class-based Views** - złożona logika
- **API Views** - endpointy JSON
- **AJAX Views** - odpowiedzi AJAX

### Middleware Stack

#### Kolejność Middleware
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',      # Bezpieczeństwo
    'django.contrib.sessions.middleware.SessionMiddleware', # Sesje
    'django.middleware.common.CommonMiddleware',          # Ogólne
    'django.middleware.csrf.CsrfViewMiddleware',         # CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware', # Auth
    'django_otp.middleware.OTPMiddleware',               # 2FA
    'django.contrib.messages.middleware.MessageMiddleware', # Wiadomości
    'crm.middleware.ViewerRestrictMiddleware',            # Ograniczenia viewer
    'crm.middleware.EmailVerificationMiddleware',        # Weryfikacja email
    'crm.middleware.TwoFactorMiddleware',                 # 2FA custom
    'django.middleware.clickjacking.XFrameOptionsMiddleware', # Clickjacking
]
```

#### Custom Middleware
```python
# middleware.py
class ViewerRestrictMiddleware:
    """Ogranicza dostęp viewer do określonych widoków"""
    
class EmailVerificationMiddleware:
    """Wymusza weryfikację email przed dostępem"""
    
class TwoFactorMiddleware:
    """Obsługuje uwierzytelnianie dwuskładnikowe"""
```

### API i Integracje

#### REST API (Ograniczone)
```python
# api_views.py
@api_view(['GET'])
def user_contact_info(request, user_id):
    """API endpoint dla informacji kontaktowych użytkownika"""
    
@api_view(['POST'])
def toggle_theme(request):
    """API endpoint dla przełączania motywu"""
```

#### Webhooks (Przyszłość)
- Integracja z systemami zewnętrznymi
- Powiadomienia w czasie rzeczywistym
- Synchronizacja danych

---

## Bezpieczeństwo

### Architektura Bezpieczeństwa

#### Warstwy Bezpieczeństwa
```
┌─────────────────────────────────────────┐
│           WARSTWA APLIKACJI             │
├─────────────────────────────────────────┤
│  • 2FA (Google Authenticator)          │
│  • Role-based Access Control (RBAC)    │
│  • Session Management                  │
│  • CSRF Protection                     │
├─────────────────────────────────────────┤
│           WARSTWA FRAMEWORKA            │
├─────────────────────────────────────────┤
│  • Django Security Middleware          │
│  • Password Hashing (PBKDF2)           │
│  • SQL Injection Protection            │
│  • XSS Protection                      │
├─────────────────────────────────────────┤
│           WARSTWA INFRASTRUKTURY        │
├─────────────────────────────────────────┤
│  • HTTPS/TLS Encryption               │
│  • Firewall Rules                      │
│  • Server Hardening                    │
│  • Database Security                   │
└─────────────────────────────────────────┘
```

### Uwierzytelnianie i Autoryzacja

#### 2FA Implementation
```python
# models.py
class UserProfile(models.Model):
    ga_enabled = models.BooleanField(default=False)
    ga_secret_key = models.CharField(max_length=64, blank=True)
    ga_recovery_hash = models.CharField(max_length=128, blank=True)
    trusted_ip = models.GenericIPAddressField(null=True, blank=True)
    trusted_until = models.DateTimeField(null=True, blank=True)
```

#### RBAC (Role-Based Access Control)
```python
# Role hierarchy
ADMIN > SUPERAGENT > AGENT > CLIENT > VIEWER

# Permission matrix
ROLE_PERMISSIONS = {
    'admin': ['all'],
    'superagent': ['assign_tickets', 'manage_team', 'view_stats'],
    'agent': ['assign_self', 'resolve_tickets', 'view_own_stats'],
    'client': ['create_tickets', 'view_own_tickets'],
    'viewer': ['view_tickets_only']
}
```

### Szyfrowanie Danych

#### Szyfrowanie Załączników
```python
# models.py
from cryptography.fernet import Fernet

class TicketAttachment(models.Model):
    encryption_key = models.BinaryField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.encryption_key:
            self.encryption_key = Fernet.generate_key()
            # Szyfrowanie zawartości pliku
            fernet = Fernet(self.encryption_key)
            encrypted_content = fernet.encrypt(file_content)
```

#### Hashowanie Haseł
```python
# Django używa PBKDF2 z domyślnie
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',
]
```

### Ochrona przed Atakami

#### CSRF Protection
```python
# Automatyczna ochrona Django
MIDDLEWARE = [
    'django.middleware.csrf.CsrfViewMiddleware',
]

# W szablonach
{% csrf_token %}
```

#### XSS Protection
```python
# Automatyczna ochrona Django
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# W szablonach
{{ user_input|escape }}
```

#### SQL Injection Protection
```python
# Django ORM automatycznie chroni przed SQL injection
# Zamiast:
# cursor.execute("SELECT * FROM users WHERE id = %s" % user_id)

# Używaj:
User.objects.filter(id=user_id)
```

### Logowanie i Audyt

#### Activity Logging
```python
# models.py
class ActivityLog(models.Model):
    ACTION_TYPES = (
        ('login', 'Zalogowanie'),
        ('ticket_created', 'Utworzenie zgłoszenia'),
        ('ticket_updated', 'Aktualizacja zgłoszenia'),
        # ...
    )
```

#### Security Headers
```python
# settings.py
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 31536000
X_FRAME_OPTIONS = 'DENY'
```

---

## Integracje

### Email Integration

#### SMTP Configuration
```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

#### Email Templates
```
templates/emails/
├── password_reset_email.html
├── ticket_created_notification.html
├── ticket_status_changed.html
├── new_comment_notification.html
└── account_approved.html
```

### Database Integration

#### Multi-Database Support
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Development
        # 'ENGINE': 'django.db.backends.mysql',  # Production
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

#### Database Optimization
```python
# Query optimization
tickets = Ticket.objects.select_related('created_by', 'assigned_to', 'organization')
tickets = Ticket.objects.prefetch_related('comments', 'attachments')
```

### File Storage

#### Media Files
```python
# settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'public', 'media')

# Secure file serving
def serve_attachment(request, attachment_id):
    # Sprawdzenie uprawnień
    # Deszyfrowanie pliku
    # Bezpieczne serwowanie
```

### External APIs (Przyszłość)

#### Planned Integrations
- **LDAP/Active Directory** - uwierzytelnianie
- **Slack/Teams** - powiadomienia
- **Jira** - synchronizacja zgłoszeń
- **Monitoring Systems** - integracja z systemami monitoringu

---

## Wydajność i Skalowalność

### Optymalizacja Wydajności

#### Database Optimization
```python
# Indeksy dla często używanych zapytań
class Ticket(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['created_at']),
            models.Index(fields=['assigned_to', 'status']),
        ]

# Query optimization
def get_user_tickets(user):
    return Ticket.objects.select_related(
        'created_by', 'assigned_to', 'organization'
    ).prefetch_related(
        'comments', 'attachments'
    ).filter(created_by=user)
```

#### Caching Strategy
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# View-level caching
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # 15 minutes
def ticket_list(request):
    # Cached view
```

#### Static Files Optimization
```python
# settings.py
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Compression
MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware',
]
```

### Skalowalność

#### Horizontal Scaling
- **Load Balancer** - dystrybucja ruchu
- **Multiple App Servers** - wiele instancji aplikacji
- **Database Replication** - replikacja bazy danych
- **CDN** - dystrybucja plików statycznych

#### Vertical Scaling
- **More CPU Cores** - więcej procesorów
- **More RAM** - więcej pamięci
- **SSD Storage** - szybsze dyski
- **Database Optimization** - optymalizacja bazy

### Monitoring i Profiling

#### Performance Monitoring
```python
# Django Debug Toolbar (development)
INSTALLED_APPS = [
    'debug_toolbar',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]
```

#### Logging Configuration
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

---

## Deployment i DevOps

### Deployment Architecture

#### Production Stack
```
┌─────────────────────────────────────────┐
│              LOAD BALANCER              │
│            (Nginx/HAProxy)             │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────┴───────────────────────┐
│              WEB SERVERS                │
│         (Apache/Nginx + mod_wsgi)       │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────┴───────────────────────┐
│            APPLICATION SERVERS          │
│              (Django Apps)               │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────┴───────────────────────┐
│            DATABASE SERVERS             │
│            (MySQL Cluster)             │
└─────────────────────────────────────────┘
```

#### Environment Configuration
```python
# settings.py
import os
from decouple import config

# Environment-based configuration
DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY')
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': config('DB_NAME', default=BASE_DIR / 'db.sqlite3'),
        'USER': config('DB_USER', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default=''),
        'PORT': config('DB_PORT', default=''),
    }
}
```

### CI/CD Pipeline

#### Continuous Integration
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.10
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          python manage.py test
      - name: Run linting
        run: |
          flake8 .
```

#### Deployment Scripts
```bash
#!/bin/bash
# deploy.sh

# Backup current version
python manage.py backup_database --format=sql

# Pull latest code
git pull origin main

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart services
sudo systemctl restart apache2
sudo systemctl restart celery  # if using Celery
```

### Infrastructure as Code

#### Docker Configuration
```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "projekt_wdrozeniowy.wsgi:application", "--bind", "0.0.0.0:8000"]
```

#### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DB_ENGINE=django.db.backends.mysql
      - DB_NAME=helpdesk_db
    depends_on:
      - db
      - redis

  db:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: helpdesk_db
      MYSQL_ROOT_PASSWORD: rootpassword
    volumes:
      - mysql_data:/var/lib/mysql

  redis:
    image: redis:alpine

volumes:
  mysql_data:
```

### Backup and Recovery

#### Automated Backups
```bash
#!/bin/bash
# backup.sh

# Database backup
python manage.py backup_database --format=sql --rotate=7

# File backup
tar -czf backups/files/backup_$(date +%Y%m%d_%H%M%S).tar.gz public/media/

# Cleanup old backups
find backups/ -name "*.gz" -mtime +30 -delete
```

#### Disaster Recovery
```bash
#!/bin/bash
# restore.sh

# Stop services
sudo systemctl stop apache2

# Restore database
python manage.py restore_database backups/database/latest.sql.gz

# Restore files
tar -xzf backups/files/latest.tar.gz

# Start services
sudo systemctl start apache2
```

---

## Przyszłe Rozszerzenia

### Planned Features

#### Real-time Features
- **WebSocket Integration** - powiadomienia w czasie rzeczywistym
- **Live Chat** - czat z zespołem IT
- **Real-time Updates** - automatyczne odświeżanie bez AJAX

#### Advanced Integrations
- **LDAP/AD Integration** - uwierzytelnianie korporacyjne
- **API Gateway** - centralne API dla integracji
- **Microservices** - podział na mniejsze serwisy

#### AI/ML Features
- **Smart Categorization** - automatyczne kategoryzowanie zgłoszeń
- **Predictive Analytics** - przewidywanie problemów
- **Chatbot Integration** - automatyczna obsługa podstawowych zgłoszeń

### Technical Debt

#### Areas for Improvement
- **Test Coverage** - zwiększenie pokrycia testami
- **API Documentation** - automatyczna dokumentacja API
- **Performance Monitoring** - zaawansowane monitorowanie
- **Security Auditing** - regularne audyty bezpieczeństwa

#### Refactoring Opportunities
- **Service Layer** - wydzielenie większej logiki biznesowej
- **Caching Strategy** - implementacja zaawansowanego cache'owania
- **Database Optimization** - optymalizacja zapytań i indeksów

---

*Ostatnia aktualizacja: Styczeń 2025*
