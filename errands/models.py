from django.db import models
from accounts.models import User
from simple_history.models import HistoricalRecords


class Errand(models.Model):
    STATUSES = (
        (0, 'Discarded'),
        (1, 'Started'),
        (2, 'In progress'),
        (3, 'Done')
    )

    assigned_users = models.ManyToManyField(User)
    name = models.CharField(max_length=50, null=False)
    description = models.CharField(max_length=200, null=False)
    status = models.IntegerField(default=1, choices=STATUSES, null=False)
    history = HistoricalRecords(
        m2m_fields=[assigned_users]
    )

    def __str__(self):
        return f'Name: {self.name}\nDesc:{self.description}'
