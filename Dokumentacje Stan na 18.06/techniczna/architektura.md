# 🏗️ Architektura Systemu Helpdesk

## Przegląd Technologii

### Stack Technologiczny
- **Backend:** Django 4.2.22 (Python framework)
- **Frontend:** Bootstrap 4 + HTML/CSS/JavaScript
- **Baza danych:** SQLite (development) / MySQL (production)
- **Hosting:** mydevil.net z Passenger WSGI
- **Bezpieczeństwo:** bcrypt, cryptography, pyotp

### Wymagania Systemowe
- **Python:** 3.8 - 3.12
- **RAM:** Minimum 512MB (zalecane 1GB)
- **Dysk:** Minimum 100MB wolnego miejsca
- **Sieć:** Dostęp do internetu dla powiadomień email

## Struktura Projektu

```
projekt-wdrozeniowy/
├── crm/                          # Główna aplikacja Django
│   ├── models.py                 # Modele bazy danych
│   ├── views.py                  # Widoki aplikacji
│   ├── forms.py                  # Formularze
│   ├── admin.py                  # Panel administracyjny
│   ├── urls.py                   # Routing URL-i
│   ├── middleware.py             # Middleware aplikacji
│   ├── decorators.py             # Dekoratory uprawnień
│   ├── auth_backends.py          # System autoryzacji
│   ├── signals.py                # Sygnały Django
│   ├── services/                 # Logika biznesowa
│   ├── utils/                    # Narzędzia pomocnicze
│   ├── templates/                # Szablony HTML
│   └── static/                   # Pliki statyczne
├── projekt_wdrozeniowy/          # Ustawienia Django
├── static/                       # Pliki statyczne globalne
├── public/                       # Pliki publiczne
├── manage.py                     # Zarządzanie Django
├── passenger_wsgi.py             # Konfiguracja WSGI
└── requirements.txt              # Zależności Python
```

## Wzorce Projektowe

### Model-View-Template (MVT)
System wykorzystuje wzorzec MVT charakterystyczny dla Django:

- **Model (models.py):** Definicja struktury danych
- **View (views.py):** Logika biznesowa i obsługa żądań
- **Template (templates/):** Prezentacja danych użytkownikowi

### Middleware Pattern
- **AuthenticationMiddleware:** Weryfikacja użytkowników
- **LoggingMiddleware:** Rejestrowanie aktywności
- **SecurityMiddleware:** Zabezpieczenia aplikacji

### Service Layer
- **EmailService:** Wysyłanie powiadomień
- **EncryptionService:** Szyfrowanie danych
- **ReportService:** Generowanie raportów

## Bezpieczeństwo

### Uwierzytelnianie
- **bcrypt** do hashowania haseł
- **Session-based authentication**
- **Blokada konta** po 5 nieudanych próbach
- **Automatyczne wylogowanie** po czasie bezczynności

### Autoryzacja
- **Role-based access control (RBAC)**
- **Dekoratory uprawnień** (@login_required, @role_required)
- **Izolacja danych** między organizacjami

### Szyfrowanie
- **AES-256** dla załączników z danymi wrażliwymi
- **HTTPS** dla komunikacji
- **Secure headers** w odpowiedziach HTTP

## Wydajność

### Optymalizacje
- **Database indexing** na kluczowych polach
- **Caching** dla często używanych danych
- **Lazy loading** dla dużych list
- **Pagination** dla wyników

### Monitoring
- **Logi aplikacji** w django.log
- **Logi bazy danych** w sql.log
- **Performance metrics** w czasie rzeczywistym

## Skalowalność

### Pozioma Skalowalność
- **Stateless design** - brak stanu w aplikacji
- **Database connection pooling**
- **Load balancing ready**

### Pionowa Skalowalność
- **Modularna architektura**
- **Service-oriented design**
- **Configurable settings**

## Integracje

### Zewnętrzne API
- **Email SMTP** dla powiadomień
- **SMS Gateway** (planowane)
- **File storage** dla załączników

### Monitoring
- **Health checks** dla systemu
- **Error tracking** i raportowanie
- **Performance monitoring**

---

**Ostatnia aktualizacja:** 18.06.2025 