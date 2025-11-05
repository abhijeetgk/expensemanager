"""
Models for split and shared expenses.

Features:
- Split expenses among multiple users
- Group expense management
- Debt tracking and settlement
- IOU tracking
"""

from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils import timezone

from apps.core.mixins import BaseModel, SoftDeleteMixin


class SplitMethod:
    """Enum-like class for split methods."""
    
    EQUAL = 'EQUAL'
    EXACT = 'EXACT'
    PERCENTAGE = 'PERCENTAGE'
    SHARES = 'SHARES'
    
    CHOICES = [
        (EQUAL, _('Equal Split')),
        (EXACT, _('Exact Amounts')),
        (PERCENTAGE, _('By Percentage')),
        (SHARES, _('By Shares')),
    ]


class SettlementStatus:
    """Enum-like class for settlement status."""
    
    PENDING = 'PENDING'
    PARTIALLY_PAID = 'PARTIALLY_PAID'
    SETTLED = 'SETTLED'
    CANCELLED = 'CANCELLED'
    
    CHOICES = [
        (PENDING, _('Pending')),
        (PARTIALLY_PAID, _('Partially Paid')),
        (SETTLED, _('Settled')),
        (CANCELLED, _('Cancelled')),
    ]


class ExpenseGroup(BaseModel, SoftDeleteMixin):
    """
    Model for expense groups (e.g., roommates, trip, project).
    """
    
    name = models.CharField(
        _('group name'),
        max_length=200,
        help_text=_("Name of the expense group")
    )
    
    description = models.TextField(
        _('description'),
        blank=True,
        help_text=_("Description of the group")
    )
    
    members = models.ManyToManyField(
        'accounts.User',
        related_name='expense_groups',
        help_text=_("Members of this group")
    )
    
    admin = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='administered_groups',
        help_text=_("Administrator of the group")
    )
    
    icon = models.CharField(
        _('icon'),
        max_length=50,
        default='fas fa-users',
        help_text=_("Font Awesome icon class")
    )
    
    color = models.CharField(
        _('color'),
        max_length=7,
        default='#3B82F6',
        help_text=_("Group color (hex code)")
    )
    
    is_active = models.BooleanField(
        _('is active'),
        default=True,
        help_text=_("Whether the group is active")
    )
    
    class Meta:
        verbose_name = _('Expense Group')
        verbose_name_plural = _('Expense Groups')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def member_count(self):
        """Get number of members in the group."""
        return self.members.count()
    
    @property
    def total_expenses(self):
        """Get total expenses for this group."""
        return sum(expense.amount for expense in self.shared_expenses.filter(is_deleted=False))
    
    def get_balance_summary(self):
        """Get balance summary for all members."""
        from django.db.models import Sum, Q
        
        balances = {}
        for member in self.members.all():
            # Total paid by member
            paid = self.shared_expenses.filter(
                paid_by=member,
                is_deleted=False
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            # Total owed by member
            owed = SharedExpenseSplit.objects.filter(
                shared_expense__group=self,
                user=member,
                shared_expense__is_deleted=False
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            balances[member] = {
                'paid': paid,
                'owed': owed,
                'balance': paid - owed
            }
        
        return balances


class SharedExpense(BaseModel, SoftDeleteMixin):
    """
    Model for shared/split expenses.
    """
    
    expense = models.ForeignKey(
        'transactions.Expense',
        on_delete=models.CASCADE,
        related_name='shared_info',
        help_text=_("Related expense transaction")
    )
    
    group = models.ForeignKey(
        ExpenseGroup,
        on_delete=models.CASCADE,
        related_name='shared_expenses',
        help_text=_("Expense group")
    )
    
    paid_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='shared_expenses_paid',
        help_text=_("User who paid for the expense")
    )
    
    split_method = models.CharField(
        _('split method'),
        max_length=20,
        choices=SplitMethod.CHOICES,
        default=SplitMethod.EQUAL,
        help_text=_("Method used to split the expense")
    )
    
    notes = models.TextField(
        _('notes'),
        blank=True,
        help_text=_("Additional notes about the split")
    )
    
    class Meta:
        verbose_name = _('Shared Expense')
        verbose_name_plural = _('Shared Expenses')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.expense.description} - {self.group.name}"
    
    @property
    def amount(self):
        """Get expense amount."""
        return self.expense.amount
    
    @property
    def is_fully_settled(self):
        """Check if all splits are settled."""
        return all(split.is_settled for split in self.splits.all())
    
    def create_equal_splits(self, members=None):
        """
        Create equal splits for all members.
        
        Args:
            members: List of User objects (defaults to all group members)
        """
        if members is None:
            members = list(self.group.members.all())
        
        if not members:
            return
        
        amount_per_person = self.expense.amount / len(members)
        
        for member in members:
            SharedExpenseSplit.objects.create(
                shared_expense=self,
                user=member,
                amount=amount_per_person
            )
    
    def create_custom_splits(self, split_data):
        """
        Create custom splits based on provided data.
        
        Args:
            split_data: List of dicts with 'user' and 'amount' keys
        """
        for data in split_data:
            SharedExpenseSplit.objects.create(
                shared_expense=self,
                user=data['user'],
                amount=data['amount']
            )


class SharedExpenseSplit(BaseModel):
    """
    Model for individual splits of a shared expense.
    """
    
    shared_expense = models.ForeignKey(
        SharedExpense,
        on_delete=models.CASCADE,
        related_name='splits',
        help_text=_("Related shared expense")
    )
    
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='expense_splits',
        help_text=_("User responsible for this split")
    )
    
    amount = models.DecimalField(
        _('amount'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text=_("Amount owed by this user")
    )
    
    percentage = models.DecimalField(
        _('percentage'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Percentage of total (if split by percentage)")
    )
    
    is_settled = models.BooleanField(
        _('is settled'),
        default=False,
        help_text=_("Whether this split has been settled")
    )
    
    settled_at = models.DateTimeField(
        _('settled at'),
        null=True,
        blank=True,
        help_text=_("When this split was settled")
    )
    
    settlement_notes = models.TextField(
        _('settlement notes'),
        blank=True,
        help_text=_("Notes about the settlement")
    )
    
    class Meta:
        verbose_name = _('Expense Split')
        verbose_name_plural = _('Expense Splits')
        unique_together = [['shared_expense', 'user']]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - ₹{self.amount}"
    
    @property
    def formatted_amount(self):
        """Get formatted amount."""
        return f"₹{self.amount:,.2f}"
    
    def settle(self, notes=''):
        """Mark this split as settled."""
        self.is_settled = True
        self.settled_at = timezone.now()
        if notes:
            self.settlement_notes = notes
        self.save()
    
    def unsettle(self):
        """Mark this split as unsettled."""
        self.is_settled = False
        self.settled_at = None
        self.save()


class Debt(BaseModel, SoftDeleteMixin):
    """
    Model for tracking debts between users.
    """
    
    creditor = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='debts_owed_to_me',
        help_text=_("User who is owed money")
    )
    
    debtor = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='my_debts',
        help_text=_("User who owes money")
    )
    
    amount = models.DecimalField(
        _('amount'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text=_("Amount owed")
    )
    
    description = models.TextField(
        _('description'),
        help_text=_("Description of the debt")
    )
    
    group = models.ForeignKey(
        ExpenseGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='debts',
        help_text=_("Related expense group (if any)")
    )
    
    shared_expense_split = models.ForeignKey(
        SharedExpenseSplit,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='debt',
        help_text=_("Related expense split (if any)")
    )
    
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=SettlementStatus.CHOICES,
        default=SettlementStatus.PENDING,
        help_text=_("Current status of the debt")
    )
    
    due_date = models.DateField(
        _('due date'),
        null=True,
        blank=True,
        help_text=_("Due date for payment")
    )
    
    settled_amount = models.DecimalField(
        _('settled amount'),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_("Amount already paid")
    )
    
    settled_at = models.DateTimeField(
        _('settled at'),
        null=True,
        blank=True,
        help_text=_("When the debt was fully settled")
    )
    
    class Meta:
        verbose_name = _('Debt')
        verbose_name_plural = _('Debts')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['creditor', 'status']),
            models.Index(fields=['debtor', 'status']),
        ]
    
    def __str__(self):
        return f"{self.debtor.username} owes {self.creditor.username} ₹{self.amount}"
    
    @property
    def remaining_amount(self):
        """Get remaining amount to be paid."""
        return self.amount - self.settled_amount
    
    @property
    def is_overdue(self):
        """Check if debt is overdue."""
        if self.due_date and self.status == SettlementStatus.PENDING:
            return timezone.now().date() > self.due_date
        return False
    
    def add_payment(self, amount, notes=''):
        """
        Add a payment towards the debt.
        
        Args:
            amount: Payment amount
            notes: Optional payment notes
        """
        self.settled_amount += amount
        
        if self.settled_amount >= self.amount:
            self.status = SettlementStatus.SETTLED
            self.settled_at = timezone.now()
            self.settled_amount = self.amount  # Cap at total amount
        elif self.settled_amount > 0:
            self.status = SettlementStatus.PARTIALLY_PAID
        
        self.save()
        
        # Create payment record
        DebtPayment.objects.create(
            debt=self,
            amount=amount,
            notes=notes,
            created_by=self.debtor
        )
    
    def settle_full(self, notes=''):
        """Settle the debt in full."""
        remaining = self.remaining_amount
        if remaining > 0:
            self.add_payment(remaining, notes)


class DebtPayment(BaseModel):
    """
    Model for tracking debt payments.
    """
    
    debt = models.ForeignKey(
        Debt,
        on_delete=models.CASCADE,
        related_name='payments',
        help_text=_("Related debt")
    )
    
    amount = models.DecimalField(
        _('amount'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text=_("Payment amount")
    )
    
    payment_method = models.CharField(
        _('payment method'),
        max_length=50,
        default='CASH',
        help_text=_("Payment method used")
    )
    
    reference_number = models.CharField(
        _('reference number'),
        max_length=100,
        blank=True,
        help_text=_("Payment reference number")
    )
    
    notes = models.TextField(
        _('notes'),
        blank=True,
        help_text=_("Payment notes")
    )
    
    class Meta:
        verbose_name = _('Debt Payment')
        verbose_name_plural = _('Debt Payments')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment of ₹{self.amount} for {self.debt}"
    
    @property
    def formatted_amount(self):
        """Get formatted amount."""
        return f"₹{self.amount:,.2f}"

