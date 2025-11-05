"""
Admin configuration for shared expenses models.
"""

from django.contrib import admin
from django.utils.html import format_html
from apps.shared_expenses.models import ExpenseGroup, SharedExpense, SharedExpenseSplit, Debt, DebtPayment


@admin.register(ExpenseGroup)
class ExpenseGroupAdmin(admin.ModelAdmin):
    """Admin interface for ExpenseGroup model."""
    
    list_display = ['name', 'admin', 'member_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description', 'admin__username']
    filter_horizontal = ['members']


@admin.register(SharedExpense)
class SharedExpenseAdmin(admin.ModelAdmin):
    """Admin interface for SharedExpense model."""
    
    list_display = ['expense', 'group', 'paid_by', 'split_method', 'amount', 'created_at']
    list_filter = ['split_method', 'group', 'created_at']
    search_fields = ['expense__description', 'group__name', 'paid_by__username']


@admin.register(SharedExpenseSplit)
class SharedExpenseSplitAdmin(admin.ModelAdmin):
    """Admin interface for SharedExpenseSplit model."""
    
    list_display = ['shared_expense', 'user', 'amount', 'is_settled', 'created_at']
    list_filter = ['is_settled', 'created_at']
    search_fields = ['shared_expense__expense__description', 'user__username']


@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    """Admin interface for Debt model."""
    
    list_display = ['debtor', 'creditor', 'amount', 'status_badge', 'remaining_amount', 'is_overdue']
    list_filter = ['status', 'created_at']
    search_fields = ['debtor__username', 'creditor__username', 'description']
    
    def status_badge(self, obj):
        """Display status as a colored badge."""
        colors = {
            'PENDING': '#F59E0B',
            'PARTIALLY_PAID': '#3B82F6',
            'SETTLED': '#10B981',
            'CANCELLED': '#6B7280',
        }
        color = colors.get(obj.status, '#6B7280')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(DebtPayment)
class DebtPaymentAdmin(admin.ModelAdmin):
    """Admin interface for DebtPayment model."""
    
    list_display = ['debt', 'amount', 'payment_method', 'created_at']
    list_filter = ['payment_method', 'created_at']
    search_fields = ['debt__description', 'reference_number']

