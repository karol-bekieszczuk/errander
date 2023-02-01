from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models import User


class CustomUserAdmin(ModelAdmin):
    model = User
    list_display = ['email', 'username', ]
    fieldsets = (
        (None, {
            'fields': ('username', 'first_name', 'last_name', 'email', 'password', )
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions', )
        }),
    )
    filter_horizontal = ('groups', 'user_permissions', )


admin.site.register(User, CustomUserAdmin)
