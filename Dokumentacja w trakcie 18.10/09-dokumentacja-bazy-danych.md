# 🗄️ Dokumentacja Bazy Danych

## Spis Treści
1. [Wprowadzenie](#wprowadzenie)
2. [Przegląd Architektury](#przegląd-architektury)
3. [Model Danych](#model-danych)
4. [Tabele i Relacje](#tabele-i-relacje)
5. [Indeksy i Optymalizacja](#indeksy-i-optymalizacja)
6. [Zapytania i Procedury](#zapytania-i-procedury)
7. [Bezpieczeństwo Danych](#bezpieczeństwo-danych)
8. [Kopie Zapasowe i Przywracanie](#kopie-zapasowe-i-przywracanie)
9. [Monitoring i Wydajność](#monitoring-i-wydajność)
10. [Migracje i Wersjonowanie](#migracje-i-wersjonowanie)
11. [Procedury Konserwacji](#procedury-konserwacji)
12. [Troubleshooting](#troubleshooting)

---

## Wprowadzenie

Dokumentacja bazy danych systemu helpdesk zawiera szczegółowy opis struktury, relacji, optymalizacji i procedur zarządzania bazą danych. Dokument ten jest przeznaczony dla administratorów bazy danych, deweloperów i analityków danych.

### Cel Dokumentacji
- **Zrozumienie struktury** bazy danych
- **Optymalizacja wydajności** zapytań
- **Planowanie rozwoju** i rozszerzeń
- **Rozwiązywanie problemów** technicznych
- **Audyt i kontrola** jakości danych

### Odbiorcy
- **Administratorzy bazy danych** - zarządzanie i optymalizacja
- **Deweloperzy** - implementacja i rozwój
- **Analitycy danych** - analiza i raportowanie
- **Audytorzy** - weryfikacja zgodności i bezpieczeństwa

### Technologie
- **Django ORM** - mapowanie obiektowo-relacyjne
- **SQLite** - baza danych deweloperska
- **MySQL** - baza danych produkcyjna
- **PostgreSQL** - opcjonalna baza danych

---

## Przegląd Architektury

### Architektura Bazy Danych

#### Wzorzec Projektowy
System wykorzystuje wzorzec **Active Record** przez Django ORM, co zapewnia:
- **Mapowanie obiektowo-relacyjne** - obiekty Python mapowane na tabele SQL
- **Abstrakcja bazy danych** - niezależność od konkretnej bazy danych
- **Migrations** - automatyczne zarządzanie zmianami schematu
- **Query optimization** - optymalizacja zapytań przez ORM

#### Diagram Architektury
```
┌─────────────────────────────────────────────────────────────┐
│                    WARSTWA APLIKACJI                        │
├─────────────────────────────────────────────────────────────┤
│  Django Models  │  Django ORM  │  Query Builder            │
├─────────────────────────────────────────────────────────────┤
│                    WARSTWA ABSTRAKCJI                       │
├─────────────────────────────────────────────────────────────┤
│  Database Driver  │  Connection Pool  │  Transaction Manager │
├─────────────────────────────────────────────────────────────┤
│                    WARSTWA BAZY DANYCH                       │
├─────────────────────────────────────────────────────────────┤
│  SQLite (Dev)  │  MySQL (Prod)  │  PostgreSQL (Opt)       │
└─────────────────────────────────────────────────────────────┘
```

### Konfiguracja Bazy Danych

#### Ustawienia Django
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Development
        # 'ENGINE': 'django.db.backends.mysql',  # Production
        # 'ENGINE': 'django.db.backends.postgresql',  # Optional
        'NAME': BASE_DIR / 'db.sqlite3',
        'USER': config('DB_USER', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default=''),
        'PORT': config('DB_PORT', default=''),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
```

#### Konfiguracja MySQL (Produkcja)
```sql
-- Konfiguracja MySQL dla produkcji
SET GLOBAL innodb_buffer_pool_size = 1G;
SET GLOBAL max_connections = 200;
SET GLOBAL query_cache_size = 64M;
SET GLOBAL query_cache_type = 1;
SET GLOBAL innodb_log_file_size = 256M;
SET GLOBAL innodb_log_buffer_size = 16M;
```

---

## Model Danych

### Przegląd Modeli

#### Hierarchia Modeli
```
User (Django Auth)
├── UserProfile (Rozszerzenie użytkownika)
├── UserPreference (Preferencje użytkownika)
└── EmailVerification (Weryfikacja email)

Organization (Organizacje)
├── Ticket (Zgłoszenia)
│   ├── TicketComment (Komentarze)
│   └── TicketAttachment (Załączniki)
└── ActivityLog (Logi aktywności)

Group (Django Auth)
├── GroupSettings (Ustawienia grup)
├── GroupViewPermission (Uprawnienia grup)
└── UserViewPermission (Uprawnienia użytkowników)

WorkHours (Godziny pracy)
├── TicketStatistics (Statystyki zgłoszeń)
└── AgentWorkLog (Logi pracy agentów)

EmailNotificationSettings (Ustawienia powiadomień)
```

### Szczegółowy Opis Modeli

#### 1. UserProfile (Profil Użytkownika)

**Cel:** Rozszerzenie standardowego modelu User Django o dodatkowe pola

**Pola:**
```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20, blank=True)
    is_approved = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    lock_reason = models.TextField(blank=True)
    ga_enabled = models.BooleanField(default=False)
    ga_secret_key = models.CharField(max_length=64, blank=True)
    ga_recovery_hash = models.CharField(max_length=128, blank=True)
    trusted_ip = models.GenericIPAddressField(null=True, blank=True)
    trusted_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Relacje:**
- `OneToOne` z `User` - jeden profil na użytkownika
- `ManyToMany` z `Organization` - użytkownik może należeć do wielu organizacji

**Indeksy:**
```python
class Meta:
    indexes = [
        models.Index(fields=['role']),
        models.Index(fields=['is_approved']),
        models.Index(fields=['is_locked']),
        models.Index(fields=['ga_enabled']),
        models.Index(fields=['trusted_until']),
    ]
```

#### 2. Organization (Organizacja)

**Cel:** Reprezentacja organizacji klientów

**Pola:**
```python
class Organization(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Relacje:**
- `ManyToMany` z `UserProfile` - organizacja może mieć wielu użytkowników
- `OneToMany` z `Ticket` - organizacja może mieć wiele zgłoszeń

**Indeksy:**
```python
class Meta:
    indexes = [
        models.Index(fields=['name']),
        models.Index(fields=['email']),
        models.Index(fields=['created_at']),
    ]
```

#### 3. Ticket (Zgłoszenie)

**Cel:** Główny model reprezentujący zgłoszenia w systemie

**Pola:**
```python
class Ticket(models.Model):
    STATUS_CHOICES = [
        ('new', 'Nowe'),
        ('in_progress', 'W trakcie'),
        ('resolved', 'Rozwiązane'),
        ('closed', 'Zamknięte'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Niski'),
        ('medium', 'Średni'),
        ('high', 'Wysoki'),
        ('critical', 'Krytyczny'),
    ]
    
    CATEGORY_CHOICES = [
        ('technical', 'Techniczne'),
        ('account', 'Konto'),
        ('billing', 'Rozliczenia'),
        ('other', 'Inne'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tickets')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
```

**Relacje:**
- `ForeignKey` do `User` (created_by) - kto utworzył zgłoszenie
- `ForeignKey` do `User` (assigned_to) - komu przypisane zgłoszenie
- `ForeignKey` do `Organization` - do której organizacji należy
- `OneToMany` z `TicketComment` - komentarze do zgłoszenia
- `OneToMany` z `TicketAttachment` - załączniki do zgłoszenia

**Indeksy:**
```python
class Meta:
    indexes = [
        models.Index(fields=['status', 'priority']),
        models.Index(fields=['created_at']),
        models.Index(fields=['assigned_to', 'status']),
        models.Index(fields=['organization', 'status']),
        models.Index(fields=['resolved_at']),
        models.Index(fields=['closed_at']),
    ]
```

#### 4. TicketComment (Komentarz)

**Cel:** Komentarze dodawane do zgłoszeń

**Pola:**
```python
class TicketComment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    is_internal = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Relacje:**
- `ForeignKey` do `Ticket` - do którego zgłoszenia należy komentarz
- `ForeignKey` do `User` - kto napisał komentarz

**Indeksy:**
```python
class Meta:
    indexes = [
        models.Index(fields=['ticket', 'created_at']),
        models.Index(fields=['author', 'created_at']),
        models.Index(fields=['is_internal']),
    ]
```

#### 5. TicketAttachment (Załącznik)

**Cel:** Załączniki do zgłoszeń z szyfrowaniem

**Pola:**
```python
class TicketAttachment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/')
    filename = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    encryption_key = models.BinaryField(blank=True, null=True)
    accepted_policy = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
```

**Relacje:**
- `ForeignKey` do `Ticket` - do którego zgłoszenia należy załącznik
- `ForeignKey` do `User` - kto przesłał załącznik

**Indeksy:**
```python
class Meta:
    indexes = [
        models.Index(fields=['ticket', 'uploaded_at']),
        models.Index(fields=['uploaded_by', 'uploaded_at']),
        models.Index(fields=['accepted_policy']),
    ]
```

#### 6. ActivityLog (Log Aktywności)

**Cel:** Logowanie wszystkich działań w systemie

**Pola:**
```python
class ActivityLog(models.Model):
    ACTION_TYPES = [
        ('login', 'Zalogowanie'),
        ('logout', 'Wylogowanie'),
        ('ticket_created', 'Utworzenie zgłoszenia'),
        ('ticket_updated', 'Aktualizacja zgłoszenia'),
        ('ticket_assigned', 'Przypisanie zgłoszenia'),
        ('ticket_resolved', 'Rozwiązanie zgłoszenia'),
        ('ticket_closed', 'Zamknięcie zgłoszenia'),
        ('comment_added', 'Dodanie komentarza'),
        ('attachment_uploaded', 'Przesłanie załącznika'),
        ('user_created', 'Utworzenie użytkownika'),
        ('user_updated', 'Aktualizacja użytkownika'),
        ('user_locked', 'Zablokowanie użytkownika'),
        ('user_unlocked', 'Odblokowanie użytkownika'),
        ('2fa_enabled', 'Włączenie 2FA'),
        ('2fa_disabled', 'Wyłączenie 2FA'),
        ('password_changed', 'Zmiana hasła'),
        ('email_verified', 'Weryfikacja email'),
        ('organization_created', 'Utworzenie organizacji'),
        ('organization_updated', 'Aktualizacja organizacji'),
        ('permission_granted', 'Przyznanie uprawnienia'),
        ('permission_revoked', 'Odwołanie uprawnienia'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    ticket = models.ForeignKey(Ticket, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

**Relacje:**
- `ForeignKey` do `User` - kto wykonał akcję
- `ForeignKey` do `Ticket` - na którym zgłoszeniu (jeśli dotyczy)

**Indeksy:**
```python
class Meta:
    indexes = [
        models.Index(fields=['user', 'created_at']),
        models.Index(fields=['action_type', 'created_at']),
        models.Index(fields=['ticket', 'created_at']),
        models.Index(fields=['ip_address', 'created_at']),
        models.Index(fields=['created_at']),
    ]
```

#### 7. GroupSettings (Ustawienia Grup)

**Cel:** Rozszerzenie standardowych grup Django o dodatkowe uprawnienia

**Pola:**
```python
class GroupSettings(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    allow_multiple_organizations = models.BooleanField(default=False)
    show_statistics = models.BooleanField(default=False)
    exempt_from_2fa = models.BooleanField(default=False)
    show_navbar = models.BooleanField(default=True)
    attachments_access_level = models.CharField(max_length=20, choices=[
        ('none', 'Brak dostępu'),
        ('own', 'Tylko własne'),
        ('organization', 'Organizacja'),
        ('all', 'Wszystkie'),
    ], default='own')
    can_assign_tickets = models.BooleanField(default=False)
    can_manage_team = models.BooleanField(default=False)
    can_view_all_tickets = models.BooleanField(default=False)
    can_manage_organizations = models.BooleanField(default=False)
    can_manage_users = models.BooleanField(default=False)
    can_access_admin = models.BooleanField(default=False)
```

**Relacje:**
- `OneToOne` z `Group` - jedno ustawienie na grupę

#### 8. TicketStatistics (Statystyki Zgłoszeń)

**Cel:** Agregowane statystyki wydajności

**Pola:**
```python
class TicketStatistics(models.Model):
    PERIOD_TYPES = [
        ('daily', 'Dziennie'),
        ('weekly', 'Tygodniowo'),
        ('monthly', 'Miesięcznie'),
        ('yearly', 'Rocznie'),
    ]
    
    period_type = models.CharField(max_length=20, choices=PERIOD_TYPES)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    agent = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    total_tickets = models.IntegerField(default=0)
    resolved_tickets = models.IntegerField(default=0)
    avg_resolution_time = models.DurationField(null=True, blank=True)
    sla_compliance = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
```

**Relacje:**
- `ForeignKey` do `Organization` - statystyki dla organizacji
- `ForeignKey` do `User` - statystyki dla agenta

**Indeksy:**
```python
class Meta:
    indexes = [
        models.Index(fields=['period_type', 'period_start']),
        models.Index(fields=['organization', 'period_start']),
        models.Index(fields=['agent', 'period_start']),
        models.Index(fields=['period_start', 'period_end']),
    ]
```

---

## Tabele i Relacje

### Diagram ERD (Entity Relationship Diagram)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     User        │    │   UserProfile   │    │   Organization │
│ (Django Auth)   │◄──►│                 │◄──►│                 │
│                 │    │ - role          │    │ - name          │
│ - username      │    │ - phone         │    │ - email         │
│ - email         │    │ - is_approved   │    │ - address       │
│ - password      │    │ - is_locked     │    │ - description   │
│ - is_active     │    │ - 2FA fields    │    │ - created_at    │
│ - last_login    │    │ - lock fields   │    │ - updated_at    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Ticket      │    │ TicketComment   │    │TicketAttachment │
│                 │    │                 │    │                 │
│ - title         │◄──►│ - content       │    │ - file          │
│ - description   │    │ - author        │    │ - filename      │
│ - status        │    │ - is_internal   │    │ - uploaded_by   │
│ - priority      │    │ - created_at    │    │ - encryption_key│
│ - category      │    │ - updated_at    │    │ - accepted_policy│
│ - created_by    │    └─────────────────┘    │ - uploaded_at   │
│ - assigned_to   │                           └─────────────────┘
│ - organization  │
│ - created_at    │
│ - updated_at    │
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
│ - user_agent    │
│ - created_at    │
└─────────────────┘
```

### Szczegółowe Relacje

#### 1. Relacje User-UserProfile
```sql
-- OneToOne relationship
User.id = UserProfile.user_id

-- Przykładowe zapytanie
SELECT u.username, up.role, up.phone
FROM auth_user u
JOIN crm_userprofile up ON u.id = up.user_id
WHERE u.is_active = 1;
```

#### 2. Relacje User-Organization
```sql
-- ManyToMany relationship przez UserProfile
User.id → UserProfile.user_id → UserProfile.organizations

-- Przykładowe zapytanie
SELECT u.username, o.name
FROM auth_user u
JOIN crm_userprofile up ON u.id = up.user_id
JOIN crm_userprofile_organizations uo ON up.id = uo.userprofile_id
JOIN crm_organization o ON uo.organization_id = o.id;
```

#### 3. Relacje Ticket-User
```sql
-- ForeignKey relationships
Ticket.created_by_id → User.id
Ticket.assigned_to_id → User.id

-- Przykładowe zapytanie
SELECT t.title, creator.username, assignee.username
FROM crm_ticket t
JOIN auth_user creator ON t.created_by_id = creator.id
LEFT JOIN auth_user assignee ON t.assigned_to_id = assignee.id;
```

#### 4. Relacje Ticket-Organization
```sql
-- ForeignKey relationship
Ticket.organization_id → Organization.id

-- Przykładowe zapytanie
SELECT t.title, o.name, COUNT(t.id) as ticket_count
FROM crm_ticket t
JOIN crm_organization o ON t.organization_id = o.id
GROUP BY o.id, o.name;
```

### Relacje Wielo-Tabelowe

#### 1. Hierarchia Zgłoszeń
```sql
-- Zgłoszenie z wszystkimi powiązanymi danymi
SELECT 
    t.id,
    t.title,
    t.status,
    t.priority,
    creator.username as created_by,
    assignee.username as assigned_to,
    o.name as organization,
    COUNT(c.id) as comment_count,
    COUNT(a.id) as attachment_count
FROM crm_ticket t
JOIN auth_user creator ON t.created_by_id = creator.id
LEFT JOIN auth_user assignee ON t.assigned_to_id = assignee.id
JOIN crm_organization o ON t.organization_id = o.id
LEFT JOIN crm_ticketcomment c ON t.id = c.ticket_id
LEFT JOIN crm_ticketattachment a ON t.id = a.ticket_id
GROUP BY t.id;
```

#### 2. Statystyki Użytkowników
```sql
-- Statystyki aktywności użytkowników
SELECT 
    u.username,
    up.role,
    COUNT(t.id) as tickets_created,
    COUNT(ta.id) as tickets_assigned,
    COUNT(c.id) as comments_added,
    COUNT(al.id) as total_actions
FROM auth_user u
JOIN crm_userprofile up ON u.id = up.user_id
LEFT JOIN crm_ticket t ON u.id = t.created_by_id
LEFT JOIN crm_ticket ta ON u.id = ta.assigned_to_id
LEFT JOIN crm_ticketcomment c ON u.id = c.author_id
LEFT JOIN crm_activitylog al ON u.id = al.user_id
GROUP BY u.id, u.username, up.role;
```

---

## Indeksy i Optymalizacja

### Strategia Indeksowania

#### 1. Indeksy Podstawowe
```sql
-- Indeksy dla tabeli Ticket
CREATE INDEX idx_ticket_status_priority ON crm_ticket(status, priority);
CREATE INDEX idx_ticket_created_at ON crm_ticket(created_at);
CREATE INDEX idx_ticket_assigned_status ON crm_ticket(assigned_to_id, status);
CREATE INDEX idx_ticket_organization_status ON crm_ticket(organization_id, status);
CREATE INDEX idx_ticket_resolved_at ON crm_ticket(resolved_at);
CREATE INDEX idx_ticket_closed_at ON crm_ticket(closed_at);

-- Indeksy dla tabeli ActivityLog
CREATE INDEX idx_activitylog_user_created ON crm_activitylog(user_id, created_at);
CREATE INDEX idx_activitylog_action_created ON crm_activitylog(action_type, created_at);
CREATE INDEX idx_activitylog_ticket_created ON crm_activitylog(ticket_id, created_at);
CREATE INDEX idx_activitylog_ip_created ON crm_activitylog(ip_address, created_at);
CREATE INDEX idx_activitylog_created_at ON crm_activitylog(created_at);

-- Indeksy dla tabeli UserProfile
CREATE INDEX idx_userprofile_role ON crm_userprofile(role);
CREATE INDEX idx_userprofile_approved ON crm_userprofile(is_approved);
CREATE INDEX idx_userprofile_locked ON crm_userprofile(is_locked);
CREATE INDEX idx_userprofile_ga_enabled ON crm_userprofile(ga_enabled);
CREATE INDEX idx_userprofile_trusted_until ON crm_userprofile(trusted_until);
```

#### 2. Indeksy Złożone
```sql
-- Indeksy złożone dla często używanych zapytań
CREATE INDEX idx_ticket_org_status_priority ON crm_ticket(organization_id, status, priority);
CREATE INDEX idx_ticket_assignee_status_created ON crm_ticket(assigned_to_id, status, created_at);
CREATE INDEX idx_activitylog_user_action_created ON crm_activitylog(user_id, action_type, created_at);
CREATE INDEX idx_ticketcomment_ticket_created ON crm_ticketcomment(ticket_id, created_at);
CREATE INDEX idx_ticketattachment_ticket_uploaded ON crm_ticketattachment(ticket_id, uploaded_at);
```

#### 3. Indeksy Częściowe
```sql
-- Indeksy tylko dla aktywnych rekordów
CREATE INDEX idx_ticket_active ON crm_ticket(status) WHERE status IN ('new', 'in_progress');
CREATE INDEX idx_user_active ON auth_user(is_active) WHERE is_active = 1;
CREATE INDEX idx_userprofile_approved ON crm_userprofile(is_approved) WHERE is_approved = 1;
```

### Optymalizacja Zapytań

#### 1. Zapytania z JOIN
```sql
-- Optymalizowane zapytanie z JOIN
SELECT 
    t.id,
    t.title,
    t.status,
    creator.username as created_by,
    assignee.username as assigned_to,
    o.name as organization
FROM crm_ticket t
INNER JOIN auth_user creator ON t.created_by_id = creator.id
LEFT JOIN auth_user assignee ON t.assigned_to_id = assignee.id
INNER JOIN crm_organization o ON t.organization_id = o.id
WHERE t.status IN ('new', 'in_progress')
ORDER BY t.created_at DESC
LIMIT 50;
```

#### 2. Zapytania z Agregacją
```sql
-- Optymalizowane zapytanie z agregacją
SELECT 
    o.name as organization,
    COUNT(t.id) as total_tickets,
    COUNT(CASE WHEN t.status = 'resolved' THEN 1 END) as resolved_tickets,
    AVG(TIMESTAMPDIFF(HOUR, t.created_at, t.resolved_at)) as avg_resolution_hours
FROM crm_ticket t
INNER JOIN crm_organization o ON t.organization_id = o.id
WHERE t.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY o.id, o.name
HAVING total_tickets > 0
ORDER BY total_tickets DESC;
```

#### 3. Zapytania z Subquery
```sql
-- Optymalizowane zapytanie z subquery
SELECT 
    u.username,
    up.role,
    (SELECT COUNT(*) FROM crm_ticket WHERE created_by_id = u.id) as tickets_created,
    (SELECT COUNT(*) FROM crm_ticket WHERE assigned_to_id = u.id AND status = 'in_progress') as active_tickets
FROM auth_user u
INNER JOIN crm_userprofile up ON u.id = up.user_id
WHERE u.is_active = 1
ORDER BY tickets_created DESC;
```

### Optymalizacja Wydajności

#### 1. Konfiguracja MySQL
```sql
-- Optymalizacja MySQL dla systemu helpdesk
SET GLOBAL innodb_buffer_pool_size = 1G;
SET GLOBAL max_connections = 200;
SET GLOBAL query_cache_size = 64M;
SET GLOBAL query_cache_type = 1;
SET GLOBAL innodb_log_file_size = 256M;
SET GLOBAL innodb_log_buffer_size = 16M;
SET GLOBAL innodb_flush_log_at_trx_commit = 2;
SET GLOBAL innodb_file_per_table = 1;
SET GLOBAL innodb_read_io_threads = 8;
SET GLOBAL innodb_write_io_threads = 8;
```

#### 2. Optymalizacja Django ORM
```python
# Optymalizacja zapytań Django ORM
from django.db import models

# Użycie select_related dla ForeignKey
tickets = Ticket.objects.select_related(
    'created_by', 'assigned_to', 'organization'
).filter(status='new')

# Użycie prefetch_related dla ManyToMany i reverse ForeignKey
tickets = Ticket.objects.prefetch_related(
    'comments', 'attachments'
).filter(status='in_progress')

# Użycie only() dla ograniczenia pól
tickets = Ticket.objects.only(
    'id', 'title', 'status', 'created_at'
).filter(status='new')

# Użycie defer() dla pominięcia ciężkich pól
tickets = Ticket.objects.defer(
    'description'
).filter(status='new')
```

#### 3. Cache'owanie Zapytań
```python
# Cache'owanie często używanych zapytań
from django.core.cache import cache

def get_ticket_stats():
    cache_key = 'ticket_stats'
    stats = cache.get(cache_key)
    
    if stats is None:
        stats = {
            'total': Ticket.objects.count(),
            'new': Ticket.objects.filter(status='new').count(),
            'in_progress': Ticket.objects.filter(status='in_progress').count(),
            'resolved': Ticket.objects.filter(status='resolved').count(),
        }
        cache.set(cache_key, stats, 300)  # Cache na 5 minut
    
    return stats
```

---

## Zapytania i Procedury

### Często Używane Zapytania

#### 1. Zapytania Administracyjne

**Lista wszystkich użytkowników z rolami:**
```sql
SELECT 
    u.id,
    u.username,
    u.email,
    u.is_active,
    u.last_login,
    up.role,
    up.is_approved,
    up.is_locked,
    GROUP_CONCAT(o.name SEPARATOR ', ') as organizations
FROM auth_user u
LEFT JOIN crm_userprofile up ON u.id = up.user_id
LEFT JOIN crm_userprofile_organizations uo ON up.id = uo.userprofile_id
LEFT JOIN crm_organization o ON uo.organization_id = o.id
GROUP BY u.id
ORDER BY u.username;
```

**Statystyki zgłoszeń według organizacji:**
```sql
SELECT 
    o.name as organization,
    COUNT(t.id) as total_tickets,
    COUNT(CASE WHEN t.status = 'new' THEN 1 END) as new_tickets,
    COUNT(CASE WHEN t.status = 'in_progress' THEN 1 END) as in_progress_tickets,
    COUNT(CASE WHEN t.status = 'resolved' THEN 1 END) as resolved_tickets,
    COUNT(CASE WHEN t.status = 'closed' THEN 1 END) as closed_tickets,
    AVG(TIMESTAMPDIFF(HOUR, t.created_at, t.resolved_at)) as avg_resolution_hours
FROM crm_organization o
LEFT JOIN crm_ticket t ON o.id = t.organization_id
GROUP BY o.id, o.name
ORDER BY total_tickets DESC;
```

**Najaktywniejsze użytkowniki:**
```sql
SELECT 
    u.username,
    up.role,
    COUNT(t.id) as tickets_created,
    COUNT(ta.id) as tickets_assigned,
    COUNT(c.id) as comments_added,
    COUNT(al.id) as total_actions,
    MAX(al.created_at) as last_activity
FROM auth_user u
JOIN crm_userprofile up ON u.id = up.user_id
LEFT JOIN crm_ticket t ON u.id = t.created_by_id
LEFT JOIN crm_ticket ta ON u.id = ta.assigned_to_id
LEFT JOIN crm_ticketcomment c ON u.id = c.author_id
LEFT JOIN crm_activitylog al ON u.id = al.user_id
WHERE al.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY u.id, u.username, up.role
ORDER BY total_actions DESC
LIMIT 20;
```

#### 2. Zapytania Operacyjne

**Zgłoszenia wymagające uwagi:**
```sql
SELECT 
    t.id,
    t.title,
    t.status,
    t.priority,
    t.created_at,
    creator.username as created_by,
    assignee.username as assigned_to,
    o.name as organization,
    TIMESTAMPDIFF(HOUR, t.created_at, NOW()) as hours_since_created
FROM crm_ticket t
JOIN auth_user creator ON t.created_by_id = creator.id
LEFT JOIN auth_user assignee ON t.assigned_to_id = assignee.id
JOIN crm_organization o ON t.organization_id = o.id
WHERE (
    (t.status = 'new' AND TIMESTAMPDIFF(HOUR, t.created_at, NOW()) > 24) OR
    (t.status = 'in_progress' AND TIMESTAMPDIFF(HOUR, t.updated_at, NOW()) > 48) OR
    (t.priority = 'critical' AND t.status != 'resolved')
)
ORDER BY t.priority DESC, t.created_at ASC;
```

**Zgłoszenia przekraczające SLA:**
```sql
SELECT 
    t.id,
    t.title,
    t.status,
    t.priority,
    t.created_at,
    creator.username as created_by,
    assignee.username as assigned_to,
    o.name as organization,
    TIMESTAMPDIFF(HOUR, t.created_at, NOW()) as hours_since_created,
    CASE 
        WHEN t.priority = 'critical' THEN 4
        WHEN t.priority = 'high' THEN 24
        WHEN t.priority = 'medium' THEN 72
        WHEN t.priority = 'low' THEN 168
    END as sla_hours
FROM crm_ticket t
JOIN auth_user creator ON t.created_by_id = creator.id
LEFT JOIN auth_user assignee ON t.assigned_to_id = assignee.id
JOIN crm_organization o ON t.organization_id = o.id
WHERE t.status IN ('new', 'in_progress')
AND TIMESTAMPDIFF(HOUR, t.created_at, NOW()) > 
    CASE 
        WHEN t.priority = 'critical' THEN 4
        WHEN t.priority = 'high' THEN 24
        WHEN t.priority = 'medium' THEN 72
        WHEN t.priority = 'low' THEN 168
    END
ORDER BY t.priority DESC, t.created_at ASC;
```

**Statystyki wydajności agentów:**
```sql
SELECT 
    u.username,
    up.role,
    COUNT(t.id) as total_assigned,
    COUNT(CASE WHEN t.status = 'resolved' THEN 1 END) as resolved,
    COUNT(CASE WHEN t.status = 'closed' THEN 1 END) as closed,
    AVG(TIMESTAMPDIFF(HOUR, t.created_at, t.resolved_at)) as avg_resolution_hours,
    COUNT(CASE WHEN TIMESTAMPDIFF(HOUR, t.created_at, t.resolved_at) <= 
        CASE 
            WHEN t.priority = 'critical' THEN 4
            WHEN t.priority = 'high' THEN 24
            WHEN t.priority = 'medium' THEN 72
            WHEN t.priority = 'low' THEN 168
        END THEN 1 END) as sla_compliant,
    ROUND(
        COUNT(CASE WHEN TIMESTAMPDIFF(HOUR, t.created_at, t.resolved_at) <= 
            CASE 
                WHEN t.priority = 'critical' THEN 4
                WHEN t.priority = 'high' THEN 24
                WHEN t.priority = 'medium' THEN 72
                WHEN t.priority = 'low' THEN 168
            END THEN 1 END) * 100.0 / COUNT(t.id), 2
    ) as sla_percentage
FROM auth_user u
JOIN crm_userprofile up ON u.id = up.user_id
LEFT JOIN crm_ticket t ON u.id = t.assigned_to_id
WHERE t.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
AND up.role IN ('agent', 'superagent')
GROUP BY u.id, u.username, up.role
HAVING total_assigned > 0
ORDER BY sla_percentage DESC, total_assigned DESC;
```

#### 3. Zapytania Raportowe

**Raport miesięczny:**
```sql
SELECT 
    DATE_FORMAT(t.created_at, '%Y-%m') as month,
    COUNT(t.id) as total_tickets,
    COUNT(CASE WHEN t.status = 'resolved' THEN 1 END) as resolved_tickets,
    COUNT(CASE WHEN t.status = 'closed' THEN 1 END) as closed_tickets,
    AVG(TIMESTAMPDIFF(HOUR, t.created_at, t.resolved_at)) as avg_resolution_hours,
    COUNT(CASE WHEN t.priority = 'critical' THEN 1 END) as critical_tickets,
    COUNT(CASE WHEN t.priority = 'high' THEN 1 END) as high_tickets,
    COUNT(CASE WHEN t.priority = 'medium' THEN 1 END) as medium_tickets,
    COUNT(CASE WHEN t.priority = 'low' THEN 1 END) as low_tickets
FROM crm_ticket t
WHERE t.created_at >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
GROUP BY DATE_FORMAT(t.created_at, '%Y-%m')
ORDER BY month DESC;
```

**Raport kategorii zgłoszeń:**
```sql
SELECT 
    t.category,
    COUNT(t.id) as total_tickets,
    COUNT(CASE WHEN t.status = 'resolved' THEN 1 END) as resolved_tickets,
    AVG(TIMESTAMPDIFF(HOUR, t.created_at, t.resolved_at)) as avg_resolution_hours,
    COUNT(CASE WHEN t.priority = 'critical' THEN 1 END) as critical_tickets,
    COUNT(CASE WHEN t.priority = 'high' THEN 1 END) as high_tickets
FROM crm_ticket t
WHERE t.created_at >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
GROUP BY t.category
ORDER BY total_tickets DESC;
```

### Procedury Składowane

#### 1. Procedura Aktualizacji Statystyk
```sql
DELIMITER //

CREATE PROCEDURE UpdateTicketStatistics()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE org_id INT;
    DECLARE agent_id INT;
    DECLARE period_start DATETIME;
    DECLARE period_end DATETIME;
    
    -- Cursor dla organizacji
    DECLARE org_cursor CURSOR FOR 
        SELECT id FROM crm_organization;
    
    -- Cursor dla agentów
    DECLARE agent_cursor CURSOR FOR 
        SELECT id FROM auth_user u
        JOIN crm_userprofile up ON u.id = up.user_id
        WHERE up.role IN ('agent', 'superagent');
    
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    -- Aktualizuj statystyki dzienne
    SET period_start = DATE_SUB(CURDATE(), INTERVAL 1 DAY);
    SET period_end = CURDATE();
    
    -- Statystyki dla organizacji
    OPEN org_cursor;
    org_loop: LOOP
        FETCH org_cursor INTO org_id;
        IF done THEN
            LEAVE org_loop;
        END IF;
        
        INSERT INTO crm_ticketstatistics (
            period_type, period_start, period_end, organization_id,
            total_tickets, resolved_tickets, avg_resolution_time, sla_compliance
        )
        SELECT 
            'daily', period_start, period_end, org_id,
            COUNT(*),
            COUNT(CASE WHEN status = 'resolved' THEN 1 END),
            AVG(TIMESTAMPDIFF(HOUR, created_at, resolved_at)),
            COUNT(CASE WHEN TIMESTAMPDIFF(HOUR, created_at, resolved_at) <= 
                CASE 
                    WHEN priority = 'critical' THEN 4
                    WHEN priority = 'high' THEN 24
                    WHEN priority = 'medium' THEN 72
                    WHEN priority = 'low' THEN 168
                END THEN 1 END) * 100.0 / COUNT(*)
        FROM crm_ticket
        WHERE organization_id = org_id
        AND created_at >= period_start
        AND created_at < period_end;
        
    END LOOP;
    CLOSE org_cursor;
    
    -- Statystyki dla agentów
    SET done = FALSE;
    OPEN agent_cursor;
    agent_loop: LOOP
        FETCH agent_cursor INTO agent_id;
        IF done THEN
            LEAVE agent_loop;
        END IF;
        
        INSERT INTO crm_ticketstatistics (
            period_type, period_start, period_end, agent_id,
            total_tickets, resolved_tickets, avg_resolution_time, sla_compliance
        )
        SELECT 
            'daily', period_start, period_end, agent_id,
            COUNT(*),
            COUNT(CASE WHEN status = 'resolved' THEN 1 END),
            AVG(TIMESTAMPDIFF(HOUR, created_at, resolved_at)),
            COUNT(CASE WHEN TIMESTAMPDIFF(HOUR, created_at, resolved_at) <= 
                CASE 
                    WHEN priority = 'critical' THEN 4
                    WHEN priority = 'high' THEN 24
                    WHEN priority = 'medium' THEN 72
                    WHEN priority = 'low' THEN 168
                END THEN 1 END) * 100.0 / COUNT(*)
        FROM crm_ticket
        WHERE assigned_to_id = agent_id
        AND created_at >= period_start
        AND created_at < period_end;
        
    END LOOP;
    CLOSE agent_cursor;
    
END //

DELIMITER ;
```

#### 2. Procedura Czyszczenia Starych Danych
```sql
DELIMITER //

CREATE PROCEDURE CleanupOldData()
BEGIN
    -- Usuń stare logi aktywności (starsze niż 1 rok)
    DELETE FROM crm_activitylog 
    WHERE created_at < DATE_SUB(NOW(), INTERVAL 1 YEAR);
    
    -- Usuń stare statystyki (starsze niż 2 lata)
    DELETE FROM crm_ticketstatistics 
    WHERE created_at < DATE_SUB(NOW(), INTERVAL 2 YEAR);
    
    -- Usuń stare logi pracy agentów (starsze niż 1 rok)
    DELETE FROM crm_agentworklog 
    WHERE created_at < DATE_SUB(NOW(), INTERVAL 1 YEAR);
    
    -- Zaktualizuj statystyki
    CALL UpdateTicketStatistics();
    
END //

DELIMITER ;
```

#### 3. Procedura Automatycznego Zamykania Zgłoszeń
```sql
DELIMITER //

CREATE PROCEDURE AutoCloseResolvedTickets()
BEGIN
    -- Zamknij zgłoszenia rozwiązane starsze niż 30 dni
    UPDATE crm_ticket 
    SET status = 'closed', closed_at = NOW()
    WHERE status = 'resolved' 
    AND resolved_at < DATE_SUB(NOW(), INTERVAL 30 DAY);
    
    -- Loguj automatyczne zamknięcie
    INSERT INTO crm_activitylog (user_id, action_type, ticket_id, description, created_at)
    SELECT 
        NULL, 'ticket_closed', t.id, 
        CONCAT('Automatyczne zamknięcie zgłoszenia ', t.id, ' - rozwiązane ', 
               TIMESTAMPDIFF(DAY, t.resolved_at, NOW()), ' dni temu'),
        NOW()
    FROM crm_ticket t
    WHERE t.status = 'closed' 
    AND t.closed_at = NOW();
    
END //

DELIMITER ;
```

---

## Bezpieczeństwo Danych

### Szyfrowanie Danych

#### 1. Szyfrowanie Załączników
```python
# Implementacja szyfrowania załączników
from cryptography.fernet import Fernet
from django.conf import settings

class FileEncryption:
    def __init__(self):
        self.key = settings.FILE_ENCRYPTION_KEY
    
    def encrypt_file(self, file_content):
        """Szyfruje zawartość pliku"""
        fernet = Fernet(self.key)
        return fernet.encrypt(file_content)
    
    def decrypt_file(self, encrypted_content):
        """Deszyfruje zawartość pliku"""
        fernet = Fernet(self.key)
        return fernet.decrypt(encrypted_content)

# Użycie w modelu
class TicketAttachment(models.Model):
    # ... inne pola ...
    encryption_key = models.BinaryField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.encryption_key:
            self.encryption_key = Fernet.generate_key()
            # Szyfrowanie zawartości pliku
            if self.file:
                file_content = self.file.read()
                encrypted_content = self.encrypt_file(file_content)
                # Zapisanie zaszyfrowanej zawartości
                self.file.save(self.filename, ContentFile(encrypted_content))
        super().save(*args, **kwargs)
```

#### 2. Szyfrowanie Wrażliwych Pól
```python
# Implementacja szyfrowania pól w bazie danych
from django.db import models
from cryptography.fernet import Fernet

class EncryptedTextField(models.TextField):
    """Pole tekstowe z automatycznym szyfrowaniem"""
    
    def __init__(self, *args, **kwargs):
        self.cipher = Fernet(settings.FILE_ENCRYPTION_KEY)
        super().__init__(*args, **kwargs)
    
    def to_python(self, value):
        """Deszyfruje wartość przy odczycie z bazy"""
        if value is None:
            return value
        try:
            return self.cipher.decrypt(value.encode()).decode()
        except:
            return value  # Jeśli deszyfrowanie się nie powiedzie
    
    def get_prep_value(self, value):
        """Szyfruje wartość przed zapisem do bazy"""
        if value is None:
            return value
        return self.cipher.encrypt(value.encode()).decode()

# Użycie w modelu
class UserProfile(models.Model):
    # ... inne pola ...
    phone = EncryptedTextField(blank=True)  # Szyfrowany numer telefonu
```

### Kontrola Dostępu

#### 1. Row-Level Security
```sql
-- Implementacja RLS dla MySQL (używając views)
CREATE VIEW secure_ticket_view AS
SELECT 
    t.*,
    CASE 
        WHEN u.id = t.created_by_id THEN 1
        WHEN u.id = t.assigned_to_id THEN 1
        WHEN up.role = 'admin' THEN 1
        WHEN up.role = 'superagent' THEN 1
        WHEN up.role = 'agent' AND o.id IN (
            SELECT organization_id FROM crm_userprofile_organizations 
            WHERE userprofile_id = up.id
        ) THEN 1
        ELSE 0
    END as can_access
FROM crm_ticket t
JOIN crm_organization o ON t.organization_id = o.id
JOIN auth_user u ON u.id = @current_user_id
JOIN crm_userprofile up ON u.id = up.user_id;
```

#### 2. Audit Trail
```python
# Implementacja audit trail
from django.db import models
from django.contrib.auth.models import User

class AuditMixin(models.Model):
    """Mixin dodający pola audit trail"""
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='%(class)s_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='%(class)s_updated')
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

# Użycie w modelu
class Ticket(AuditMixin, models.Model):
    # ... pola zgłoszenia ...
    pass
```

### Backup i Recovery

#### 1. Strategia Kopii Zapasowych
```bash
#!/bin/bash
# Skrypt tworzenia kopii zapasowych

# Konfiguracja
BACKUP_DIR="/backups/$(date +%Y%m%d)"
DB_NAME="helpdesk_db"
DB_USER="root"
DB_PASS="password"

# Utwórz katalog na kopie
mkdir -p $BACKUP_DIR

# Kopia bazy danych
mysqldump -u$DB_USER -p$DB_PASS $DB_NAME | gzip > $BACKUP_DIR/database.sql.gz

# Kopia plików
tar -czf $BACKUP_DIR/files.tar.gz /var/www/helpdesk/media/

# Kopia konfiguracji
tar -czf $BACKUP_DIR/config.tar.gz /etc/apache2/ /etc/mysql/

# Szyfrowanie kopii
gpg --symmetric --cipher-algo AES256 $BACKUP_DIR/database.sql.gz
gpg --symmetric --cipher-algo AES256 $BACKUP_DIR/files.tar.gz
gpg --symmetric --cipher-algo AES256 $BACKUP_DIR/config.tar.gz

# Usuń nieszyfrowane kopie
rm $BACKUP_DIR/database.sql.gz
rm $BACKUP_DIR/files.tar.gz
rm $BACKUP_DIR/config.tar.gz

# Wyślij kopie na zdalny serwer
rsync -avz $BACKUP_DIR/ backup-server:/backups/helpdesk/

# Usuń kopie starsze niż 30 dni
find /backups -name "*.gz.gpg" -mtime +30 -delete
```

#### 2. Procedura Przywracania
```bash
#!/bin/bash
# Skrypt przywracania kopii zapasowych

# Konfiguracja
BACKUP_DATE=$1
BACKUP_DIR="/backups/$BACKUP_DATE"
DB_NAME="helpdesk_db"
DB_USER="root"
DB_PASS="password"

# Sprawdź czy kopia istnieje
if [ ! -d "$BACKUP_DIR" ]; then
    echo "Kopia zapasowa z $BACKUP_DATE nie istnieje"
    exit 1
fi

# Zatrzymaj usługi
systemctl stop apache2
systemctl stop mysql

# Deszyfrowanie kopii
gpg --decrypt $BACKUP_DIR/database.sql.gz.gpg > $BACKUP_DIR/database.sql.gz
gpg --decrypt $BACKUP_DIR/files.tar.gz.gpg > $BACKUP_DIR/files.tar.gz
gpg --decrypt $BACKUP_DIR/config.tar.gz.gpg > $BACKUP_DIR/config.tar.gz

# Przywróć bazę danych
gunzip -c $BACKUP_DIR/database.sql.gz | mysql -u$DB_USER -p$DB_PASS $DB_NAME

# Przywróć pliki
tar -xzf $BACKUP_DIR/files.tar.gz -C /

# Przywróć konfigurację
tar -xzf $BACKUP_DIR/config.tar.gz -C /

# Uruchom usługi
systemctl start mysql
systemctl start apache2

# Test funkcjonalności
python manage.py check --deploy

# Wyczyść pliki tymczasowe
rm $BACKUP_DIR/database.sql.gz
rm $BACKUP_DIR/files.tar.gz
rm $BACKUP_DIR/config.tar.gz
```

---

## Monitoring i Wydajność

### Monitoring Bazy Danych

#### 1. Metryki Wydajności
```sql
-- Sprawdzenie wydajności zapytań
SELECT 
    query,
    count_star,
    avg_timer_wait/1000000000 as avg_time_seconds,
    max_timer_wait/1000000000 as max_time_seconds
FROM performance_schema.events_statements_summary_by_digest
ORDER BY avg_timer_wait DESC
LIMIT 10;

-- Sprawdzenie użycia indeksów
SELECT 
    table_name,
    index_name,
    cardinality,
    sub_part,
    packed,
    nullable,
    index_type
FROM information_schema.statistics
WHERE table_schema = 'helpdesk_db'
ORDER BY table_name, seq_in_index;

-- Sprawdzenie rozmiaru tabel
SELECT 
    table_name,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size in MB',
    ROUND((data_length / 1024 / 1024), 2) AS 'Data Size in MB',
    ROUND((index_length / 1024 / 1024), 2) AS 'Index Size in MB'
FROM information_schema.tables
WHERE table_schema = 'helpdesk_db'
ORDER BY (data_length + index_length) DESC;
```

#### 2. Monitoring Wolnych Zapytań
```sql
-- Sprawdzenie wolnych zapytań
SELECT 
    id,
    user,
    host,
    db,
    command,
    time,
    state,
    info
FROM information_schema.processlist
WHERE time > 5 AND command != 'Sleep'
ORDER BY time DESC;

-- Sprawdzenie blokad
SELECT 
    r.trx_id waiting_trx_id,
    r.trx_mysql_thread_id waiting_thread,
    r.trx_query waiting_query,
    b.trx_id blocking_trx_id,
    b.trx_mysql_thread_id blocking_thread,
    b.trx_query blocking_query
FROM information_schema.innodb_lock_waits w
INNER JOIN information_schema.innodb_trx b ON b.trx_id = w.blocking_trx_id
INNER JOIN information_schema.innodb_trx r ON r.trx_id = w.requesting_trx_id;
```

#### 3. Monitoring Połączeń
```sql
-- Sprawdzenie połączeń
SELECT 
    user,
    host,
    db,
    command,
    time,
    state,
    COUNT(*) as connection_count
FROM information_schema.processlist
GROUP BY user, host, db, command, state
ORDER BY connection_count DESC;

-- Sprawdzenie limitów połączeń
SHOW VARIABLES LIKE 'max_connections';
SHOW STATUS LIKE 'Threads_connected';
SHOW STATUS LIKE 'Threads_running';
```

### Optymalizacja Wydajności

#### 1. Analiza Zapytań
```python
# Analiza zapytań Django
from django.db import connection
from django.conf import settings

def analyze_queries():
    """Analiza zapytań wykonanych przez Django"""
    if settings.DEBUG:
        queries = connection.queries
        print(f"Liczba zapytań: {len(queries)}")
        
        for query in queries:
            print(f"SQL: {query['sql']}")
            print(f"Czas: {query['time']}s")
            print("---")
    else:
        print("Analiza zapytań dostępna tylko w trybie DEBUG")

# Użycie w widoku
def ticket_list(request):
    # ... logika widoku ...
    
    # Analiza zapytań
    analyze_queries()
    
    return render(request, 'tickets/list.html', context)
```

#### 2. Cache'owanie Zapytań
```python
# Cache'owanie często używanych zapytań
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key

def get_ticket_stats():
    """Pobiera statystyki zgłoszeń z cache"""
    cache_key = 'ticket_stats'
    stats = cache.get(cache_key)
    
    if stats is None:
        stats = {
            'total': Ticket.objects.count(),
            'new': Ticket.objects.filter(status='new').count(),
            'in_progress': Ticket.objects.filter(status='in_progress').count(),
            'resolved': Ticket.objects.filter(status='resolved').count(),
            'closed': Ticket.objects.filter(status='closed').count(),
        }
        cache.set(cache_key, stats, 300)  # Cache na 5 minut
    
    return stats

def invalidate_ticket_cache():
    """Unieważnia cache statystyk zgłoszeń"""
    cache.delete('ticket_stats')
```

#### 3. Optymalizacja Indeksów
```sql
-- Analiza użycia indeksów
SELECT 
    object_schema,
    object_name,
    index_name,
    count_read,
    count_read / (count_read + count_fetch) as read_ratio
FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE object_schema = 'helpdesk_db'
ORDER BY count_read DESC;

-- Sprawdzenie nieużywanych indeksów
SELECT 
    object_schema,
    object_name,
    index_name,
    count_read,
    count_fetch
FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE object_schema = 'helpdesk_db'
AND count_read = 0
AND count_fetch = 0;
```

---

## Migracje i Wersjonowanie

### Zarządzanie Migracjami

#### 1. Struktura Migracji
```
crm/migrations/
├── __init__.py
├── 0001_initial.py
├── 0002_auto_20240101_1200.py
├── 0003_auto_20240115_1400.py
├── 0004_set_resolved_at_for_existing.py
├── 0005_add_ticket_statistics.py
├── 0006_add_encryption_fields.py
└── 0007_optimize_indexes.py
```

#### 2. Tworzenie Migracji
```bash
# Tworzenie migracji
python manage.py makemigrations

# Tworzenie migracji dla konkretnej aplikacji
python manage.py makemigrations crm

# Tworzenie pustej migracji
python manage.py makemigrations --empty crm

# Sprawdzenie statusu migracji
python manage.py showmigrations

# Zastosowanie migracji
python manage.py migrate

# Zastosowanie migracji dla konkretnej aplikacji
python manage.py migrate crm

# Wycofanie migracji
python manage.py migrate crm 0003
```

#### 3. Przykłady Migracji
```python
# Migracja dodająca nowe pole
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('crm', '0003_auto_20240115_1400'),
    ]
    
    operations = [
        migrations.AddField(
            model_name='ticket',
            name='resolution_notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]
```

```python
# Migracja dodająca indeks
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('crm', '0004_add_resolution_notes'),
    ]
    
    operations = [
        migrations.RunSQL(
            "CREATE INDEX idx_ticket_resolution_notes ON crm_ticket(resolution_notes(100));",
            reverse_sql="DROP INDEX idx_ticket_resolution_notes ON crm_ticket;"
        ),
    ]
```

```python
# Migracja z danymi
from django.db import migrations

def populate_resolution_notes(apps, schema_editor):
    Ticket = apps.get_model('crm', 'Ticket')
    for ticket in Ticket.objects.filter(status='resolved'):
        ticket.resolution_notes = f"Zgłoszenie rozwiązane automatycznie"
        ticket.save()

def reverse_populate_resolution_notes(apps, schema_editor):
    Ticket = apps.get_model('crm', 'Ticket')
    Ticket.objects.update(resolution_notes='')

class Migration(migrations.Migration):
    dependencies = [
        ('crm', '0004_add_resolution_notes'),
    ]
    
    operations = [
        migrations.RunPython(
            populate_resolution_notes,
            reverse_populate_resolution_notes
        ),
    ]
```

### Wersjonowanie Schematu

#### 1. Historia Zmian
```python
# Dokumentacja zmian schematu
SCHEMA_CHANGES = {
    'v1.0.0': {
        'date': '2024-01-01',
        'changes': [
            'Utworzenie podstawowych tabel',
            'Implementacja modeli User, Organization, Ticket',
            'Dodanie podstawowych indeksów',
        ]
    },
    'v1.1.0': {
        'date': '2024-01-15',
        'changes': [
            'Dodanie tabeli TicketComment',
            'Dodanie tabeli TicketAttachment',
            'Implementacja szyfrowania załączników',
        ]
    },
    'v1.2.0': {
        'date': '2024-02-01',
        'changes': [
            'Dodanie tabeli ActivityLog',
            'Implementacja logowania aktywności',
            'Dodanie indeksów dla wydajności',
        ]
    },
}
```

#### 2. Procedura Aktualizacji
```bash
#!/bin/bash
# Skrypt aktualizacji schematu bazy danych

# Sprawdź aktualną wersję
CURRENT_VERSION=$(python manage.py showmigrations crm | grep '\[X\]' | wc -l)
echo "Aktualna wersja: $CURRENT_VERSION"

# Utwórz kopię zapasową
python manage.py backup_database --format=sql

# Sprawdź czy są nowe migracje
python manage.py showmigrations crm

# Zastosuj migracje
python manage.py migrate

# Sprawdź nową wersję
NEW_VERSION=$(python manage.py showmigrations crm | grep '\[X\]' | wc -l)
echo "Nowa wersja: $NEW_VERSION"

# Test funkcjonalności
python manage.py check --deploy

# Restart usług
systemctl restart apache2
```

---

## Procedury Konserwacji

### Konserwacja Codzienna

#### 1. Sprawdzenie Stanu Bazy Danych
```bash
#!/bin/bash
# Skrypt codziennej konserwacji

# Sprawdź połączenia
mysql -u root -p -e "SHOW PROCESSLIST;"

# Sprawdź wolne miejsce
df -h

# Sprawdź logi błędów
tail -100 /var/log/mysql/error.log | grep -i error

# Sprawdź wydajność
mysql -u root -p -e "SHOW STATUS LIKE 'Threads_connected';"
mysql -u root -p -e "SHOW STATUS LIKE 'Threads_running';"

# Sprawdź indeksy
mysql -u root -p -e "SHOW INDEX FROM crm_ticket;"
```

#### 2. Optymalizacja Tabel
```sql
-- Optymalizacja tabel
OPTIMIZE TABLE crm_ticket;
OPTIMIZE TABLE crm_ticketcomment;
OPTIMIZE TABLE crm_ticketattachment;
OPTIMIZE TABLE crm_activitylog;
OPTIMIZE TABLE crm_userprofile;
OPTIMIZE TABLE crm_organization;

-- Analiza tabel
ANALYZE TABLE crm_ticket;
ANALYZE TABLE crm_ticketcomment;
ANALYZE TABLE crm_ticketattachment;
ANALYZE TABLE crm_activitylog;
ANALYZE TABLE crm_userprofile;
ANALYZE TABLE crm_organization;
```

### Konserwacja Tygodniowa

#### 1. Czyszczenie Starych Danych
```sql
-- Usuń stare logi aktywności (starsze niż 1 rok)
DELETE FROM crm_activitylog 
WHERE created_at < DATE_SUB(NOW(), INTERVAL 1 YEAR);

-- Usuń stare statystyki (starsze niż 2 lata)
DELETE FROM crm_ticketstatistics 
WHERE created_at < DATE_SUB(NOW(), INTERVAL 2 YEAR);

-- Usuń stare logi pracy agentów (starsze niż 1 rok)
DELETE FROM crm_agentworklog 
WHERE created_at < DATE_SUB(NOW(), INTERVAL 1 YEAR);
```

#### 2. Aktualizacja Statystyk
```sql
-- Zaktualizuj statystyki tabel
ANALYZE TABLE crm_ticket;
ANALYZE TABLE crm_ticketcomment;
ANALYZE TABLE crm_ticketattachment;
ANALYZE TABLE crm_activitylog;
ANALYZE TABLE crm_userprofile;
ANALYZE TABLE crm_organization;

-- Zaktualizuj statystyki indeksów
ANALYZE TABLE crm_ticket;
ANALYZE TABLE crm_ticketcomment;
ANALYZE TABLE crm_ticketattachment;
ANALYZE TABLE crm_activitylog;
```

### Konserwacja Miesięczna

#### 1. Przegląd Wydajności
```sql
-- Sprawdź wolne zapytania
SELECT 
    query,
    count_star,
    avg_timer_wait/1000000000 as avg_time_seconds,
    max_timer_wait/1000000000 as max_time_seconds
FROM performance_schema.events_statements_summary_by_digest
ORDER BY avg_timer_wait DESC
LIMIT 20;

-- Sprawdź użycie indeksów
SELECT 
    table_name,
    index_name,
    cardinality,
    sub_part,
    packed,
    nullable,
    index_type
FROM information_schema.statistics
WHERE table_schema = 'helpdesk_db'
ORDER BY table_name, seq_in_index;

-- Sprawdź rozmiar tabel
SELECT 
    table_name,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size in MB',
    ROUND((data_length / 1024 / 1024), 2) AS 'Data Size in MB',
    ROUND((index_length / 1024 / 1024), 2) AS 'Index Size in MB'
FROM information_schema.tables
WHERE table_schema = 'helpdesk_db'
ORDER BY (data_length + index_length) DESC;
```

#### 2. Optymalizacja Indeksów
```sql
-- Sprawdź nieużywane indeksy
SELECT 
    object_schema,
    object_name,
    index_name,
    count_read,
    count_fetch
FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE object_schema = 'helpdesk_db'
AND count_read = 0
AND count_fetch = 0;

-- Sprawdź indeksy wymagające optymalizacji
SELECT 
    object_schema,
    object_name,
    index_name,
    count_read,
    count_fetch,
    count_read / (count_read + count_fetch) as read_ratio
FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE object_schema = 'helpdesk_db'
ORDER BY count_read DESC;
```

---

## Troubleshooting

### Częste Problemy

#### 1. Problemy z Połączeniem
```bash
# Sprawdź status MySQL
systemctl status mysql

# Sprawdź logi MySQL
tail -100 /var/log/mysql/error.log

# Sprawdź konfigurację MySQL
mysql --help | grep -A 1 "Default options"

# Test połączenia
mysql -u root -p -e "SELECT 1;"
```

#### 2. Problemy z Wydajnością
```sql
-- Sprawdź wolne zapytania
SELECT 
    id,
    user,
    host,
    db,
    command,
    time,
    state,
    info
FROM information_schema.processlist
WHERE time > 5 AND command != 'Sleep'
ORDER BY time DESC;

-- Sprawdź blokady
SELECT 
    r.trx_id waiting_trx_id,
    r.trx_mysql_thread_id waiting_thread,
    r.trx_query waiting_query,
    b.trx_id blocking_trx_id,
    b.trx_mysql_thread_id blocking_thread,
    b.trx_query blocking_query
FROM information_schema.innodb_lock_waits w
INNER JOIN information_schema.innodb_trx b ON b.trx_id = w.blocking_trx_id
INNER JOIN information_schema.innodb_trx r ON r.trx_id = w.requesting_trx_id;
```

#### 3. Problemy z Miejscem na Dysk
```bash
# Sprawdź wolne miejsce
df -h

# Sprawdź rozmiar bazy danych
mysql -u root -p -e "SELECT table_schema AS 'Database', ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size in MB' FROM information_schema.tables GROUP BY table_schema;"

# Sprawdź rozmiar tabel
mysql -u root -p -e "SELECT table_name, ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size in MB' FROM information_schema.tables WHERE table_schema = 'helpdesk_db' ORDER BY (data_length + index_length) DESC;"
```

### Procedury Naprawcze

#### 1. Naprawa Uszkodzonej Tabeli
```sql
-- Sprawdź integralność tabeli
CHECK TABLE crm_ticket;

-- Napraw tabelę
REPAIR TABLE crm_ticket;

-- Jeśli naprawa nie pomoże, użyj myisamchk
-- myisamchk -r /var/lib/mysql/helpdesk_db/crm_ticket.MYI
```

#### 2. Przywracanie z Kopii Zapasowej
```bash
# Zatrzymaj usługi
systemctl stop apache2
systemctl stop mysql

# Przywróć bazę danych
gunzip -c /backups/database/latest.sql.gz | mysql -u root -p helpdesk_db

# Uruchom usługi
systemctl start mysql
systemctl start apache2

# Test funkcjonalności
python manage.py check --deploy
```

#### 3. Optymalizacja Wolnych Zapytań
```sql
-- Sprawdź plan wykonania zapytania
EXPLAIN SELECT * FROM crm_ticket WHERE status = 'new' ORDER BY created_at DESC;

-- Sprawdź indeksy dla tabeli
SHOW INDEX FROM crm_ticket;

-- Dodaj brakujący indeks
CREATE INDEX idx_ticket_status_created ON crm_ticket(status, created_at);
```

### Monitoring i Alerty

#### 1. Skrypt Monitoringu
```bash
#!/bin/bash
# Skrypt monitoringu bazy danych

# Sprawdź połączenia
CONNECTIONS=$(mysql -u root -p -e "SHOW STATUS LIKE 'Threads_connected';" | grep Threads_connected | awk '{print $2}')
MAX_CONNECTIONS=$(mysql -u root -p -e "SHOW VARIABLES LIKE 'max_connections';" | grep max_connections | awk '{print $2}')

if [ $CONNECTIONS -gt $((MAX_CONNECTIONS * 80 / 100)) ]; then
    echo "ALERT: Wysokie użycie połączeń: $CONNECTIONS/$MAX_CONNECTIONS"
fi

# Sprawdź wolne miejsce
DISK_USAGE=$(df /var/lib/mysql | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "ALERT: Wysokie użycie dysku: $DISK_USAGE%"
fi

# Sprawdź wolne zapytania
SLOW_QUERIES=$(mysql -u root -p -e "SHOW STATUS LIKE 'Slow_queries';" | grep Slow_queries | awk '{print $2}')
if [ $SLOW_QUERIES -gt 10 ]; then
    echo "ALERT: Wysoka liczba wolnych zapytań: $SLOW_QUERIES"
fi
```

#### 2. Konfiguracja Alertów
```bash
# Dodaj do crontab
# */5 * * * * /path/to/monitoring_script.sh >> /var/log/db_monitoring.log

# Konfiguracja logrotate
cat > /etc/logrotate.d/db_monitoring << EOF
/var/log/db_monitoring.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
EOF
```

---

*Ostatnia aktualizacja: Styczeń 2025*
