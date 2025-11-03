"""
Web interface views for user-facing pages.

Provides login, dashboard, transaction management, and reports.
"""

from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from decimal import Decimal

from apps.accounts.models import User
from apps.categories.models import IncomeCategory, ExpenseCategory
from apps.transactions.models import Income, Expense
from apps.reports.services import ReportService


def login_view(request):
    """User login page."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name()}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'web/login.html')


def logout_view(request):
    """User logout."""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def dashboard_view(request):
    """User dashboard with statistics and charts."""
    user = request.user
    
    # Current month data
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).date()
    
    # Get current month transactions
    month_income_qs = Income.objects.for_user(user).filter(transaction_date__gte=month_start)
    month_income = month_income_qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    month_expense_qs = Expense.objects.for_user(user).filter(transaction_date__gte=month_start)
    month_expense = month_expense_qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    # Overall statistics
    total_income_qs = Income.objects.for_user(user)
    total_income = total_income_qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    total_expense_qs = Expense.objects.for_user(user)
    total_expense = total_expense_qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    # Recent transactions
    recent_income = Income.objects.for_user(user).select_related('category')[:5]
    recent_expense = Expense.objects.for_user(user).select_related('category')[:5]
    
    # Category breakdown for current month
    expense_by_category = Expense.objects.for_user(user).filter(
        transaction_date__gte=month_start
    ).values('category__name', 'category__color').annotate(
        total=Sum('amount')
    ).order_by('-total')[:5]
    
    # Pending reimbursements
    pending_reimbursement_qs = Expense.objects.for_user(user).filter(
        is_reimbursable=True,
        reimbursed=False
    )
    pending_reimbursement = pending_reimbursement_qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    context = {
        'month_income': month_income,
        'month_expense': month_expense,
        'month_balance': month_income - month_expense,
        'total_income': total_income,
        'total_expense': total_expense,
        'total_balance': total_income - total_expense,
        'recent_income': recent_income,
        'recent_expense': recent_expense,
        'expense_by_category': expense_by_category,
        'pending_reimbursement': pending_reimbursement,
        'current_month': now.strftime('%B %Y'),
    }
    
    return render(request, 'web/dashboard.html', context)


@login_required
def add_income_view(request):
    """Add income entry."""
    if request.method == 'POST':
        try:
            income = Income.objects.create(
                amount=Decimal(request.POST.get('amount')),
                description=request.POST.get('description'),
                transaction_date=request.POST.get('transaction_date'),
                category_id=request.POST.get('category'),
                source=request.POST.get('source', ''),
                created_by=request.user,
                status='COMPLETED'
            )
            messages.success(request, 'Income entry added successfully!')
            return redirect('income_list')
        except Exception as e:
            messages.error(request, f'Error adding income: {str(e)}')
    
    categories = IncomeCategory.objects.filter(is_active=True).order_by('name')
    
    context = {
        'categories': categories,
        'today': datetime.now().date()
    }
    
    return render(request, 'web/add_income.html', context)


@login_required
def add_expense_view(request):
    """Add expense entry."""
    if request.method == 'POST':
        try:
            expense = Expense.objects.create(
                amount=Decimal(request.POST.get('amount')),
                description=request.POST.get('description'),
                transaction_date=request.POST.get('transaction_date'),
                category_id=request.POST.get('category'),
                payment_method=request.POST.get('payment_method', 'CASH'),
                vendor=request.POST.get('vendor', ''),
                location=request.POST.get('location', ''),
                created_by=request.user,
                status='COMPLETED'
            )
            
            # Handle receipt upload
            if request.FILES.get('receipt'):
                expense.receipt = request.FILES['receipt']
                expense.save()
            
            messages.success(request, 'Expense entry added successfully!')
            return redirect('expense_list')
        except Exception as e:
            messages.error(request, f'Error adding expense: {str(e)}')
    
    categories = ExpenseCategory.objects.filter(is_active=True).order_by('name')
    
    context = {
        'categories': categories,
        'today': datetime.now().date(),
        'payment_methods': [
            ('CASH', 'Cash'),
            ('CREDIT_CARD', 'Credit Card'),
            ('DEBIT_CARD', 'Debit Card'),
            ('BANK_TRANSFER', 'Bank Transfer'),
            ('MOBILE_PAYMENT', 'Mobile Payment'),
        ]
    }
    
    return render(request, 'web/add_expense.html', context)


@login_required
def income_list_view(request):
    """List all income transactions."""
    incomes = Income.objects.for_user(request.user).select_related('category').order_by('-transaction_date')
    
    # Filtering
    category = request.GET.get('category')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if category:
        incomes = incomes.filter(category_id=category)
    if start_date:
        incomes = incomes.filter(transaction_date__gte=start_date)
    if end_date:
        incomes = incomes.filter(transaction_date__lte=end_date)
    
    total = incomes.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    categories = IncomeCategory.objects.filter(is_active=True).order_by('name')
    
    context = {
        'incomes': incomes,
        'total': total,
        'categories': categories,
    }
    
    return render(request, 'web/income_list.html', context)


@login_required
def expense_list_view(request):
    """List all expense transactions."""
    expenses = Expense.objects.for_user(request.user).select_related('category').order_by('-transaction_date')
    
    # Filtering
    category = request.GET.get('category')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    payment_method = request.GET.get('payment_method')
    
    if category:
        expenses = expenses.filter(category_id=category)
    if start_date:
        expenses = expenses.filter(transaction_date__gte=start_date)
    if end_date:
        expenses = expenses.filter(transaction_date__lte=end_date)
    if payment_method:
        expenses = expenses.filter(payment_method=payment_method)
    
    total = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    categories = ExpenseCategory.objects.filter(is_active=True).order_by('name')
    
    context = {
        'expenses': expenses,
        'total': total,
        'categories': categories,
    }
    
    return render(request, 'web/expense_list.html', context)


@login_required
def reports_view(request):
    """Reports and analytics page."""
    user = request.user
    
    # Get date range
    end_date = datetime.now().date()
    start_date = request.GET.get('start_date')
    end_date_param = request.GET.get('end_date')
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    else:
        start_date = end_date.replace(day=1)
    
    if end_date_param:
        end_date = datetime.strptime(end_date_param, '%Y-%m-%d').date()
    
    # Get report data
    report = ReportService.get_summary_report(user, start_date, end_date)
    category_breakdown = ReportService.get_category_wise_report(user, 'EXPENSE', start_date, end_date)
    trend_data = ReportService.get_trend_analysis(user, months=6)
    
    context = {
        'report': report,
        'category_breakdown': category_breakdown,
        'trend_data': trend_data,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'web/reports.html', context)


@login_required
def delete_income_view(request, pk):
    """Delete income entry."""
    income = get_object_or_404(Income, pk=pk, created_by=request.user)
    income.soft_delete(request.user)
    messages.success(request, 'Income entry deleted successfully!')
    return redirect('income_list')


@login_required
def delete_expense_view(request, pk):
    """Delete expense entry."""
    expense = get_object_or_404(Expense, pk=pk, created_by=request.user)
    expense.soft_delete(request.user)
    messages.success(request, 'Expense entry deleted successfully!')
    return redirect('expense_list')

