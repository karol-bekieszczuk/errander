from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime
from django.utils import timezone


class User(AbstractUser):
    email = models.EmailField(blank=False, null=False, unique=True, max_length=254, verbose_name='email address')
    token_generated_timestamp = models.DateTimeField(auto_now_add=True)
    account_activation_timestamp = models.DateTimeField(null=True)

    class Meta:
        permissions = [
            ('register_user', 'User can acces registration form and send invitaion to app'),
            ('view_index', 'User can view index of all app users'),
            ('view_any_user', 'User can view any user in profile page')
        ]

    def __str__(self):
        return self.username

    def token_expired(self):
        return self.token_generated_timestamp <= timezone.now() - datetime.timedelta(days=1)
