"""
Accounts app configuration for user management.
"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Configuration for the accounts application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    verbose_name = 'User Accounts'

    def ready(self) -> None:
        """Import signals when the app is ready."""
        from . import signals  # noqa

