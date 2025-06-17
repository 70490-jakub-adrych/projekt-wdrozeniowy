from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0002_add_2fa_fields'),  # Make sure this points to your last migration
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='ga_enabled',
            field=models.BooleanField(default=False, verbose_name='2FA włączone'),
        ),
        # Run SQL to update existing rows
        migrations.RunSQL(
            "UPDATE crm_userprofile SET ga_enabled = FALSE WHERE ga_enabled IS NULL;",
            reverse_sql=migrations.RunSQL.noop
        ),
    ]
