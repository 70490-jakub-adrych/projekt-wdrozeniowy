# Technologie

## Backend

### Framework Django
- Wersja: najnowsza stabilna
- Cel: główny framework aplikacji
- Zalety:
  - Szybki rozwój
  - Wbudowany system autoryzacji
  - ORM do zarządzania bazą danych
  - System szablonów
  - Wbudowane zabezpieczenia

### Baza danych
- SQLite 3
- Cel: przechowywanie danych aplikacji
- Zalety:
  - Prosta konfiguracja
  - Nie wymaga osobnego serwera
  - Wystarczająca wydajność dla planowanego obciążenia
  - Łatwe backupowanie

## Frontend

### HTML5/CSS3
- Cel: struktura i stylizacja interfejsu
- Framework CSS: Bootstrap 5
- Responsywność: tak

### JavaScript
- Cel: interaktywność interfejsu
- Framework: Vue.js
- Zalety:
  - Łatwa integracja z Django
  - Reaktywność
  - Komponentowy model

## Hosting

### mydevil.net
- Cel: hosting aplikacji
- Wymagania:
  - Python 3.8+
  - SQLite 3
  - SSL/HTTPS
  - Cron jobs (dla backupów)

## Dodatkowe technologie

### System powiadomień
- E-mail: wbudowany system Django
- SMS: bramka SMS (faza końcowa)
  - Cel: powiadomienia 2FA i nowych zgłoszeń
  - Integracja: API bramki SMS

### Bezpieczeństwo
- Szyfrowanie haseł: bcrypt
- Szyfrowanie danych wrażliwych: AES-256
- HTTPS: Let's Encrypt
- CSRF protection: wbudowane w Django
- XSS protection: wbudowane w Django

### Backup
- Cel: codzienna kopia bazy danych
- Czas: 3:00-5:00
- Format: SQL dump
- Przechowywanie: 30 dni

## Wymagania systemowe

### Serwer
- CPU: 2 rdzenie
- RAM: 4GB
- Dysk: 20GB
- System: Linux

### Klient
- Przeglądarka: Chrome, Firefox, Edge (najnowsze wersje)
- JavaScript: włączony
- Cookies: włączone

## Planowane aktualizacje

### Faza 1
- Podstawowa funkcjonalność
- System zgłoszeń
- Panel użytkownika
- Panel agenta

### Faza 2
- System raportów
- Statystyki
- Wizualizacje

### Faza 3
- Integracja SMS
- 2FA
- Zaawansowane funkcje 