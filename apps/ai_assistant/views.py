"""
Views for AI assistant chatbot.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from decimal import Decimal

from apps.ai_assistant.nlp_parser import TransactionParser, ConversationalBot
from apps.categories.models import IncomeCategory, ExpenseCategory
from apps.transactions.models import Income, Expense


@login_required
def chat_assistant_view(request):
    """Chat assistant page."""
    return render(request, 'web/chat_assistant.html')


@login_required
@require_http_methods(["POST"])
def parse_transaction_api(request):
    """
    API endpoint to parse natural language transaction input.
    """
    try:
        data = json.loads(request.body)
        message = data.get('message', '')
        context = data.get('context', {})
        
        if not message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        # Use conversational bot
        bot = ConversationalBot()
        result = bot.process_message(message, context)
        
        # If asking for category, fetch available categories
        if result['response'].get('requires_fetch'):
            trans_type = result['context'].get('type', 'expense')
            if trans_type == 'income':
                categories = list(IncomeCategory.objects.filter(
                    is_active=True
                ).values('id', 'name'))
            else:
                categories = list(ExpenseCategory.objects.filter(
                    is_active=True
                ).values('id', 'name'))
            
            result['response']['categories'] = categories
        
        return JsonResponse(result)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def create_transaction_from_chat_api(request):
    """
    API endpoint to create transaction from parsed data.
    """
    try:
        data = json.loads(request.body)
        trans_type = data.get('type')
        amount = data.get('amount')
        category_name = data.get('category')
        date = data.get('date')
        description = data.get('description', '')
        
        if not all([trans_type, amount, category_name, date]):
            return JsonResponse({
                'error': 'Missing required fields'
            }, status=400)
        
        # Convert amount to Decimal
        amount = Decimal(str(amount))
        
        # Find or create category
        if trans_type == 'income':
            category = IncomeCategory.objects.filter(
                name__iexact=category_name,
                is_active=True
            ).first()
            
            if not category:
                # Try to create it if user has permission
                if request.user.can_create_categories():
                    category = IncomeCategory.objects.create(
                        name=category_name.title(),
                        created_by=request.user
                    )
                else:
                    return JsonResponse({
                        'error': f'Category "{category_name}" not found'
                    }, status=400)
            
            # Create income transaction
            income = Income.objects.create(
                amount=amount,
                description=description or f"Income via chat: {category_name}",
                transaction_date=date,
                category=category,
                source=data.get('source', ''),
                created_by=request.user,
                status='COMPLETED'
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Income added successfully!',
                'transaction': {
                    'id': str(income.id),
                    'type': 'income',
                    'amount': float(amount),
                    'category': category.name,
                    'date': date
                }
            })
        
        else:  # expense
            category = ExpenseCategory.objects.filter(
                name__iexact=category_name,
                is_active=True
            ).first()
            
            if not category:
                # Try to create it if user has permission
                if request.user.can_create_categories():
                    category = ExpenseCategory.objects.create(
                        name=category_name.title(),
                        created_by=request.user
                    )
                else:
                    return JsonResponse({
                        'error': f'Category "{category_name}" not found'
                    }, status=400)
            
            # Create expense transaction
            expense = Expense.objects.create(
                amount=amount,
                description=description or f"Expense via chat: {category_name}",
                transaction_date=date,
                category=category,
                payment_method=data.get('payment_method', 'CASH'),
                vendor=data.get('vendor', ''),
                created_by=request.user,
                status='COMPLETED'
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Expense added successfully!',
                'transaction': {
                    'id': str(expense.id),
                    'type': 'expense',
                    'amount': float(amount),
                    'category': category.name,
                    'date': date
                }
            })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def quick_suggestions_api(request):
    """
    API endpoint to get quick suggestion templates.
    """
    suggestions = [
        "Add income of ₹50000 under salary today",
        "Spent ₹500 on groceries yesterday",
        "Add expense of ₹2000 for electricity bill on 15th",
        "Received ₹10000 from freelance project",
        "Paid ₹5000 rent via bank transfer",
    ]
    
    return JsonResponse({'suggestions': suggestions})

