from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.utils import timezone
from crm.models import Organization, UserProfile, Ticket
import random

class Command(BaseCommand):
    help = 'Sets up demo data for the Helpdesk system'

    def handle(self, *args, **kwargs):
        # Run setup_groups command first to ensure groups exist
        from django.core.management import call_command
        call_command('setup_groups')
        
        self.stdout.write(self.style.SUCCESS('Setting up demo data...'))
        
        # Create organizations
        organizations = self._create_organizations()
        
        # Create users with different roles
        admin_user = self._create_admin_user()
        agent_users = self._create_agent_users(organizations)
        client_users = self._create_client_users(organizations)
        
        # Create sample tickets
        self._create_sample_tickets(client_users, agent_users, organizations)
        
        self.stdout.write(self.style.SUCCESS('Demo data setup completed successfully!'))
        
        # Print login credentials for reference
        self.stdout.write("\nDemo Account Credentials:")
        self.stdout.write("-------------------------")
        self.stdout.write(f"Admin: username=admin, password=admin123")
        
        for i, user in enumerate(agent_users):
            self.stdout.write(f"Agent {i+1}: username={user.username}, password=agent123")
            
        for i, user in enumerate(client_users):
            self.stdout.write(f"Client {i+1}: username={user.username}, password=client123")
    
    def _create_organizations(self):
        """Create sample organizations"""
        org_data = [
            {
                'name': 'Firma IT Solutions',
                'email': 'kontakt@itsolutions.pl',
                'phone': '123-456-789',
                'website': 'https://itsolutions.pl',
                'address': 'ul. Programistów 10, 00-001 Warszawa',
                'description': 'Firma zajmująca się rozwiązaniami IT dla biznesu.'
            },
            {
                'name': 'Marketing Pro',
                'email': 'biuro@marketingpro.pl',
                'phone': '987-654-321',
                'website': 'https://marketingpro.pl',
                'address': 'ul. Reklamowa 5, 00-002 Kraków',
                'description': 'Agencja marketingowa specjalizująca się w marketingu cyfrowym.'
            },
            {
                'name': 'E-commerce Shop',
                'email': 'info@eshop.pl',
                'phone': '111-222-333',
                'website': 'https://eshop.pl',
                'address': 'ul. Zakupowa 15, 00-003 Wrocław',
                'description': 'Sklep internetowy z elektroniką i akcesoriami.'
            }
        ]
        
        organizations = []
        for data in org_data:
            org, created = Organization.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            if created:
                self.stdout.write(f"Created organization: {org.name}")
            else:
                self.stdout.write(f"Organization already exists: {org.name}")
            organizations.append(org)
            
        return organizations
    
    def _create_admin_user(self):
        """Create an admin user"""
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        
        # Create superuser if doesn't exist
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            
            # Update profile (should be created by signal)
            try:
                profile = admin.profile
                profile.role = 'admin'
                profile.is_approved = True
                profile.save()
            except:
                profile = UserProfile.objects.create(
                    user=admin,
                    role='admin',
                    is_approved=True
                )
            
            admin.groups.add(admin_group)
            self.stdout.write(f"Created admin user: {admin.username}")
            return admin
        else:
            admin = User.objects.get(username='admin')
            self.stdout.write(f"Admin user already exists: {admin.username}")
            return admin
    
    def _create_agent_users(self, organizations):
        """Create agent users for each organization"""
        agent_group, _ = Group.objects.get_or_create(name='Agent')
        agent_users = []
        
        for i, org in enumerate(organizations):
            username = f"agent{i+1}"
            
            if not User.objects.filter(username=username).exists():
                agent = User.objects.create_user(
                    username=username,
                    email=f"agent{i+1}@example.com",
                    password='agent123',
                    first_name=f"Agent",
                    last_name=f"User {i+1}"
                )
                
                # Update profile
                try:
                    profile = agent.profile
                    profile.role = 'agent'
                    profile.organization = org
                    profile.is_approved = True
                    profile.save()
                except:
                    profile = UserProfile.objects.create(
                        user=agent,
                        role='agent',
                        organization=org,
                        is_approved=True
                    )
                
                agent.groups.add(agent_group)
                self.stdout.write(f"Created agent user: {agent.username} for {org.name}")
            else:
                agent = User.objects.get(username=username)
                self.stdout.write(f"Agent user already exists: {agent.username}")
            
            agent_users.append(agent)
            
        return agent_users
    
    def _create_client_users(self, organizations):
        """Create client users for each organization"""
        client_group, _ = Group.objects.get_or_create(name='Klient')
        client_users = []
        
        # Create 2 clients per organization
        for org in organizations:
            for i in range(2):
                client_num = len(client_users) + 1
                username = f"client{client_num}"
                
                if not User.objects.filter(username=username).exists():
                    client = User.objects.create_user(
                        username=username,
                        email=f"client{client_num}@example.com",
                        password='client123',
                        first_name=f"Client",
                        last_name=f"User {client_num}"
                    )
                    
                    # Update profile
                    try:
                        profile = client.profile
                        profile.role = 'client'
                        profile.organization = org
                        profile.is_approved = True
                        profile.save()
                    except:
                        profile = UserProfile.objects.create(
                            user=client,
                            role='client',
                            organization=org,
                            is_approved=True
                        )
                    
                    client.groups.add(client_group)
                    self.stdout.write(f"Created client user: {client.username} for {org.name}")
                else:
                    client = User.objects.get(username=username)
                    self.stdout.write(f"Client user already exists: {client.username}")
                
                client_users.append(client)
                
        return client_users
    
    def _create_sample_tickets(self, client_users, agent_users, organizations):
        """Create sample tickets with various statuses"""
        statuses = ['new', 'in_progress', 'waiting', 'resolved', 'closed']
        priorities = ['low', 'medium', 'high', 'critical']
        categories = ['hardware', 'software', 'network', 'account', 'other']
        
        ticket_data = [
            {
                'title': 'Problem z logowaniem do systemu',
                'description': 'Nie mogę zalogować się do panelu administracyjnego. Wyświetla błąd "Nieprawidłowe dane logowania".',
                'category': 'account',
                'priority': 'high'
            },
            {
                'title': 'Awaria drukarki sieciowej',
                'description': 'Drukarka HP w dziale księgowości nie drukuje. Świeci się czerwona dioda.',
                'category': 'hardware',
                'priority': 'medium'
            },
            {
                'title': 'Prośba o instalację oprogramowania',
                'description': 'Potrzebuję zainstalować najnowszą wersję Adobe Creative Suite na moim komputerze służbowym.',
                'category': 'software',
                'priority': 'low'
            },
            {
                'title': 'Brak dostępu do internetu',
                'description': 'Od rana nie mam połączenia z internetem. Inne osoby w biurze nie zgłaszają problemów.',
                'category': 'network',
                'priority': 'high'
            },
            {
                'title': 'Błędy w aplikacji księgowej',
                'description': 'System księgowy wyświetla błędy przy próbie generowania raportu miesięcznego. Błąd: "Nieprawidłowy format daty".',
                'category': 'software',
                'priority': 'critical'
            },
            {
                'title': 'Wymiana baterii w laptopie',
                'description': 'Bateria w moim laptopie służbowym trzyma tylko około 30 minut. Proszę o wymianę.',
                'category': 'hardware',
                'priority': 'low'
            },
            {
                'title': 'Problem z VPN',
                'description': 'Nie mogę połączyć się z siecią firmową przez VPN pracując z domu. Błąd: "Timeout connection".',
                'category': 'network',
                'priority': 'medium'
            },
            {
                'title': 'Resetowanie hasła dla nowego pracownika',
                'description': 'Proszę o reset hasła dla Jana Kowalskiego, który dołączył do zespołu wczoraj.',
                'category': 'account',
                'priority': 'medium'
            },
            {
                'title': 'Aktualizacja systemu Windows',
                'description': 'Po ostatniej aktualizacji Windows mój komputer działa bardzo wolno. Czy można cofnąć aktualizację?',
                'category': 'software',
                'priority': 'high'
            },
            {
                'title': 'Prośba o dodatkowy monitor',
                'description': 'W związku z nowymi obowiązkami potrzebuję dodatkowego monitora do pracy.',
                'category': 'other',
                'priority': 'low'
            }
        ]
        
        created_tickets = []
        
        # Create tickets
        for data in ticket_data:
            client = random.choice(client_users)
            organization = client.profile.organization
            
            # Choose a status - weight towards new tickets
            status = random.choices(
                statuses,
                weights=[0.4, 0.3, 0.1, 0.1, 0.1],
                k=1
            )[0]
            
            # For in_progress/resolved/closed tickets, assign an agent
            assigned_to = None
            if status in ['in_progress', 'resolved', 'closed']:
                for agent in agent_users:
                    if agent.profile.organization == organization:
                        assigned_to = agent
                        break
            
            # Set dates based on status
            resolved_at = None
            closed_at = None
            
            if status == 'resolved':
                resolved_at = timezone.now()
            
            if status == 'closed':
                resolved_at = timezone.now() - timezone.timedelta(days=1)
                closed_at = timezone.now()
                
            ticket = Ticket.objects.create(
                title=data['title'],
                description=data['description'],
                category=data['category'],
                priority=data['priority'],
                status=status,
                created_by=client,
                assigned_to=assigned_to,
                organization=organization,
                resolved_at=resolved_at,
                closed_at=closed_at
            )
            
            self.stdout.write(f"Created ticket: {ticket.title} ({ticket.get_status_display()})")
            created_tickets.append(ticket)
            
        return created_tickets
