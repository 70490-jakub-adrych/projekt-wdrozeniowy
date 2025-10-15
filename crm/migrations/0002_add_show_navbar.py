# Generated migration - Add show_navbar field to GroupSettings

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0001_add_exempt_from_2fa'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupsettings',
            name='show_navbar',
            field=models.BooleanField(
                default=True,
                help_text='Jeśli zaznaczone, użytkownicy w tej grupie będą widzieć górny pasek nawigacyjny. Jeśli odznaczone, pasek będzie ukryty.',
                verbose_name='Pokaż pasek nawigacyjny'
            ),
        ),
    ]
