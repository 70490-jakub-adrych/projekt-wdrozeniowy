import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from crm.models import Organization, Ticket, TicketComment

class Command(BaseCommand):
    help = 'Generuje testowe zgłoszenia różnego typu dla Organizacji Testowej'

    def handle(self, *args, **options):
        self.stdout.write('Rozpoczynam generowanie testowych zgłoszeń...')
        
        # Sprawdzanie czy istnieje organizacja testowa
        try:
            organizacja = Organization.objects.get(name='Organizacja Testowa')
            self.stdout.write(self.style.SUCCESS(f'Znaleziono organizację: {organizacja.name}'))
        except Organization.DoesNotExist:
            self.stdout.write(self.style.WARNING('Nie znaleziono organizacji "Firma IT Solutions". Tworzę nową.'))
            organizacja = Organization.objects.create(
                name='Firma IT Solutions',
                email='kontakt@itsolutions.pl',
                phone='123-456-789',
                website='https://itsolutions.pl',
                address='ul. Programistów 10, 00-001 Warszawa',
                description='Firma zajmująca się rozwiązaniami IT dla biznesu.'
            )
        
        # Sprawdzanie czy istnieją wymagani użytkownicy
        try:
            agent = User.objects.get(username='agent1')
            self.stdout.write(self.style.SUCCESS(f'Znaleziono agenta: {agent.username}'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Nie znaleziono użytkownika agent1! Użyj najpierw komendy setup_demo_data'))
            return
        
        try:
            client = User.objects.get(username='client1')
            self.stdout.write(self.style.SUCCESS(f'Znaleziono klienta: {client.username}'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Nie znaleziono użytkownika client1! Użyj najpierw komendy setup_demo_data'))
            return
        
        # Sprawdź czy agent ma przypisaną organizację
        if not agent.profile.organizations.filter(id=organizacja.id).exists():
            agent.profile.organizations.add(organizacja)
            self.stdout.write(self.style.SUCCESS(f'Przypisano agenta {agent.username} do organizacji {organizacja.name}'))
        
        # Sprawdź czy klient ma przypisaną organizację
        if not client.profile.organizations.filter(id=organizacja.id).exists():
            client.profile.organizations.add(organizacja)
            self.stdout.write(self.style.SUCCESS(f'Przypisano klienta {client.username} do organizacji {organizacja.name}'))
            
        # Lista tytułów zgłoszeń
        tytuly_zgloszen = [
            # NOWE
            {
                'title': 'Problem z logowaniem do panelu klienta',
                'description': 'Od dzisiaj rano nie mogę się zalogować do panelu klienta. System wyświetla błąd "Nieprawidłowa nazwa użytkownika lub hasło" mimo że jestem pewien, że dane są poprawne.',
                'status': 'new',
                'category': 'account',
                'priority': 'high'
            },
            {
                'title': 'Prośba o dodatkowe uprawnienia w systemie CRM',
                'description': 'Potrzebuję dodatkowych uprawnień w systemie CRM, aby móc generować zaawansowane raporty sprzedaży. Obecnie mam tylko dostęp podstawowy.',
                'status': 'new',
                'category': 'account',
                'priority': 'medium'
            },
            {
                'title': 'Awaria drukarki sieciowej w dziale księgowości',
                'description': 'Drukarka HP LaserJet Pro w dziale księgowości nie drukuje dokumentów. Na panelu wyświetla się komunikat "Paper jam" mimo że nie ma zablokowanego papieru.',
                'status': 'new',
                'category': 'hardware',
                'priority': 'high'
            },
            
            # W TRAKCIE
            {
                'title': 'Aktualizacja oprogramowania księgowego',
                'description': 'Prośba o aktualizację programu księgowego do najnowszej wersji. Obecna wersja ma błędy w module raportowania VAT.',
                'status': 'in_progress',
                'category': 'software',
                'priority': 'medium'
            },
            {
                'title': 'Problemy z wydajnością serwera bazodanowego',
                'description': 'Od tygodnia obserwujemy spadek wydajności naszego serwera SQL. Zapytania, które wcześniej wykonywały się w kilka sekund, teraz trwają kilka minut.',
                'status': 'in_progress',
                'category': 'network',
                'priority': 'critical'
            },
            {
                'title': 'Konfiguracja nowego laptopa dla pracownika',
                'description': 'Proszę o przygotowanie nowego laptopa dla nowego pracownika działu marketingu. Potrzebne standardowe oprogramowanie plus pakiet graficzny Adobe.',
                'status': 'in_progress',
                'category': 'hardware',
                'priority': 'low'
            },
            
            # NIEROZWIĄZANE
            {
                'title': 'Awaria klimatyzacji w serwerowni',
                'description': 'W serwerowni przestała działać klimatyzacja, temperatura rośnie. Serwisanci zostali wezwani, ale potrzebny monitoring sytuacji.',
                'status': 'unresolved',
                'category': 'other',
                'priority': 'critical'
            },
            {
                'title': 'Problem z synchronizacją kalendarzy',
                'description': 'Kalendarze w Outlooku i na urządzeniach mobilnych nie synchronizują się prawidłowo. Spotkania dodane na telefonie nie pojawiają się w Outlooku.',
                'status': 'unresolved',
                'category': 'software',
                'priority': 'medium'
            },
            {
                'title': 'Brak dostępu do dysku sieciowego',
                'description': 'Nie mogę uzyskać dostępu do dysku sieciowego Z:. Wyświetla się komunikat "Sieć niedostępna" mimo działającego połączenia internetowego.',
                'status': 'unresolved',
                'category': 'network',
                'priority': 'high'
            },
            
            # ROZWIĄZANE
            {
                'title': 'Wymiana baterii w UPS',
                'description': 'Prośba o wymianę baterii w zasilaczu awaryjnym UPS w serwerowni. Obecna bateria pokazuje 20% pojemności.',
                'status': 'resolved',
                'category': 'hardware',
                'priority': 'medium'
            },
            {
                'title': 'Reset hasła dla użytkownika systemu kadrowego',
                'description': 'Proszę o reset hasła dla użytkownika jkowalski w systemie kadrowym. Użytkownik nie pamięta hasła i nie może się zalogować.',
                'status': 'resolved',
                'category': 'account',
                'priority': 'medium'
            },
            {
                'title': 'Instalacja oprogramowania antywirusowego',
                'description': 'Proszę o instalację pakietu antywirusowego na komputerach w dziale obsługi klienta (5 stanowisk).',
                'status': 'resolved',
                'category': 'software',
                'priority': 'medium'
            },
            
            # ZAMKNIĘTE
            {
                'title': 'Awaria łącza internetowego',
                'description': 'Brak dostępu do internetu w całym biurze. Problem z routerem głównym, nie świecą się diody.',
                'status': 'closed',
                'category': 'network',
                'priority': 'critical'
            },
            {
                'title': 'Konfiguracja nowej drukarki w recepcji',
                'description': 'Prośba o instalację i konfigurację nowej drukarki Brother MFC-L3750CDW w recepcji. Drukarka jest już rozpakowana i podłączona do prądu.',
                'status': 'closed',
                'category': 'hardware',
                'priority': 'low'
            },
            {
                'title': 'Szkolenie z obsługi nowego systemu CRM',
                'description': 'Potrzebujemy zorganizować szkolenie z obsługi nowego systemu CRM dla 10 pracowników działu sprzedaży. Preferowany termin to przyszły tydzień.',
                'status': 'closed',
                'category': 'other',
                'priority': 'medium'
            }
        ]
        
        # Komentarze do zgłoszeń
        komentarze = [
            "Dziękuję za zgłoszenie. Zajmuję się problemem i będę informować o postępach.",
            "Proszę o więcej szczegółów dotyczących problemu.",
            "Sprawdziłem sytuację. Problem wymaga interwencji serwisu zewnętrznego.",
            "Problem został rozwiązany. Proszę o potwierdzenie, że wszystko działa poprawnie.",
            "Wydłuża się czas naprawy ze względu na konieczność zamówienia części.",
            "Przesyłam instrukcję tymczasowego rozwiązania problemu. Docelowe rozwiązanie będzie wdrożone jutro.",
            "To znany błąd, który zostanie naprawiony w najbliższej aktualizacji systemu.",
            "Przekazałem problem do działu rozwoju oprogramowania. Ustalą priorytet i czas naprawy.",
            "Zaplanowałem wizytę technika na jutro między 10:00 a 12:00.",
            "Po analizie okazuje się, że problem jest bardziej złożony niż początkowo zakładaliśmy.",
        ]
        
        now = timezone.now()
        liczba_utworzonych = 0
        
        # Tworzenie zgłoszeń
        for dane in tytuly_zgloszen:
            # Losowe określenie dat dla różnych statusów
            created_at = now - timedelta(days=random.randint(1, 30))
            resolved_at = None
            closed_at = None
            
            if dane['status'] in ['resolved', 'closed']:
                resolved_at = created_at + timedelta(days=random.randint(1, 5))
                
            if dane['status'] == 'closed':
                closed_at = resolved_at + timedelta(days=random.randint(1, 3))
            
            # Tworzenie zgłoszenia
            zgloszenie = Ticket.objects.create(
                title=dane['title'],
                description=dane['description'],
                status=dane['status'],
                priority=dane['priority'],
                category=dane['category'],
                created_by=client,
                assigned_to=agent if dane['status'] not in ['new'] else None,
                organization=organizacja,
                created_at=created_at,
                resolved_at=resolved_at,
                closed_at=closed_at
            )
            
            # Dodawanie komentarzy
            if dane['status'] in ['in_progress', 'unresolved', 'resolved', 'closed']:
                # Komentarz od agenta
                comment_date = created_at + timedelta(hours=random.randint(1, 8))
                TicketComment.objects.create(
                    ticket=zgloszenie,
                    author=agent,
                    content=random.choice(komentarze),
                    created_at=comment_date
                )
                
                # Dla rozwiązanych i zamkniętych dodaj dodatkowy komentarz
                if dane['status'] in ['resolved', 'closed']:
                    comment_date = comment_date + timedelta(days=1)
                    TicketComment.objects.create(
                        ticket=zgloszenie,
                        author=agent,
                        content="Problem został rozwiązany. Zgłoszenie można zamknąć.",
                        created_at=comment_date
                    )
                    
                    # Czasem dodaj odpowiedź klienta
                    if random.choice([True, False]):
                        comment_date = comment_date + timedelta(hours=random.randint(1, 12))
                        TicketComment.objects.create(
                            ticket=zgloszenie,
                            author=client,
                            content="Dziękuję za pomoc. Problem został rozwiązany.",
                            created_at=comment_date
                        )
            
            liczba_utworzonych += 1
            self.stdout.write(f"Utworzono zgłoszenie: {dane['title']} (Status: {dane['status']})")
            
        self.stdout.write(self.style.SUCCESS(f'\nPomyślnie utworzono {liczba_utworzonych} testowych zgłoszeń dla organizacji {organizacja.name}'))
