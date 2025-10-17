# Hotfix - Django Admin Error 500

## 2025-10-17 - Naprawa błędu get_app_list()

### 🐛 Problem
```
TypeError: CrmAdminSite.get_app_list() takes 2 positional arguments but 3 were given
```

**Występował przy:**
- Kliknięciu na linki typu: `/admin/crm/`, `/admin/django_apscheduler/`, `/admin/otp_totp/`
- Te linki prowadziły do strony z listą modeli danej aplikacji
- Generowało to błąd 500

### ✅ Rozwiązanie

**Plik:** `crm/admin_site.py`

**Problem 1:** Brak parametru `app_label` w metodzie `get_app_list()`
```python
# PRZED (błędne):
def get_app_list(self, request):
    app_list = super().get_app_list(request)  # ❌ Brak app_label
    ...

# PO (poprawne):
def get_app_list(self, request, app_label=None):
    app_list = super().get_app_list(request, app_label)  # ✅ Dodano app_label
    ...
```

**Problem 2:** Niepotrzebne linki do stron aplikacji
```python
# Dodano:
for app in app_list:
    app['app_url'] = None  # Usuwa klikalny link
```

### 🎯 Efekt

**PRZED:**
- Kliknięcie "CRM" lub "Django Apscheduler" → błąd 500
- Strony `/admin/crm/`, `/admin/django_apscheduler/` nie działały

**PO:**
- Nazwy aplikacji w Django Admin nie są już linkami
- Brak błędów 500
- Można nadal klikać w poszczególne modele (User, Ticket, etc.)

### 📝 Zmiany techniczne

1. **Sygnatura metody:** `get_app_list(self, request)` → `get_app_list(self, request, app_label=None)`
2. **Wywołanie super():** `super().get_app_list(request)` → `super().get_app_list(request, app_label)`
3. **Usunięcie linków:** `app['app_url'] = None` dla każdej aplikacji

### 🧪 Testowanie

```bash
# 1. Zaloguj się do Django Admin
# 2. Sprawdź stronę główną /admin/
# OCZEKIWANE: Nazwy aplikacji (CRM, Django Apscheduler) nie są już linkami
# 3. Kliknij na model (np. "Users")
# OCZEKIWANE: Działa normalnie
# 4. Spróbuj wejść bezpośrednio na /admin/crm/
# OCZEKIWANE: Brak błędu 500 (może być 404 lub przekierowanie)
```

### 🚀 Deployment

```bash
git add crm/admin_site.py
git commit -m "fix(admin): Fix get_app_list() signature and disable app index links"
git push

# Na serwerze:
git pull
touch tmp/restart.txt
```

### 📚 Dokumentacja Django

**Django 4.x:** `get_app_list(request, app_label=None)`
- `request` - obiekt HttpRequest
- `app_label` - opcjonalny string z nazwą aplikacji (np. 'crm')
- Zwraca: lista słowników z informacjami o aplikacjach

**Metoda używana przez:**
- `/admin/` - główna strona (app_label=None, pokazuje wszystkie aplikacje)
- `/admin/crm/` - strona aplikacji (app_label='crm', pokazuje tylko CRM)

---

**Autor:** AI Assistant (GitHub Copilot)  
**Data:** 2025-10-17  
**Typ:** Hotfix  
**Priorytet:** Wysoki (błąd 500)  
**Status:** ✅ Naprawione
