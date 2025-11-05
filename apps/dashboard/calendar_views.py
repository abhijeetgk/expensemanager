"""
Calendar views for transaction visualization.
"""

from datetime import datetime, timedelta
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum
from django.utils import timezone
from decimal import Decimal

from apps.transactions.models import Income, Expense


@login_required
def calendar_view(request):
    """Calendar view page."""
    return render(request, 'web/calendar.html')


@login_required
def calendar_events_api(request):
    """
    API endpoint for calendar events.
    Returns transactions formatted for FullCalendar.
    """
    # Get date range from query params
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    
    if start_date:
        start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00')).date()
    if end_date:
        end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00')).date()
    
    user = request.user
    events = []
    
    # Get income transactions
    income_qs = Income.objects.for_user(user)
    if start_date and end_date:
        income_qs = income_qs.filter(
            transaction_date__gte=start_date,
            transaction_date__lte=end_date
        )
    
    for income in income_qs.select_related('category'):
        events.append({
            'id': f'income-{income.id}',
            'title': f'💰 {income.category.name}: ₹{income.amount}',
            'start': income.transaction_date.isoformat(),
            'backgroundColor': '#10B981',
            'borderColor': '#059669',
            'textColor': '#FFFFFF',
            'extendedProps': {
                'type': 'income',
                'amount': float(income.amount),
                'description': income.description,
                'category': income.category.name,
                'source': income.source,
                'transactionId': str(income.id)
            }
        })
    
    # Get expense transactions
    expense_qs = Expense.objects.for_user(user)
    if start_date and end_date:
        expense_qs = expense_qs.filter(
            transaction_date__gte=start_date,
            transaction_date__lte=end_date
        )
    
    for expense in expense_qs.select_related('category'):
        events.append({
            'id': f'expense-{expense.id}',
            'title': f'💸 {expense.category.name}: ₹{expense.amount}',
            'start': expense.transaction_date.isoformat(),
            'backgroundColor': '#EF4444',
            'borderColor': '#DC2626',
            'textColor': '#FFFFFF',
            'extendedProps': {
                'type': 'expense',
                'amount': float(expense.amount),
                'description': expense.description,
                'category': expense.category.name,
                'vendor': expense.vendor,
                'payment_method': expense.payment_method,
                'transactionId': str(expense.id)
            }
        })
    
    return JsonResponse(events, safe=False)


@login_required
def calendar_day_summary_api(request):
    """
    API endpoint for daily summary.
    Returns aggregated income/expense for a specific date.
    """
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'error': 'Date parameter required'}, status=400)
    
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)
    
    user = request.user
    
    # Get income for the day
    income_total = Income.objects.for_user(user).filter(
        transaction_date=date
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    income_list = Income.objects.for_user(user).filter(
        transaction_date=date
    ).select_related('category').values(
        'id', 'amount', 'description', 'category__name', 'source'
    )
    
    # Get expenses for the day
    expense_total = Expense.objects.for_user(user).filter(
        transaction_date=date
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    expense_list = Expense.objects.for_user(user).filter(
        transaction_date=date
    ).select_related('category').values(
        'id', 'amount', 'description', 'category__name', 'vendor', 'payment_method'
    )
    
    return JsonResponse({
        'date': date_str,
        'income_total': float(income_total),
        'expense_total': float(expense_total),
        'net_balance': float(income_total - expense_total),
        'income_transactions': list(income_list),
        'expense_transactions': list(expense_list)
    })


@login_required
def calendar_month_summary_api(request):
    """
    API endpoint for monthly summary.
    Returns aggregated data for a specific month.
    """
    year = int(request.GET.get('year', timezone.now().year))
    month = int(request.GET.get('month', timezone.now().month))
    
    # Get first and last day of month
    first_day = datetime(year, month, 1).date()
    if month == 12:
        last_day = datetime(year + 1, 1, 1).date() - timedelta(days=1)
    else:
        last_day = datetime(year, month + 1, 1).date() - timedelta(days=1)
    
    user = request.user
    
    # Get income for the month
    income_total = Income.objects.for_user(user).filter(
        transaction_date__gte=first_day,
        transaction_date__lte=last_day
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    income_by_category = Income.objects.for_user(user).filter(
        transaction_date__gte=first_day,
        transaction_date__lte=last_day
    ).values('category__name').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # Get expenses for the month
    expense_total = Expense.objects.for_user(user).filter(
        transaction_date__gte=first_day,
        transaction_date__lte=last_day
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    expense_by_category = Expense.objects.for_user(user).filter(
        transaction_date__gte=first_day,
        transaction_date__lte=last_day
    ).values('category__name').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # Get daily totals for the month
    daily_data = []
    current_date = first_day
    while current_date <= last_day:
        day_income = Income.objects.for_user(user).filter(
            transaction_date=current_date
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        day_expense = Expense.objects.for_user(user).filter(
            transaction_date=current_date
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        if day_income > 0 or day_expense > 0:
            daily_data.append({
                'date': current_date.isoformat(),
                'income': float(day_income),
                'expense': float(day_expense),
                'net': float(day_income - day_expense)
            })
        
        current_date += timedelta(days=1)
    
    return JsonResponse({
        'year': year,
        'month': month,
        'income_total': float(income_total),
        'expense_total': float(expense_total),
        'net_balance': float(income_total - expense_total),
        'income_by_category': list(income_by_category),
        'expense_by_category': list(expense_by_category),
        'daily_data': daily_data
    })

