from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime
from django.utils import timezone


class User(AbstractUser):
    uid = models.CharField(max_length=10)
    token = models.CharField(max_length=64)
    token_generated_timestamp = models.DateTimeField(auto_now_add=True)
    account_activation_timestamp = models.DateTimeField(null=True)
    reset_password_timestamp = models.DateTimeField(null=True)

    class Meta:
        permissions = [
            ("register_user", "User can acces registration form and send invitaion to app"),
        ]

    def __str__(self):
        return self.username

    def token_expired(self):
        return self.token_generated_timestamp <= timezone.now() - datetime.timedelta(days=1)
