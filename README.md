# System Helpdesk - Instrukcja uruchomienia

Poniżej znajdują się komendy niezbędne do skonfigurowania i uruchomienia systemu Helpdesk.

## 1. Klonowanie repozytorium

```bash
# Klonowanie repozytorium z GitHub
git clone https://github.com/70490-jakub-adrych/projekt-wdrozeniowy/
cd projekt-wdrozeniowy-crm/projekt-wdrozeniowy
```

## 2. Instalacja pakietów

```bash
pip install -r requirements.txt
```

## 3. Tworzenie i aplikacja migracji

```bash
# Tworzenie migracji na podstawie modeli
python manage.py makemigrations

# Zastosowanie migracji do bazy danych
python manage.py migrate
```

## 4. Tworzenie użytkownika administratora

```bash
# Tworzenie konta superużytkownika
python manage.py createsuperuser
```

## 5. Tworzenie profili dla istniejących użytkowników

```bash
# Automatyczne tworzenie profili dla istniejących użytkowników
python manage.py create_missing_profiles
```

## 6. Uruchomienie aplikacji

```bash
# Uruchomienie serwera deweloperskiego
python manage.py runserver
```

Po wykonaniu tych kroków aplikacja będzie dostępna pod adresem: http://127.0.0.1:8000/

### Pierwsze logowanie

1. Zaloguj się na utworzone wcześniej konto administratora
2. Konto administratora automatycznie otrzyma rolę "Admin"
3. Możesz teraz tworzyć organizacje, zgłoszenia oraz zarządzać użytkownikami
