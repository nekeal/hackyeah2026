from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from hackyeah2026.accounts.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    pass
