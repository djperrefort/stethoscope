"""ORM layer used to define the database schema and facilitate queries."""

import secrets

from django.db import models
from django.utils import timezone

from stethoscope.apps.licensing.shortcuts import hash_token

__all__ = [
    'Application',
    'Customer',
    'HeartBeat',
    'LicenseToken',
]


class Customer(models.Model):
    """Customer contact information."""

    class Meta:
        """Database model settings."""

        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['email']),
        ]

    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    notes = models.TextField(blank=True)

    # Billing address
    billing_address_line_1 = models.CharField(max_length=255, blank=True)
    billing_address_line_2 = models.CharField(max_length=255, blank=True)
    billing_city = models.CharField(max_length=100, blank=True)
    billing_state = models.CharField(max_length=100, blank=True)
    billing_postal_code = models.CharField(max_length=20, blank=True)
    billing_country = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:  # pragma: nocover
        return self.name


class Application(models.Model):
    """A licensable software product offered to customers."""

    class Meta:
        """Database model settings."""

        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['version']),
        ]

        constraints = [
            models.UniqueConstraint(fields=['name', 'version'], name='unique_application_name_version'),
        ]

    name = models.CharField(max_length=255)
    version = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:  # pragma: nocover
        return self.name


class LicenseToken(models.Model):
    """A time-bounded access token granting a customer the right to use an application."""

    class Meta:
        """Database model settings."""

        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['customer']),
            models.Index(fields=['application']),
            models.Index(fields=['starts_at', 'expires_at']),
        ]

    token = models.CharField(max_length=64, editable=False)
    token_plain = models.CharField(max_length=64, null=True, editable=False)
    retrieve_id = models.CharField(max_length=64, null=True)
    starts_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    retrieved_at = models.DateTimeField(null=True)

    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='license_tokens')
    application = models.ForeignKey('Application', on_delete=models.CASCADE, related_name='license_tokens')

    @property
    def is_expired(self) -> bool:
        """Return whether the license token is expired."""

        return self.expires_at is not None and timezone.now() > self.expires_at

    @property
    def is_active(self) -> bool:
        """Return whether the license token is active."""

        now = timezone.now()
        not_yet_expired = self.expires_at is None or now <= self.expires_at
        return self.starts_at <= now and not_yet_expired

    @property
    def is_retrieved(self) -> bool:
        """Return whether the license token has been retrieved by the user."""

        return bool(self.retrieved_at)

    def mark_retrieved(self) -> None:
        """Mark the license token as retrieved."""

        self.token_plain = None
        self.retrieve_id = None
        self.retrieved_at = timezone.now()
        self.save()

    def save(self, *args, **kwargs) -> None:
        """Save the token object.

         When a new token is created, the token value and retrieval ID are set
         using dynamically generated value and can not be set manually.
         """

        if self.pk is None:
            token_plain = secrets.token_hex(32)
            self.token = hash_token(token_plain)
            self.token_plain = token_plain
            self.retrieve_id = secrets.token_hex(32)

        super().save(*args, **kwargs)

    def __str__(self) -> str:  # pragma: nocover
        return f'Token {self.id}'


class HeartBeat(models.Model):
    """A periodic check-in from a deployment running under a license token."""

    class Meta:
        """Database model settings."""

        indexes = [
            models.Index(fields=['ip']),
            models.Index(fields=['uuid']),
            models.Index(fields=['created_at']),
            models.Index(fields=['ip', 'created_at']),
            models.Index(fields=['uuid', 'created_at']),
            models.Index(fields=['license_token', 'created_at']),
        ]

    ip = models.GenericIPAddressField()
    uuid = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)

    license_token = models.ForeignKey('LicenseToken', on_delete=models.CASCADE, related_name='heartbeats')

    def __str__(self) -> str:  # pragma: nocover
        return f'Heartbeat {self.id}'
