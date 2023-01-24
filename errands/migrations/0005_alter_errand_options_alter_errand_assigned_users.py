# Generated by Django 4.1.5 on 2023-01-24 21:09

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('errands', '0004_alter_errand_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='errand',
            options={'permissions': [('create', 'User can create Errand object'), ('assign_users', 'User can add/remove users to Errand object'), ('can_list_and_view_every_errand', 'User can view every existing errand')]},
        ),
        migrations.AlterField(
            model_name='errand',
            name='assigned_users',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
