# System Helpdesk - Instrukcja uruchomienia

System zarządzania zgłoszeniami IT z funkcjami zarządzania użytkownikami, organizacjami i zabezpieczeniami.

## Funkcje systemu

- ✅ Zarządzanie zgłoszeniami IT (tickets)
- ✅ Zarządzanie organizacjami i użytkownikami
- ✅ System ról (Admin, Agent, Klient)
- ✅ Blokada konta po 5 nieudanych próbach logowania
- ✅ Szyfrowane załączniki
- ✅ Logi aktywności
- ✅ Automatyczne sugerowanie kategorii zgłoszeń

## Szybkie uruchomienie

### Linux/macOS
```bash
# Klonowanie repozytorium
git clone https://github.com/70490-jakub-adrych/projekt-wdrozeniowy.git
cd projekt-wdrozeniowy

# Instalacja zależności
pip install -r requirements.txt

# Pobieranie bibliotek statycznych
./download_static_files.sh

# Konfiguracja bazy danych
python manage.py makemigrations
python manage.py migrate

# Tworzenie danych demonstracyjnych
python manage.py setup_demo_data

# Uruchomienie serwera
python manage.py runserver
```

### Windows (PowerShell)
```powershell
# Klonowanie repozytorium
git clone https://github.com/70490-jakub-adrych/projekt-wdrozeniowy.git
cd projekt-wdrozeniowy

# Instalacja zależności
pip install -r requirements.txt

# Pobieranie bibliotek statycznych
.\download_static_files.ps1

# Konfiguracja bazy danych
python manage.py makemigrations
python manage.py migrate

# Tworzenie danych demonstracyjnych
python manage.py setup_demo_data

# Uruchomienie serwera
python manage.py runserver
```

## Dostęp do systemu

Po uruchomieniu aplikacja będzie dostępna pod adresem: **http://127.0.0.1:8000/**

### Konta demonstracyjne

- **Admin**: username=`admin`, password=`admin123`
- **Agent 1**: username=`agent1`, password=`agent123`
- **Klient 1**: username=`client1`, password=`client123`

## Struktura projektu
