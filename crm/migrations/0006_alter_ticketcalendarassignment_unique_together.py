# Generated migration for TicketCalendarAssignment constraint change

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0005_ticketcalendarassignment'),
    ]

    operations = [
        # First, remove the old unique_together constraint
        migrations.AlterUniqueTogether(
            name='ticketcalendarassignment',
            unique_together=set(),
        ),
        # Then, add the new unique_together constraint
        migrations.AlterUniqueTogether(
            name='ticketcalendarassignment',
            unique_together={('ticket', 'assigned_to')},
        ),
    ]
