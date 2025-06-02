# Struktura bazy danych

## Tabele

### Zgłoszenia (tickets)
- id (PK)
- title (tytuł zgłoszenia)
- category (kategoria problemu)
- priority (priorytet)
- description (opis)
- status (status zgłoszenia)
- created_at (data utworzenia)
- updated_at (data aktualizacji)
- closed_at (data zamknięcia)
- created_by (FK do users)
- assigned_to (FK do users)
- company (FK do companies)
- is_sensitive (flaga danych wrażliwych)

### Użytkownicy (users)
- id (PK)
- email (login)
- password (hasło)
- first_name
- last_name
- phone_number
- company (FK do companies)
- role (admin/agent/client)
- is_active
- is_approved
- last_login
- created_at

### Firmy (companies)
- id (PK)
- name (nazwa firmy)
- address
- contact_email
- contact_phone
- created_at

### Komentarze (comments)
- id (PK)
- ticket (FK do tickets)
- user (FK do users)
- content
- created_at
- is_internal

### Załączniki (attachments)
- id (PK)
- ticket (FK do tickets)
- file_name
- file_path
- file_size
- is_encrypted
- uploaded_by (FK do users)
- uploaded_at

### Historia zmian (ticket_history)
- id (PK)
- ticket (FK do tickets)
- user (FK do users)
- field_name
- old_value
- new_value
- changed_at

### Logi aktywności (activity_logs)
- id (PK)
- user (FK do users)
- action_type
- action_details
- ip_address
- created_at

## Relacje

1. Zgłoszenia -> Użytkownicy
   - created_by: jeden użytkownik może utworzyć wiele zgłoszeń
   - assigned_to: jeden użytkownik może być przypisany do wielu zgłoszeń

2. Zgłoszenia -> Firmy
   - company: jedna firma może mieć wiele zgłoszeń

3. Użytkownicy -> Firmy
   - company: jedna firma może mieć wielu użytkowników

4. Komentarze -> Zgłoszenia
   - ticket: jedno zgłoszenie może mieć wiele komentarzy

5. Komentarze -> Użytkownicy
   - user: jeden użytkownik może dodać wiele komentarzy

6. Załączniki -> Zgłoszenia
   - ticket: jedno zgłoszenie może mieć wiele załączników

7. Historia zmian -> Zgłoszenia
   - ticket: jedno zgłoszenie może mieć wiele wpisów w historii

8. Historia zmian -> Użytkownicy
   - user: jeden użytkownik może wprowadzić wiele zmian

9. Logi aktywności -> Użytkownicy
   - user: jeden użytkownik może mieć wiele wpisów w logach

## Indeksy

1. Zgłoszenia
   - created_by
   - assigned_to
   - company
   - status
   - created_at

2. Użytkownicy
   - email
   - company
   - role

3. Komentarze
   - ticket
   - created_at

4. Załączniki
   - ticket
   - uploaded_at

5. Historia zmian
   - ticket
   - changed_at

6. Logi aktywności
   - user
   - created_at

## Uwagi implementacyjne

1. Hasła będą przechowywane w formie zahaszowanej (bcrypt)
2. Dane wrażliwe w załącznikach będą szyfrowane
3. Historia zmian będzie przechowywać wszystkie modyfikacje zgłoszeń
4. Logi aktywności będą rejestrować wszystkie istotne działania użytkowników
5. Indeksy zostały zaprojektowane pod kątem optymalizacji najczęstszych zapytań 