# 🗄️ Baza Danych - System Helpdesk

## Przegląd Bazy Danych

System wykorzystuje relacyjną bazę danych z następującymi opcjami:
- **SQLite** - dla rozwoju i testowania
- **MySQL** - dla środowiska produkcyjnego

## Główne Tabele

### 1. Użytkownicy i Organizacje

#### `auth_user` (Django User)
```sql
- id (Primary Key)
- username (Unique)
- email (Unique)
- password (Hashed)
- first_name
- last_name
- is_active
- is_staff
- is_superuser
- date_joined
- last_login
```

#### `crm_organization`
```sql
- id (Primary Key)
- name (Nazwa organizacji)
- address (Adres)
- phone (Telefon)
- email (Email kontaktowy)
- created_at
- updated_at
```

#### `crm_userprofile`
```sql
- id (Primary Key)
- user_id (Foreign Key -> auth_user)
- organization_id (Foreign Key -> crm_organization)
- role (Admin/Agent/Client/Viewer)
- phone (Telefon użytkownika)
- is_approved (Czy konto zatwierdzone)
- failed_login_attempts (Liczba nieudanych logowań)
- is_locked (Czy konto zablokowane)
- created_at
- updated_at
```

### 2. Zgłoszenia i Kategorie

#### `crm_ticketcategory`
```sql
- id (Primary Key)
- name (Nazwa kategorii)
- description (Opis kategorii)
- color (Kolor w interfejsie)
- is_active
- created_at
```

#### `crm_ticket`
```sql
- id (Primary Key)
- title (Tytuł zgłoszenia)
- description (Opis problemu)
- category_id (Foreign Key -> crm_ticketcategory)
- priority (Low/Medium/High/Critical)
- status (Open/In Progress/Closed)
- created_by_id (Foreign Key -> auth_user)
- assigned_to_id (Foreign Key -> auth_user)
- organization_id (Foreign Key -> crm_organization)
- created_at
- updated_at
- closed_at
- client_confirmation (Czy klient potwierdził rozwiązanie)
```

### 3. Komentarze i Historia

#### `crm_ticketcomment`
```sql
- id (Primary Key)
- ticket_id (Foreign Key -> crm_ticket)
- author_id (Foreign Key -> auth_user)
- content (Treść komentarza)
- is_internal (Czy komentarz wewnętrzny)
- created_at
```

#### `crm_tickethistory`
```sql
- id (Primary Key)
- ticket_id (Foreign Key -> crm_ticket)
- changed_by_id (Foreign Key -> auth_user)
- field_name (Nazwa zmienionego pola)
- old_value (Stara wartość)
- new_value (Nowa wartość)
- change_type (Created/Updated/Status Changed)
- created_at
```

### 4. Załączniki i Szyfrowanie

#### `crm_ticketattachment`
```sql
- id (Primary Key)
- ticket_id (Foreign Key -> crm_ticket)
- uploaded_by_id (Foreign Key -> auth_user)
- file_name (Nazwa pliku)
- file_path (Ścieżka do pliku)
- file_size (Rozmiar pliku)
- mime_type (Typ MIME)
- is_encrypted (Czy plik zaszyfrowany)
- encryption_key (Klucz szyfrowania - zaszyfrowany)
- created_at
```

### 5. Logi i Monitoring

#### `crm_useractivitylog`
```sql
- id (Primary Key)
- user_id (Foreign Key -> auth_user)
- action (Login/Logout/Ticket Created/Ticket Updated)
- ip_address (Adres IP)
- user_agent (User Agent przeglądarki)
- details (Szczegóły akcji)
- created_at
```

#### `crm_systemlog`
```sql
- id (Primary Key)
- level (INFO/WARNING/ERROR/CRITICAL)
- message (Wiadomość logu)
- source (Źródło logu)
- stack_trace (Stack trace dla błędów)
- created_at
```

## Relacje i Klucze Obce

### Hierarchia Organizacji
```
Organization (1) ←→ (N) UserProfile
UserProfile (N) ←→ (1) User (Django)
```

### Zarządzanie Zgłoszeniami
```
Ticket (1) ←→ (N) TicketComment
Ticket (1) ←→ (N) TicketHistory
Ticket (1) ←→ (N) TicketAttachment
Ticket (N) ←→ (1) TicketCategory
Ticket (N) ←→ (1) Organization
```

### Przypisania i Uprawnienia
```
Ticket (N) ←→ (1) User (created_by)
Ticket (N) ←→ (1) User (assigned_to)
UserProfile (N) ←→ (1) Organization
```

## Indeksy i Optymalizacja

### Indeksy Kluczowe
```sql
-- Indeksy dla szybkiego wyszukiwania zgłoszeń
CREATE INDEX idx_ticket_status ON crm_ticket(status);
CREATE INDEX idx_ticket_organization ON crm_ticket(organization_id);
CREATE INDEX idx_ticket_assigned_to ON crm_ticket(assigned_to_id);
CREATE INDEX idx_ticket_created_at ON crm_ticket(created_at);

-- Indeksy dla logów aktywności
CREATE INDEX idx_activity_user ON crm_useractivitylog(user_id);
CREATE INDEX idx_activity_created_at ON crm_useractivitylog(created_at);

-- Indeksy dla komentarzy
CREATE INDEX idx_comment_ticket ON crm_ticketcomment(ticket_id);
CREATE INDEX idx_comment_created_at ON crm_ticketcomment(created_at);
```

### Optymalizacja Zapytań
- **Select_related()** dla relacji Foreign Key
- **Prefetch_related()** dla relacji Many-to-Many
- **Database constraints** dla integralności danych
- **Caching** dla często używanych zapytań

## Backup i Odzyskiwanie

### Automatyczny Backup
- **Codzienny backup** w godzinach 3:00-5:00
- **Pełny backup** bazy danych
- **Retention policy** - 30 dni
- **Compression** plików backup

### Procedura Odzyskiwania
1. Zatrzymanie aplikacji
2. Przywrócenie bazy z backup
3. Weryfikacja integralności danych
4. Uruchomienie aplikacji
5. Test funkcjonalności

## Bezpieczeństwo Danych

### Szyfrowanie
- **Hasła** - bcrypt z salt
- **Załączniki** - AES-256 dla danych wrażliwych
- **Klucze szyfrowania** - przechowywane w bezpiecznym miejscu

### Izolacja Danych
- **Organizacje** - klienci widzą tylko swoje dane
- **Role** - różne poziomy dostępu
- **Audit trail** - śledzenie wszystkich zmian

### Compliance
- **GDPR** - ochrona danych osobowych
- **Logi** - przechowywanie przez wymagany czas
- **Anonimizacja** - możliwość anonimizacji danych

---

**Ostatnia aktualizacja:** 18.06.2025 