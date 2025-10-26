# Role w Systemie

System wspiera **5 różnych ról** użytkowników, każda z określonymi uprawnieniami i dostępem.

---

## 👨‍💼 Administrator (Admin)

**Pełny dostęp** do wszystkich funkcji systemu.

### Możliwości:
- Zarządzanie użytkownikami (dodawanie, usuwanie, zatwierdzanie)
- Zarządzanie organizacjami
- Dostęp do panelu Django (admin panel)
- Zarządzanie zgłoszeniami
- Dostęp do logów i statystyk
- Zarządzanie uprawnieniami
- Blokowanie/odblokowanie kont
- Zarządzanie powiadomieniami email

**Szczegółowe instrukcje:** [04_administrator.md](04_administrator.md)

---

## 🔧 Super Agent

Zarządzanie zgłoszeniami **wszystkich organizacji**.

### Możliwości:
- Przypisywanie zgłoszeń **innym agentom**
- Przeglądanie **wszystkich** zgłoszeń ze wszystkich organizacji
- Zarządzanie zgłoszeniami wszystkich organizacji
- Zamykanie **dowolnych** zgłoszeń
- Edycja zgłoszeń
- Przeglądanie statystyk wszystkich organizacji

**Szczegółowe instrukcje:** [05_superagent.md](05_superagent.md)

---

## 👨‍🔧 Agent

Obsługa zgłoszeń w **swojej organizacji**.

### Możliwości:
- Przypisywanie zgłoszeń **tylko do siebie**
- Przeglądanie i obsługa zgłoszeń swojej organizacji
- Zamykanie zgłoszeń przypisanych do niego
- Dodawanie komentarzy
- Dodawanie załączników

**Szczegółowe instrukcje:** [06_agent.md](06_agent.md)

---

## 👤 Klient (Client)

Tworzenie i przeglądanie **własnych zgłoszeń**.

### Możliwości:
- Tworzenie własnych zgłoszeń
- Przeglądanie zgłoszeń swojej organizacji
- Dodawanie komentarzy do swoich zgłoszeń
- Dodawanie załączników
- Przeglądanie statusu zgłoszeń

**Szczegółowe instrukcje:** [07_klient.md](07_klient.md)

---

## 👁️ Viewer (Przeglądający)

**Tylko przeglądanie** zgłoszeń w trybie monitorowania.

### Możliwości:
- Przeglądanie zgłoszeń
- Widzenie statusu i szczegółów
- Przeglądanie komentarzy
- Oglądanie załączników (według uprawnień)

**Uwaga:** Po zalogowaniu automatyczne przekierowanie do widoku zgłoszeń bez standardowej nawigacji.

**Szczegółowe instrukcje:** [08_viewer.md](08_viewer.md)

---

## 📊 Porównanie Uprawnień

| Funkcja | Admin | Super Agent | Agent | Klient | Viewer |
|---------|-------|-------------|-------|--------|--------|
| Zatwierdzanie kont | ✅ | ❌ | ❌ | ❌ | ❌ |
| Zarządzanie użytkownikami | ✅ | ❌ | ❌ | ❌ | ❌ |
| Wszystkie zgłoszenia | ✅ | ✅ | ❌ | ❌ | ❌ |
| Zgłoszenia swojej org. | ✅ | ✅ | ✅ | ❌ | ❌ |
| Przypisywanie innym | ✅ | ✅ | ❌ | ❌ | ❌ |
| Przypisywanie do siebie | ✅ | ❌ | ✅ | ❌ | ❌ |
| Zamykanie zgłoszeń | ✅ | ✅ | Tylko swoje | ❌ | ❌ |
| Tworzenie zgłoszeń | ✅ | ✅ | ❌ | ✅ | ❌ |
| Edycja zgłoszeń | ✅ | ✅ | ❌ | ❌ | ❌ |
| Dodawanie komentarzy | ✅ | ✅ | ✅ | Tylko swoje | ❌ |
| Załączniki (wszystkie) | ✅ | ✅ | ❌ | ❌ | ❌ |
| Logi aktywności | ✅ | ✅ | ❌ | ❌ | ❌ |
| Statystyki | ✅ | ✅ | ❌ | ❌ | ❌ |

---

**Następny krok:** [03_logowanie.md](03_logowanie.md) ←  
**Powrót do:** [README.md](README.md)

