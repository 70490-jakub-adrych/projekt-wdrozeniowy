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

!! WYMAGANA WERSJA PYTHON: 3.8 lub nowsza

### Linux/macOS
```bash
# Klonowanie repozytorium
git clone https://github.com/70490-jakub-adrych/projekt-wdrozeniowy.git
cd projekt-wdrozeniowy

# Utworzenie i aktywacja wirtualnego środowiska
python3 -m venv venv
source venv/bin/activate

# Sprawdzenie poprawnej aktywacji - powinno pokazać ścieżkę do wirtualnego środowiska
which python
which pip

# Instalacja zależności w wirtualnym środowisku
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Upewnienie się, że Django jest zainstalowany
python -c "import django; print(django.__version__)"

# Pobieranie bibliotek statycznych
bash download_static_files.sh

# Konfiguracja bazy danych
python manage.py makemigrations
python manage.py migrate

# Tworzenie danych demonstracyjnych
python manage.py setup_demo_data

# Uruchomienie serwera
python manage.py runserver
```

### Rozwiązywanie problemów z wirtualnym środowiskiem na Linux/macOS

Jeśli mimo aktywacji wirtualnego środowiska (`venv`) występują problemy z importowaniem Django, sprawdź:

1. Czy używasz właściwego interpretera Python:
   ```bash
   which python
   # Powinno pokazać ścieżkę do Python w Twoim wirtualnym środowisku
   # np. /home/username/projekt-wdrozeniowy/venv/bin/python
   ```

2. Ponowna instalacja Django bezpośrednio:
   ```bash
   pip uninstall django
   pip install django==3.2.25
   ```

3. Sprawdź zmienną PYTHONPATH:
   ```bash
   echo $PYTHONPATH
   # Jeśli jest ustawiona, może powodować konflikty
   # Wyczyść ją tymczasowo: export PYTHONPATH=
   ```

### Windows (PowerShell)
```powershell
# Klonowanie repozytorium
git clone https://github.com/70490-jakub-adrych/projekt-wdrozeniowy.git
cd projekt-wdrozeniowy

# Utworzenie i aktywacja wirtualnego środowiska
python -m venv venv
.\venv\Scripts\Activate.ps1

# Instalacja zależności
pip install --upgrade pip setuptools wheel
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
- **Viewer**: username=`viewer`, password=`viewer123`
- **Superagent**: username=`superagent`, password=`superagent123`

## Konfiguracja MySQL dla produkcji

Domyślnie aplikacja używa bazy SQLite dla szybkiego rozwoju i testowania. Aby skonfigurować aplikację do pracy z MySQL:

1. Zainstaluj sterownik MySQL:
   ```bash
   pip install mysqlclient
   ```

2. Utwórz bazę danych MySQL:
   ```sql
   CREATE DATABASE helpdesk_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'helpdesk_user'@'localhost' IDENTIFIED BY 'twoje_haslo';
   GRANT ALL PRIVILEGES ON helpdesk_db.* TO 'helpdesk_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

3. Skopiuj plik `.env-mysql-example` do `.env` i dostosuj wartości:
   ```bash
   cp .env-mysql-example .env
   # Następnie edytuj plik .env z właściwymi danymi
   ```

4. Uruchom migracje i serwer:
   ```bash
   python manage.py migrate
   python manage.py setup_demo_data
   python manage.py runserver
   ```

## Przełączanie między bazami danych

- Do szybkich testów i rozwoju lokalnego, nie musisz tworzyć pliku `.env` - aplikacja domyślnie użyje SQLite
- Aby używać MySQL, skonfiguruj wszystkie parametry w pliku `.env` zgodnie z przykładem w `.env-mysql-example`
- Możesz łatwo przełączać się między trybami usuwając lub zmieniając nazwę pliku `.env`

## Automatyczne odświeżanie zgłoszeń na współdzielonych hostingach (AJAX polling)

Na hostingach takich jak mydevil.net, gdzie nie można użyć WebSocket/Channels, lista zgłoszeń dla viewer odświeża się automatycznie co 15 sekund dzięki AJAX polling.

- Nie jest wymagany WebSocket, Channels ani serwer ASGI.
- Działa na każdym hostingu obsługującym klasyczne Django (WSGI).
- Viewer widzi zawsze aktualną listę zgłoszeń bez przeładowania strony.