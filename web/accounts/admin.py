from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
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

    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {
            'fields': ('email',)
        }),
    )


admin.site.register(User, CustomUserAdmin)
