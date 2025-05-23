# Generated by Django 3.2.25 on 2025-04-18 13:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('crm', '0003_auto_20250418_1315'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activitylog',
            name='action_type',
            field=models.CharField(choices=[('login', 'Zalogowanie'), ('logout', 'Wylogowanie'), ('ticket_created', 'Utworzenie'), ('ticket_updated', 'Aktualizacja'), ('ticket_commented', 'Komentarz'), ('ticket_resolved', 'Rozwiązanie'), ('ticket_closed', 'Zamknięcie'), ('ticket_reopened', 'Wznowienie'), ('preferences_updated', 'Aktualizacja preferencji')], max_length=30, verbose_name='Typ akcji'),
        ),
        migrations.CreateModel(
            name='UserPreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('show_closed_tickets', models.BooleanField(default=False, verbose_name='Pokaż zamknięte zgłoszenia')),
                ('items_per_page', models.IntegerField(default=10, verbose_name='Elementów na stronę')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='preferences', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Preferencja użytkownika',
                'verbose_name_plural': 'Preferencje użytkownika',
            },
        ),
    ]
