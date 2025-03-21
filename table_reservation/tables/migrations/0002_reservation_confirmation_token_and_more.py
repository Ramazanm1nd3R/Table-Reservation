# Generated by Django 5.1.6 on 2025-03-05 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tables', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='confirmation_token',
            field=models.CharField(blank=True, max_length=64, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='reservation',
            name='is_confirmed',
            field=models.BooleanField(default=False),
        ),
    ]
