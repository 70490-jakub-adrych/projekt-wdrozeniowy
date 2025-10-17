# System Powiadomień Email - Podsumowanie

## 📧 Kiedy kto dostaje maile?

### **KLIENT** (role='client')

#### Otrzymuje powiadomienia o:
- ✅ **Zatwierdzeniu konta** - gdy admin zatwierdzi jego konto
- ✅ **Swoich ticketach**:
  - Zmiana statusu (status_changed)
  - Nowy komentarz (commented)
  - Aktualizacja (updated)
  - Zamknięcie (closed)
  - Ponowne otwarcie (reopened)
  - Przypisanie do agenta (assigned)

#### NIE otrzymuje powiadomień o:
- ❌ Ticketach innych klientów
- ❌ Nowych ticketach w systemie (tylko własne)

---

### **AGENT** (role='agent')

#### Otrzymuje powiadomienia o:
- ✅ **Zatwierdzeniu konta**
- ✅ **Nowych użytkownikach oczekujących na zatwierdzenie** (po weryfikacji emaila)
- ✅ **Nowych ticketach** w swojej organizacji (notification_type='created')
  - Tylko tickety z organizacji, do których należy agent
- ✅ **Ticketach przypisanych do niego**:
  - Zmiana statusu
  - Nowy komentarz
  - Aktualizacja
  - Zamknięcie
  - Ponowne otwarcie
- ✅ **Nieprzypisanych ticketach** w swojej organizacji:
  - Zmiana statusu
  - Nowy komentarz
  - Aktualizacja

#### NIE otrzymuje powiadomień o:
- ❌ Ticketach z innych organizacji (chyba że jest przypisany)
- ❌ Ticketach przypisanych do innych agentów (chyba że należą do jego organizacji i są nieprzypisane)

---

### **SUPERAGENT** (role='superagent')

#### Otrzymuje powiadomienia o:
- ✅ **Nowych użytkownikach oczekujących na zatwierdzenie** (po weryfikacji emaila)
- ✅ **WSZYSTKICH nowych ticketach** niezależnie od organizacji (notification_type='created')
- ✅ **WSZYSTKICH ticketach przypisanych do niego**
- ✅ **WSZYSTKICH nieprzypisanych ticketach** z wszystkich organizacji
- ✅ **WSZYSTKICH aktualizacjach ticketów**:
  - Zmiana statusu
  - Nowy komentarz
  - Aktualizacja
  - Zamknięcie
  - Ponowne otwarcie

#### Różnica od agenta:
- ✅ Widzi i dostaje powiadomienia o ticketach ze **wszystkich organizacji**, nie tylko swojej

---

### **ADMIN** (role='admin')

#### Otrzymuje powiadomienia o:
- ✅ **Dokładnie to samo co SUPERAGENT**
- ✅ **Nowych użytkownikach oczekujących na zatwierdzenie** (po weryfikacji emaila)
- ✅ Wszystkie tickety z wszystkich organizacji
- ✅ Wszystkie zmiany statusów, komentarze, aktualizacje

---

## 🎯 Szczegóły logiki powiadomień

### Rejestracja nowego użytkownika

```
UŻYTKOWNIK rejestruje się i weryfikuje email → Powiadomienia dostają:
  ✅ Wszyscy AGENCI (mogą zatwierdzać użytkowników w swoich organizacjach)
  ✅ Wszyscy SUPERAGENCI (mogą zatwierdzać wszystkich użytkowników)
  ✅ Wszyscy ADMINI (mogą zatwierdzać wszystkich użytkowników)
  ❌ Klienci NIE dostają powiadomień o nowych użytkownikach
```

### Typ powiadomienia: `created` (Nowy ticket)

```
KLIENT tworzy ticket → Powiadomienia dostają:
  ✅ Wszyscy AGENCI z organizacji ticketa
  ✅ Wszyscy SUPERAGENCI (niezależnie od organizacji)
  ✅ Wszyscy ADMINI (niezależnie od organizacji)
  ❌ Sam klient NIE dostaje powiadomienia (utworzył ticket sam)
```

### Typ powiadomienia: `assigned` (Przypisanie)

```
Ticket zostaje przypisany do AGENTA → Powiadomienia dostają:
  ✅ Agent, do którego przypisano ticket
  ✅ Twórca ticketa (klient)
  ❌ Osoba, która przypisała ticket (triggered_by)
```

### Typ powiadomienia: `status_changed`, `commented`, `updated`

```
Jeśli ticket JEST PRZYPISANY:
  ✅ Przypisany agent (chyba że on sam dokonał zmiany)
  ✅ Twórca ticketa (klient)

Jeśli ticket JEST NIEPRZYPISANY:
  ✅ Twórca ticketa (klient)
  ✅ Wszyscy AGENCI z organizacji ticketa
  ✅ Wszyscy SUPERAGENCI
  ✅ Wszyscy ADMINI
```

### Typ powiadomienia: `closed`, `reopened`

```
Działa tak samo jak `status_changed`
```

---

## 🗑️ Usuwanie użytkownika (np. agenta)

### Co się dzieje z ticketami?

```python
# W models.py linia 308:
assigned_to = models.ForeignKey(
    User, 
    on_delete=models.SET_NULL,  # ← TUTAJ!
    null=True, 
    blank=True
)
```

**Rezultat:**
- ✅ Gdy agent zostanie usunięty, wszystkie jego tickety mają `assigned_to = NULL`
- ✅ Tickety stają się **nieprzypisane**
- ✅ Pojawią się na liście ticketów dla innych agentów w tej samej organizacji
- ✅ Pojawią się na liście ticketów dla superagentów i adminów

**NIE są usuwane**, tylko odłączone od usuniętego użytkownika.

---

## ⚙️ Ustawienia użytkownika

Każdy użytkownik może wyłączyć konkretne typy powiadomień w `EmailNotificationSettings`:

```python
class EmailNotificationSettings(models.Model):
    notify_ticket_created = BooleanField(default=True)
    notify_ticket_assigned = BooleanField(default=True)
    notify_ticket_status_changed = BooleanField(default=True)
    notify_ticket_commented = BooleanField(default=True)
    notify_ticket_updated = BooleanField(default=True)
    notify_ticket_closed = BooleanField(default=True)
    notify_ticket_reopened = BooleanField(default=True)
    notify_account_approved = BooleanField(default=True)
    notify_password_reset = BooleanField(default=True)
```

Jeśli użytkownik wyłączy np. `notify_ticket_commented = False`, to NIE dostanie emaili o nowych komentarzach.

---

## 📝 Przykłady scenariuszy

### Scenariusz 0: Nowy użytkownik się rejestruje

```
1. Użytkownik Jan wypełnia formularz rejestracji
2. System wysyła kod weryfikacyjny na email Jana
3. Jan wprowadza kod i weryfikuje email
4. Powiadomienia dostają:
   ✅ Agent Piotr (może zatwierdzać użytkowników)
   ✅ Agent Anna (może zatwierdzać użytkowników)
   ✅ Superagent Marek (może zatwierdzać użytkowników)
   ✅ Admin Tomasz (może zatwierdzać użytkowników)
5. Admin/Superagent/Agent zatwierdza konto Jana
6. Jan dostaje email o zatwierdzeniu konta
7. Jan może się zalogować i korzystać z systemu
```

### Scenariusz 1: Klient tworzy nowy ticket w organizacji "Firma ABC"

```
1. Klient Jan tworzy ticket w organizacji "Firma ABC"
2. Powiadomienia dostają:
   ✅ Agent Piotr (należy do "Firma ABC")
   ✅ Agent Anna (należy do "Firma ABC")
   ✅ Superagent Marek (widzi wszystkie organizacje)
   ✅ Admin Tomasz (widzi wszystkie organizacje)
   ❌ Klient Jan (sam utworzył, nie dostaje powiadomienia)
   ❌ Agent Karol (należy do "Firma XYZ", innej organizacji)
```

### Scenariusz 2: Admin przypisuje ticket do agenta Piotra

```
1. Admin Tomasz przypisuje ticket do Agenta Piotra
2. Powiadomienia dostają:
   ✅ Agent Piotr (dostał przypisany ticket)
   ✅ Klient Jan (twórca ticketa)
   ❌ Admin Tomasz (sam przypisał, triggered_by)
```

### Scenariusz 3: Agent Piotr dodaje komentarz do przypisanego ticketa

```
1. Agent Piotr dodaje komentarz do ticketa przypisanego do niego
2. Powiadomienia dostają:
   ✅ Klient Jan (twórca ticketa)
   ❌ Agent Piotr (sam dodał komentarz, triggered_by)
   ❌ Inni agenci (ticket jest przypisany, więc tylko twórca dostaje powiadomienie)
```

### Scenariusz 4: Agent Piotr zostaje usunięty z systemu

```
1. Admin usuwa konto Agenta Piotra
2. Co się dzieje:
   ✅ Wszystkie tickety przypisane do Piotra: assigned_to = NULL (nieprzypisane)
   ✅ Tickety pojawiają się na liście dla innych agentów z tej samej organizacji
   ✅ Tickety pojawiają się na liście dla superagentów i adminów
   ✅ Komentarze/logi Piotra pozostają (on_delete=models.CASCADE dla innych relacji)
```

### Scenariusz 5: Klient dodaje komentarz do nieprzypisanego ticketa

```
1. Klient Jan dodaje komentarz do nieprzypisanego ticketa
2. Powiadomienia dostają:
   ✅ Wszyscy agenci z organizacji "Firma ABC"
   ✅ Wszyscy superagenci
   ✅ Wszyscy admini
   ❌ Klient Jan (sam dodał komentarz)
```

---

## 🔧 Pliki kluczowe

1. **`crm/services/email/ticket.py`** - Logika powiadomień o ticketach
2. **`crm/services/email/account.py`** - Powiadomienia o kontach (zatwierdzenie, nowy użytkownik)
3. **`crm/models.py`** - Definicje modeli (on_delete=SET_NULL dla assigned_to)
4. **`crm/signals.py`** - Sygnały dla zatwierdzania kont
5. **`crm/views/auth_views.py`** - Widok rejestracji wywołujący `send_new_user_notification_to_admins()`
6. **`crm/views/tickets/*.py`** - Widoki wywołujące `notify_ticket_stakeholders()`

---

## ✅ Potwierdzenie wymagań

| Wymaganie | Status | Szczegóły |
|-----------|--------|-----------|
| Klient dostaje maile o swoich ticketach | ✅ | Zawsze jako creator/stakeholder |
| Klient dostaje maile o koncie | ✅ | Zatwierdzenie, reset hasła |
| Agent dostaje maile o przypisanych ticketach | ✅ | Wszystkie typy powiadomień |
| Agent dostaje maile o nowych ticketach w organizacji | ✅ | notification_type='created' |
| Agent dostaje maile o nieprzypisanych w organizacji | ✅ | status_changed, commented, updated |
| Agent dostaje maile o nowych użytkownikach | ✅ | Po weryfikacji emaila |
| Superagent dostaje maile o WSZYSTKICH ticketach | ✅ | Niezależnie od organizacji |
| Superagent dostaje maile o nowych użytkownikach | ✅ | Po weryfikacji emaila |
| Admin dostaje maile o WSZYSTKICH ticketach | ✅ | Tak samo jak superagent |
| Admin dostaje maile o nowych użytkownikach | ✅ | Po weryfikacji emaila |
| Usunięcie agenta → tickety nieprzypisane | ✅ | on_delete=SET_NULL |

---

## 🆕 Ostatnie zmiany

### 2025-10-17
- ✅ Dodano powiadomienia email dla adminów/superagentów/agentów o nowych użytkownikach oczekujących na zatwierdzenie
- ✅ Powiadomienie wysyłane zaraz po weryfikacji emaila przez użytkownika
- ✅ Utworzono szablon `emails/new_user_pending_approval.html` i `.txt`
- ✅ Dodano funkcję `send_new_user_notification_to_admins()` w `crm/services/email/account.py`

---

**Data aktualizacji:** 2025-10-17  
**Wersja:** 1.1
