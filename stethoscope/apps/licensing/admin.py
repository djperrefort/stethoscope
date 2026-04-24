"""Admin dashboard configuration."""

from typing import Literal

from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import Application, Customer, HeartBeat, LicenseToken

__all__ = [
    'ApplicationAdmin',
    'CustomerAdmin',
    'HeartBeatAdmin',
    'LicenseTokenAdmin',
]


class HeartBeatInline(TabularInline):
    """An inline table of `HeartBeat` objects."""

    model = HeartBeat
    extra = 0
    readonly_fields = ('ip', 'uuid', 'created_at')
    fields = ('ip', 'uuid', 'created_at')
    ordering = ('-created_at',)

    def has_add_permission(self, *args, **kwargs) -> Literal[False]:
        """Disable record creation."""

        return False


class LicenseTokenInline(TabularInline):
    """An inline table of `LicenseToken` objects."""

    model = LicenseToken
    extra = 0
    readonly_fields = ('token', 'starts_at', 'expires_at', 'created_at', 'updated_at')
    fields = ('token', 'customer', 'application', 'starts_at', 'expires_at')
    autocomplete_fields = ('customer', 'application')


@admin.register(Application)
class ApplicationAdmin(ModelAdmin):
    """Admin configuration for the `Application` model."""

    list_display = ('name', 'version', 'url', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'version', 'description', 'url')
    readonly_fields = ('created_at', 'updated_at')
    inlines = (LicenseTokenInline,)
    list_display_links = list_display

    fieldsets = (
        (None, {
            'fields': ('name', 'version', 'description', 'url'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )


@admin.register(Customer)
class CustomerAdmin(ModelAdmin):
    """Admin configuration for the `Customer` model."""

    list_display = ('name', 'website', 'created_at')
    list_filter = ('billing_country', 'billing_state', 'created_at')
    search_fields = ('name', 'email', 'phone', 'website')
    readonly_fields = ('created_at', 'updated_at')
    inlines = (LicenseTokenInline,)
    list_display_links = list_display

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'email',
                'phone',
                'website',
                'notes'
            ),
        }),
        ('Billing Address', {
            'fields': (
                'billing_address_line_1',
                'billing_address_line_2',
                'billing_city',
                'billing_state',
                'billing_postal_code',
                'billing_country',
            ),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )


@admin.register(HeartBeat)
class HeartBeatAdmin(ModelAdmin):
    """Admin configuration for the `HeartBeat` model."""

    list_display = ('uuid', 'ip', 'license_token', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('ip', 'uuid', 'license_token__token')
    readonly_fields = ('ip', 'uuid', 'license_token', 'created_at')
    list_display_links = list_display

    fieldsets = (
        (None, {
            'fields': ('license_token', 'ip', 'uuid', 'created_at'),
        }),
    )

    def has_change_permission(self, *args, **kwargs) -> Literal[False]:
        """Disable record modification."""

        return False

    def has_add_permission(self, *args, **kwargs) -> Literal[False]:
        """Disable record creation."""

        return False


@admin.register(LicenseToken)
class LicenseTokenAdmin(ModelAdmin):
    """Admin configuration for the `LicenseToken` model."""

    list_display = ('customer', 'application', 'starts_at', 'expires_at', 'created_at')
    list_filter = ('application', 'starts_at', 'expires_at', 'created_at')
    search_fields = ('customer__name', 'customer__email', 'application__name')
    readonly_fields = ('created_at', 'updated_at', 'retrieved_at', 'retrieve_id')
    autocomplete_fields = ('customer', 'application')
    inlines = (HeartBeatInline,)
    list_display_links = list_display

    fieldsets = (
        (None, {
            'fields': ('customer', 'application', 'retrieve_id'),
        }),
        ('Validity Window', {
            'fields': ('starts_at', 'expires_at'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'retrieved_at'),
        }),
    )
