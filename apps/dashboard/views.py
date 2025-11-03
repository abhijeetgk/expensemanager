"""
Dashboard views for admin analytics and widgets.

Demonstrates:
- Dashboard service layer
- Widget pattern
- Chart data preparation
"""

from datetime import datetime, timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count
from django.utils import timezone

from apps.accounts.permissions import IsAdmin
from apps.transactions.models import Income, Expense
from apps.categories.models import IncomeCategory, ExpenseCategory
from apps.accounts.models import User
from apps.reports.services import ReportService


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def dashboard_stats(request):
    """
    Get dashboard statistics for admin.
    
    Returns overall system statistics.
    """
    now = timezone.now()
    current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # User statistics
    total_users = User.objects.count()
    active_users = User.active.count()
    new_users_this_month = User.objects.filter(
        date_joined__gte=current_month_start
    ).count()
    
    # Category statistics
    income_categories = IncomeCategory.objects.active().count()
    expense_categories = ExpenseCategory.objects.active().count()
    
    # Transaction statistics
    total_income = Income.objects.completed().total_amount()
    total_expense = Expense.objects.completed().total_amount()
    
    # Current month statistics
    current_month_income = Income.objects.completed().filter(
        transaction_date__gte=current_month_start.date()
    ).total_amount()
    current_month_expense = Expense.objects.completed().filter(
        transaction_date__gte=current_month_start.date()
    ).total_amount()
    
    # Transaction counts
    total_transactions = (
        Income.objects.completed().count() + 
        Expense.objects.completed().count()
    )
    
    return Response({
        'users': {
            'total': total_users,
            'active': active_users,
            'new_this_month': new_users_this_month
        },
        'categories': {
            'income': income_categories,
            'expense': expense_categories,
            'total': income_categories + expense_categories
        },
        'transactions': {
            'total_count': total_transactions,
            'total_income': float(total_income),
            'total_expense': float(total_expense),
            'net_balance': float(total_income - total_expense)
        },
        'current_month': {
            'income': float(current_month_income),
            'expense': float(current_month_expense),
            'net': float(current_month_income - current_month_expense)
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def income_expense_chart(request):
    """
    Get income vs expense chart data for the last N months.
    
    Query params:
        - months: Number of months (default: 6)
    """
    months = int(request.query_params.get('months', 6))
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30 * months)
    
    chart_data = []
    current_date = start_date.replace(day=1)
    
    while current_date <= end_date:
        month_start = current_date
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)
        
        # Get income and expense for this month
        income = Income.objects.completed().filter(
            transaction_date__gte=month_start,
            transaction_date__lte=month_end
        ).total_amount()
        
        expense = Expense.objects.completed().filter(
            transaction_date__gte=month_start,
            transaction_date__lte=month_end
        ).total_amount()
        
        chart_data.append({
            'month': month_start.strftime('%b %Y'),
            'income': float(income),
            'expense': float(expense),
            'net': float(income - expense)
        })
        
        # Move to next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    return Response({
        'chart_type': 'line',
        'data': chart_data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def category_breakdown_chart(request):
    """
    Get category breakdown chart data.
    
    Query params:
        - type: Transaction type ('income' or 'expense', default: 'expense')
        - period: Period ('month', 'quarter', 'year', default: 'month')
    """
    transaction_type = request.query_params.get('type', 'expense').lower()
    period = request.query_params.get('period', 'month').lower()
    
    # Calculate date range based on period
    end_date = timezone.now().date()
    if period == 'month':
        start_date = end_date.replace(day=1)
    elif period == 'quarter':
        quarter_month = ((end_date.month - 1) // 3) * 3 + 1
        start_date = end_date.replace(month=quarter_month, day=1)
    else:  # year
        start_date = end_date.replace(month=1, day=1)
    
    if transaction_type == 'income':
        queryset = Income.objects.completed().filter(
            transaction_date__gte=start_date,
            transaction_date__lte=end_date
        )
        category_data = queryset.values(
            'category__name', 'category__color'
        ).annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')
    else:
        queryset = Expense.objects.completed().filter(
            transaction_date__gte=start_date,
            transaction_date__lte=end_date
        )
        category_data = queryset.values(
            'category__name', 'category__color'
        ).annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')
    
    total = queryset.total_amount()
    
    chart_data = [
        {
            'category': item['category__name'],
            'amount': float(item['total']),
            'count': item['count'],
            'percentage': float((item['total'] / total * 100)) if total > 0 else 0.0,
            'color': item['category__color']
        }
        for item in category_data
    ]
    
    return Response({
        'chart_type': 'pie',
        'transaction_type': transaction_type,
        'period': period,
        'data': chart_data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def top_users_widget(request):
    """
    Get top users by transaction volume.
    
    Query params:
        - limit: Number of users (default: 10)
        - period: Period in days (default: 30)
    """
    limit = int(request.query_params.get('limit', 10))
    period = int(request.query_params.get('period', 30))
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=period)
    
    # Get user transaction statistics
    user_stats = []
    
    for user in User.active.all()[:limit]:
        income = Income.objects.completed().filter(
            created_by=user,
            transaction_date__gte=start_date,
            transaction_date__lte=end_date
        ).total_amount()
        
        expense = Expense.objects.completed().filter(
            created_by=user,
            transaction_date__gte=start_date,
            transaction_date__lte=end_date
        ).total_amount()
        
        total_transactions = (
            Income.objects.completed().filter(created_by=user).count() +
            Expense.objects.completed().filter(created_by=user).count()
        )
        
        user_stats.append({
            'user_id': str(user.id),
            'username': user.username,
            'full_name': user.get_full_name(),
            'email': user.email,
            'total_income': float(income),
            'total_expense': float(expense),
            'transaction_count': total_transactions
        })
    
    # Sort by transaction count
    user_stats.sort(key=lambda x: x['transaction_count'], reverse=True)
    
    return Response({
        'top_users': user_stats[:limit],
        'period_days': period
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def recent_transactions_widget(request):
    """
    Get recent transactions across all users.
    
    Query params:
        - limit: Number of transactions (default: 10)
    """
    limit = int(request.query_params.get('limit', 10))
    
    # Get recent income and expense transactions
    recent_income = Income.objects.completed().select_related(
        'category', 'created_by'
    ).order_by('-transaction_date', '-created_at')[:limit]
    
    recent_expense = Expense.objects.completed().select_related(
        'category', 'created_by'
    ).order_by('-transaction_date', '-created_at')[:limit]
    
    # Combine and format
    transactions = []
    
    for income in recent_income:
        transactions.append({
            'id': str(income.id),
            'type': 'income',
            'date': income.transaction_date.isoformat(),
            'amount': float(income.amount),
            'description': income.description,
            'category': income.category.name,
            'user': income.created_by.get_full_name() if income.created_by else 'Unknown'
        })
    
    for expense in recent_expense:
        transactions.append({
            'id': str(expense.id),
            'type': 'expense',
            'date': expense.transaction_date.isoformat(),
            'amount': float(expense.amount),
            'description': expense.description,
            'category': expense.category.name,
            'user': expense.created_by.get_full_name() if expense.created_by else 'Unknown'
        })
    
    # Sort by date
    transactions.sort(key=lambda x: x['date'], reverse=True)
    
    return Response({
        'recent_transactions': transactions[:limit]
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_dashboard_stats(request):
    """
    Get dashboard statistics for regular users.
    
    Returns statistics for the current user only.
    """
    user = request.user
    now = timezone.now()
    current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Current month statistics
    current_month_income = Income.objects.for_user(user).filter(
        transaction_date__gte=current_month_start.date()
    ).total_amount()
    
    current_month_expense = Expense.objects.for_user(user).filter(
        transaction_date__gte=current_month_start.date()
    ).total_amount()
    
    # Overall statistics
    total_income = Income.objects.for_user(user).total_amount()
    total_expense = Expense.objects.for_user(user).total_amount()
    
    # Transaction counts
    income_count = Income.objects.for_user(user).count()
    expense_count = Expense.objects.for_user(user).count()
    
    # Pending reimbursements
    pending_reimbursement = Expense.objects.for_user(user).filter(
        is_reimbursable=True,
        reimbursed=False
    ).total_amount()
    
    return Response({
        'current_month': {
            'income': float(current_month_income),
            'expense': float(current_month_expense),
            'net': float(current_month_income - current_month_expense),
            'savings_rate': float((current_month_income - current_month_expense) / current_month_income * 100) if current_month_income > 0 else 0.0
        },
        'overall': {
            'total_income': float(total_income),
            'total_expense': float(total_expense),
            'net_balance': float(total_income - total_expense)
        },
        'transactions': {
            'income_count': income_count,
            'expense_count': expense_count,
            'total_count': income_count + expense_count
        },
        'pending_reimbursement': float(pending_reimbursement)
    })

