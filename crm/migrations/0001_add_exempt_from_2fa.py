# Generated migration - Add exempt_from_2fa field to GroupSettings

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        # Add your last existing migration here, or leave empty if this is after initial
        # Example: ('crm', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupsettings',
            name='exempt_from_2fa',
            field=models.BooleanField(
                default=False,
                help_text='Jeśli zaznaczone, użytkownicy w tej grupie nie będą musieli konfigurować uwierzytelniania dwuskładnikowego.',
                verbose_name='Zwolnij z 2FA'
            ),
        ),
    ]
