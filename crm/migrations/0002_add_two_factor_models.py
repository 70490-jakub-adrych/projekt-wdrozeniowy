# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('crm', '0001_initial'),  # Replace with your last migration
    ]

    operations = [
        migrations.CreateModel(
            name='TwoFactorAuth',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ga_enabled', models.BooleanField(default=False, verbose_name='Google Authenticator aktywny')),
                ('ga_secret', models.CharField(blank=True, max_length=32, null=True, verbose_name='Sekret Google Authenticator')),
                ('ga_enabled_on', models.DateTimeField(blank=True, null=True, verbose_name='Data włączenia 2FA')),
                ('ga_last_authenticated', models.DateTimeField(blank=True, null=True, verbose_name='Ostatnia weryfikacja 2FA')),
                ('recovery_code_hash', models.CharField(blank=True, max_length=128, null=True, verbose_name='Hash kodu odzyskiwania')),
                ('recovery_code_generated', models.DateTimeField(blank=True, null=True, verbose_name='Data wygenerowania kodu odzyskiwania')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='two_factor', to='auth.user')),
            ],
            options={
                'verbose_name': 'Uwierzytelnianie dwuskładnikowe',
                'verbose_name_plural': 'Uwierzytelnianie dwuskładnikowe',
            },
        ),
        migrations.CreateModel(
            name='TrustedDevice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_identifier', models.CharField(max_length=255, verbose_name='Identyfikator urządzenia')),
                ('ip_address', models.GenericIPAddressField(verbose_name='Adres IP')),
                ('user_agent', models.TextField(verbose_name='User Agent')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('last_used', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trusted_devices', to='auth.user')),
            ],
            options={
                'verbose_name': 'Zaufane urządzenie',
                'verbose_name_plural': 'Zaufane urządzenia',
                'unique_together': {('user', 'device_identifier')},
            },
        ),
    ]
