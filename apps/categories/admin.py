"""
Admin interface for categories app.
"""

from django.contrib import admin
from apps.categories.models import IncomeCategory, ExpenseCategory


@admin.register(IncomeCategory)
class IncomeCategoryAdmin(admin.ModelAdmin):
    """Admin for Income Category."""
    
    list_display = [
        'name', 'parent', 'is_recurring', 'tax_applicable',
        'is_active', 'sort_order', 'created_at'
    ]
    list_filter = ['is_active', 'is_recurring', 'tax_applicable', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['sort_order', 'name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'parent')
        }),
        ('Appearance', {
            'fields': ('icon', 'color', 'sort_order')
        }),
        ('Settings', {
            'fields': ('is_recurring', 'tax_applicable', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['activate_categories', 'deactivate_categories']
    
    def activate_categories(self, request, queryset):
        """Bulk activate categories."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} categories activated.')
    activate_categories.short_description = 'Activate selected categories'
    
    def deactivate_categories(self, request, queryset):
        """Bulk deactivate categories."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} categories deactivated.')
    deactivate_categories.short_description = 'Deactivate selected categories'


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    """Admin for Expense Category."""
    
    list_display = [
        'name', 'parent', 'budget_limit', 'is_essential',
        'is_active', 'sort_order', 'created_at'
    ]
    list_filter = ['is_active', 'is_essential', 'allows_split', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['sort_order', 'name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'parent')
        }),
        ('Appearance', {
            'fields': ('icon', 'color', 'sort_order')
        }),
        ('Budget & Settings', {
            'fields': ('budget_limit', 'is_essential', 'allows_split', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['activate_categories', 'deactivate_categories', 'mark_essential']
    
    def activate_categories(self, request, queryset):
        """Bulk activate categories."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} categories activated.')
    activate_categories.short_description = 'Activate selected categories'
    
    def deactivate_categories(self, request, queryset):
        """Bulk deactivate categories."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} categories deactivated.')
    deactivate_categories.short_description = 'Deactivate selected categories'
    
    def mark_essential(self, request, queryset):
        """Mark categories as essential."""
        updated = queryset.update(is_essential=True)
        self.message_user(request, f'{updated} categories marked as essential.')
    mark_essential.short_description = 'Mark as essential'

