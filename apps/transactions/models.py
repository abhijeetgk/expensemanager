"""
Transaction models for income and expense tracking.

Demonstrates advanced OOP concepts:
- Abstract base classes
- Factory pattern
- Strategy pattern
- Template method pattern
- Polymorphism
"""

from decimal import Decimal
from typing import ClassVar, Optional
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils import timezone

from apps.core.mixins import BaseModel, SoftDeleteMixin


class PaymentMethod:
    """Enum-like class for payment methods."""
    
    CASH = 'CASH'
    CREDIT_CARD = 'CREDIT_CARD'
    DEBIT_CARD = 'DEBIT_CARD'
    BANK_TRANSFER = 'BANK_TRANSFER'
    MOBILE_PAYMENT = 'MOBILE_PAYMENT'
    CHECK = 'CHECK'
    OTHER = 'OTHER'
    
    CHOICES = [
        (CASH, _('Cash')),
        (CREDIT_CARD, _('Credit Card')),
        (DEBIT_CARD, _('Debit Card')),
        (BANK_TRANSFER, _('Bank Transfer')),
        (MOBILE_PAYMENT, _('Mobile Payment')),
        (CHECK, _('Check')),
        (OTHER, _('Other')),
    ]


class TransactionStatus:
    """Enum-like class for transaction statuses."""
    
    PENDING = 'PENDING'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'
    FAILED = 'FAILED'
    
    CHOICES = [
        (PENDING, _('Pending')),
        (COMPLETED, _('Completed')),
        (CANCELLED, _('Cancelled')),
        (FAILED, _('Failed')),
    ]


class TransactionManager(models.Manager):
    """Custom manager for transactions."""
    
    def completed(self):
        """Return only completed transactions."""
        return self.filter(status=TransactionStatus.COMPLETED, is_deleted=False)
    
    def for_user(self, user):
        """
        Get transactions for a specific user.
        
        Args:
            user: The user to filter transactions for
            
        Returns:
            QuerySet of transactions
        """
        if user.can_view_all_transactions():
            return self.completed()
        return self.completed().filter(created_by=user)
    
    def for_date_range(self, start_date, end_date):
        """
        Get transactions for a specific date range.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            QuerySet of transactions
        """
        return self.completed().filter(
            transaction_date__gte=start_date,
            transaction_date__lte=end_date
        )
    
    def total_amount(self):
        """
        Calculate total amount of transactions in the queryset.
        
        Returns:
            Total amount as Decimal
        """
        from django.db.models import Sum
        result = self.aggregate(total=Sum('amount'))
        return result['total'] or Decimal('0.00')


class TransactionBase(BaseModel, SoftDeleteMixin):
    """
    Abstract base class for all transactions.
    
    This class provides common functionality for both income and
    expense transactions using the Template Method pattern.
    """
    
    # Class variable to track transaction type
    transaction_type: ClassVar[str] = "BASE"
    
    amount = models.DecimalField(
        _('amount'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        db_index=True,
        help_text=_("Transaction amount")
    )
    
    description = models.TextField(
        _('description'),
        help_text=_("Description or notes about the transaction")
    )
    
    transaction_date = models.DateField(
        _('transaction date'),
        default=timezone.now,
        db_index=True,
        help_text=_("Date when the transaction occurred")
    )
    
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=TransactionStatus.CHOICES,
        default=TransactionStatus.COMPLETED,
        db_index=True,
        help_text=_("Current status of the transaction")
    )
    
    reference_number = models.CharField(
        _('reference number'),
        max_length=100,
        blank=True,
        help_text=_("External reference number (e.g., invoice number)")
    )
    
    metadata = models.JSONField(
        _('metadata'),
        default=dict,
        blank=True,
        help_text=_("Additional metadata for the transaction")
    )
    
    tags = models.JSONField(
        _('tags'),
        default=list,
        blank=True,
        help_text=_("Tags for categorizing and searching")
    )
    
    objects = TransactionManager()
    
    class Meta:
        abstract = True
        ordering = ['-transaction_date', '-created_at']
        indexes = [
            models.Index(fields=['transaction_date', 'created_by']),
            models.Index(fields=['amount', 'transaction_date']),
            models.Index(fields=['status', 'transaction_date']),
        ]
        
    def __str__(self) -> str:
        """String representation of the transaction."""
        return f"{self.get_type_display()} - {self.amount} on {self.transaction_date}"
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"<{self.__class__.__name__} amount={self.amount} date={self.transaction_date}>"
    
    @classmethod
    def get_type_display(cls) -> str:
        """Get the display name for this transaction type."""
        return cls.transaction_type
    
    @property
    def is_completed(self) -> bool:
        """Check if the transaction is completed."""
        return self.status == TransactionStatus.COMPLETED
    
    @property
    def is_pending(self) -> bool:
        """Check if the transaction is pending."""
        return self.status == TransactionStatus.PENDING
    
    @property
    def is_cancelled(self) -> bool:
        """Check if the transaction is cancelled."""
        return self.status == TransactionStatus.CANCELLED
    
    @property
    def formatted_amount(self) -> str:
        """Get formatted amount with currency symbol."""
        return f"₹{self.amount:,.2f}"
    
    def complete(self) -> None:
        """Mark the transaction as completed."""
        self.status = TransactionStatus.COMPLETED
        self.save(update_fields=['status'])
    
    def cancel(self, reason: Optional[str] = None) -> None:
        """
        Cancel the transaction.
        
        Args:
            reason: Optional reason for cancellation
        """
        self.status = TransactionStatus.CANCELLED
        if reason:
            self.metadata['cancellation_reason'] = reason
            self.metadata['cancelled_at'] = timezone.now().isoformat()
        self.save(update_fields=['status', 'metadata'])
    
    def add_tag(self, tag: str) -> None:
        """
        Add a tag to the transaction.
        
        Args:
            tag: Tag to add
        """
        if tag not in self.tags:
            self.tags.append(tag)
            self.save(update_fields=['tags'])
    
    def remove_tag(self, tag: str) -> None:
        """
        Remove a tag from the transaction.
        
        Args:
            tag: Tag to remove
        """
        if tag in self.tags:
            self.tags.remove(tag)
            self.save(update_fields=['tags'])


class Income(TransactionBase):
    """
    Income transaction model.
    
    Represents income entries such as salary, freelance work,
    investments, gifts, etc.
    """
    
    transaction_type = "INCOME"
    
    category = models.ForeignKey(
        'categories.IncomeCategory',
        on_delete=models.PROTECT,
        related_name='transactions',
        help_text=_("Income category")
    )
    
    source = models.CharField(
        _('source'),
        max_length=200,
        help_text=_("Source of income (e.g., employer name, client name)")
    )
    
    is_recurring = models.BooleanField(
        _('is recurring'),
        default=False,
        help_text=_("Whether this is a recurring income")
    )
    
    recurrence_period = models.CharField(
        _('recurrence period'),
        max_length=20,
        choices=[
            ('DAILY', _('Daily')),
            ('WEEKLY', _('Weekly')),
            ('BIWEEKLY', _('Bi-weekly')),
            ('MONTHLY', _('Monthly')),
            ('QUARTERLY', _('Quarterly')),
            ('ANNUALLY', _('Annually')),
        ],
        blank=True,
        null=True,
        help_text=_("Frequency of recurring income")
    )
    
    next_occurrence = models.DateField(
        _('next occurrence'),
        blank=True,
        null=True,
        help_text=_("Next expected occurrence date for recurring income")
    )
    
    tax_amount = models.DecimalField(
        _('tax amount'),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_("Tax deducted from this income")
    )
    
    class Meta:
        verbose_name = _('Income')
        verbose_name_plural = _('Income Entries')
        ordering = ['-transaction_date', '-created_at']
        indexes = [
            models.Index(fields=['category', 'transaction_date']),
            models.Index(fields=['source', 'transaction_date']),
            models.Index(fields=['is_recurring', 'next_occurrence']),
        ]
    
    @property
    def net_amount(self) -> Decimal:
        """Calculate net amount after tax deduction."""
        return self.amount - self.tax_amount
    
    @property
    def tax_percentage(self) -> Decimal:
        """Calculate tax percentage."""
        if self.amount > 0:
            return (self.tax_amount / self.amount) * 100
        return Decimal('0.00')
    
    def set_next_occurrence(self) -> None:
        """Calculate and set the next occurrence date for recurring income."""
        if not self.is_recurring or not self.recurrence_period:
            return
        
        from dateutil.relativedelta import relativedelta
        
        base_date = self.next_occurrence or self.transaction_date
        
        period_mapping = {
            'DAILY': relativedelta(days=1),
            'WEEKLY': relativedelta(weeks=1),
            'BIWEEKLY': relativedelta(weeks=2),
            'MONTHLY': relativedelta(months=1),
            'QUARTERLY': relativedelta(months=3),
            'ANNUALLY': relativedelta(years=1),
        }
        
        delta = period_mapping.get(self.recurrence_period)
        if delta:
            self.next_occurrence = base_date + delta
            self.save(update_fields=['next_occurrence'])


class Expense(TransactionBase):
    """
    Expense transaction model.
    
    Represents expense entries such as food, transportation,
    healthcare, entertainment, etc.
    """
    
    transaction_type = "EXPENSE"
    
    category = models.ForeignKey(
        'categories.ExpenseCategory',
        on_delete=models.PROTECT,
        related_name='transactions',
        help_text=_("Expense category")
    )
    
    payment_method = models.CharField(
        _('payment method'),
        max_length=20,
        choices=PaymentMethod.CHOICES,
        default=PaymentMethod.CASH,
        db_index=True,
        help_text=_("Method used for payment")
    )
    
    vendor = models.CharField(
        _('vendor'),
        max_length=200,
        blank=True,
        help_text=_("Vendor or merchant name")
    )
    
    location = models.CharField(
        _('location'),
        max_length=200,
        blank=True,
        help_text=_("Location where the expense occurred")
    )
    
    receipt = models.FileField(
        _('receipt'),
        upload_to='receipts/%Y/%m/',
        blank=True,
        null=True,
        help_text=_("Receipt image or file")
    )
    
    is_reimbursable = models.BooleanField(
        _('is reimbursable'),
        default=False,
        help_text=_("Whether this expense is reimbursable")
    )
    
    reimbursed = models.BooleanField(
        _('reimbursed'),
        default=False,
        help_text=_("Whether this expense has been reimbursed")
    )
    
    reimbursement_date = models.DateField(
        _('reimbursement date'),
        blank=True,
        null=True,
        help_text=_("Date when the expense was reimbursed")
    )
    
    class Meta:
        verbose_name = _('Expense')
        verbose_name_plural = _('Expense Entries')
        ordering = ['-transaction_date', '-created_at']
        indexes = [
            models.Index(fields=['category', 'transaction_date']),
            models.Index(fields=['payment_method', 'transaction_date']),
            models.Index(fields=['vendor', 'transaction_date']),
            models.Index(fields=['is_reimbursable', 'reimbursed']),
        ]
    
    @property
    def is_pending_reimbursement(self) -> bool:
        """Check if the expense is pending reimbursement."""
        return self.is_reimbursable and not self.reimbursed
    
    def mark_reimbursed(self, date: Optional[timezone.datetime] = None) -> None:
        """
        Mark the expense as reimbursed.
        
        Args:
            date: Optional reimbursement date (defaults to today)
        """
        self.reimbursed = True
        self.reimbursement_date = date or timezone.now().date()
        self.save(update_fields=['reimbursed', 'reimbursement_date'])

