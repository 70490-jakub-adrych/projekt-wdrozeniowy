# Generated migration for TicketCalendarAssignment model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0004_set_resolved_at_for_existing'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TicketCalendarAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assigned_date', models.DateField(verbose_name='Data przypisania')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Data utworzenia')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notatki')),
                ('assigned_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='calendar_assignments_created', to=settings.AUTH_USER_MODEL, verbose_name='Przypisany przez')),
                ('assigned_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='calendar_assignments', to=settings.AUTH_USER_MODEL, verbose_name='Przypisany do')),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='calendar_assignments', to='crm.ticket', verbose_name='Zgłoszenie')),
            ],
            options={
                'verbose_name': 'Przypisanie ticketu do kalendarza',
                'verbose_name_plural': 'Przypisania ticketów do kalendarza',
                'ordering': ['assigned_date', 'created_at'],
                'unique_together': {('ticket', 'assigned_to')},
            },
        ),
    ]
