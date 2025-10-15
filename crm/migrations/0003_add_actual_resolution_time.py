# Generated migration - Add actual_resolution_time field to Ticket

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0002_add_show_navbar'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='actual_resolution_time',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Podaj rzeczywisty czas poświęcony na wykonanie zgłoszenia w godzinach',
                max_digits=6,
                null=True,
                verbose_name='Rzeczywisty czas wykonania (godziny)'
            ),
        ),
    ]
