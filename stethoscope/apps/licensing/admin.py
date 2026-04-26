"""Admin dashboard configuration."""

from typing import Literal

from django.conf import settings
from django.contrib import admin
from django.urls import reverse
from unfold.admin import ModelAdmin, TabularInline

from .models import Application, Customer, Deployment, HeartBeat, LicenseToken

__all__ = [
    'ApplicationAdmin',
    'CustomerAdmin',
    'DeploymentAdmin',
    'HeartBeatAdmin',
    'LicenseTokenAdmin',
]


class DeploymentInline(TabularInline):
    """An inline table of `Deployment` objects."""

    extra = 0
    model = Deployment
    fields = ('identifier', 'activated_at')
    readonly_fields = fields
    ordering = ('-activated_at',)

    def has_add_permission(self, *args, **kwargs) -> Literal[False]:
        """Disable record creation."""

        return False


class HeartBeatInline(TabularInline):
    """An inline table of `HeartBeat` objects."""

    extra = 0
    model = HeartBeat
    fields = ('ip', 'uuid', 'created_at')
    readonly_fields = fields
    ordering = ('-created_at',)

    def has_add_permission(self, *args, **kwargs) -> Literal[False]:
        """Disable record creation."""

        return False


class LicenseTokenInline(TabularInline):
    """An inline table of `LicenseToken` objects."""

    extra = 0
    model = LicenseToken
    fields = ('customer', 'application', 'starts_at', 'expires_at', 'enabled')
    readonly_fields = fields


@admin.register(Application)
class ApplicationAdmin(ModelAdmin):
    """Admin configuration for the `Application` model."""

    list_display = ('name', 'version', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'version', 'description', 'url')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = (LicenseTokenInline,)
    list_display_links = list_display

    fieldsets = (
        (None, {
            'fields': ('name', 'version', 'description'),
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
    ordering = ('name',)
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


@admin.register(Deployment)
class DeploymentAdmin(ModelAdmin):
    """Admin configuration for the `Deployment` model."""

    list_display = ('identifier', 'license_token', 'activated_at')
    list_filter = ('activated_at',)
    search_fields = ('identifier', 'license_token__token')
    ordering = ('-activated_at',)
    readonly_fields = ('identifier', 'license_token', 'activated_at')
    list_display_links = list_display

    fieldsets = (
        (None, {
            'fields': ('license_token', 'identifier', 'activated_at'),
        }),
    )

    def has_change_permission(self, *args, **kwargs) -> Literal[False]:
        """Disable record modification."""

        return False

    def has_add_permission(self, *args, **kwargs) -> Literal[False]:
        """Disable record creation."""

        return False


@admin.register(HeartBeat)
class HeartBeatAdmin(ModelAdmin):
    """Admin configuration for the `HeartBeat` model."""

    list_display = ('uuid', 'ip', 'license_token', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('ip', 'uuid', 'license_token__token')
    ordering = ('created_at',)
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

    list_display = ('customer', 'application', 'starts_at', 'expires_at', 'enabled', 'created_at')
    list_filter = ('application', 'starts_at', 'expires_at', 'created_at')
    search_fields = ('customer__name', 'customer__email', 'application__name')
    ordering = ('customer', 'application')
    autocomplete_fields = ('customer', 'application')
    inlines = (DeploymentInline, HeartBeatInline)
    list_display_links = list_display

    fieldsets = (
        (None, {
            'fields': ('customer', 'application', 'retrieval_url'),
        }),
        ('Validity Window', {
            'fields': ('enabled', 'starts_at', 'expires_at'),
        }),
        ('Deployments', {
            'fields': ('max_deployments', 'allow_deactivation'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'retrieved_at'),
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        """Return the list of readonly fields for the model.

        The `customer` and `application` are writable on record creation
        but marked as readonly for existing records.
        """

        always_readonly = ('created_at', 'updated_at', 'retrieved_at', 'retrieval_url')
        readonly_on_edit = always_readonly + ('customer', 'application')

        if obj is None:
            return always_readonly

        return readonly_on_edit

    def retrieval_url(self, obj: LicenseToken) -> str:
        """Return the retrieve endpoint URL for this token's retrieve ID as a hyperlink.

        Args:
            obj: The LicenseToken instance being displayed.

        Returns:
            An HTML anchor tag pointing to the retrieve endpoint, or a dash if no
            retrieve ID has been assigned.
        """

        if obj.retrieved_at:
            return 'Token has already been retrieved.'

        if not obj.retrieve_id:
            return '-'

        path = reverse('licensing:retrieve', kwargs={'retrieve_id': obj.retrieve_id})
        return settings.SERVER_URL.rstrip('/') + path
