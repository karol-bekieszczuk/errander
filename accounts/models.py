from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    uid = models.CharField(max_length=10)
    token = models.CharField(max_length=64)
    token_generated_timestamp = models.DateTimeField(auto_now_add=True)
    account_activation_timestamp = models.DateTimeField(null=True)
    reset_password_timestamp = models.DateTimeField(null=True)

    def __str__(self):
        return self.username
