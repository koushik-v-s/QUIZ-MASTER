from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('email', 'username')
    ordering = ('-date_joined',)
    readonly_fields = ('id', 'date_joined', 'last_login')
    fieldsets = (
        (None, {'fields': ('id', 'email', 'username', 'password')}),
        ('Role & Status', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('Profile', {'fields': ('avatar_url',)}),
        ('Timestamps', {'fields': ('date_joined', 'last_login')}),
    )
