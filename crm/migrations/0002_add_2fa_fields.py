from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0001_initial'),  # Update this to match your actual most recent migration
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='ga_enabled',
            field=models.BooleanField(default=False, verbose_name='2FA włączone'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='ga_enabled_on',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Data włączenia 2FA'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='ga_last_authenticated',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Ostatnie uwierzytelnienie 2FA'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='ga_recovery_hash',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='Hash kodu odzyskiwania'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='ga_recovery_last_generated',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Ostatnia generacja kodu odzyskiwania'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='ga_secret_key',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='Klucz tajny 2FA'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='device_fingerprint',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Odcisk urządzenia'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='trusted_ip',
            field=models.GenericIPAddressField(blank=True, null=True, verbose_name='Zaufany adres IP'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='trusted_until',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Zaufany do'),
        ),
        migrations.AddIndex(
            model_name='userprofile',
            index=models.Index(fields=['trusted_until'], name='idx_trusted_until'),
        ),
        migrations.AddIndex(
            model_name='userprofile',
            index=models.Index(fields=['ga_enabled'], name='idx_ga_enabled'),
        ),
    ]
