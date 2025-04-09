# Generated by Django 3.2.25 on 2025-04-09 18:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('company', models.CharField(blank=True, max_length=100)),
                ('lead_source', models.CharField(choices=[('website', 'Website'), ('phone', 'Phone Inquiry'), ('referral', 'Referral'), ('social', 'Social Media'), ('other', 'Other')], default='other', max_length=20)),
                ('status', models.CharField(choices=[('new', 'New'), ('contacted', 'Contacted'), ('active', 'Active'), ('inactive', 'Inactive')], default='new', max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contacts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('website', models.URLField(blank=True)),
                ('address', models.TextField(blank=True)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='organizations', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Deal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('value', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('stage', models.CharField(choices=[('lead', 'Lead'), ('qualified', 'Qualified'), ('proposal', 'Proposal'), ('negotiation', 'Negotiation'), ('closed_won', 'Closed Won'), ('closed_lost', 'Closed Lost')], default='lead', max_length=20)),
                ('expected_close_date', models.DateField(blank=True, null=True)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deals', to='crm.contact')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deals', to=settings.AUTH_USER_MODEL)),
                ('organization', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='deals', to='crm.organization')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
