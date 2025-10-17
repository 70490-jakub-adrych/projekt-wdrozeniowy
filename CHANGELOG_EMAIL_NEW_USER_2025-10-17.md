# Changelog - System Powiadomień Email

## 2025-10-17 - Dodanie powiadomień o nowych użytkownikach

### 🎯 Problem
Admini, superagenci i agenci nie dostawali powiadomień email gdy nowy użytkownik się rejestrował i czekał na zatwierdzenie konta. Musieli ręcznie sprawdzać sekcję "Oczekujące zatwierdzenia" na dashboardzie.

### ✅ Rozwiązanie
Dodano automatyczne powiadomienia email dla wszystkich użytkowników z rolami admin/superagent/agent, które są wysyłane zaraz po tym jak nowy użytkownik zweryfikuje swój email.

### 📝 Zmiany w kodzie

#### 1. Nowa funkcja w `crm/services/email/account.py`
```python
def send_new_user_notification_to_admins(user):
    """
    Wysyła powiadomienie do adminów/superagentów/agentów 
    gdy nowy użytkownik się zarejestruje i czeka na zatwierdzenie
    """
```

**Co robi:**
- Znajduje wszystkich użytkowników z rolami: `admin`, `superagent`, `agent`
- Wysyła do każdego email z informacjami o nowym użytkowniku:
  - Nazwa użytkownika
  - Email
  - Imię i nazwisko
  - Data rejestracji
  - Link do strony zatwierdzeń
- Zwraca `True` jeśli chociaż jeden email został wysłany pomyślnie

#### 2. Aktualizacja `crm/services/email_service.py`
```python
from .email.account import send_account_approved_email, send_new_user_notification_to_admins

class EmailNotificationService:
    send_new_user_notification_to_admins = staticmethod(send_new_user_notification_to_admins)
```

#### 3. Aktualizacja widoku rejestracji `crm/views/auth_views.py`
```python
# Po weryfikacji emaila:
try:
    EmailNotificationService.send_new_user_notification_to_admins(user)
    logger.info(f"Sent new user notification to admins for {user.username}")
except Exception as e:
    logger.error(f"Failed to send new user notification to admins: {str(e)}")
```

**Kiedy się wywołuje:**
- Zaraz po tym jak użytkownik wpisuje poprawny kod weryfikacyjny z emaila
- PRZED przekierowaniem na stronę "Oczekiwanie na zatwierdzenie"

#### 4. Nowe szablony email

**`crm/templates/emails/new_user_pending_approval.txt`**
- Prosty tekstowy szablon dla klientów email bez HTML
- Zawiera wszystkie kluczowe informacje o nowym użytkowniku
- Link do strony zatwierdzeń

**`crm/templates/emails/new_user_pending_approval.html`**
- Ładnie sformatowany szablon HTML
- Responsywny design
- Gradient header (purple/blue)
- Przejrzysta tabela z danymi użytkownika
- Wyraźny przycisk "Przejdź do zatwierdzeń"
- Alert box z ikoną ⏳ informującą o oczekującym użytkowniku

### 📧 Format emaila

**Temat:** `System Helpdesk - Nowy użytkownik oczekuje na zatwierdzenie`

**Treść zawiera:**
- Powitanie odbiorcy (imię lub username)
- Alert box z informacją o nowym użytkowniku
- Dane użytkownika:
  - Nazwa użytkownika
  - Email
  - Imię i nazwisko
  - Data rejestracji (format: YYYY-MM-DD HH:MM)
- Przycisk/link do strony zatwierdzeń (`/approvals/`)
- Stopka z nazwą systemu i informacją o automatycznej wiadomości

### 🔄 Flow procesu rejestracji (zaktualizowany)

```
1. Użytkownik wypełnia formularz rejestracji
   ↓
2. System tworzy konto (is_active=False, is_approved=False)
   ↓
3. System wysyła kod weryfikacyjny na email użytkownika
   ↓
4. Użytkownik wprowadza kod weryfikacyjny
   ↓
5. System weryfikuje email (email_verified=True, is_active=True)
   ↓
6. 🆕 System wysyła powiadomienia do adminów/superagentów/agentów
   ↓
7. Użytkownik widzi stronę "Oczekiwanie na zatwierdzenie"
   ↓
8. Admin/Superagent/Agent zatwierdza konto (is_approved=True)
   ↓
9. System wysyła email do użytkownika o zatwierdzeniu
   ↓
10. Użytkownik może się zalogować i korzystać z pełnej funkcjonalności
```

### 👥 Kto dostaje powiadomienia?

| Rola | Dostaje powiadomienie? | Może zatwierdzać? |
|------|------------------------|-------------------|
| **Admin** | ✅ Tak | ✅ Wszystkich użytkowników |
| **Superagent** | ✅ Tak | ✅ Wszystkich użytkowników |
| **Agent** | ✅ Tak | ✅ Użytkowników w swoich organizacjach |
| **Client** | ❌ Nie | ❌ Nie |

### 🧪 Testowanie

#### Scenariusz testowy 1: Rejestracja nowego użytkownika
```
1. Otwórz stronę rejestracji
2. Wypełnij formularz (username, email, hasło)
3. Sprawdź email - powinien przyjść kod weryfikacyjny
4. Wprowadź kod weryfikacyjny
5. OCZEKIWANY REZULTAT:
   - Użytkownik widzi stronę "Oczekiwanie na zatwierdzenie"
   - Wszyscy admini/superagenci/agenci dostają email:
     * Temat: "System Helpdesk - Nowy użytkownik oczekuje na zatwierdzenie"
     * Zawiera dane nowego użytkownika
     * Zawiera link do /approvals/
```

#### Scenariusz testowy 2: Sprawdzenie logów
```
1. Po rejestracji sprawdź logi Django
2. OCZEKIWANE LOGI:
   - "Starting new user notification for user@example.com"
   - "New user notification sent to admin@example.com"
   - "Sent new user notification to X/Y recipients"
3. Jeśli X=0: sprawdź czy są admini/superagenci/agenci w systemie
4. Jeśli błąd wysyłania: sprawdź konfigurację EMAIL_BACKEND
```

#### Scenariusz testowy 3: Brak adminów w systemie
```
1. Upewnij się że nie ma użytkowników z rolą admin/superagent/agent
2. Zarejestruj nowego użytkownika i zweryfikuj email
3. OCZEKIWANY REZULTAT:
   - W logach: "No admins/superagents/agents found to notify about new user"
   - Użytkownik może się zarejestrować normalnie
   - Brak crashu aplikacji
```

### 🐛 Możliwe problemy i rozwiązania

#### Problem: Email nie został wysłany
```
PRZYCZYNA: Błędna konfiguracja EMAIL_BACKEND
ROZWIĄZANIE:
1. Sprawdź .env file: EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
2. Sprawdź ustawienia SMTP w settings.py
3. Uruchom test: python manage.py test_email admin@example.com
```

#### Problem: Żaden admin nie dostał emaila
```
PRZYCZYNA: Brak użytkowników z odpowiednią rolą
ROZWIĄZANIE:
1. Sprawdź w Django Admin → User profiles
2. Upewnij się że przynajmniej jeden użytkownik ma rolę: admin, superagent lub agent
3. Sprawdź czy użytkownik ma ustawiony email (user.email)
4. Sprawdź czy użytkownik jest aktywny (is_active=True)
```

#### Problem: Email idzie do spamu
```
PRZYCZYNA: Brak prawidłowej konfiguracji SPF/DKIM
ROZWIĄZANIE:
1. Skontaktuj się z administratorem serwera (mydevil.net)
2. Skonfiguruj SPF record dla domeny
3. Skonfiguruj DKIM dla domeny
4. Użyj prawdziwego adresu nadawcy (nie noreply@localhost)
```

### 📊 Metryki i monitoring

**Logi do monitorowania:**
```bash
# Wszystkie powiadomienia o nowych użytkownikach
grep "new user notification" logs/django.log

# Powiadomienia wysłane pomyślnie
grep "New user notification sent" logs/django.log

# Błędy wysyłania
grep "Failed to send new user notification" logs/django.log
```

**Statystyki:**
- Ile emaili zostało wysłanych: sprawdź logi
- Do ilu odbiorców: `Sent new user notification to X/Y recipients`
- Czy były błędy: szukaj "Failed to send" lub "Error in send_new_user_notification"

### 🔐 Bezpieczeństwo

✅ **Funkcja jest bezpieczna:**
- Nie ujawnia danych użytkownika osobom nieuprawnionym (tylko admini/superagenci/agenci)
- Nie zawiera hasła ani kodu weryfikacyjnego
- Link prowadzi do chronionej strony (wymaga logowania)
- Email wysyłany tylko po pomyślnej weryfikacji adresu email

⚠️ **Uwagi:**
- Email zawiera dane osobowe (imię, nazwisko, email) - zgodne z RODO (uzasadniony interes)
- Odbiorcy to tylko osoby uprawnione do zatwierdzania użytkowników

### 📋 Checklist wdrożenia

- [x] Dodana funkcja `send_new_user_notification_to_admins()`
- [x] Zaktualizowany `EmailNotificationService`
- [x] Dodane wywołanie w widoku rejestracji
- [x] Utworzone szablony email (HTML + TXT)
- [x] Zaktualizowana dokumentacja `EMAIL_NOTIFICATIONS_SUMMARY.md`
- [ ] Przetestowane na środowisku DEV
- [ ] Przetestowane na środowisku PROD
- [ ] Sprawdzone logi po pierwszej rejestracji
- [ ] Potwierdzone otrzymanie emaili przez adminów

### 🚀 Deployment

**Na DEV (dev.betulait.usermd.net):**
```bash
git pull
touch tmp/restart.txt
```

**Na PROD (betulait.usermd.net):**
```bash
git pull
touch tmp/restart.txt
```

**Po deploymencie:**
1. Zarejestruj testowego użytkownika
2. Sprawdź czy email przychodzi do adminów
3. Sprawdź logi: `tail -f logs/django.log | grep "new user"`
4. Zatwierdź testowego użytkownika
5. Usuń testowego użytkownika jeśli niepotrzebny

---

**Autor zmian:** AI Assistant (GitHub Copilot)  
**Data:** 2025-10-17  
**Powiązane issue:** Brak powiadomień o nowych użytkownikach  
**Status:** ✅ Zaimplementowane, oczekuje na testy
