from django.db import models
from accounts.models import User
from simple_history.models import HistoricalRecords


class Errand(models.Model):
    STATUSES = (
        (0, 'Discarded'),
        (1, 'Pending'),
        (2, 'Accepted'),
        (3, 'In progress'),
        (4, 'Done')
    )

    assigned_users = models.ManyToManyField(User)
    name = models.CharField(max_length=50, null=False)
    description = models.CharField(max_length=200, null=False)
    status = models.IntegerField(default=1, choices=STATUSES, null=False)
    address = models.CharField(max_length=200, null=False)
    geolocation = models.CharField(max_length=200, null=False)
    history = HistoricalRecords(
        m2m_fields=[assigned_users]
    )

    class Meta:
        permissions = [
            ("create", "User can create Errand object"),
            ("assign_users", "User can add users to Errand object")
        ]

    def __str__(self):
        return f'Name: {self.name}\nDesc: {self.description}'

