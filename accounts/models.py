from django.db import models
from django.utils import timezone
from django.contrib import admin
from django.contrib.auth.models import User


class ErranderUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    uid = models.CharField(max_length=10)
    token = models.CharField(max_length=64)
    token_generated_timestamp = models.DateTimeField(auto_now_add=True)
    account_activation_timestamp = models.DateTimeField(default=None)
    reset_password_timestamp = models.DateTimeField(default=None)
