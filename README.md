# System Helpdesk - Instrukcja uruchomienia

Poniżej znajdują się komendy niezbędne do skonfigurowania i uruchomienia systemu Helpdesk.


```bash
# Klonowanie repozytorium z GitHub
git clone https://github.com/70490-jakub-adrych/projekt-wdrozeniowy/
cd projekt-wdrozeniowy-crm/projekt-wdrozeniowy

pip install -r requirements.txt

# Tworzenie migracji na podstawie modeli
python manage.py makemigrations

# Zastosowanie migracji do bazy danych
python manage.py migrate

# Tworzenie kont i ustawienie grup oraz uprawnień
python manage.py setup_demo_data

# Uruchomienie serwera deweloperskiego
python manage.py runserver
```

Po wykonaniu tych kroków aplikacja będzie dostępna pod adresem: http://127.0.0.1:8000/

### Pierwsze logowanie

1. Zaloguj się na utworzone wcześniej konto administratora
2. Konto administratora automatycznie otrzyma rolę "Admin"
3. Możesz teraz tworzyć organizacje, zgłoszenia oraz zarządzać użytkownikami
