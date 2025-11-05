"""
Signals for budget tracking and alerts.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.transactions.models import Expense


@receiver(post_save, sender=Expense)
def check_budget_on_expense(sender, instance, created, **kwargs):
    """
    Check budgets when an expense is created or updated.
    
    This signal automatically checks if any budgets are affected
    by the new or updated expense and sends alerts if needed.
    """
    if instance.status == 'COMPLETED' and not instance.is_deleted:
        from apps.budgets.models import Budget
        from django.utils import timezone
        
        # Find budgets that could be affected by this expense
        budgets = Budget.objects.filter(
            user=instance.created_by,
            category=instance.category,
            start_date__lte=instance.transaction_date,
            end_date__gte=instance.transaction_date,
            status='ACTIVE',
            is_deleted=False
        )
        
        # Check each affected budget for alerts
        for budget in budgets:
            budget.check_and_send_alerts()

