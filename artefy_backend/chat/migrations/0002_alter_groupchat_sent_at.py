# Generated by Django 5.1.5 on 2025-01-30 02:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupchat',
            name='sent_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
