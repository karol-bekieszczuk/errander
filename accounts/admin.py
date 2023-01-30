from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import User


class CustomUserAdmin(ModelAdmin):
    # model = User
    list_display = ['email', 'username', ]
    fieldsets = (
        (None, {
            'fields': ('username', 'email', 'password')
        }),
    )


admin.site.register(User, CustomUserAdmin)
