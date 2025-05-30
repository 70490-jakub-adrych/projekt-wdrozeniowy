from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from crm.models import Organization, Ticket, TicketComment, TicketAttachment

class Command(BaseCommand):
    help = 'Clears all demo data from the system'

    def handle(self, *args, **kwargs):
        self.stdout.write('Clearing demo data...')

        # Delete all tickets and related data
        TicketAttachment.objects.all().delete()
        self.stdout.write('Deleted all ticket attachments')
        
        TicketComment.objects.all().delete()
        self.stdout.write('Deleted all ticket comments')
        
        Ticket.objects.all().delete()
        self.stdout.write('Deleted all tickets')

        # Delete demo organizations
        Organization.objects.filter(
            name__in=[
                'Firma IT Solutions',
                'Marketing Pro',
                'E-commerce Shop'
            ]
        ).delete()
        self.stdout.write('Deleted demo organizations')

        # Delete demo users (except admin)
        demo_usernames = [
            'viewer',
            'agent1', 'agent2', 'agent3',
            'client1', 'client2', 'client3', 'client4', 'client5', 'client6'
        ]
        User.objects.filter(username__in=demo_usernames).delete()
        self.stdout.write('Deleted demo users')

        # Delete demo groups
        Group.objects.filter(
            name__in=['Agent', 'Klient', 'Viewer']
        ).delete()
        self.stdout.write('Deleted demo groups')

        self.stdout.write(self.style.SUCCESS('Successfully cleared all demo data')) 