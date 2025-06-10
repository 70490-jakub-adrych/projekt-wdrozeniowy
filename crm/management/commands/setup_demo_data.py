from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from crm.models import (
    Organization, UserProfile, Ticket, TicketComment, TicketAttachment,
    ViewPermission, GroupViewPermission, GroupSettings  # Add GroupSettings import
)
import random

class Command(BaseCommand):
    help = 'Sets up demo data for the Helpdesk system including user groups and permissions'

    def handle(self, *args, **kwargs):
        # Step 1: Set up groups and permissions
        self._setup_groups_and_permissions()
        
        # Step 1b: Set up view permissions
        self._setup_view_permissions()
        
        self.stdout.write(self.style.SUCCESS('Setting up demo data...'))
        
        # Create organizations
        organizations = self._create_organizations()
        
        # Create users with different roles
        admin_user = self._create_admin_user(organizations)  # Pass organizations to admin creation
        superagent_user = self._create_superagent_user(organizations)  # Dodaj superagenta
        agent_users = self._create_agent_users(organizations)
        client_users = self._create_client_users(organizations)
        viewer_user = self._create_viewer_user()  # Create viewer user
        
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
            
        self.stdout.write(f"Viewer: username=viewer, password=viewer123")
        self.stdout.write(f"Superagent: username=superagent, password=superagent123")
    
    def _setup_groups_and_permissions(self):
        """Create user groups and assign permissions"""
        self.stdout.write("Setting up user groups and permissions...")
        
        # Get or create the groups
        admin_group, created_admin = Group.objects.get_or_create(name='Admin')
        superagent_group, created_superagent = Group.objects.get_or_create(name='Superagent')
        agent_group, created_agent = Group.objects.get_or_create(name='Agent')
        client_group, created_client = Group.objects.get_or_create(name='Klient')
        viewer_group, created_viewer = Group.objects.get_or_create(name='Viewer')
        
        # Clear existing permissions for a fresh start
        admin_group.permissions.clear()
        superagent_group.permissions.clear()
        agent_group.permissions.clear()
        client_group.permissions.clear()
        viewer_group.permissions.clear()
        
        # Create or update group settings
        GroupSettings.objects.update_or_create(
            group=admin_group,
            defaults={
                'allow_multiple_organizations': True,
                'show_statistics': True,
                'attachments_access_level': 'all'  # Admins can see all attachments
            }
        )
        
        GroupSettings.objects.update_or_create(
            group=superagent_group,
            defaults={
                'allow_multiple_organizations': True,
                'show_statistics': True,
                'attachments_access_level': 'all'  # Superagents can see all attachments
            }
        )
        
        GroupSettings.objects.update_or_create(
            group=agent_group,
            defaults={
                'allow_multiple_organizations': True,
                'show_statistics': False,
                'attachments_access_level': 'organization'  # Agents can see attachments in their organizations
            }
        )
        
        GroupSettings.objects.update_or_create(
            group=client_group,
            defaults={
                'allow_multiple_organizations': False,
                'show_statistics': False,
                'attachments_access_level': 'own'  # Clients can only see own attachments
            }
        )
        
        GroupSettings.objects.update_or_create(
            group=viewer_group,
            defaults={
                'allow_multiple_organizations': False,
                'show_statistics': False,
                'attachments_access_level': 'own'  # Viewers can only see own attachments
            }
        )
        
        # Get content types
        ticket_ct = ContentType.objects.get_for_model(Ticket)
        comment_ct = ContentType.objects.get_for_model(TicketComment)
        attachment_ct = ContentType.objects.get_for_model(TicketAttachment)
        org_ct = ContentType.objects.get_for_model(Organization)
        profile_ct = ContentType.objects.get_for_model(UserProfile)
        
        # Define additional owner-specific permissions
        owner_permissions = [
            ('change_own_ticket', 'Can change tickets created by self'),
            ('close_own_ticket', 'Can close tickets created by self'),
            ('comment_own_ticket', 'Can comment on tickets created by self'),
            ('attach_to_own_ticket', 'Can add attachments to tickets created by self'),
        ]
        
        # Create custom permissions if they don't exist
        for codename, name in owner_permissions:
            Permission.objects.get_or_create(
                codename=codename,
                name=name,
                content_type=ticket_ct,
            )
        
        # Admin permissions (full access)
        admin_permissions = Permission.objects.filter(
            content_type__in=[ticket_ct, org_ct, profile_ct, comment_ct, attachment_ct]
        )
        admin_group.permissions.add(*admin_permissions)
        
        # Superagent permissions (full access jak admin)
        superagent_group.permissions.set(admin_permissions)
        
        # Agent permissions
        agent_permissions = Permission.objects.filter(
            content_type=ticket_ct,
            codename__in=[
                'add_ticket', 'change_ticket', 'view_ticket',
            ]
        )
        agent_permissions |= Permission.objects.filter(
            content_type=comment_ct,
            codename__in=['add_ticketcomment', 'change_ticketcomment', 'view_ticketcomment']
        )
        agent_permissions |= Permission.objects.filter(
            content_type=attachment_ct,
            codename__in=['add_ticketattachment', 'view_ticketattachment']
        )
        agent_permissions |= Permission.objects.filter(
            content_type__in=[org_ct, profile_ct],
            codename__startswith='view_'
        )
        agent_permissions |= Permission.objects.filter(
            content_type=profile_ct,
            codename__in=['change_userprofile']
        )
        # Add owner-specific permissions
        owner_perms = Permission.objects.filter(
            content_type=ticket_ct,
            codename__in=['change_own_ticket', 'close_own_ticket', 'comment_own_ticket', 'attach_to_own_ticket']
        )
        agent_permissions |= owner_perms
        agent_group.permissions.add(*agent_permissions)
        
        # Client permissions
        client_permissions = Permission.objects.filter(
            content_type=ticket_ct,
            codename__in=['add_ticket', 'view_ticket']
        )
        # Add owner-specific permissions for clients
        client_permissions |= owner_perms
        client_group.permissions.add(*client_permissions)
        
        # Viewer permissions (only view tickets)
        viewer_permissions = Permission.objects.filter(
            content_type=ticket_ct,
            codename__in=['view_ticket']
        )
        viewer_group.permissions.add(*viewer_permissions)
        
        # Report results
        if created_admin:
            self.stdout.write(self.style.SUCCESS('Created Admin group'))
        else:
            self.stdout.write(self.style.SUCCESS('Updated Admin group permissions'))

        if created_superagent:
            self.stdout.write(self.style.SUCCESS('Created Superagent group'))
        else:
            self.stdout.write(self.style.SUCCESS('Updated Superagent group permissions'))
            
        if created_agent:
            self.stdout.write(self.style.SUCCESS('Created Agent group'))
        else:
            self.stdout.write(self.style.SUCCESS('Updated Agent group permissions'))
            
        if created_client:
            self.stdout.write(self.style.SUCCESS('Created Klient group'))
        else:
            self.stdout.write(self.style.SUCCESS('Updated Klient group permissions'))
            
        if created_viewer:
            self.stdout.write(self.style.SUCCESS('Created Viewer group'))
        else:
            self.stdout.write(self.style.SUCCESS('Updated Viewer group permissions'))

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
    
    def _create_admin_user(self, organizations):
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
                profile.email_verified = True  # Mark email as verified
                profile.save()
                
                # Assign admin to all organizations
                for org in organizations:
                    profile.organizations.add(org)
                    
            except Exception as e:
                self.stdout.write(f"Error updating admin profile: {str(e)}")
                profile = UserProfile.objects.create(
                    user=admin,
                    role='admin',
                    is_approved=True,
                    email_verified=True  # Mark email as verified
                )
                # Assign admin to all organizations
                for org in organizations:
                    profile.organizations.add(org)
            
            admin.groups.add(admin_group)
            self.stdout.write(f"Created admin user: {admin.username}")
            return admin
        else:
            admin = User.objects.get(username='admin')
            # Make sure existing admin has organizations and verified email
            profile = admin.profile
            profile.email_verified = True  # Ensure email is verified
            profile.save()
            
            # Assign admin to all organizations
            for org in organizations:
                profile.organizations.add(org)
                
            self.stdout.write(f"Admin user already exists: {admin.username}")
            return admin
    
    def _create_superagent_user(self, organizations):
        """Create a superagent user"""
        superagent_group, _ = Group.objects.get_or_create(name='Superagent')
        if not User.objects.filter(username='superagent').exists():
            superagent = User.objects.create_user(
                username='superagent',
                email='superagent@example.com',
                password='superagent123',
                first_name='Super',
                last_name='Agent'
            )
            try:
                profile = superagent.profile
                profile.role = 'superagent'
                profile.is_approved = True
                profile.email_verified = True  # Mark email as verified
                profile.save()
                for org in organizations:
                    profile.organizations.add(org)
            except Exception as e:
                self.stdout.write(f"Error updating superagent profile: {str(e)}")
                profile = UserProfile.objects.create(
                    user=superagent,
                    role='superagent',
                    is_approved=True,
                    email_verified=True  # Mark email as verified
                )
                for org in organizations:
                    profile.organizations.add(org)
            superagent.groups.add(superagent_group)
            self.stdout.write(f"Created superagent user: {superagent.username}")
            return superagent
        else:
            superagent = User.objects.get(username='superagent')
            profile = superagent.profile
            profile.email_verified = True  # Ensure email is verified
            profile.save()
            for org in organizations:
                profile.organizations.add(org)
            self.stdout.write(f"Superagent user already exists: {superagent.username}")
            return superagent
    
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
                    profile.is_approved = True
                    profile.email_verified = True  # Mark email as verified
                    profile.save()
                    profile.organizations.add(org)
                    self.stdout.write(f"Added organization {org.name} to agent {agent.username}")
                except Exception as e:
                    self.stdout.write(f"Error updating agent profile: {str(e)}")
                    profile = UserProfile.objects.create(
                        user=agent,
                        role='agent',
                        is_approved=True,
                        email_verified=True  # Mark email as verified
                    )
                    profile.organizations.add(org)
                    self.stdout.write(f"Created new profile and added organization {org.name} to agent {agent.username}")
                
                agent.groups.add(agent_group)
                self.stdout.write(f"Created agent user: {agent.username} for {org.name}")
            else:
                agent = User.objects.get(username=username)
                # Make sure existing agent has organization
                profile = agent.profile
                profile.email_verified = True  # Ensure email is verified
                profile.save()
                profile.organizations.add(org)
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
                        profile.is_approved = True
                        profile.email_verified = True  # Mark email as verified
                        profile.save()
                        profile.organizations.add(org)
                        self.stdout.write(f"Added organization {org.name} to client {client.username}")
                    except Exception as e:
                        self.stdout.write(f"Error updating client profile: {str(e)}")
                        profile = UserProfile.objects.create(
                            user=client,
                            role='client',
                            is_approved=True,
                            email_verified=True  # Mark email as verified
                        )
                        profile.organizations.add(org)
                        self.stdout.write(f"Created new profile and added organization {org.name} to client {client.username}")
                    
                    client.groups.add(client_group)
                    self.stdout.write(f"Created client user: {client.username} for {org.name}")
                else:
                    client = User.objects.get(username=username)
                    # Make sure existing client has organization
                    profile = client.profile
                    profile.email_verified = True  # Ensure email is verified
                    profile.save()
                    profile.organizations.add(org)
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
            
            # Get the first organization from the client's organizations
            client_orgs = client.profile.organizations.all()
            if client_orgs.exists():
                organization = client_orgs.first()
            else:
                # Skip this ticket if client has no organization
                self.stdout.write(f"Skipping ticket: {data['title']} - Client has no organization")
                continue
            
            # Choose a status - weight towards new tickets
            status = random.choices(
                statuses,
                weights=[0.4, 0.3, 0.1, 0.1, 0.1],
                k=1
            )[0]
            
            # For in_progress/resolved/closed tickets, assign an agent
            assigned_to = None
            if status in ['in_progress', 'resolved', 'closed']:
                # Find agents who are members of this organization
                possible_agents = []
                for agent in agent_users:
                    if organization in agent.profile.organizations.all():
                        possible_agents.append(agent)
                
                if possible_agents:
                    assigned_to = random.choice(possible_agents)
            
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

    def _create_viewer_user(self):
        """Create a viewer user"""
        viewer_group, _ = Group.objects.get_or_create(name='Viewer')
        
        if not User.objects.filter(username='viewer').exists():
            viewer = User.objects.create_user(
                username='viewer',
                email='viewer@example.com',
                password='viewer123',
                first_name='Viewer',
                last_name='User'
            )
            
            # Update profile (should be created by signal)
            try:
                profile = viewer.profile
                profile.role = 'viewer'
                profile.is_approved = True
                profile.email_verified = True  # Mark email as verified
                profile.save()
            except Exception as e:
                self.stdout.write(f"Error updating viewer profile: {str(e)}")
                profile = UserProfile.objects.create(
                    user=viewer,
                    role='viewer',
                    is_approved=True,
                    email_verified=True  # Mark email as verified
                )
            
            viewer.groups.add(viewer_group)
            self.stdout.write(f"Created viewer user: {viewer.username}")
            return viewer
        else:
            viewer = User.objects.get(username='viewer')
            profile = viewer.profile
            profile.email_verified = True  # Ensure email is verified
            profile.save()
            self.stdout.write(f"Viewer user already exists: {viewer.username}")
            return viewer
    
    def _setup_view_permissions(self):
        """Create view permissions and assign them to groups"""
        self.stdout.write("Setting up view permissions...")
        
        # Create all view permissions
        views = [
            ('dashboard', 'Panel główny'),
            ('tickets', 'Zgłoszenia'),
            ('organizations', 'Organizacje'),
            ('approvals', 'Zatwierdzanie kont'),
            ('logs', 'Logi'),
            ('admin_panel', 'Panel admina'),
        ]
        
        for code, description in views:
            view, created = ViewPermission.objects.get_or_create(
                name=code,
                defaults={'description': description}
            )
            if created:
                self.stdout.write(f"Created view permission: {description}")
        
        # Set permissions for each group
        for group in Group.objects.all():
            # Clear existing permissions
            GroupViewPermission.objects.filter(group=group).delete()
            
            # Determine which views to grant based on group name
            if group.name == 'Admin':
                view_codes = ['dashboard', 'tickets', 'organizations', 'approvals', 'logs', 'admin_panel']
            elif group.name == 'Superagent':
                view_codes = ['dashboard', 'tickets', 'organizations', 'approvals', 'logs']
            elif group.name == 'Agent':
                view_codes = ['dashboard', 'tickets', 'organizations', 'approvals']
            elif group.name == 'Klient':
                view_codes = ['dashboard', 'tickets']
            elif group.name == 'Viewer':
                view_codes = ['tickets']
            else:
                # Unknown group - grant basic views
                view_codes = ['dashboard', 'tickets']
            
            # Grant permissions
            for code in view_codes:
                view = ViewPermission.objects.get(name=code)
                GroupViewPermission.objects.create(group=group, view=view)
                
            self.stdout.write(f"Set up view permissions for group: {group.name}")
