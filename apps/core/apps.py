"""
Core app configuration for Expense Manager.
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configuration for the core application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = 'Core'

    def ready(self) -> None:
        """
        Import signal handlers when the app is ready.
        """
        # Import signals here if needed
        pass

