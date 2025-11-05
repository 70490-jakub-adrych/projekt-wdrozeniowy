# Generated manually on 2025-10-16

from django.db import migrations
from django.utils import timezone


def set_resolved_at_for_existing_tickets(apps, schema_editor):
    """
    Ustawia resolved_at na obecną datę dla wszystkich ticketów 
    które są resolved ale nie mają ustawionej daty rozwiązania.
    """
    Ticket = apps.get_model('crm', 'Ticket')
    
    resolved_tickets = Ticket.objects.filter(status='resolved', resolved_at__isnull=True)
    count = resolved_tickets.count()
    
    if count > 0:
        resolved_tickets.update(resolved_at=timezone.now())
        print(f"✅ Ustawiono resolved_at dla {count} istniejących ticketów resolved")
    else:
        print("ℹ️ Brak ticketów resolved bez daty rozwiązania")


def reverse_set_resolved_at(apps, schema_editor):
    """
    Cofnięcie migracji - wyczyść resolved_at dla ticketów resolved
    """
    Ticket = apps.get_model('crm', 'Ticket')
    Ticket.objects.filter(status='resolved').update(resolved_at=None)


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0002_add_actual_resolution_time_manually'),
    ]

    operations = [
        migrations.RunPython(
            set_resolved_at_for_existing_tickets,
            reverse_set_resolved_at
        ),
    ]
