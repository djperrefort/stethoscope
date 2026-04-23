"""ORM layer used to define the database schema and facilitate queries."""

from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager

__all__ = ['User']


class User(AbstractUser):
    """Application user account.

    All user accounts are automatically elevated to staff status.
    """

    class Meta:
        """Database model settings."""

        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
        ]

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    @property
    def is_staff(self) -> bool:
        """Return True for any active user, granting staff-level access."""

        return self.is_active

    @is_staff.setter
    def is_staff(self, value: bool) -> None:
        """Ignore attempts to modify staff status."""

    def has_perm(self, perm: str, obj: object = None) -> bool:
        """Return `True` for any active user, granting all object-level permissions."""

        return self.is_active

    def has_module_perms(self, app_label: str) -> bool:
        """Return `True` for any active user, granting access to all admin modules."""

        return self.is_active

    def __str__(self) -> str:  # pragma: nocover
        return self.username
