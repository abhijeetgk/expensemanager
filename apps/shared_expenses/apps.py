"""
App configuration for shared expenses.
"""
from django.apps import AppConfig


class SharedExpensesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.shared_expenses'
    verbose_name = 'Shared Expenses'

    def ready(self):
        """Import signals when app is ready."""
        import apps.shared_expenses.signals

