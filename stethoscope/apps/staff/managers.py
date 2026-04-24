"""Database managers for common table-level operations."""

import typing

from django.contrib.auth.models import BaseUserManager

if typing.TYPE_CHECKING:
    from .models import User

__all__ = ['UserManager']


class UserManager(BaseUserManager):
    """Object manager for the `User` model."""

    def create_user(self, username: str, password: str | None = None, **extra_fields) -> 'User':
        """Create and return a new user account.

        Args:
            username: The user's login identifier.
            password: The plaintext password to hash and store.
            **extra_fields: Additional field values passed to the model constructor.

        Returns:
            The newly created `User` instance.
        """

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username: str, password: str | None = None, **extra_fields) -> 'User':
        """Create and return a new user account with superuser privileges.

        Args:
            username: The user's login identifier.
            password: The plaintext password to hash and store.
            **extra_fields: Additional field values passed to the model constructor.

        Returns:
            The newly created `User` instance with superuser privileges.
        """

        extra_fields['is_superuser'] = True
        return self.create_user(username, password, **extra_fields)
