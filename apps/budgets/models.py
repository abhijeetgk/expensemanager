"""
Budget models for tracking and alerting.

Features:
- Monthly/yearly budget tracking
- Category-wise budgets
- Budget alerts and notifications
- Spending analysis
"""

from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from apps.core.mixins import BaseModel, SoftDeleteMixin


class BudgetPeriod:
    """Enum-like class for budget periods."""
    
    WEEKLY = 'WEEKLY'
    MONTHLY = 'MONTHLY'
    QUARTERLY = 'QUARTERLY'
    YEARLY = 'YEARLY'
    CUSTOM = 'CUSTOM'
    
    CHOICES = [
        (WEEKLY, _('Weekly')),
        (MONTHLY, _('Monthly')),
        (QUARTERLY, _('Quarterly')),
        (YEARLY, _('Yearly')),
        (CUSTOM, _('Custom Period')),
    ]


class BudgetStatus:
    """Enum-like class for budget status."""
    
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    EXCEEDED = 'EXCEEDED'
    COMPLETED = 'COMPLETED'
    
    CHOICES = [
        (ACTIVE, _('Active')),
        (INACTIVE, _('Inactive')),
        (EXCEEDED, _('Exceeded')),
        (COMPLETED, _('Completed')),
    ]


class BudgetManager(models.Manager):
    """Custom manager for Budget model."""
    
    def active(self):
        """Return only active budgets."""
        return self.filter(status=BudgetStatus.ACTIVE, is_deleted=False)
    
    def for_user(self, user):
        """Get budgets for a specific user."""
        return self.active().filter(user=user)
    
    def for_period(self, start_date, end_date):
        """Get budgets for a specific period."""
        return self.active().filter(
            start_date__lte=end_date,
            end_date__gte=start_date
        )
    
    def current_month(self, user):
        """Get current month's budgets for a user."""
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        end_of_month = (start_of_month + relativedelta(months=1)) - relativedelta(days=1)
        
        return self.for_user(user).filter(
            start_date__lte=end_of_month,
            end_date__gte=start_of_month
        )


class Budget(BaseModel, SoftDeleteMixin):
    """
    Budget model for tracking spending limits.
    
    Supports multiple periods (weekly, monthly, quarterly, yearly)
    and provides alerts when spending approaches or exceeds limits.
    """
    
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='budgets',
        help_text=_("User who owns this budget")
    )
    
    category = models.ForeignKey(
        'categories.ExpenseCategory',
        on_delete=models.CASCADE,
        related_name='budgets',
        help_text=_("Expense category for this budget")
    )
    
    name = models.CharField(
        _('budget name'),
        max_length=200,
        help_text=_("Descriptive name for the budget")
    )
    
    amount = models.DecimalField(
        _('budget amount'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text=_("Total budget amount for the period")
    )
    
    period = models.CharField(
        _('period'),
        max_length=20,
        choices=BudgetPeriod.CHOICES,
        default=BudgetPeriod.MONTHLY,
        help_text=_("Budget period type")
    )
    
    start_date = models.DateField(
        _('start date'),
        help_text=_("Budget period start date")
    )
    
    end_date = models.DateField(
        _('end date'),
        help_text=_("Budget period end date")
    )
    
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=BudgetStatus.CHOICES,
        default=BudgetStatus.ACTIVE,
        help_text=_("Current status of the budget")
    )
    
    alert_threshold_80 = models.BooleanField(
        _('alert at 80%'),
        default=True,
        help_text=_("Send alert when 80% of budget is used")
    )
    
    alert_threshold_100 = models.BooleanField(
        _('alert at 100%'),
        default=True,
        help_text=_("Send alert when budget is exceeded")
    )
    
    alerted_at_80 = models.BooleanField(
        _('80% alert sent'),
        default=False,
        help_text=_("Whether 80% alert has been sent")
    )
    
    alerted_at_100 = models.BooleanField(
        _('100% alert sent'),
        default=False,
        help_text=_("Whether 100% alert has been sent")
    )
    
    rollover_unused = models.BooleanField(
        _('rollover unused amount'),
        default=False,
        help_text=_("Roll over unused budget to next period")
    )
    
    notes = models.TextField(
        _('notes'),
        blank=True,
        help_text=_("Additional notes about the budget")
    )
    
    objects = BudgetManager()
    
    class Meta:
        verbose_name = _('Budget')
        verbose_name_plural = _('Budgets')
        ordering = ['-start_date', 'category']
        unique_together = [['user', 'category', 'start_date', 'end_date']]
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['category', 'start_date']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.user.username} ({self.period})"
    
    @property
    def spent_amount(self):
        """Calculate total spent amount for this budget."""
        from apps.transactions.models import Expense
        
        expenses = Expense.objects.filter(
            created_by=self.user,
            category=self.category,
            transaction_date__gte=self.start_date,
            transaction_date__lte=self.end_date,
            status='COMPLETED',
            is_deleted=False
        )
        
        total = sum(expense.amount for expense in expenses)
        return Decimal(str(total))
    
    @property
    def remaining_amount(self):
        """Calculate remaining budget amount."""
        return self.amount - self.spent_amount
    
    @property
    def utilization_percentage(self):
        """Calculate budget utilization percentage."""
        if self.amount > 0:
            return (self.spent_amount / self.amount) * 100
        return Decimal('0.00')
    
    @property
    def is_over_budget(self):
        """Check if budget is exceeded."""
        return self.spent_amount > self.amount
    
    @property
    def is_near_limit(self):
        """Check if spending is near limit (>80%)."""
        return self.utilization_percentage >= 80
    
    @property
    def days_remaining(self):
        """Calculate days remaining in budget period."""
        today = timezone.now().date()
        if today > self.end_date:
            return 0
        return (self.end_date - today).days
    
    @property
    def is_active_period(self):
        """Check if budget is in active period."""
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date
    
    def check_and_send_alerts(self):
        """Check budget status and send alerts if needed."""
        utilization = self.utilization_percentage
        
        # Check 80% threshold
        if (self.alert_threshold_80 and not self.alerted_at_80 and 
            utilization >= 80 and utilization < 100):
            self._send_alert_80()
            self.alerted_at_80 = True
            self.save(update_fields=['alerted_at_80'])
        
        # Check 100% threshold
        if (self.alert_threshold_100 and not self.alerted_at_100 and 
            utilization >= 100):
            self._send_alert_100()
            self.alerted_at_100 = True
            self.status = BudgetStatus.EXCEEDED
            self.save(update_fields=['alerted_at_100', 'status'])
    
    def _send_alert_80(self):
        """Send 80% threshold alert."""
        from apps.budgets.services import NotificationService
        
        NotificationService.send_budget_alert(
            user=self.user,
            budget=self,
            alert_type='80_PERCENT',
            message=f"You've used 80% of your {self.name} budget."
        )
    
    def _send_alert_100(self):
        """Send 100% threshold alert."""
        from apps.budgets.services import NotificationService
        
        NotificationService.send_budget_alert(
            user=self.user,
            budget=self,
            alert_type='EXCEEDED',
            message=f"Budget exceeded for {self.name}!"
        )
    
    def reset_alerts(self):
        """Reset alert flags (for new period)."""
        self.alerted_at_80 = False
        self.alerted_at_100 = False
        self.save(update_fields=['alerted_at_80', 'alerted_at_100'])
    
    @classmethod
    def create_monthly_budget(cls, user, category, amount, start_date=None):
        """
        Helper method to create a monthly budget.
        
        Args:
            user: User instance
            category: ExpenseCategory instance
            amount: Budget amount
            start_date: Optional start date (defaults to first of current month)
        
        Returns:
            Budget instance
        """
        if start_date is None:
            start_date = timezone.now().date().replace(day=1)
        
        end_date = (start_date + relativedelta(months=1)) - relativedelta(days=1)
        
        return cls.objects.create(
            user=user,
            category=category,
            name=f"{category.name} - {start_date.strftime('%B %Y')}",
            amount=amount,
            period=BudgetPeriod.MONTHLY,
            start_date=start_date,
            end_date=end_date
        )


class BudgetAlert(BaseModel):
    """
    Model to track budget alerts sent to users.
    """
    
    ALERT_TYPES = [
        ('80_PERCENT', _('80% Threshold')),
        ('EXCEEDED', _('Budget Exceeded')),
        ('CUSTOM', _('Custom Alert')),
    ]
    
    budget = models.ForeignKey(
        Budget,
        on_delete=models.CASCADE,
        related_name='alerts',
        help_text=_("Related budget")
    )
    
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='budget_alerts',
        help_text=_("User who received the alert")
    )
    
    alert_type = models.CharField(
        _('alert type'),
        max_length=20,
        choices=ALERT_TYPES,
        help_text=_("Type of alert")
    )
    
    message = models.TextField(
        _('message'),
        help_text=_("Alert message content")
    )
    
    is_read = models.BooleanField(
        _('is read'),
        default=False,
        help_text=_("Whether the alert has been read")
    )
    
    sent_via_email = models.BooleanField(
        _('sent via email'),
        default=False,
        help_text=_("Whether alert was sent via email")
    )
    
    class Meta:
        verbose_name = _('Budget Alert')
        verbose_name_plural = _('Budget Alerts')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['budget', 'alert_type']),
        ]
    
    def __str__(self):
        return f"{self.alert_type} - {self.budget.name}"
    
    def mark_as_read(self):
        """Mark alert as read."""
        self.is_read = True
        self.save(update_fields=['is_read'])

