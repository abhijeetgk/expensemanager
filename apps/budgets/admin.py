"""
Admin configuration for budget models.
"""

from django.contrib import admin
from django.utils.html import format_html
from apps.budgets.models import Budget, BudgetAlert


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    """Admin interface for Budget model."""
    
    list_display = [
        'name', 'user', 'category', 'amount', 'period',
        'utilization_display', 'status_badge', 'date_range',
        'is_active_period'
    ]
    list_filter = ['status', 'period', 'start_date', 'category']
    search_fields = ['name', 'user__email', 'user__username', 'category__name']
    readonly_fields = [
        'spent_amount', 'remaining_amount', 'utilization_percentage',
        'is_over_budget', 'is_near_limit', 'days_remaining',
        'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'category', 'name', 'amount', 'period', 'status')
        }),
        ('Period', {
            'fields': ('start_date', 'end_date', 'days_remaining')
        }),
        ('Spending Information', {
            'fields': ('spent_amount', 'remaining_amount', 'utilization_percentage',
                      'is_over_budget', 'is_near_limit')
        }),
        ('Alert Settings', {
            'fields': ('alert_threshold_80', 'alert_threshold_100',
                      'alerted_at_80', 'alerted_at_100')
        }),
        ('Additional Options', {
            'fields': ('rollover_unused', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def utilization_display(self, obj):
        """Display utilization as a colored percentage."""
        percentage = obj.utilization_percentage
        if percentage >= 100:
            color = '#EF4444'  # Red
        elif percentage >= 80:
            color = '#F59E0B'  # Orange
        elif percentage >= 60:
            color = '#3B82F6'  # Blue
        else:
            color = '#10B981'  # Green
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color, percentage
        )
    utilization_display.short_description = 'Utilization'
    
    def status_badge(self, obj):
        """Display status as a colored badge."""
        colors = {
            'ACTIVE': '#10B981',
            'INACTIVE': '#6B7280',
            'EXCEEDED': '#EF4444',
            'COMPLETED': '#3B82F6',
        }
        color = colors.get(obj.status, '#6B7280')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def date_range(self, obj):
        """Display date range."""
        return f"{obj.start_date} to {obj.end_date}"
    date_range.short_description = 'Period'


@admin.register(BudgetAlert)
class BudgetAlertAdmin(admin.ModelAdmin):
    """Admin interface for BudgetAlert model."""
    
    list_display = [
        'budget', 'user', 'alert_type_badge', 'is_read',
        'sent_via_email', 'created_at'
    ]
    list_filter = ['alert_type', 'is_read', 'sent_via_email', 'created_at']
    search_fields = ['budget__name', 'user__email', 'message']
    readonly_fields = ['budget', 'user', 'alert_type', 'message', 'created_at']
    
    def alert_type_badge(self, obj):
        """Display alert type as a colored badge."""
        colors = {
            '80_PERCENT': '#F59E0B',  # Orange
            'EXCEEDED': '#EF4444',    # Red
            'CUSTOM': '#3B82F6',      # Blue
        }
        color = colors.get(obj.alert_type, '#6B7280')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-size: 11px;">{}</span>',
            color, obj.get_alert_type_display()
        )
    alert_type_badge.short_description = 'Alert Type'

