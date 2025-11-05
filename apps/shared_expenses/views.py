"""
Views for shared expenses management.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.shared_expenses.models import ExpenseGroup, SharedExpense, SharedExpenseSplit, Debt, DebtPayment
from apps.shared_expenses.serializers import (
    ExpenseGroupSerializer, SharedExpenseSerializer, SharedExpenseSplitSerializer,
    DebtSerializer, DebtPaymentSerializer
)


class ExpenseGroupViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing expense groups.
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = ExpenseGroupSerializer
    
    def get_queryset(self):
        """Return groups where user is a member."""
        return ExpenseGroup.objects.filter(
            members=self.request.user,
            is_deleted=False
        ).distinct()
    
    @action(detail=True, methods=['get'])
    def balance_summary(self, request, pk=None):
        """Get balance summary for all members of the group."""
        group = self.get_object()
        summary = group.get_balance_summary()
        
        result = []
        for user, data in summary.items():
            result.append({
                'user': user.username,
                'user_id': str(user.id),
                'paid': float(data['paid']),
                'owed': float(data['owed']),
                'balance': float(data['balance'])
            })
        
        return Response(result)


class SharedExpenseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing shared expenses.
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = SharedExpenseSerializer
    
    def get_queryset(self):
        """Return shared expenses for user's groups."""
        user_groups = ExpenseGroup.objects.filter(members=self.request.user)
        return SharedExpense.objects.filter(
            group__in=user_groups,
            is_deleted=False
        )
    
    @action(detail=True, methods=['post'])
    def create_equal_splits(self, request, pk=None):
        """Create equal splits for all group members."""
        shared_expense = self.get_object()
        member_ids = request.data.get('members', [])
        
        if member_ids:
            members = shared_expense.group.members.filter(id__in=member_ids)
        else:
            members = None
        
        shared_expense.create_equal_splits(members)
        
        return Response({
            'message': 'Splits created successfully',
            'splits': SharedExpenseSplitSerializer(shared_expense.splits.all(), many=True).data
        })


class DebtViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing debts.
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = DebtSerializer
    
    def get_queryset(self):
        """Return debts where user is creditor or debtor."""
        from django.db.models import Q
        return Debt.objects.filter(
            Q(creditor=self.request.user) | Q(debtor=self.request.user),
            is_deleted=False
        )
    
    @action(detail=False, methods=['get'])
    def my_debts(self, request):
        """Get debts owed by the current user."""
        debts = Debt.objects.filter(debtor=request.user, is_deleted=False)
        serializer = self.get_serializer(debts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def owed_to_me(self, request):
        """Get debts owed to the current user."""
        debts = Debt.objects.filter(creditor=request.user, is_deleted=False)
        serializer = self.get_serializer(debts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_payment(self, request, pk=None):
        """Add a payment towards the debt."""
        debt = self.get_object()
        amount = request.data.get('amount')
        notes = request.data.get('notes', '')
        
        if not amount:
            return Response(
                {'error': 'Amount is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        debt.add_payment(amount, notes)
        
        return Response({
            'message': 'Payment recorded successfully',
            'remaining': float(debt.remaining_amount)
        })
    
    @action(detail=True, methods=['post'])
    def settle(self, request, pk=None):
        """Settle the debt in full."""
        debt = self.get_object()
        notes = request.data.get('notes', '')
        
        debt.settle_full(notes)
        
        return Response({
            'message': 'Debt settled successfully'
        })

