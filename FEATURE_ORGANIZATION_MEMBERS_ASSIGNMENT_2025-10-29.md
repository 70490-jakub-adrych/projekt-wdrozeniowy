# Przypisywanie Użytkowników podczas Tworzenia/Edycji Organizacji - 2025-10-29

## Problem
Podczas tworzenia nowej organizacji:
1. **Nie było możliwości** przypisania użytkowników (Agentów, Superagentów, Klientów) bezpośrednio z formularza
2. **Twórca organizacji** nie był automatycznie do niej przypisywany
3. Trzeba było po utworzeniu organizacji ręcznie edytować profile użytkowników i dodawać ich do organizacji

## Rozwiązanie
Dodano funkcjonalność przypisywania użytkowników bezpośrednio z formularza organizacji.

### Zmiany w `crm/forms.py`

#### Rozszerzono `OrganizationForm`

Dodano pole `members` typu `ModelMultipleChoiceField`:
- Widget: `CheckboxSelectMultiple` (checkboxy dla wszystkich użytkowników)
- Wyświetla użytkowników w formacie: `"Imię Nazwisko (Rola)"` np. `"Jan Kowalski (Agent)"`
- Sortowanie według roli i nazwy użytkownika
- Podczas edycji automatycznie zaznacza aktualnych członków

```python
members = forms.ModelMultipleChoiceField(
    queryset=User.objects.none(),
    required=False,
    widget=forms.CheckboxSelectMultiple,
    label="Członkowie organizacji",
    help_text="Wybierz użytkowników, którzy będą przypisani do tej organizacji. Twórca organizacji zostanie dodany automatycznie."
)
```

### Zmiany w `crm/views/organization_views.py`

#### `organization_create()`
- **Automatyczne dodanie twórcy**: Po utworzeniu organizacji, twórca jest automatycznie do niej przypisywany
- **Dodanie wybranych członków**: Wszyscy wybrani użytkownicy są przypisywani do organizacji
- **Informacyjna wiadomość**: Pokazuje liczbę przypisanych użytkowników (w tym twórcę)

```python
# Automatically add the creator to the organization
request.user.profile.organizations.add(organization)

# Add selected members to the organization
selected_members = form.cleaned_data.get('members', [])
for user in selected_members:
    if hasattr(user, 'profile'):
        user.profile.organizations.add(organization)
```

#### `organization_update()`
- **Aktualizacja członków**: Przy edycji organizacji można dodawać i usuwać członków
- **Inteligentne zarządzanie**: 
  - Usuwa użytkowników, którzy zostali odznaczeni
  - Dodaje nowo zaznaczonych użytkowników
  - Zachowuje użytkowników, którzy pozostają zaznaczeni

### Zmiany w `crm/templates/crm/organizations/organization_form.html`

Dodano:
- **Niestandardowy layout** dla pola członków z przewijanym kontenerem (max 300px wysokości)
- **CSS styling** dla lepszej czytelności checkboxów
- **Sekcja pomocy** z informacją o automatycznym dodaniu twórcy

## Korzyści

1. ✅ **Wszystko w jednym miejscu** - przypisanie członków podczas tworzenia organizacji
2. ✅ **Automatyczne przypisanie twórcy** - twórca zawsze jest członkiem swojej organizacji
3. ✅ **Oszczędność czasu** - nie trzeba już ręcznie edytować profili użytkowników
4. ✅ **Przejrzysty interfejs** - checkboxy z nazwami i rolami użytkowników
5. ✅ **Łatwa edycja** - można dodawać/usuwać członków przy edycji organizacji
6. ✅ **Przewijanie** - długa lista użytkowników nie rozbija layoutu (max 300px + scroll)

## Przypadki użycia

### Scenariusz 1: Tworzenie nowej organizacji
1. Admin/Superagent wypełnia formularz organizacji
2. Zaznacza użytkowników na liście "Członkowie organizacji"
3. Klika "Zapisz"
4. **Rezultat**: 
   - Organizacja utworzona ✅
   - Twórca automatycznie przypisany ✅
   - Wybrani użytkownicy przypisani ✅
   - Komunikat: *"Organizacja została utworzona! Przypisano 5 użytkowników (w tym Ciebie)."*

### Scenariusz 2: Edycja istniejącej organizacji
1. Admin/Superagent otwiera edycję organizacji
2. Widzi zaznaczonych aktualnych członków
3. Zaznacza dodatkowych użytkowników lub odznacza niektórych
4. Klika "Zapisz"
5. **Rezultat**:
   - Nowi użytkownicy dodani ✅
   - Odznaczeni użytkownicy usunięci ✅
   - Komunikat: *"Organizacja została zaktualizowana!"*

## Techniczne szczegóły

### Relacja ManyToMany
- `UserProfile.organizations` ↔ `Organization.members`
- Django automatycznie zarządza tabelą pośrednią
- Używamy metod `.add()` i `.remove()` do zarządzania relacjami

### Widoczność użytkowników
- Formularz pokazuje tylko użytkowników z profilem (`profile__isnull=False`)
- Wyklucza superuserów bez profilu
- Sortowanie: najpierw według roli, potem alfabetycznie

### Format wyświetlania
```
Jan Kowalski (Administrator)
Anna Nowak (Super Agent)
Piotr Wiśniewski (Agent)
Maria Kowalczyk (Klient)
```

## Pliki zmodyfikowane
- `crm/forms.py` - dodano pole `members` do `OrganizationForm`
- `crm/views/organization_views.py` - logika przypisywania użytkowników w `organization_create()` i `organization_update()`
- `crm/templates/crm/organizations/organization_form.html` - ulepszony layout z przewijanym kontenerem

## Testowanie

Po wdrożeniu należy przetestować:
1. ✅ Tworzenie organizacji z wybranymi członkami
2. ✅ Automatyczne dodanie twórcy do organizacji
3. ✅ Edycja organizacji - dodawanie nowych członków
4. ✅ Edycja organizacji - usuwanie członków
5. ✅ Poprawne wyświetlanie ról użytkowników w formularzu
6. ✅ Przewijanie długiej listy użytkowników

## Uwagi
- Pole `members` jest **opcjonalne** - można utworzyć organizację bez dodatkowych członków
- Twórca jest **zawsze** dodawany automatycznie, niezależnie od wyboru checkboxów
- Przy edycji można usunąć członków, ale zaleca się pozostawienie co najmniej jednego admina/superagenta
