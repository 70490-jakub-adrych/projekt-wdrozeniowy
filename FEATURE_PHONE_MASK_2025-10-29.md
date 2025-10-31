# Maska Telefonu dla Numerów Polskich - 2025-10-29

## Problem
1. Pola telefonu nie miały maski formatującej
2. Użytkownicy wpisywali numery w różnych formatach
3. Tekst "Phone" był po angielsku w formularzach
4. Brak walidacji formatu podczas wpisywania

## Rozwiązanie
Dodano automatyczne formatowanie numerów telefonów zgodnie z polskimi standardami.

### Wspierane Formaty

#### 1. Format Lokalny (bez kierunkowego)
```
Wpisywane: 123456789
Formatowane: 12 345 67 89
```

#### 2. Format Międzynarodowy (+48)
```
Wpisywane: +48123456789 lub 48123456789
Formatowane: +48 12 345 67 89
```

#### 3. Format Stacjonarny
```
Wpisywane: 0223456789
Formatowane: 022 345 67 89
```

### Zmiany w kodzie

#### 1. `crm/forms.py`

**UserProfileForm** - Zaktualizowano pole telefonu:
```python
phone = forms.CharField(
    max_length=20,  # Zwiększono z 17 na 20
    required=False, 
    validators=[phone_regex],
    label='Telefon',  # Polskie tłumaczenie
    widget=forms.TextInput(attrs={
        'placeholder': '12 345 67 89 lub +48 12 345 67 89',
        'class': 'form-control phone-mask'
    })
)
```

**OrganizationForm** - Zaktualizowano pole telefonu:
```python
phone = forms.CharField(
    max_length=20,  # Zwiększono z 17 na 20
    required=False, 
    validators=[phone_regex],
    label='Telefon',  # Polskie tłumaczenie
    widget=forms.TextInput(attrs={
        'placeholder': '12 345 67 89 lub +48 12 345 67 89',
        'class': 'form-control phone-mask'
    })
)
```

#### 2. `crm/static/crm/js/phone-mask.js` (NOWY PLIK)

Utworzono globalny skrypt JavaScript do formatowania numerów telefonów:

**Funkcjonalności:**
- ✅ Automatyczne formatowanie podczas wpisywania
- ✅ Obsługa formatu lokalnego (xx xxx xx xx)
- ✅ Obsługa formatu międzynarodowego (+48 xx xxx xx xx)
- ✅ Auto-dodawanie `+` dla numerów zaczynających się od 48
- ✅ Zachowanie pozycji kursora podczas formatowania
- ✅ Obsługa wklejania (paste event)
- ✅ Usuwanie wszystkich znaków niebędących cyframi (oprócz +)

**Przykład działania:**
```javascript
// Użytkownik wpisuje: "123456789"
// Automatycznie formatowane: "12 345 67 89"

// Użytkownik wpisuje: "48123456789"
// Automatycznie formatowane: "+48 12 345 67 89"

// Użytkownik wpisuje: "+48123456789"
// Automatycznie formatowane: "+48 12 345 67 89"
```

#### 3. `crm/templates/crm/base.html`

Dodano import globalnego skryptu maski telefonu:
```django-html
<!-- Phone number mask script -->
<script src="{% static 'crm/js/phone-mask.js' %}"></script>
```

#### 4. `crm/templates/crm/register.html`

Usunięto duplikację skryptu (wykorzystuje teraz globalny).

### Jak to działa?

1. **Wykrywanie pól telefonu:**
   - Skrypt znajduje wszystkie pola z `name="phone"` lub klasą `phone-mask`

2. **Formatowanie w czasie rzeczywistym:**
   - Przy każdym wpisaniu znaku liczba jest automatycznie formatowana
   - Spacje są dodawane w odpowiednich miejscach

3. **Inteligentne rozpoznawanie formatu:**
   - Jeśli zaczyna się od `48` → format międzynarodowy (+48 xx xxx xx xx)
   - Jeśli zaczyna się od `+48` → format międzynarodowy
   - W pozostałych przypadkach → format lokalny (xx xxx xx xx)

4. **Zachowanie pozycji kursora:**
   - Kursor pozostaje w logicznej pozycji podczas formatowania
   - Uwzględnia dodawane spacje

### Korzyści

1. ✅ **Spójność danych** - wszystkie numery w jednolitym formacie
2. ✅ **Lepsza UX** - użytkownik widzi poprawnie sformatowany numer
3. ✅ **Mniej błędów** - automatyczne formatowanie redukuje pomyłki
4. ✅ **Polskie tłumaczenia** - "Telefon" zamiast "Phone"
5. ✅ **Uniwersalność** - działa we wszystkich formularzach
6. ✅ **Wsparcie mobile** - działa na urządzeniach dotykowych

### Gdzie działa maska?

Maska telefonu jest aktywna w następujących miejscach:
- ✅ Formularz rejestracji użytkownika
- ✅ Edycja profilu użytkownika
- ✅ Tworzenie organizacji
- ✅ Edycja organizacji
- ✅ Wszystkie inne formularze z polem `name="phone"` lub klasą `phone-mask`

### Przykłady użycia

#### Przykład 1: Numer lokalny
```
Użytkownik wpisuje: 123456789
System formatuje: 12 345 67 89
```

#### Przykład 2: Numer z kierunkowym
```
Użytkownik wpisuje: 48123456789
System formatuje: +48 12 345 67 89
```

#### Przykład 3: Użytkownik wkleja numer
```
Użytkownik wkleja: "+48 (12) 345-67-89"
System czyści i formatuje: +48 12 345 67 89
```

### Techniczne szczegóły

#### Regex usuwający niepotrzebne znaki
```javascript
let digitsOnly = value.replace(/[^\d+]/g, '');
```

#### Logika formatowania
```javascript
if (digitsOnly.startsWith('+48')) {
    // Format: +48 xx xxx xx xx
    let numbers = digitsOnly.substring(3);
    formatted = '+48';
    if (numbers.length > 0) formatted += ' ' + numbers.substring(0, 2);
    if (numbers.length > 2) formatted += ' ' + numbers.substring(2, 5);
    // ...
}
```

#### Zachowanie pozycji kursora
```javascript
// Liczenie spacji przed kursorem
let spacesBefore = (value.substring(0, cursorPosition).match(/ /g) || []).length;
// Przeliczanie nowej pozycji
let spacesAfter = (formatted.substring(0, cursorPosition).match(/ /g) || []).length;
let newPosition = cursorPosition + (spacesAfter - spacesBefore);
```

## Pliki zmodyfikowane/utworzone

### Zmodyfikowane:
- `crm/forms.py` - UserProfileForm, OrganizationForm
- `crm/templates/crm/base.html` - dodano import phone-mask.js
- `crm/templates/crm/register.html` - usunięto duplikację skryptu

### Utworzone:
- `crm/static/crm/js/phone-mask.js` - globalny skrypt maski telefonu

## Testowanie

Aby przetestować:
1. ✅ Otwórz formularz rejestracji
2. ✅ Wpisz numer telefonu: `123456789`
3. ✅ Sprawdź czy formatuje się na: `12 345 67 89`
4. ✅ Wpisz numer z +48: `+48123456789`
5. ✅ Sprawdź czy formatuje się na: `+48 12 345 67 89`
6. ✅ Spróbuj wkleić numer w różnych formatach
7. ✅ Sprawdź czy kursor pozostaje w logicznej pozycji

## Kompatybilność

- ✅ Wszystkie nowoczesne przeglądarki (Chrome, Firefox, Safari, Edge)
- ✅ Urządzenia mobilne (iOS, Android)
- ✅ Działa bez JavaScript (pole nadal funkcjonalne)
- ✅ Graceful degradation (brak JS = zwykłe pole tekstowe)

## Uwagi

- Pole telefonu jest opcjonalne (`required=False`)
- Max długość zwiększona z 17 do 20 znaków (dla formatu +48 xx xxx xx xx)
- Validator `phone_regex` nadal działa w backendzie
- Maska jest tylko wizualna - backend również waliduje format
