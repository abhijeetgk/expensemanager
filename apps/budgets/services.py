"""
Budget services for business logic.
"""

from decimal import Decimal
from typing import List, Dict, Optional
from django.utils import timezone
from django.db.models import Sum, Q
from dateutil.relativedelta import relativedelta

from apps.budgets.models import Budget, BudgetAlert, BudgetStatus


class BudgetService:
    """Service class for budget-related operations."""
    
    @staticmethod
    def get_user_budgets(user, period_type=None):
        """
        Get all budgets for a user, optionally filtered by period type.
        
        Args:
            user: User instance
            period_type: Optional period type filter
        
        Returns:
            QuerySet of Budget objects
        """
        budgets = Budget.objects.for_user(user)
        
        if period_type:
            budgets = budgets.filter(period=period_type)
        
        return budgets
    
    @staticmethod
    def get_current_budgets(user):
        """
        Get active budgets for the current period.
        
        Args:
            user: User instance
        
        Returns:
            QuerySet of active Budget objects
        """
        today = timezone.now().date()
        return Budget.objects.for_user(user).filter(
            start_date__lte=today,
            end_date__gte=today
        )
    
    @staticmethod
    def calculate_budget_summary(user, start_date=None, end_date=None):
        """
        Calculate budget summary for a user.
        
        Args:
            user: User instance
            start_date: Optional start date
            end_date: Optional end date
        
        Returns:
            Dictionary with budget summary data
        """
        if not start_date:
            start_date = timezone.now().date().replace(day=1)
        if not end_date:
            end_date = (start_date + relativedelta(months=1)) - relativedelta(days=1)
        
        budgets = Budget.objects.for_period(start_date, end_date).filter(user=user)
        
        total_budget = sum(b.amount for b in budgets)
        total_spent = sum(b.spent_amount for b in budgets)
        total_remaining = total_budget - total_spent
        
        over_budget_count = sum(1 for b in budgets if b.is_over_budget)
        near_limit_count = sum(1 for b in budgets if b.is_near_limit and not b.is_over_budget)
        
        return {
            'total_budget': total_budget,
            'total_spent': total_spent,
            'total_remaining': total_remaining,
            'utilization_percentage': (total_spent / total_budget * 100) if total_budget > 0 else 0,
            'budget_count': budgets.count(),
            'over_budget_count': over_budget_count,
            'near_limit_count': near_limit_count,
            'budgets': budgets
        }
    
    @staticmethod
    def check_all_budgets_for_alerts(user):
        """
        Check all active budgets for a user and send alerts if needed.
        
        Args:
            user: User instance
        """
        active_budgets = BudgetService.get_current_budgets(user)
        
        for budget in active_budgets:
            budget.check_and_send_alerts()
    
    @staticmethod
    def create_recurring_budgets(user, category, amount, months=12):
        """
        Create recurring monthly budgets for multiple months.
        
        Args:
            user: User instance
            category: ExpenseCategory instance
            amount: Budget amount
            months: Number of months to create budgets for
        
        Returns:
            List of created Budget instances
        """
        budgets = []
        start_date = timezone.now().date().replace(day=1)
        
        for i in range(months):
            month_start = start_date + relativedelta(months=i)
            month_end = (month_start + relativedelta(months=1)) - relativedelta(days=1)
            
            budget = Budget.objects.create(
                user=user,
                category=category,
                name=f"{category.name} - {month_start.strftime('%B %Y')}",
                amount=amount,
                period='MONTHLY',
                start_date=month_start,
                end_date=month_end
            )
            budgets.append(budget)
        
        return budgets
    
    @staticmethod
    def get_budget_forecast(user, months=3):
        """
        Forecast budget needs based on historical spending.
        
        Args:
            user: User instance
            months: Number of months to look back
        
        Returns:
            Dictionary with forecast data
        """
        from apps.transactions.models import Expense
        from apps.categories.models import ExpenseCategory
        
        end_date = timezone.now().date()
        start_date = end_date - relativedelta(months=months)
        
        categories = ExpenseCategory.objects.filter(is_active=True)
        forecast = []
        
        for category in categories:
            total_spent = Expense.objects.filter(
                created_by=user,
                category=category,
                transaction_date__gte=start_date,
                transaction_date__lte=end_date,
                status='COMPLETED',
                is_deleted=False
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            avg_monthly = total_spent / months if months > 0 else Decimal('0.00')
            suggested_budget = avg_monthly * Decimal('1.1')  # 10% buffer
            
            forecast.append({
                'category': category,
                'avg_monthly_spending': avg_monthly,
                'suggested_budget': suggested_budget,
                'total_spent_period': total_spent
            })
        
        return sorted(forecast, key=lambda x: x['avg_monthly_spending'], reverse=True)


class NotificationService:
    """Service for sending budget notifications."""
    
    @staticmethod
    def send_budget_alert(user, budget, alert_type, message):
        """
        Send a budget alert to user.
        
        Args:
            user: User instance
            budget: Budget instance
            alert_type: Type of alert
            message: Alert message
        
        Returns:
            BudgetAlert instance
        """
        alert = BudgetAlert.objects.create(
            budget=budget,
            user=user,
            alert_type=alert_type,
            message=message
        )
        
        # Send email if user has email notifications enabled
        if hasattr(user, 'profile') and getattr(user.profile, 'email_notifications', True):
            NotificationService._send_email_alert(user, message)
            alert.sent_via_email = True
            alert.save(update_fields=['sent_via_email'])
        
        return alert
    
    @staticmethod
    def _send_email_alert(user, message):
        """
        Send email alert to user.
        
        Args:
            user: User instance
            message: Alert message
        """
        from django.core.mail import send_mail
        from django.conf import settings
        
        try:
            send_mail(
                subject='Budget Alert - Expense Manager',
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception as e:
            # Log error but don't fail
            print(f"Failed to send email alert: {e}")
    
    @staticmethod
    def get_unread_alerts(user):
        """
        Get all unread alerts for a user.
        
        Args:
            user: User instance
        
        Returns:
            QuerySet of unread BudgetAlert objects
        """
        return BudgetAlert.objects.filter(user=user, is_read=False).select_related('budget')
    
    @staticmethod
    def mark_alerts_as_read(user, alert_ids=None):
        """
        Mark alerts as read for a user.
        
        Args:
            user: User instance
            alert_ids: Optional list of specific alert IDs to mark as read
        """
        alerts = BudgetAlert.objects.filter(user=user, is_read=False)
        
        if alert_ids:
            alerts = alerts.filter(id__in=alert_ids)
        
        alerts.update(is_read=True)

