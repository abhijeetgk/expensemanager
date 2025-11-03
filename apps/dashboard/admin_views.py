"""
Admin Dashboard Views

This module provides views for the admin dashboard with comprehensive
statistics, analytics, and management widgets.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from collections import defaultdict

from apps.accounts.models import User
from apps.categories.models import IncomeCategory, ExpenseCategory
from apps.transactions.models import Income, Expense


def is_admin_or_power_user(user):
    """Check if user is admin or power user."""
    return user.is_authenticated and user.role in ['ADMIN', 'POWER_USER']


@login_required
@user_passes_test(is_admin_or_power_user, login_url='/')
def admin_dashboard_view(request):
    """
    Admin dashboard with comprehensive statistics and analytics.
    
    Features:
    - Overall system statistics
    - User activity metrics
    - Category performance
    - Recent transactions
    - Trend analysis
    - Top users by spending/income
    """
    
    # Time periods
    now = timezone.now()
    today = now.date()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).date()
    week_start = (now - timedelta(days=now.weekday())).date()
    year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0).date()
    
    # ==================== USER STATISTICS ====================
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    admin_users = User.objects.filter(role='ADMIN').count()
    power_users = User.objects.filter(role='POWER_USER').count()
    regular_users = User.objects.filter(role='USER').count()
    
    # Users registered this month
    new_users_this_month = User.objects.filter(
        date_joined__gte=month_start
    ).count()
    
    # ==================== TRANSACTION STATISTICS ====================
    # All time
    total_income_qs = Income.objects.all()
    total_income = total_income_qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_income_count = total_income_qs.count()
    
    total_expense_qs = Expense.objects.all()
    total_expense = total_expense_qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_expense_count = total_expense_qs.count()
    
    # This month
    month_income_qs = Income.objects.filter(transaction_date__gte=month_start)
    month_income = month_income_qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    month_income_count = month_income_qs.count()
    
    month_expense_qs = Expense.objects.filter(transaction_date__gte=month_start)
    month_expense = month_expense_qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    month_expense_count = month_expense_qs.count()
    
    # This week
    week_income_qs = Income.objects.filter(transaction_date__gte=week_start)
    week_income = week_income_qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    week_expense_qs = Expense.objects.filter(transaction_date__gte=week_start)
    week_expense = week_expense_qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    # Today
    today_income_qs = Income.objects.filter(transaction_date=today)
    today_income = today_income_qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    today_expense_qs = Expense.objects.filter(transaction_date=today)
    today_expense = today_expense_qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    # ==================== CATEGORY STATISTICS ====================
    total_income_categories = IncomeCategory.objects.filter(is_active=True).count()
    total_expense_categories = ExpenseCategory.objects.filter(is_active=True).count()
    
    # Top income categories
    top_income_categories = Income.objects.filter(
        transaction_date__gte=month_start
    ).values(
        'category__name', 'category__color'
    ).annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')[:5]
    
    # Top expense categories
    top_expense_categories = Expense.objects.filter(
        transaction_date__gte=month_start
    ).values(
        'category__name', 'category__color'
    ).annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')[:5]
    
    # ==================== USER ACTIVITY ====================
    # Top users by expense
    top_spenders = Expense.objects.filter(
        transaction_date__gte=month_start
    ).values(
        'created_by__first_name', 'created_by__last_name', 'created_by__email'
    ).annotate(
        total_spent=Sum('amount'),
        transaction_count=Count('id')
    ).order_by('-total_spent')[:5]
    
    # Top users by income
    top_earners = Income.objects.filter(
        transaction_date__gte=month_start
    ).values(
        'created_by__first_name', 'created_by__last_name', 'created_by__email'
    ).annotate(
        total_earned=Sum('amount'),
        transaction_count=Count('id')
    ).order_by('-total_earned')[:5]
    
    # Most active users (by transaction count)
    active_users_list = []
    user_activity = defaultdict(lambda: {'income_count': 0, 'expense_count': 0, 'total_transactions': 0})
    
    for user in User.objects.filter(is_active=True)[:10]:
        income_count = Income.objects.filter(created_by=user, transaction_date__gte=month_start).count()
        expense_count = Expense.objects.filter(created_by=user, transaction_date__gte=month_start).count()
        total = income_count + expense_count
        
        if total > 0:
            active_users_list.append({
                'name': user.get_full_name() or user.email,
                'email': user.email,
                'income_count': income_count,
                'expense_count': expense_count,
                'total_transactions': total
            })
    
    active_users_list.sort(key=lambda x: x['total_transactions'], reverse=True)
    active_users_list = active_users_list[:5]
    
    # ==================== RECENT TRANSACTIONS ====================
    recent_income = Income.objects.select_related('created_by', 'category').order_by('-created_at')[:5]
    recent_expense = Expense.objects.select_related('created_by', 'category').order_by('-created_at')[:5]
    
    # ==================== TREND ANALYSIS (Last 7 days) ====================
    last_7_days = []
    daily_income = []
    daily_expense = []
    
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        last_7_days.append(day.strftime('%d %b'))
        
        day_income = Income.objects.filter(
            transaction_date=day
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        day_expense = Expense.objects.filter(
            transaction_date=day
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        daily_income.append(float(day_income))
        daily_expense.append(float(day_expense))
    
    # ==================== MONTHLY TREND (Last 6 months) ====================
    monthly_labels = []
    monthly_income_data = []
    monthly_expense_data = []
    
    for i in range(5, -1, -1):
        month_date = (now - timedelta(days=30*i)).replace(day=1)
        month_label = month_date.strftime('%b %Y')
        monthly_labels.append(month_label)
        
        month_start_date = month_date.date()
        if i == 0:
            month_end_date = today
        else:
            next_month = month_date.replace(day=28) + timedelta(days=4)
            month_end_date = (next_month - timedelta(days=next_month.day)).date()
        
        m_income = Income.objects.filter(
            transaction_date__gte=month_start_date,
            transaction_date__lte=month_end_date
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        m_expense = Expense.objects.filter(
            transaction_date__gte=month_start_date,
            transaction_date__lte=month_end_date
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        monthly_income_data.append(float(m_income))
        monthly_expense_data.append(float(m_expense))
    
    # ==================== PAYMENT METHOD BREAKDOWN ====================
    payment_methods = Expense.objects.filter(
        transaction_date__gte=month_start
    ).values('payment_method').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # ==================== REIMBURSEMENT STATS ====================
    pending_reimbursements = Expense.objects.filter(
        is_reimbursable=True,
        reimbursed=False
    ).aggregate(
        total=Sum('amount'),
        count=Count('id')
    )
    
    context = {
        # User stats
        'total_users': total_users,
        'active_users': active_users,
        'admin_users': admin_users,
        'power_users': power_users,
        'regular_users': regular_users,
        'new_users_this_month': new_users_this_month,
        
        # Transaction stats - All time
        'total_income': total_income,
        'total_expense': total_expense,
        'total_balance': total_income - total_expense,
        'total_income_count': total_income_count,
        'total_expense_count': total_expense_count,
        'total_transactions': total_income_count + total_expense_count,
        
        # Transaction stats - This month
        'month_income': month_income,
        'month_expense': month_expense,
        'month_balance': month_income - month_expense,
        'month_income_count': month_income_count,
        'month_expense_count': month_expense_count,
        
        # Transaction stats - This week
        'week_income': week_income,
        'week_expense': week_expense,
        'week_balance': week_income - week_expense,
        
        # Transaction stats - Today
        'today_income': today_income,
        'today_expense': today_expense,
        'today_balance': today_income - today_expense,
        
        # Category stats
        'total_income_categories': total_income_categories,
        'total_expense_categories': total_expense_categories,
        'top_income_categories': top_income_categories,
        'top_expense_categories': top_expense_categories,
        
        # User activity
        'top_spenders': top_spenders,
        'top_earners': top_earners,
        'active_users_list': active_users_list,
        
        # Recent transactions
        'recent_income': recent_income,
        'recent_expense': recent_expense,
        
        # Trends
        'last_7_days': last_7_days,
        'daily_income': daily_income,
        'daily_expense': daily_expense,
        'monthly_labels': monthly_labels,
        'monthly_income_data': monthly_income_data,
        'monthly_expense_data': monthly_expense_data,
        
        # Payment methods
        'payment_methods': payment_methods,
        
        # Reimbursements
        'pending_reimbursement_amount': pending_reimbursements['total'] or Decimal('0.00'),
        'pending_reimbursement_count': pending_reimbursements['count'] or 0,
        
        # Current period
        'current_month': now.strftime('%B %Y'),
        'current_date': now.strftime('%d %B %Y'),
    }
    
    return render(request, 'admin/admin_dashboard.html', context)

