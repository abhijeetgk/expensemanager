"""
App configuration for budgets.
"""
from django.apps import AppConfig


class BudgetsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.budgets'
    verbose_name = 'Budget Management'

    def ready(self):
        """Import signals when app is ready."""
        import apps.budgets.signals

