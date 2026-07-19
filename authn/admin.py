from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_superuser",
        "email_verified",
    )
    search_fields = ("username", "email", "first_name", "last_name")
    list_filter = ("is_staff", "is_superuser", "email_verified")
    ordering = ("username",)
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {"fields": ("email_verified", "avatar_url", "phone_number")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {"fields": ("email_verified", "avatar_url", "phone_number")}),
    )
