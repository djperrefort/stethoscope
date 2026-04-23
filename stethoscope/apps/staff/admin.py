"""Admin dashboard configuration."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.http import HttpRequest
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from .models import User

__all__ = ['UserAdmin']

admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    """Admin configuration for the `User` model.

    Read/write access is restricted to superusers only.
    """

    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    readonly_fields = ('last_login', 'date_joined', 'created_at', 'updated_at')
    list_display_links = list_display

    fieldsets = (
        (None, {
            'fields': ('username', 'password'),
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email'),
        }),
        ('Account status', {
            'fields': ('is_active', 'is_superuser'),
        }),
        ('Timestamps', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
        }),
    )

    add_fieldsets = (
        (None, {
            'fields': ('username', 'password1', 'password2'),
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email'),
        }),
        ('Account status', {
            'fields': ('is_superuser',),
        }),
    )

    def has_view_permission(self, request: HttpRequest, obj: User | None = None) -> bool:
        """Allow viewing user accounts only for superusers."""

        return request.user.is_superuser

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Allow account creation only for superusers."""

        return request.user.is_superuser

    def has_change_permission(self, request: HttpRequest, obj: User | None = None) -> bool:
        """Allow editing user accounts only for superusers."""

        return request.user.is_superuser

    def has_delete_permission(self, request: HttpRequest, obj: User | None = None) -> bool:
        """Allow deleting user accounts only for superusers."""

        return request.user.is_superuser
