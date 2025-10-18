# 📋 Procedury Operacyjne

## Spis Treści
1. [Wprowadzenie](#wprowadzenie)
2. [Procedury Codzienne](#procedury-codzienne)
3. [Procedury Tygodniowe](#procedury-tygodniowe)
4. [Procedury Miesięczne](#procedury-miesięczne)
5. [Procedury Awaryjne](#procedury-awaryjne)
6. [Procedury Bezpieczeństwa](#procedury-bezpieczeństwa)
7. [Procedury Konserwacji](#procedury-konserwacji)
8. [Procedury Rozwoju](#procedury-rozwoju)
9. [Kontakty i Eskalacja](#kontakty-i-eskalacja)
10. [Szablony i Formularze](#szablony-i-formularze)

---

## Wprowadzenie

Dokument zawiera szczegółowe procedury operacyjne dla systemu helpdesk. Procedury te zapewniają spójność działań, minimalizują ryzyko błędów i gwarantują wysoką jakość usług.

### Cel Dokumentu
- **Standaryzacja** procesów operacyjnych
- **Minimalizacja błędów** ludzkich
- **Zapewnienie ciągłości** działania systemu
- **Szkolenie personelu** operacyjnego
- **Audyt i kontrola** jakości

### Odbiorcy
- **Administratorzy systemu** - główni wykonawcy procedur
- **Zespół IT** - wsparcie techniczne
- **Kierownictwo** - nadzór i kontrola
- **Audytorzy** - weryfikacja zgodności

### Zasady Procedur
- **Szczegółowość** - każdy krok dokładnie opisany
- **Weryfikowalność** - możliwość sprawdzenia wykonania
- **Aktualność** - regularne przeglądy i aktualizacje
- **Dostępność** - łatwy dostęp dla wszystkich uprawnionych

---

## Procedury Codzienne

### 1. Sprawdzenie Stanu Systemu

#### 1.1 Monitoring Podstawowy
**Częstotliwość:** Codziennie o 8:00  
**Odpowiedzialny:** Administrator systemu  
**Czas wykonania:** 15 minut

**Kroki:**
1. **Sprawdzenie dostępności systemu**
   ```bash
   # Test dostępności strony głównej
   curl -I https://helpdesk.company.com
   # Oczekiwany wynik: HTTP 200 OK
   ```

2. **Sprawdzenie bazy danych**
   ```bash
   # Test połączenia z bazą danych
   python manage.py dbshell
   # Wykonaj: SELECT 1;
   # Oczekiwany wynik: 1
   ```

3. **Sprawdzenie logów błędów**
   ```bash
   # Sprawdzenie logów z ostatnich 24h
   tail -n 100 /var/log/apache2/error.log | grep -i error
   tail -n 100 /var/log/django.log | grep -i error
   ```

4. **Sprawdzenie miejsca na dysku**
   ```bash
   df -h
   # Sprawdź czy wolne miejsce > 20%
   ```

5. **Sprawdzenie procesów**
   ```bash
   ps aux | grep -E "(apache|mysql|python)"
   # Sprawdź czy wszystkie procesy działają
   ```

**Kryteria sukcesu:**
- ✅ System dostępny (HTTP 200)
- ✅ Baza danych odpowiada
- ✅ Brak krytycznych błędów w logach
- ✅ Wolne miejsce > 20%
- ✅ Wszystkie procesy działają

**Eskalacja:** Jeśli jakikolwiek test nie przejdzie → Zespół IT

#### 1.2 Sprawdzenie Kopii Zapasowych
**Częstotliwość:** Codziennie o 9:00  
**Odpowiedzialny:** Administrator systemu  
**Czas wykonania:** 10 minut

**Kroki:**
1. **Sprawdzenie automatycznych kopii**
   ```bash
   ls -la /backups/database/
   # Sprawdź czy istnieje backup z wczoraj
   ```

2. **Weryfikacja integralności backupu**
   ```bash
   # Test przywracania (tylko struktura)
   python manage.py restore_database --dry-run /backups/database/latest.sql.gz
   ```

3. **Sprawdzenie rozmiaru backupów**
   ```bash
   du -sh /backups/database/*
   # Sprawdź czy rozmiar jest rozsądny
   ```

**Kryteria sukcesu:**
- ✅ Backup z wczoraj istnieje
- ✅ Backup można przywrócić
- ✅ Rozmiar backupu jest normalny

**Eskalacja:** Brak backupu → Zespół IT natychmiast

### 2. Zarządzanie Użytkownikami

#### 2.1 Przetwarzanie Nowych Rejestracji
**Częstotliwość:** Codziennie o 10:00  
**Odpowiedzialny:** Administrator systemu  
**Czas wykonania:** 30 minut

**Kroki:**
1. **Sprawdzenie oczekujących rejestracji**
   - Zaloguj się do panelu administracyjnego
   - Przejdź do sekcji "Użytkownicy"
   - Filtruj: Status = "Oczekujący"

2. **Weryfikacja danych użytkownika**
   - Sprawdź poprawność emaila
   - Sprawdź dane organizacji
   - Sprawdź zgodność z polityką firmy

3. **Zatwierdzenie lub odrzucenie**
   ```python
   # Przykład zatwierdzenia
   user = User.objects.get(id=user_id)
   user.is_active = True
   user.save()
   
   # Wysłanie emaila powitalnego
   send_welcome_email(user)
   ```

4. **Dokumentacja decyzji**
   - Zapisz powód zatwierdzenia/odrzucenia
   - Dodaj notatkę w systemie

**Kryteria sukcesu:**
- ✅ Wszystkie rejestracje przetworzone w ciągu 24h
- ✅ Email powitalny wysłany
- ✅ Decyzja udokumentowana

#### 2.2 Zarządzanie Kontami Zablokowanymi
**Częstotliwość:** Codziennie o 11:00  
**Odpowiedzialny:** Administrator systemu  
**Czas wykonania:** 20 minut

**Kroki:**
1. **Sprawdzenie zablokowanych kont**
   ```python
   # Znajdź zablokowane konta
   blocked_users = UserProfile.objects.filter(is_locked=True)
   ```

2. **Analiza przyczyn blokady**
   - Sprawdź logi aktywności
   - Sprawdź liczbę nieudanych logowań
   - Sprawdź podejrzane aktywności

3. **Decyzja o odblokowaniu**
   - Jeśli to błąd systemu → odblokuj
   - Jeśli podejrzana aktywność → skontaktuj się z użytkownikiem
   - Jeśli naruszenie bezpieczeństwa → eskalacja

4. **Odblokowanie konta**
   ```python
   user_profile = UserProfile.objects.get(user=user)
   user_profile.is_locked = False
   user_profile.lock_reason = ""
   user_profile.save()
   ```

**Kryteria sukcesu:**
- ✅ Wszystkie blokady przeanalizowane
- ✅ Odblokowane konta bezpieczne
- ✅ Podejrzane aktywności zgłoszone

### 3. Monitoring Zgłoszeń

#### 3.1 Sprawdzenie Krytycznych Zgłoszeń
**Częstotliwość:** Co 2 godziny (8:00, 10:00, 12:00, 14:00, 16:00)  
**Odpowiedzialny:** Administrator systemu  
**Czas wykonania:** 15 minut

**Kroki:**
1. **Sprawdzenie zgłoszeń krytycznych**
   ```python
   # Znajdź zgłoszenia krytyczne bez przypisania
   critical_tickets = Ticket.objects.filter(
       priority='critical',
       assigned_to__isnull=True,
       status__in=['new', 'in_progress']
   )
   ```

2. **Sprawdzenie przekroczeń SLA**
   ```python
   # Znajdź zgłoszenia przekraczające SLA
   overdue_tickets = Ticket.objects.filter(
       created_at__lt=timezone.now() - timedelta(hours=24),
       status__in=['new', 'in_progress']
   )
   ```

3. **Eskalacja jeśli potrzeba**
   - Wyślij alert do zespołu IT
   - Przypisz zgłoszenie do dostępnego agenta
   - Zaktualizuj status zgłoszenia

**Kryteria sukcesu:**
- ✅ Brak nieprzypisanych zgłoszeń krytycznych
- ✅ Wszystkie przekroczenia SLA zgłoszone
- ✅ Zgłoszenia eskalowane w ciągu 30 minut

#### 3.2 Sprawdzenie Statystyk Dziennych
**Częstotliwość:** Codziennie o 17:00  
**Odpowiedzialny:** Administrator systemu  
**Czas wykonania:** 20 minut

**Kroki:**
1. **Generowanie raportu dziennego**
   ```python
   # Statystyki za dzisiaj
   today = timezone.now().date()
   stats = {
       'new_tickets': Ticket.objects.filter(created_at__date=today).count(),
       'resolved_tickets': Ticket.objects.filter(resolved_at__date=today).count(),
       'avg_resolution_time': calculate_avg_resolution_time(today),
       'sla_compliance': calculate_sla_compliance(today)
   }
   ```

2. **Analiza trendów**
   - Porównaj z poprzednim dniem
   - Sprawdź czy są anomalie
   - Zidentyfikuj problemy

3. **Raportowanie**
   - Wyślij raport do kierownictwa
   - Zapisz w systemie raportowania

**Kryteria sukcesu:**
- ✅ Raport wygenerowany przed 18:00
- ✅ Anomalie zidentyfikowane i zgłoszone
- ✅ Raport wysłany do kierownictwa

---

## Procedury Tygodniowe

### 1. Przegląd Bezpieczeństwa

#### 1.1 Audyt Logów Bezpieczeństwa
**Częstotliwość:** Każdy poniedziałek o 9:00  
**Odpowiedzialny:** Administrator bezpieczeństwa  
**Czas wykonania:** 2 godziny

**Kroki:**
1. **Analiza logów uwierzytelniania**
   ```bash
   # Sprawdź nieudane logowania
   grep "Failed login" /var/log/django.log | tail -100
   
   # Sprawdź podejrzane IP
   grep "Suspicious activity" /var/log/django.log
   ```

2. **Sprawdzenie aktywności 2FA**
   ```python
   # Sprawdź wyłączenia 2FA
   disabled_2fa = ActivityLog.objects.filter(
       action_type='2fa_disabled',
       created_at__gte=timezone.now() - timedelta(days=7)
   )
   ```

3. **Analiza uprawnień**
   ```python
   # Sprawdź zmiany uprawnień
   permission_changes = ActivityLog.objects.filter(
       action_type__in=['user_role_changed', 'group_permissions_changed'],
       created_at__gte=timezone.now() - timedelta(days=7)
   )
   ```

4. **Raport bezpieczeństwa**
   - Przygotuj raport tygodniowy
   - Zidentyfikuj zagrożenia
   - Zaproponuj działania naprawcze

**Kryteria sukcesu:**
- ✅ Wszystkie logi przeanalizowane
- ✅ Zagrożenia zidentyfikowane
- ✅ Raport bezpieczeństwa przygotowany
- ✅ Działania naprawcze zaplanowane

#### 1.2 Test Kopii Zapasowych
**Częstotliwość:** Każdy piątek o 14:00  
**Odpowiedzialny:** Administrator systemu  
**Czas wykonania:** 1 godzina

**Kroki:**
1. **Wybór backupu do testu**
   ```bash
   # Wybierz backup z początku tygodnia
   BACKUP_FILE="/backups/database/backup_$(date -d '4 days ago' +%Y%m%d).sql.gz"
   ```

2. **Przygotowanie środowiska testowego**
   ```bash
   # Utwórz testową bazę danych
   mysql -u root -p -e "CREATE DATABASE helpdesk_test;"
   ```

3. **Przywrócenie backupu**
   ```bash
   # Przywróć backup do testowej bazy
   gunzip -c $BACKUP_FILE | mysql -u root -p helpdesk_test
   ```

4. **Test integralności**
   ```bash
   # Sprawdź podstawowe tabele
   mysql -u root -p helpdesk_test -e "SELECT COUNT(*) FROM auth_user;"
   mysql -u root -p helpdesk_test -e "SELECT COUNT(*) FROM crm_ticket;"
   ```

5. **Czyszczenie środowiska testowego**
   ```bash
   mysql -u root -p -e "DROP DATABASE helpdesk_test;"
   ```

**Kryteria sukcesu:**
- ✅ Backup przywrócony bez błędów
- ✅ Dane są kompletne
- ✅ Środowisko testowe wyczyszczone

### 2. Optymalizacja Wydajności

#### 2.1 Analiza Wydajności Bazy Danych
**Częstotliwość:** Każdy wtorek o 10:00  
**Odpowiedzialny:** Administrator bazy danych  
**Czas wykonania:** 1.5 godziny

**Kroki:**
1. **Sprawdzenie wolnych zapytań**
   ```sql
   -- Sprawdź wolne zapytania
   SELECT * FROM information_schema.processlist 
   WHERE TIME > 5 AND COMMAND != 'Sleep';
   ```

2. **Analiza indeksów**
   ```sql
   -- Sprawdź nieużywane indeksy
   SELECT * FROM information_schema.statistics 
   WHERE table_schema = 'helpdesk_db';
   ```

3. **Optymalizacja zapytań**
   ```python
   # Sprawdź najczęściej używane zapytania
   from django.db import connection
   print(connection.queries[-10:])  # Ostatnie 10 zapytań
   ```

4. **Rekomendacje optymalizacji**
   - Dodaj brakujące indeksy
   - Zoptymalizuj wolne zapytania
   - Usuń nieużywane indeksy

**Kryteria sukcesu:**
- ✅ Wolne zapytania zidentyfikowane
- ✅ Indeksy przeanalizowane
- ✅ Rekomendacje przygotowane
- ✅ Optymalizacje zaplanowane

#### 2.2 Czyszczenie Systemu
**Częstotliwość:** Każdą środę o 15:00  
**Odpowiedzialny:** Administrator systemu  
**Czas wykonania:** 1 godzina

**Kroki:**
1. **Czyszczenie starych logów**
   ```bash
   # Usuń logi starsze niż 30 dni
   find /var/log -name "*.log" -mtime +30 -delete
   ```

2. **Czyszczenie cache**
   ```bash
   # Wyczyść cache aplikacji
   python manage.py clear_cache
   ```

3. **Czyszczenie starych sesji**
   ```python
   # Usuń stare sesje
   from django.contrib.sessions.models import Session
   Session.objects.filter(expire_date__lt=timezone.now()).delete()
   ```

4. **Czyszczenie plików tymczasowych**
   ```bash
   # Wyczyść pliki tymczasowe
   find /tmp -name "django_*" -mtime +7 -delete
   ```

**Kryteria sukcesu:**
- ✅ Stare logi usunięte
- ✅ Cache wyczyszczony
- ✅ Sesje wyczyszczone
- ✅ Pliki tymczasowe usunięte

---

## Procedury Miesięczne

### 1. Przegląd Architektury

#### 1.1 Audyt Architektury Systemu
**Częstotliwość:** Pierwszy poniedziałek miesiąca o 9:00  
**Odpowiedzialny:** Architekt systemu  
**Czas wykonania:** 4 godziny

**Kroki:**
1. **Przegląd komponentów systemu**
   - Sprawdź wszystkie aplikacje Django
   - Przeanalizuj zależności
   - Zidentyfikuj przestarzałe komponenty

2. **Analiza wydajności**
   ```python
   # Sprawdź metryki wydajności
   performance_metrics = {
       'avg_response_time': get_avg_response_time(),
       'database_connections': get_db_connections(),
       'memory_usage': get_memory_usage(),
       'cpu_usage': get_cpu_usage()
   }
   ```

3. **Przegląd bezpieczeństwa**
   - Sprawdź aktualizacje bezpieczeństwa
   - Przeanalizuj luki bezpieczeństwa
   - Zaktualizuj polityki bezpieczeństwa

4. **Planowanie rozwoju**
   - Zidentyfikuj obszary do poprawy
   - Zaplanuj nowe funkcjonalności
   - Przygotuj roadmapę rozwoju

**Kryteria sukcesu:**
- ✅ Wszystkie komponenty przeanalizowane
- ✅ Metryki wydajności zebrane
- ✅ Luki bezpieczeństwa zidentyfikowane
- ✅ Plan rozwoju przygotowany

#### 1.2 Przegląd Użytkowników i Uprawnień
**Częstotliwość:** Pierwszy wtorek miesiąca o 10:00  
**Odpowiedzialny:** Administrator systemu  
**Czas wykonania:** 2 godziny

**Kroki:**
1. **Audyt użytkowników**
   ```python
   # Sprawdź nieaktywnych użytkowników
   inactive_users = User.objects.filter(
       last_login__lt=timezone.now() - timedelta(days=90),
       is_active=True
   )
   ```

2. **Przegląd uprawnień**
   ```python
   # Sprawdź użytkowników z uprawnieniami admin
   admin_users = User.objects.filter(
       groups__name='Admin',
       is_active=True
   )
   ```

3. **Weryfikacja zgodności**
   - Sprawdź czy uprawnienia są zgodne z polityką
   - Zidentyfikuj nadmiarowe uprawnienia
   - Sprawdź czy brakuje uprawnień

4. **Czyszczenie kont**
   - Dezaktywuj nieaktywne konta
   - Usuń nadmiarowe uprawnienia
   - Zaktualizuj role użytkowników

**Kryteria sukcesu:**
- ✅ Wszyscy użytkownicy przeanalizowani
- ✅ Uprawnienia zweryfikowane
- ✅ Nieaktywne konta dezaktywowane
- ✅ Nadmiarowe uprawnienia usunięte

### 2. Planowanie Rozwoju

#### 2.1 Przegląd Funkcjonalności
**Częstotliwość:** Pierwsza środa miesiąca o 14:00  
**Odpowiedzialny:** Product Owner  
**Czas wykonania:** 3 godziny

**Kroki:**
1. **Analiza użycia funkcjonalności**
   ```python
   # Sprawdź najczęściej używane funkcje
   feature_usage = ActivityLog.objects.values('action_type').annotate(
       count=Count('id')
   ).order_by('-count')[:10]
   ```

2. **Zbieranie feedbacku użytkowników**
   - Przeanalizuj zgłoszenia użytkowników
   - Sprawdź prośby o nowe funkcje
   - Zbierz opinie od zespołu

3. **Priorytetyzacja rozwoju**
   - Określ priorytety funkcjonalności
   - Zaplanuj harmonogram rozwoju
   - Przygotuj specyfikacje wymagań

4. **Planowanie zasobów**
   - Określ wymagane zasoby
   - Zaplanuj harmonogram prac
   - Przygotuj budżet

**Kryteria sukcesu:**
- ✅ Użycie funkcjonalności przeanalizowane
- ✅ Feedback zebrany i przeanalizowany
- ✅ Priorytety określone
- ✅ Plan rozwoju przygotowany

---

## Procedury Awaryjne

### 1. Procedura Awaryjna - Niedostępność Systemu

#### 1.1 Identyfikacja Problemu
**Czas reakcji:** Natychmiast  
**Odpowiedzialny:** Administrator systemu  
**Czas wykonania:** 15 minut

**Kroki:**
1. **Potwierdzenie problemu**
   ```bash
   # Test dostępności
   curl -I https://helpdesk.company.com
   # Jeśli HTTP != 200 → problem potwierdzony
   ```

2. **Sprawdzenie podstawowych usług**
   ```bash
   # Sprawdź procesy
   systemctl status apache2
   systemctl status mysql
   ps aux | grep python
   ```

3. **Sprawdzenie logów**
   ```bash
   # Sprawdź najnowsze błędy
   tail -50 /var/log/apache2/error.log
   tail -50 /var/log/django.log
   ```

4. **Eskalacja**
   - Jeśli problem krytyczny → Zespół IT natychmiast
   - Jeśli problem średni → Zespół IT w ciągu 1h
   - Jeśli problem niski → Zespół IT w ciągu 4h

**Kryteria sukcesu:**
- ✅ Problem zidentyfikowany w ciągu 15 minut
- ✅ Eskalacja wykonana zgodnie z procedurą
- ✅ Użytkownicy powiadomieni o problemie

#### 1.2 Przywracanie Działania
**Czas reakcji:** W ciągu 1 godziny  
**Odpowiedzialny:** Zespół IT  
**Czas wykonania:** 2 godziny

**Kroki:**
1. **Diagnoza głęboka**
   ```bash
   # Sprawdź wszystkie usługi
   systemctl status apache2 mysql redis
   
   # Sprawdź miejsce na dysku
   df -h
   
   # Sprawdź pamięć
   free -h
   ```

2. **Próba szybkiego przywrócenia**
   ```bash
   # Restart usług
   systemctl restart apache2
   systemctl restart mysql
   ```

3. **Jeśli restart nie pomaga**
   ```bash
   # Sprawdź konfigurację
   apache2ctl configtest
   mysql -u root -p -e "SHOW PROCESSLIST;"
   ```

4. **Przywrócenie z backupu**
   ```bash
   # Jeśli baza danych uszkodzona
   python manage.py restore_database /backups/database/latest.sql.gz
   ```

5. **Test funkcjonalności**
   - Sprawdź logowanie
   - Sprawdź tworzenie zgłoszeń
   - Sprawdź podstawowe funkcje

**Kryteria sukcesu:**
- ✅ System przywrócony w ciągu 2 godzin
- ✅ Wszystkie funkcje działają
- ✅ Użytkownicy powiadomieni o przywróceniu
- ✅ Przyczyna problemu zidentyfikowana

### 2. Procedura Awaryjna - Utrata Danych

#### 2.1 Identyfikacja Utraty Danych
**Czas reakcji:** Natychmiast  
**Odpowiedzialny:** Administrator systemu  
**Czas wykonania:** 30 minut

**Kroki:**
1. **Potwierdzenie utraty danych**
   ```python
   # Sprawdź integralność bazy danych
   python manage.py check --deploy
   python manage.py dbshell
   # Wykonaj: CHECK TABLE auth_user;
   ```

2. **Oszacowanie zakresu utraty**
   - Sprawdź które tabele są uszkodzone
   - Sprawdź które dane są utracone
   - Sprawdź kiedy nastąpiła utrata

3. **Natychmiastowa eskalacja**
   - Zespół IT natychmiast
   - Kierownictwo w ciągu 15 minut
   - Użytkownicy w ciągu 30 minut

**Kryteria sukcesu:**
- ✅ Utrata danych potwierdzona w ciągu 30 minut
- ✅ Zakres utraty oszacowany
- ✅ Eskalacja wykonana natychmiast

#### 2.2 Przywracanie Danych
**Czas reakcji:** Natychmiast  
**Odpowiedzialny:** Zespół IT  
**Czas wykonania:** 4 godziny

**Kroki:**
1. **Zatrzymanie systemu**
   ```bash
   # Zatrzymaj wszystkie usługi
   systemctl stop apache2
   systemctl stop mysql
   ```

2. **Przygotowanie środowiska**
   ```bash
   # Utwórz kopię uszkodzonej bazy
   cp /var/lib/mysql/helpdesk_db /backups/corrupted/
   ```

3. **Przywrócenie z backupu**
   ```bash
   # Przywróć najnowszy backup
   python manage.py restore_database /backups/database/latest.sql.gz
   ```

4. **Weryfikacja danych**
   ```python
   # Sprawdź integralność przywróconych danych
   python manage.py check --deploy
   python manage.py dbshell
   # Wykonaj podstawowe zapytania testowe
   ```

5. **Przywrócenie systemu**
   ```bash
   # Uruchom usługi
   systemctl start mysql
   systemctl start apache2
   ```

6. **Test funkcjonalności**
   - Sprawdź wszystkie funkcje
   - Sprawdź dane użytkowników
   - Sprawdź zgłoszenia

**Kryteria sukcesu:**
- ✅ Dane przywrócone w ciągu 4 godzin
- ✅ System działa poprawnie
- ✅ Wszystkie dane są integralne
- ✅ Użytkownicy powiadomieni o przywróceniu

---

## Procedury Bezpieczeństwa

### 1. Procedura Reagowania na Incydenty Bezpieczeństwa

#### 1.1 Identyfikacja Incydentu
**Czas reakcji:** Natychmiast  
**Odpowiedzialny:** Administrator bezpieczeństwa  
**Czas wykonania:** 30 minut

**Kroki:**
1. **Potwierdzenie incydentu**
   ```bash
   # Sprawdź logi bezpieczeństwa
   grep -i "security\|breach\|attack" /var/log/django.log
   grep -i "failed login" /var/log/django.log | tail -20
   ```

2. **Oszacowanie zagrożenia**
   - Określ typ ataku
   - Oszacuj zakres szkód
   - Określ priorytet incydentu

3. **Natychmiastowa eskalacja**
   - Kierownictwo natychmiast
   - Zespół IT natychmiast
   - Jeśli krytyczny → Zespół bezpieczeństwa

**Kryteria sukcesu:**
- ✅ Incydent zidentyfikowany w ciągu 30 minut
- ✅ Zagrożenie oszacowane
- ✅ Eskalacja wykonana natychmiast

#### 1.2 Neutralizacja Zagrożenia
**Czas reakcji:** W ciągu 1 godziny  
**Odpowiedzialny:** Zespół bezpieczeństwa  
**Czas wykonania:** 2 godziny

**Kroki:**
1. **Izolacja systemu**
   ```bash
   # Jeśli konieczne, zatrzymaj usługi
   systemctl stop apache2
   ```

2. **Blokada podejrzanych kont**
   ```python
   # Zablokuj podejrzane konta
   suspicious_users = UserProfile.objects.filter(
       last_login_ip__in=suspicious_ips
   )
   for user in suspicious_users:
       user.is_locked = True
       user.lock_reason = "Security incident"
       user.save()
   ```

3. **Zmiana haseł**
   ```python
   # Wymuś zmianę haseł dla wszystkich użytkowników
   User.objects.update(password_reset_required=True)
   ```

4. **Aktualizacja bezpieczeństwa**
   ```bash
   # Zaktualizuj system
   apt update && apt upgrade
   pip install --upgrade django
   ```

**Kryteria sukcesu:**
- ✅ Zagrożenie zneutralizowane w ciągu 2 godzin
- ✅ Podejrzane konta zablokowane
- ✅ System zaktualizowany
- ✅ Użytkownicy powiadomieni

### 2. Procedura Audytu Bezpieczeństwa

#### 2.1 Przegląd Uprawnień
**Częstotliwość:** Co 2 tygodnie  
**Odpowiedzialny:** Administrator bezpieczeństwa  
**Czas wykonania:** 2 godziny

**Kroki:**
1. **Audyt użytkowników z uprawnieniami admin**
   ```python
   admin_users = User.objects.filter(
       groups__name='Admin',
       is_active=True
   )
   for user in admin_users:
       print(f"Admin: {user.username}, Last login: {user.last_login}")
   ```

2. **Sprawdzenie zmian uprawnień**
   ```python
   permission_changes = ActivityLog.objects.filter(
       action_type__in=['user_role_changed', 'group_permissions_changed'],
       created_at__gte=timezone.now() - timedelta(days=14)
   )
   ```

3. **Weryfikacja zgodności z polityką**
   - Sprawdź czy uprawnienia są zgodne z polityką
   - Zidentyfikuj nadmiarowe uprawnienia
   - Sprawdź czy brakuje uprawnień

4. **Raport audytu**
   - Przygotuj raport audytu
   - Zidentyfikuj naruszenia
   - Zaproponuj działania naprawcze

**Kryteria sukcesu:**
- ✅ Wszyscy admini przeanalizowani
- ✅ Zmiany uprawnień zidentyfikowane
- ✅ Naruszenia zidentyfikowane
- ✅ Raport audytu przygotowany

---

## Procedury Konserwacji

### 1. Procedura Aktualizacji Systemu

#### 1.1 Planowanie Aktualizacji
**Częstotliwość:** Co 3 miesiące  
**Odpowiedzialny:** Administrator systemu  
**Czas wykonania:** 1 godzina

**Kroki:**
1. **Sprawdzenie dostępnych aktualizacji**
   ```bash
   # Sprawdź aktualizacje Django
   pip list --outdated | grep Django
   
   # Sprawdź aktualizacje systemu
   apt list --upgradable
   ```

2. **Ocena ryzyka**
   - Sprawdź changelog aktualizacji
   - Oszacuj wpływ na system
   - Określ wymagane testy

3. **Planowanie harmonogramu**
   - Wybierz okno czasowe (najlepiej weekend)
   - Przygotuj plan rollback
   - Zaplanuj testy

4. **Komunikacja**
   - Powiadom użytkowników o planowanej aktualizacji
   - Powiadom zespół IT
   - Przygotuj dokumentację

**Kryteria sukcesu:**
- ✅ Aktualizacje zidentyfikowane
- ✅ Ryzyko oszacowane
- ✅ Harmonogram zaplanowany
- ✅ Komunikacja wykonana

#### 1.2 Wykonanie Aktualizacji
**Częstotliwość:** Według harmonogramu  
**Odpowiedzialny:** Zespół IT  
**Czas wykonania:** 4 godziny

**Kroki:**
1. **Przygotowanie środowiska**
   ```bash
   # Utwórz pełny backup
   python manage.py backup_database --format=sql
   tar -czf /backups/full_system_$(date +%Y%m%d).tar.gz /var/www/helpdesk/
   ```

2. **Test w środowisku testowym**
   ```bash
   # Wdróż na środowisko testowe
   git checkout main
   git pull origin main
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

3. **Wdrożenie na produkcję**
   ```bash
   # Zatrzymaj usługi
   systemctl stop apache2
   
   # Wdróż aktualizacje
   git pull origin main
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py collectstatic --noinput
   
   # Uruchom usługi
   systemctl start apache2
   ```

4. **Test funkcjonalności**
   - Sprawdź logowanie
   - Sprawdź tworzenie zgłoszeń
   - Sprawdź wszystkie funkcje

5. **Rollback jeśli potrzeba**
   ```bash
   # Jeśli coś nie działa
   git checkout previous_version
   python manage.py restore_database /backups/database/latest.sql.gz
   systemctl restart apache2
   ```

**Kryteria sukcesu:**
- ✅ Backup utworzony przed aktualizacją
- ✅ Testy w środowisku testowym przeszły
- ✅ Aktualizacja wdrożona bez błędów
- ✅ Wszystkie funkcje działają
- ✅ Plan rollback przygotowany

### 2. Procedura Konserwacji Bazy Danych

#### 2.1 Optymalizacja Bazy Danych
**Częstotliwość:** Co miesiąc  
**Odpowiedzialny:** Administrator bazy danych  
**Czas wykonania:** 2 godziny

**Kroki:**
1. **Analiza wydajności**
   ```sql
   -- Sprawdź wolne zapytania
   SELECT * FROM information_schema.processlist 
   WHERE TIME > 5 AND COMMAND != 'Sleep';
   
   -- Sprawdź rozmiar tabel
   SELECT 
       table_name,
       ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size in MB'
   FROM information_schema.tables
   WHERE table_schema = 'helpdesk_db'
   ORDER BY (data_length + index_length) DESC;
   ```

2. **Optymalizacja tabel**
   ```sql
   -- Optymalizuj wszystkie tabele
   OPTIMIZE TABLE auth_user;
   OPTIMIZE TABLE crm_ticket;
   OPTIMIZE TABLE crm_ticketcomment;
   -- ... dla wszystkich tabel
   ```

3. **Czyszczenie starych danych**
   ```python
   # Usuń stare logi aktywności (starsze niż 1 rok)
   old_logs = ActivityLog.objects.filter(
       created_at__lt=timezone.now() - timedelta(days=365)
   )
   old_logs.delete()
   ```

4. **Aktualizacja statystyk**
   ```sql
   -- Zaktualizuj statystyki tabel
   ANALYZE TABLE auth_user;
   ANALYZE TABLE crm_ticket;
   -- ... dla wszystkich tabel
   ```

**Kryteria sukcesu:**
- ✅ Wydajność przeanalizowana
- ✅ Tabele zoptymalizowane
- ✅ Stare dane usunięte
- ✅ Statystyki zaktualizowane

---

## Procedury Rozwoju

### 1. Procedura Wdrażania Nowych Funkcjonalności

#### 1.1 Planowanie Rozwoju
**Częstotliwość:** Co 2 tygodnie  
**Odpowiedzialny:** Product Owner  
**Czas wykonania:** 2 godziny

**Kroki:**
1. **Zbieranie wymagań**
   - Przeanalizuj zgłoszenia użytkowników
   - Sprawdź prośby o nowe funkcje
   - Zbierz opinie od zespołu

2. **Priorytetyzacja**
   - Określ priorytety funkcjonalności
   - Oszacuj czas realizacji
   - Zaplanuj harmonogram

3. **Specyfikacja wymagań**
   - Przygotuj szczegółową specyfikację
   - Zdefiniuj kryteria akceptacji
   - Zaplanuj testy

4. **Planowanie zasobów**
   - Określ wymagane zasoby
   - Zaplanuj harmonogram prac
   - Przygotuj budżet

**Kryteria sukcesu:**
- ✅ Wymagania zebrane i przeanalizowane
- ✅ Priorytety określone
- ✅ Specyfikacja przygotowana
- ✅ Zasoby zaplanowane

#### 1.2 Wykonanie Rozwoju
**Częstotliwość:** Według harmonogramu  
**Odpowiedzialny:** Zespół deweloperski  
**Czas wykonania:** Według specyfikacji

**Kroki:**
1. **Przygotowanie środowiska**
   ```bash
   # Utwórz branch dla nowej funkcjonalności
   git checkout -b feature/new-functionality
   ```

2. **Rozwój funkcjonalności**
   - Implementuj zgodnie ze specyfikacją
   - Pisz testy jednostkowe
   - Dokumentuj kod

3. **Testowanie**
   ```bash
   # Uruchom testy
   python manage.py test
   
   # Testy integracyjne
   python manage.py test --settings=test_settings
   ```

4. **Code Review**
   - Prześlij kod do review
   - Wprowadź poprawki
   - Uzyskaj aprobatę

5. **Wdrożenie**
   ```bash
   # Merge do main branch
   git checkout main
   git merge feature/new-functionality
   git push origin main
   ```

**Kryteria sukcesu:**
- ✅ Funkcjonalność zaimplementowana zgodnie ze specyfikacją
- ✅ Testy przeszły
- ✅ Code review zakończony
- ✅ Wdrożenie wykonane bez błędów

---

## Kontakty i Eskalacja

### Hierarchia Eskalacji

#### Poziom 1 - Administrator Systemu
- **Odpowiedzialność:** Codzienne operacje, podstawowe problemy
- **Czas reakcji:** Natychmiast
- **Kontakt:** admin@company.com, +48 123 456 789

#### Poziom 2 - Zespół IT
- **Odpowiedzialność:** Problemy techniczne, aktualizacje
- **Czas reakcji:** W ciągu 1 godziny
- **Kontakt:** it-team@company.com, +48 123 456 790

#### Poziom 3 - Kierownictwo
- **Odpowiedzialność:** Problemy biznesowe, decyzje strategiczne
- **Czas reakcji:** W ciągu 4 godzin
- **Kontakt:** management@company.com, +48 123 456 791

#### Poziom 4 - Zespół Bezpieczeństwa
- **Odpowiedzialność:** Incydenty bezpieczeństwa
- **Czas reakcji:** Natychmiast
- **Kontakt:** security@company.com, +48 123 456 792

### Procedura Eskalacji

#### Kryteria Eskalacji
- **Krytyczny:** System niedostępny, utrata danych, incydent bezpieczeństwa
- **Wysoki:** Problemy z wydajnością, błędy funkcjonalne
- **Średni:** Problemy z konfiguracją, drobne błędy
- **Niski:** Prośby o nowe funkcje, drobne ulepszenia

#### Proces Eskalacji
1. **Identyfikacja problemu** - określ priorytet
2. **Próba rozwiązania** - na swoim poziomie
3. **Eskalacja** - jeśli nie można rozwiązać
4. **Komunikacja** - powiadom wszystkich zainteresowanych
5. **Dokumentacja** - zapisz wszystkie działania

---

## Szablony i Formularze

### 1. Szablon Raportu Dziennego

```markdown
# Raport Dzienny - [DATA]

## Podsumowanie
- Nowe zgłoszenia: [LICZBA]
- Rozwiązane zgłoszenia: [LICZBA]
- Średni czas rozwiązania: [CZAS]
- Zgodność z SLA: [PROCENT]

## Problemy
- [OPIS PROBLEMU 1]
- [OPIS PROBLEMU 2]

## Działania
- [DZIAŁANIE 1]
- [DZIAŁANIE 2]

## Uwagi
[UWAGI]
```

### 2. Szablon Raportu Bezpieczeństwa

```markdown
# Raport Bezpieczeństwa - [OKRES]

## Podsumowanie
- Próby logowania: [LICZBA]
- Nieudane logowania: [LICZBA]
- Zablokowane konta: [LICZBA]
- Incydenty bezpieczeństwa: [LICZBA]

## Analiza
- Najczęstsze źródła ataków: [IP/LOKALIZACJE]
- Najczęstsze typy ataków: [TYPY]
- Trendy bezpieczeństwa: [TRENDY]

## Rekomendacje
- [REKOMENDACJA 1]
- [REKOMENDACJA 2]

## Działania
- [DZIAŁANIE 1]
- [DZIAŁANIE 2]
```

### 3. Szablon Procedury Awaryjnej

```markdown
# Procedura Awaryjna - [TYP PROBLEMU]

## Identyfikacja
- Problem: [OPIS]
- Czas wystąpienia: [CZAS]
- Zakres: [ZAKRES]
- Priorytet: [PRIORYTET]

## Działania
1. [DZIAŁANIE 1]
2. [DZIAŁANIE 2]
3. [DZIAŁANIE 3]

## Komunikacja
- Powiadomieni: [OSOBY]
- Czas powiadomienia: [CZAS]
- Status: [STATUS]

## Rozwiązanie
- Rozwiązanie: [OPIS]
- Czas rozwiązania: [CZAS]
- Przyczyna: [PRZYCZYNA]

## Działania naprawcze
- [DZIAŁANIE 1]
- [DZIAŁANIE 2]
```

---

*Ostatnia aktualizacja: Styczeń 2025*
