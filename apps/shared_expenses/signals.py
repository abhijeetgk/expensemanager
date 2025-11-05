"""
Signals for shared expenses.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.shared_expenses.models import SharedExpenseSplit, Debt


@receiver(post_save, sender=SharedExpenseSplit)
def create_debt_on_split(sender, instance, created, **kwargs):
    """
    Create a debt record when a split is created.
    """
    if created and not instance.is_settled:
        # Only create debt if the split user is not the one who paid
        if instance.user != instance.shared_expense.paid_by:
            Debt.objects.get_or_create(
                creditor=instance.shared_expense.paid_by,
                debtor=instance.user,
                shared_expense_split=instance,
                defaults={
                    'amount': instance.amount,
                    'description': f"Split for: {instance.shared_expense.expense.description}",
                    'group': instance.shared_expense.group,
                    'created_by': instance.shared_expense.paid_by,
                }
            )

