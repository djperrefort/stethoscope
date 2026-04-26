"""Application configuration and setup."""

from django.apps import AppConfig

__all__ = ['StaffAppConfig']


class StaffAppConfig(AppConfig):
    """General application configuration and metadata."""

    name = 'stethoscope.apps.staff'

    def ready(self) -> None:
        """Register application signal handlers."""

        from django.db.models.signals import post_migrate

        post_migrate.connect(_create_default_superuser, sender=self)


def _create_default_superuser(*args, **kwargs) -> None:
    """Create the default admin superuser if no users exist."""

    from .models import User

    if not User.objects.exists():
        User.objects.create_superuser(username='admin', password='admin')
