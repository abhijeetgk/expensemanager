"""
Reporting services using Service Layer pattern.

Demonstrates:
- Service Layer pattern
- Strategy pattern for different report types
- Dependency injection
- Type hints
- Comprehensive business logic separation
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Optional, Any
from django.db.models import Sum, Count, Q, F
from django.utils import timezone

from apps.transactions.models import Income, Expense
from apps.categories.models import IncomeCategory, ExpenseCategory


@dataclass
class ReportData:
    """
    Data transfer object for report data.
    
    Demonstrates the use of dataclasses for DTOs.
    """
    total_income: Decimal
    total_expense: Decimal
    net_balance: Decimal
    transaction_count: int
    period_start: date
    period_end: date
    details: Dict[str, Any]


@dataclass
class CategorySummary:
    """DTO for category-wise summary data."""
    category_name: str
    category_id: str
    total_amount: Decimal
    transaction_count: int
    percentage: Decimal
    color: str


class ReportService:
    """
    Base service for generating reports.
    
    This class demonstrates the Service Layer pattern for
    encapsulating business logic.
    """
    
    @staticmethod
    def get_summary_report(
        user,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> ReportData:
        """
        Generate a summary report for a user.
        
        Args:
            user: The user to generate the report for
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            ReportData object containing summary information
        """
        # Default to current month if dates not provided
        if not end_date:
            end_date = timezone.now().date()
        if not start_date:
            start_date = end_date.replace(day=1)
        
        # Get user's transactions with date filtering
        income_qs = Income.objects.for_user(user).filter(
            transaction_date__gte=start_date,
            transaction_date__lte=end_date
        )
        expense_qs = Expense.objects.for_user(user).filter(
            transaction_date__gte=start_date,
            transaction_date__lte=end_date
        )
        
        # Calculate totals using aggregate
        total_income = income_qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        total_expense = expense_qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        net_balance = total_income - total_expense
        
        transaction_count = income_qs.count() + expense_qs.count()
        
        # Additional details
        income_count = income_qs.count()
        expense_count = expense_qs.count()
        
        details = {
            'income_count': income_count,
            'expense_count': expense_count,
            'average_income': total_income / income_count if income_count > 0 else Decimal('0.00'),
            'average_expense': total_expense / expense_count if expense_count > 0 else Decimal('0.00'),
        }
        
        return ReportData(
            total_income=total_income,
            total_expense=total_expense,
            net_balance=net_balance,
            transaction_count=transaction_count,
            period_start=start_date,
            period_end=end_date,
            details=details
        )
    
    @staticmethod
    def get_monthly_report(
        user,
        year: int,
        month: int
    ) -> ReportData:
        """
        Generate a monthly report.
        
        Args:
            user: The user to generate the report for
            year: Year for the report
            month: Month for the report
            
        Returns:
            ReportData object
        """
        start_date = date(year, month, 1)
        
        # Calculate last day of month
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        return ReportService.get_summary_report(user, start_date, end_date)
    
    @staticmethod
    def get_category_wise_report(
        user,
        transaction_type: str,  # 'INCOME' or 'EXPENSE'
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[CategorySummary]:
        """
        Generate a category-wise breakdown report.
        
        Args:
            user: The user to generate the report for
            transaction_type: Type of transaction ('INCOME' or 'EXPENSE')
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            List of CategorySummary objects
        """
        # Default to current month if dates not provided
        if not end_date:
            end_date = timezone.now().date()
        if not start_date:
            start_date = end_date.replace(day=1)
        
        if transaction_type == 'INCOME':
            qs = Income.objects.for_user(user).filter(
                transaction_date__gte=start_date,
                transaction_date__lte=end_date
            )
            category_field = 'category'
        else:
            qs = Expense.objects.for_user(user).filter(
                transaction_date__gte=start_date,
                transaction_date__lte=end_date
            )
            category_field = 'category'
        
        # Group by category and calculate totals
        category_data = qs.values(
            f'{category_field}__id',
            f'{category_field}__name',
            f'{category_field}__color'
        ).annotate(
            total_amount=Sum('amount'),
            transaction_count=Count('id')
        ).order_by('-total_amount')
        
        # Calculate total for percentage
        total = qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Build category summaries
        summaries = []
        for item in category_data:
            percentage = (item['total_amount'] / total * 100) if total > 0 else Decimal('0.00')
            
            summaries.append(CategorySummary(
                category_name=item[f'{category_field}__name'],
                category_id=str(item[f'{category_field}__id']),
                total_amount=item['total_amount'],
                transaction_count=item['transaction_count'],
                percentage=percentage,
                color=item[f'{category_field}__color']
            ))
        
        return summaries
    
    @staticmethod
    def get_trend_analysis(
        user,
        months: int = 6
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate trend analysis for the last N months.
        
        Args:
            user: The user to generate the report for
            months: Number of months to analyze
            
        Returns:
            Dictionary containing trend data
        """
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30 * months)
        
        # Get monthly data
        monthly_data = []
        current_date = start_date.replace(day=1)
        
        while current_date <= end_date:
            month_start = current_date
            
            # Calculate last day of month
            if month_start.month == 12:
                month_end = date(month_start.year + 1, 1, 1) - timedelta(days=1)
            else:
                month_end = date(month_start.year, month_start.month + 1, 1) - timedelta(days=1)
            
            # Get data for this month using proper filtering
            income_qs = Income.objects.for_user(user).filter(
                transaction_date__gte=month_start,
                transaction_date__lte=month_end
            )
            income = income_qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            expense_qs = Expense.objects.for_user(user).filter(
                transaction_date__gte=month_start,
                transaction_date__lte=month_end
            )
            expense = expense_qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            monthly_data.append({
                'month': month_start.strftime('%Y-%m'),
                'month_name': month_start.strftime('%B %Y'),
                'income': float(income),
                'expense': float(expense),
                'net': float(income - expense)
            })
            
            # Move to next month
            if current_date.month == 12:
                current_date = date(current_date.year + 1, 1, 1)
            else:
                current_date = date(current_date.year, current_date.month + 1, 1)
        
        return {
            'monthly_trend': monthly_data,
            'period_start': start_date,
            'period_end': end_date
        }
    
    @staticmethod
    def get_top_expenses(
        user,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get top N expenses for a user.
        
        Args:
            user: The user to query for
            start_date: Optional start date
            end_date: Optional end date
            limit: Number of top expenses to return
            
        Returns:
            List of expense dictionaries
        """
        if not end_date:
            end_date = timezone.now().date()
        if not start_date:
            start_date = end_date.replace(day=1)
        
        expenses = Expense.objects.for_user(user).filter(
            transaction_date__gte=start_date,
            transaction_date__lte=end_date
        ).select_related('category').order_by('-amount')[:limit]
        
        return [
            {
                'id': str(expense.id),
                'amount': float(expense.amount),
                'description': expense.description,
                'category': expense.category.name,
                'date': expense.transaction_date.isoformat(),
                'vendor': expense.vendor,
            }
            for expense in expenses
        ]
    
    @staticmethod
    def get_budget_analysis(
        user,
        month: Optional[int] = None,
        year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Analyze budget utilization for expense categories.
        
        Args:
            user: The user to analyze for
            month: Month to analyze (defaults to current month)
            year: Year to analyze (defaults to current year)
            
        Returns:
            List of budget analysis data
        """
        now = timezone.now()
        month = month or now.month
        year = year or now.year
        
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        # Get categories with budget limits
        categories = ExpenseCategory.objects.active().filter(
            budget_limit__isnull=False
        )
        
        analysis = []
        for category in categories:
            # Calculate total expenses for this category
            expense_qs = Expense.objects.for_user(user).filter(
                transaction_date__gte=start_date,
                transaction_date__lte=end_date,
                category=category
            )
            total_spent = expense_qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            budget_limit = category.budget_limit
            utilization = (total_spent / budget_limit * 100) if budget_limit > 0 else Decimal('0.00')
            remaining = budget_limit - total_spent
            
            analysis.append({
                'category_id': str(category.id),
                'category_name': category.name,
                'budget_limit': float(budget_limit),
                'total_spent': float(total_spent),
                'remaining': float(remaining),
                'utilization_percentage': float(utilization),
                'is_over_budget': total_spent > budget_limit,
                'color': category.color
            })
        
        # Sort by utilization percentage (highest first)
        analysis.sort(key=lambda x: x['utilization_percentage'], reverse=True)
        
        return analysis


class AnalyticsService:
    """
    Advanced analytics service with statistical methods.
    """
    
    @staticmethod
    def get_spending_patterns(
        user,
        months: int = 12
    ) -> Dict[str, Any]:
        """
        Analyze spending patterns over time.
        
        Args:
            user: The user to analyze
            months: Number of months to analyze
            
        Returns:
            Dictionary containing pattern analysis
        """
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30 * months)
        
        expenses = Expense.objects.for_user(user).filter(
            transaction_date__gte=start_date,
            transaction_date__lte=end_date
        )
        
        # Day of week analysis
        expenses_by_day = expenses.extra(
            select={'day_of_week': 'strftime("%%w", transaction_date)'}
        ).values('day_of_week').annotate(
            total=Sum('amount'),
            count=Count('id')
        )
        
        # Payment method analysis
        payment_method_data = expenses.values('payment_method').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')
        
        return {
            'expenses_by_day_of_week': list(expenses_by_day),
            'expenses_by_payment_method': list(payment_method_data),
            'period_start': start_date,
            'period_end': end_date
        }

