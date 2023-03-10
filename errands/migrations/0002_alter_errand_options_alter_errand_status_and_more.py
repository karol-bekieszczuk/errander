# Generated by Django 4.1.2 on 2023-01-14 23:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('errands', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='errand',
            options={'permissions': [('create', 'User can create Errand object'), ('assign_users', 'User can add users to Errand object')]},
        ),
        migrations.AlterField(
            model_name='errand',
            name='status',
            field=models.IntegerField(choices=[(0, 'Discarded'), (1, 'Pending'), (2, 'Accepted'), (3, 'In progress'), (4, 'Done')], default=1),
        ),
        migrations.AlterField(
            model_name='historicalerrand',
            name='status',
            field=models.IntegerField(choices=[(0, 'Discarded'), (1, 'Pending'), (2, 'Accepted'), (3, 'In progress'), (4, 'Done')], default=1),
        ),
    ]
