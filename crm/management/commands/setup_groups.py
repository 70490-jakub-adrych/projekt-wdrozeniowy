from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from crm.models import Ticket, Organization, UserProfile, TicketComment, TicketAttachment

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
