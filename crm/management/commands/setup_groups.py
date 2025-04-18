from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from crm.models import Ticket, Organization, UserProfile

class Command(BaseCommand):
    help = 'Creates user groups and assigns permissions'

    def handle(self, *args, **kwargs):
        # Get or create the three groups
        admin_group, created_admin = Group.objects.get_or_create(name='Admin')
        agent_group, created_mod = Group.objects.get_or_create(name='Agent')
        client_group, created_client = Group.objects.get_or_create(name='Klient')
        
        # Clear existing permissions for a fresh start
        admin_group.permissions.clear()
        agent_group.permissions.clear()
        client_group.permissions.clear()
        
        # Get content types
        ticket_ct = ContentType.objects.get_for_model(Ticket)
        org_ct = ContentType.objects.get_for_model(Organization)
        profile_ct = ContentType.objects.get_for_model(UserProfile)
        
        # Define permissions for each group
        
        # Admin permissions (full access)
        admin_permissions = Permission.objects.filter(
            content_type__in=[ticket_ct, org_ct, profile_ct]
        )
        admin_group.permissions.add(*admin_permissions)
        
        # Agent permissions
        # Can view all models, can change and add tickets
        agent_permissions = Permission.objects.filter(
            content_type=ticket_ct,
            codename__in=[
                'add_ticket', 'change_ticket', 'view_ticket',
                'add_ticketcomment', 'change_ticketcomment'
            ]
        )
        agent_permissions |= Permission.objects.filter(
            content_type__in=[org_ct, profile_ct],
            codename__startswith='view_'
        )
        agent_permissions |= Permission.objects.filter(
            content_type=profile_ct,
            codename__in=['change_userprofile']
        )
        agent_group.permissions.add(*agent_permissions)
        
        # Client permissions
        # Can only view and create tickets, no admin access
        client_permissions = Permission.objects.filter(
            content_type=ticket_ct,
            codename__in=['add_ticket', 'view_ticket']
        )
        client_group.permissions.add(*client_permissions)
        
        # Report results
        if created_admin:
            self.stdout.write(self.style.SUCCESS('Created Admin group'))
        else:
            self.stdout.write(self.style.SUCCESS('Updated Admin group permissions'))

        if created_mod:
            self.stdout.write(self.style.SUCCESS('Created Agent group'))
        else:
            self.stdout.write(self.style.SUCCESS('Updated Agent group permissions'))
            
        if created_client:
            self.stdout.write(self.style.SUCCESS('Created Klient group'))
        else:
            self.stdout.write(self.style.SUCCESS('Updated Klient group permissions'))
