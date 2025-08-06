from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from crm.models import Ticket, Organization, UserProfile
import random
from datetime import datetime, timedelta
from django.utils import timezone


class Command(BaseCommand):
    help = 'Create 25 random tickets for testing purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=25,
            help='Number of tickets to create (default: 25)',
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Sample data for random generation
        ticket_titles = [
            'Problem z logowaniem do systemu',
            'Błąd podczas zapisywania danych',
            'Nie działa drukarka w biurze',
            'Wolno ładuje się aplikacja',
            'Brak dostępu do serwera email',
            'Problem z połączeniem internetowym',
            'Aplikacja się zawiesza',
            'Nie można otworzyć pliku PDF',
            'Błąd synchronizacji danych',
            'Problem z aktualizacją oprogramowania',
            'Nie działa mikrofon w aplikacji',
            'Błąd przy eksporcie raportu',
            'Problem z bazą danych',
            'Nie można dodać nowego użytkownika',
            'Błąd autoryzacji w systemie',
            'Problem z kopią zapasową',
            'Nie działa funkcja wyszukiwania',
            'Błąd podczas importu danych',
            'Problem z certyfikatem SSL',
            'Nie można wysłać emaila',
            'Aplikacja wylogowuje automatycznie',
            'Problem z uprawnieniami użytkownika',
            'Błąd podczas generowania faktury',
            'Nie działa integracja z zewnętrznym API',
            'Problem z wydajnością systemu'
        ]
        
        ticket_descriptions = [
            'Użytkownik nie może się zalogować do systemu pomimo prawidłowych danych.',
            'Podczas próby zapisania formularza pojawia się błąd i dane nie są zapisywane.',
            'Drukarka w głównym biurze nie odpowiada na polecenia drukowania.',
            'Aplikacja ładuje się bardzo wolno, szczególnie przy większych zbiorach danych.',
            'Brak możliwości połączenia z serwerem poczty elektronicznej.',
            'Przerwy w połączeniu internetowym w całym budynku.',
            'Aplikacja przestaje odpowiadać podczas wykonywania określonych operacji.',
            'Pliki PDF nie otwierają się w przeglądarce ani w zewnętrznych aplikacjach.',
            'Dane nie synchronizują się między różnymi modułami systemu.',
            'Aktualizacja oprogramowania kończy się błędem i przerywa instalację.',
            'Mikrofon nie jest rozpoznawany przez aplikację podczas wideokonferencji.',
            'Eksport raportu do formatu Excel kończy się błędem.',
            'Sporadyczne błędy połączenia z bazą danych powodujące timeout.',
            'Formularz dodawania nowego użytkownika nie działa poprawnie.',
            'Błędy autoryzacji uniemożliwiają dostęp do niektórych funkcji.',
            'Proces tworzenia kopii zapasowej kończy się niepowodzeniem.',
            'Funkcja wyszukiwania nie zwraca żadnych wyników pomimo istnienia danych.',
            'Import danych z pliku CSV kończy się błędem walidacji.',
            'Certyfikat SSL wygasł i wymaga odnowienia.',
            'System nie może wysłać powiadomień email do użytkowników.',
            'Użytkownicy są automatycznie wylogowywani po kilku minutach.',
            'Niektórzy użytkownicy nie mają dostępu do wymaganych funkcji systemu.',
            'Generowanie faktury kończy się błędem i dokument nie jest tworzony.',
            'Integracja z zewnętrznym API zwraca błędy 500.',
            'System działa bardzo wolno podczas godzin szczytu.'
        ]
        
        # Get available choices
        statuses = ['new', 'in_progress', 'unresolved', 'resolved', 'closed']
        priorities = ['low', 'medium', 'high', 'critical']
        categories = ['hardware', 'software', 'network', 'account', 'other']
        
        # Get existing users and organizations
        try:
            users = list(User.objects.filter(profile__is_approved=True))
            if not users:
                self.stdout.write(
                    self.style.ERROR('No approved users found. Please create some users first.')
                )
                return
                
            organizations = list(Organization.objects.all())
            if not organizations:
                self.stdout.write(
                    self.style.ERROR('No organizations found. Please create some organizations first.')
                )
                return
                
            # Get agents for assignment
            agents = list(User.objects.filter(
                profile__role__in=['admin', 'superagent', 'agent'],
                profile__is_approved=True
            ))
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error fetching data: {e}')
            )
            return
        
        created_tickets = []
        
        for i in range(count):
            try:
                # Random title and description
                title = random.choice(ticket_titles)
                description = random.choice(ticket_descriptions)
                
                # Random choices
                status = random.choice(statuses)
                priority = random.choice(priorities)
                category = random.choice(categories)
                
                # Random user and organization
                created_by = random.choice(users)
                organization = random.choice(organizations)
                
                # Random assignment (50% chance to be assigned)
                assigned_to = random.choice(agents) if agents and random.random() > 0.5 else None
                
                # Random creation time (within last 30 days)
                days_ago = random.randint(0, 30)
                hours_ago = random.randint(0, 23)
                minutes_ago = random.randint(0, 59)
                created_at = timezone.now() - timedelta(
                    days=days_ago, 
                    hours=hours_ago, 
                    minutes=minutes_ago
                )
                
                # Create the ticket
                ticket = Ticket.objects.create(
                    title=title,
                    description=description,
                    status=status,
                    priority=priority,
                    category=category,
                    created_by=created_by,
                    assigned_to=assigned_to,
                    organization=organization,
                    created_at=created_at
                )
                
                # Set resolved/closed dates if status requires it
                if status == 'resolved':
                    ticket.resolved_at = created_at + timedelta(
                        days=random.randint(1, 5),
                        hours=random.randint(1, 12)
                    )
                    ticket.save()
                elif status == 'closed':
                    ticket.resolved_at = created_at + timedelta(
                        days=random.randint(1, 3),
                        hours=random.randint(1, 8)
                    )
                    ticket.closed_at = ticket.resolved_at + timedelta(
                        hours=random.randint(1, 24)
                    )
                    ticket.save()
                
                created_tickets.append(ticket)
                
                self.stdout.write(f'Created ticket #{ticket.id}: {ticket.title}')
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating ticket {i+1}: {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(created_tickets)} tickets!'
            )
        )
        
        # Show summary statistics
        if created_tickets:
            self.stdout.write('\n--- Summary ---')
            status_counts = {}
            priority_counts = {}
            category_counts = {}
            
            for ticket in created_tickets:
                status_counts[ticket.status] = status_counts.get(ticket.status, 0) + 1
                priority_counts[ticket.priority] = priority_counts.get(ticket.priority, 0) + 1
                category_counts[ticket.category] = category_counts.get(ticket.category, 0) + 1
            
            self.stdout.write('Status distribution:')
            for status, count in status_counts.items():
                self.stdout.write(f'  {status}: {count}')
            
            self.stdout.write('\nPriority distribution:')
            for priority, count in priority_counts.items():
                self.stdout.write(f'  {priority}: {count}')
                
            self.stdout.write('\nCategory distribution:')
            for category, count in category_counts.items():
                self.stdout.write(f'  {category}: {count}')
