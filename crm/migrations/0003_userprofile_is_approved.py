from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0002_remove_deal_contact_remove_deal_created_by_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='is_approved',
            field=models.BooleanField(default=False, verbose_name='Zatwierdzony'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='role',
            field=models.CharField(choices=[('admin', 'Administrator'), ('agent', 'Agent'), ('client', 'Klient')], default='client', max_length=20, verbose_name='Rola'),
        ),
        migrations.AlterField(
            model_name='activitylog',
            name='action_type',
            field=models.CharField(choices=[('login', 'Zalogowanie'), ('logout', 'Wylogowanie'), ('ticket_created', 'Utworzenie zgłoszenia'), ('ticket_updated', 'Aktualizacja zgłoszenia'), ('ticket_commented', 'Komentarz do zgłoszenia'), ('ticket_resolved', 'Rozwiązanie zgłoszenia'), ('ticket_closed', 'Zamknięcie zgłoszenia'), ('ticket_reopened', 'Ponowne otwarcie zgłoszenia')], max_length=30, verbose_name='Typ akcji'),
        ),
    ]
