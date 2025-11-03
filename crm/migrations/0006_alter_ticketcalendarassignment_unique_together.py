# Generated migration for TicketCalendarAssignment constraint change

from django.db import migrations


def drop_old_indexes(apps, schema_editor):
    """Drop problematic indexes manually before altering unique_together"""
    if schema_editor.connection.vendor == 'mysql':
        with schema_editor.connection.cursor() as cursor:
            # Drop the old unique constraint
            try:
                cursor.execute(
                    "ALTER TABLE crm_ticketcalendarassignment "
                    "DROP INDEX crm_ticketcalendarassign_ticket_id_assigned_to_id_7f445d8d_uniq"
                )
            except Exception:
                pass  # Index might not exist
            
            # Drop any duplicate indexes that might exist
            try:
                cursor.execute(
                    "ALTER TABLE crm_ticketcalendarassignment "
                    "DROP INDEX crm_ticketcalendarassignment_ticket_id_e1ad8f37"
                )
            except Exception:
                pass  # Index might not exist
            
            try:
                cursor.execute(
                    "ALTER TABLE crm_ticketcalendarassignment "
                    "DROP INDEX crm_ticketcalendarassignment_assigned_to_id_6c8b0e5f"
                )
            except Exception:
                pass  # Index might not exist


def reverse_indexes(apps, schema_editor):
    """Recreate original indexes if needed"""
    pass  # We'll let Django handle the reverse


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0005_ticketcalendarassignment'),
    ]

    operations = [
        # First, manually drop old indexes
        migrations.RunPython(drop_old_indexes, reverse_indexes),
        # Then, add the new unique_together constraint
        migrations.AlterUniqueTogether(
            name='ticketcalendarassignment',
            unique_together={('ticket', 'assigned_to')},
        ),
    ]
