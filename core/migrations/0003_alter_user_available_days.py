# Generated by Django 5.2.1 on 2025-05-28 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='available_days',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
    ]
