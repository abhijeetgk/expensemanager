"""
Admin interface for transactions app.
"""

from django.contrib import admin
from apps.transactions.models import Income, Expense


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    """Admin for Income."""
    
    list_display = [
        'transaction_date', 'source', 'category', 'amount',
        'status', 'is_recurring', 'created_by'
    ]
    list_filter = ['status', 'is_recurring', 'category', 'transaction_date', 'created_at']
    search_fields = ['source', 'description', 'reference_number']
    ordering = ['-transaction_date', '-created_at']
    date_hierarchy = 'transaction_date'
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('transaction_date', 'amount', 'description', 'category', 'source')
        }),
        ('Status & Reference', {
            'fields': ('status', 'reference_number')
        }),
        ('Recurring Income', {
            'fields': ('is_recurring', 'recurrence_period', 'next_occurrence'),
            'classes': ('collapse',)
        }),
        ('Tax Information', {
            'fields': ('tax_amount',),
            'classes': ('collapse',)
        }),
        ('Additional Data', {
            'fields': ('metadata', 'tags'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['mark_completed', 'mark_cancelled']
    
    def mark_completed(self, request, queryset):
        """Bulk mark as completed."""
        for income in queryset:
            income.complete()
        self.message_user(request, f'{queryset.count()} incomes marked as completed.')
    mark_completed.short_description = 'Mark selected as completed'
    
    def mark_cancelled(self, request, queryset):
        """Bulk cancel."""
        for income in queryset:
            income.cancel()
        self.message_user(request, f'{queryset.count()} incomes cancelled.')
    mark_cancelled.short_description = 'Cancel selected incomes'


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    """Admin for Expense."""
    
    list_display = [
        'transaction_date', 'vendor', 'category', 'amount',
        'payment_method', 'status', 'is_reimbursable', 'created_by'
    ]
    list_filter = [
        'status', 'payment_method', 'is_reimbursable',
        'reimbursed', 'category', 'transaction_date', 'created_at'
    ]
    search_fields = ['vendor', 'description', 'reference_number', 'location']
    ordering = ['-transaction_date', '-created_at']
    date_hierarchy = 'transaction_date'
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('transaction_date', 'amount', 'description', 'category')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'vendor', 'location', 'receipt')
        }),
        ('Status & Reference', {
            'fields': ('status', 'reference_number')
        }),
        ('Reimbursement', {
            'fields': ('is_reimbursable', 'reimbursed', 'reimbursement_date'),
            'classes': ('collapse',)
        }),
        ('Additional Data', {
            'fields': ('metadata', 'tags'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['mark_completed', 'mark_cancelled', 'mark_reimbursed']
    
    def mark_completed(self, request, queryset):
        """Bulk mark as completed."""
        for expense in queryset:
            expense.complete()
        self.message_user(request, f'{queryset.count()} expenses marked as completed.')
    mark_completed.short_description = 'Mark selected as completed'
    
    def mark_cancelled(self, request, queryset):
        """Bulk cancel."""
        for expense in queryset:
            expense.cancel()
        self.message_user(request, f'{queryset.count()} expenses cancelled.')
    mark_cancelled.short_description = 'Cancel selected expenses'
    
    def mark_reimbursed(self, request, queryset):
        """Bulk mark as reimbursed."""
        count = 0
        for expense in queryset:
            if expense.is_reimbursable and not expense.reimbursed:
                expense.mark_reimbursed()
                count += 1
        self.message_user(request, f'{count} expenses marked as reimbursed.')
    mark_reimbursed.short_description = 'Mark as reimbursed'

