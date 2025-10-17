# Enhancement: Marginsy i bordery dla rozwijanych list zgłoszeń

## Problem
W rozwijanych tabelach ze zgłoszeniami agentów na panelu statystyk:
- Pierwszy rekord był zbyt blisko góry tabeli (brak marginu górnego)
- Między rekordami brakowało marginesów (wiersze były zbyt ciasno)
- Brak wyraźnego bordera oddzielającego rozwiniętą listę
- Brak wsparcia dla trybu ciemnego

## Rozwiązanie

### 1. **Zmienione tło kontenera**
**Plik:** `crm/templates/crm/statistics/statistics_dashboard.html`
**Linia:** ~645

```html
<!-- PRZED -->
<div class="tickets-content-wrapper bg-light">

<!-- PO -->
<div class="tickets-content-wrapper">
```

**Powód:** Usunięto klasę `bg-light`, aby tło było kontrolowane przez CSS z pełnym wsparciem dla trybu ciemnego.

### 2. **Dodano tło i border w CSS**
**Plik:** `crm/templates/crm/statistics/statistics_dashboard.html`
**Linie:** ~122-175

#### Podstawowe style:
```css
.tickets-content-wrapper {
    max-height: 0;
    overflow: hidden;
    opacity: 0;
    transition: max-height 0.3s ease-in-out, opacity 0.3s ease-in-out, padding 0.3s ease-in-out;
    padding: 0 1rem;
    border-radius: 8px;
    background-color: #f8f9fa;  /* Jasne tło dla trybu jasnego */
}

.tickets-content-wrapper.expanded {
    max-height: 2000px;
    opacity: 1;
    padding: 1rem;
    border: 1px solid #dee2e6;  /* Border w trybie jasnym */
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);  /* Subtelny cień */
}
```

#### Tryb ciemny:
```css
[data-bs-theme="dark"] .tickets-content-wrapper.expanded {
    border-color: #495057;  /* Ciemniejszy border */
    background-color: #2b3035 !important;  /* Ciemne tło */
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.3);  /* Mocniejszy cień */
}
```

### 3. **Dodano marginsy dla tabeli**
```css
/* Odstęp od nagłówka */
.tickets-content-wrapper .table-responsive {
    margin-top: 0.75rem;
}

/* Odstęp od dolnej informacji */
.tickets-content-wrapper .table {
    margin-bottom: 0.5rem;
}
```

### 4. **Dodano padding dla wierszy tabeli**
```css
/* Wyraźniejszy header */
.tickets-content-wrapper .table thead th {
    padding-top: 0.75rem;
    padding-bottom: 0.75rem;
    border-bottom: 2px solid #dee2e6;
}

/* Pierwszy wiersz z większym paddingiem */
.tickets-content-wrapper .table tbody tr:first-child td {
    padding-top: 0.75rem;  /* Więcej miejsca od góry */
}

/* Standardowe wiersze z marginesami */
.tickets-content-wrapper .table tbody tr td {
    padding-top: 0.5rem;    /* Margines górny */
    padding-bottom: 0.5rem; /* Margines dolny */
}
```

### 5. **Style dla trybu ciemnego - tabela**
```css
[data-bs-theme="dark"] .tickets-content-wrapper .table {
    color: #dee2e6;  /* Jasny tekst */
}

[data-bs-theme="dark"] .tickets-content-wrapper .table thead th {
    border-bottom-color: #495057;  /* Ciemniejszy border nagłówka */
    color: #f8f9fa;  /* Biały tekst w nagłówku */
}

[data-bs-theme="dark"] .tickets-content-wrapper .table tbody tr {
    border-color: #495057;  /* Ciemniejsze bordery wierszy */
}

[data-bs-theme="dark"] .tickets-content-wrapper .table-hover tbody tr:hover {
    background-color: rgba(255, 255, 255, 0.05);  /* Subtelne podświetlenie */
}
```

## Efekt wizualny

### Tryb jasny:
- **Tło:** Jasno szare (#f8f9fa)
- **Border:** Jasno szary (#dee2e6)
- **Cień:** Subtelny wewnętrzny cień
- **Header tabeli:** Gruby border (2px)
- **Pierwszy wiersz:** 0.75rem padding od góry
- **Wiersze:** 0.5rem padding góra/dół między nimi

### Tryb ciemny:
- **Tło:** Ciemno szare (#2b3035)
- **Border:** Średnio szary (#495057)
- **Cień:** Mocniejszy wewnętrzny cień
- **Tekst:** Jasny (#dee2e6)
- **Hover:** Subtelne białe podświetlenie

## Struktura paddingów

```
┌─────────────────────────────────────┐
│ tickets-content-wrapper             │
│ padding: 1rem (wszystkie strony)    │
│ ┌─────────────────────────────────┐ │
│ │ Nagłówek: "Zgłoszenia agenta X" │ │
│ │ margin-bottom: 0.75rem          │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ table-responsive                │ │
│ │ margin-top: 0.75rem             │ │
│ │ ┌─────────────────────────────┐ │ │
│ │ │ thead                       │ │ │
│ │ │ padding: 0.75rem (góra/dół) │ │ │
│ │ │ border-bottom: 2px          │ │ │
│ │ ├─────────────────────────────┤ │ │
│ │ │ tbody                       │ │ │
│ │ │ tr:first-child              │ │ │
│ │ │   padding-top: 0.75rem      │ │ │
│ │ │ ├─────────────────────────┐ │ │ │
│ │ │ │ pozostałe wiersze       │ │ │ │
│ │ │ │ padding: 0.5rem (góra)  │ │ │ │
│ │ │ │ padding: 0.5rem (dół)   │ │ │ │
│ │ │ └─────────────────────────┘ │ │ │
│ │ └─────────────────────────────┘ │ │
│ │ margin-bottom: 0.5rem           │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ "Łącznie: X zgłoszeń"           │ │
│ │ (margin from table: 0.5rem)     │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

## Zgodność z istniejącymi stylami

### Bootstrap 5
- Używamy natywnych klas Bootstrap: `.table`, `.table-responsive`, `.table-hover`
- Kolory zgodne z Bootstrap 5: `#dee2e6`, `#495057`, `#f8f9fa`
- Tryb ciemny: `[data-bs-theme="dark"]`

### Animacje
- Zachowano istniejącą animację: `max-height`, `opacity`, `padding`
- Czas trwania: `0.3s ease-in-out`
- Smooth transitions dla wszystkich właściwości

## Testowanie

### Tryb jasny:
1. Przejdź do panelu statystyk
2. Kliknij na agenta, aby rozwinąć listę
3. Sprawdź:
   - ✅ Jasne tło (#f8f9fa)
   - ✅ Wyraźny border (#dee2e6)
   - ✅ Pierwszy wiersz ma odstęp od góry
   - ✅ Wiersze mają odstępy między sobą
   - ✅ Płynna animacja

### Tryb ciemny:
1. Przełącz na tryb ciemny (ikona księżyca)
2. Kliknij na agenta, aby rozwinąć listę
3. Sprawdź:
   - ✅ Ciemne tło (#2b3035)
   - ✅ Wyraźny ciemny border (#495057)
   - ✅ Jasny tekst (#dee2e6)
   - ✅ Hover działa z subtelnym podświetleniem
   - ✅ Płynna animacja

### Responsywność:
1. Zmień szerokość okna
2. Sprawdź na mobile/tablet:
   - ✅ Tabela scrolluje się poziomo w `.table-responsive`
   - ✅ Marginsy i paddingi zachowane
   - ✅ Border i tło działają poprawnie

## Pliki zmodyfikowane
- ✅ `crm/templates/crm/statistics/statistics_dashboard.html`
  - Linia ~645: Usunięto klasę `bg-light` z HTML
  - Linie ~122-175: Dodano nowe style CSS

## Kompatybilność
- ✅ Bootstrap 5.x
- ✅ Wszystkie nowoczesne przeglądarki
- ✅ Dark mode / Light mode
- ✅ Responsive design
- ✅ Istniejące animacje

## Powiązane zmiany
- Related: `ENHANCEMENT_SMOOTH_ANIMATION_2025-10-17.md` (bazowa animacja)
- Related: `HOTFIX_BADGE_COLORS_2025-10-17.md` (kolory badge'ów w tabelach)
- Related: `HOTFIX_THEME_ICON_COLOR_2025-10-17.md` (tryb ciemny)

---
**Data utworzenia:** 2025-10-17  
**Status:** ✅ IMPLEMENTED  
**Autor:** GitHub Copilot  
**Kategoria:** UI/UX Enhancement
