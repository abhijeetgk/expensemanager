"""
Views for transactions app.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone

from apps.transactions.models import Income, Expense
from apps.transactions.serializers import (
    IncomeSerializer, ExpenseSerializer, TransactionBulkSerializer
)
from apps.accounts.permissions import IsOwnerOrAdmin


class IncomeViewSet(viewsets.ModelViewSet):
    """ViewSet for managing income transactions."""
    
    serializer_class = IncomeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'status', 'is_recurring', 'transaction_date']
    search_fields = ['description', 'source', 'reference_number']
    ordering_fields = ['transaction_date', 'amount', 'created_at']
    
    def get_queryset(self):
        """Filter queryset based on user permissions."""
        user = self.request.user
        return Income.objects.for_user(user)
    
    def perform_create(self, serializer):
        """Set created_by on creation."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark income as completed."""
        income = self.get_object()
        income.complete()
        return Response({'message': 'Income marked as completed'})
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel income."""
        income = self.get_object()
        reason = request.data.get('reason', '')
        income.cancel(reason)
        return Response({'message': 'Income cancelled successfully'})
    
    @action(detail=True, methods=['post'])
    def add_tag(self, request, pk=None):
        """Add tag to income."""
        income = self.get_object()
        tag = request.data.get('tag')
        
        if not tag:
            return Response(
                {'error': 'Tag is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        income.add_tag(tag)
        return Response({'message': 'Tag added successfully'})
    
    @action(detail=False, methods=['get'])
    def recurring(self, request):
        """Get recurring income."""
        incomes = self.get_queryset().filter(is_recurring=True)
        serializer = self.get_serializer(incomes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get income summary."""
        queryset = self.get_queryset()
        
        # Date filtering
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date and end_date:
            queryset = queryset.for_date_range(start_date, end_date)
        
        total = queryset.total_amount()
        count = queryset.count()
        
        return Response({
            'total_amount': float(total),
            'transaction_count': count,
            'average_amount': float(total / count) if count > 0 else 0.0
        })


class ExpenseViewSet(viewsets.ModelViewSet):
    """ViewSet for managing expense transactions."""
    
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        'category', 'status', 'payment_method',
        'is_reimbursable', 'reimbursed', 'transaction_date'
    ]
    search_fields = ['description', 'vendor', 'reference_number', 'location']
    ordering_fields = ['transaction_date', 'amount', 'created_at']
    
    def get_queryset(self):
        """Filter queryset based on user permissions."""
        user = self.request.user
        return Expense.objects.for_user(user)
    
    def perform_create(self, serializer):
        """Set created_by on creation."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark expense as completed."""
        expense = self.get_object()
        expense.complete()
        return Response({'message': 'Expense marked as completed'})
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel expense."""
        expense = self.get_object()
        reason = request.data.get('reason', '')
        expense.cancel(reason)
        return Response({'message': 'Expense cancelled successfully'})
    
    @action(detail=True, methods=['post'])
    def mark_reimbursed(self, request, pk=None):
        """Mark expense as reimbursed."""
        expense = self.get_object()
        
        if not expense.is_reimbursable:
            return Response(
                {'error': 'This expense is not marked as reimbursable'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        expense.mark_reimbursed()
        return Response({'message': 'Expense marked as reimbursed'})
    
    @action(detail=True, methods=['post'])
    def add_tag(self, request, pk=None):
        """Add tag to expense."""
        expense = self.get_object()
        tag = request.data.get('tag')
        
        if not tag:
            return Response(
                {'error': 'Tag is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        expense.add_tag(tag)
        return Response({'message': 'Tag added successfully'})
    
    @action(detail=False, methods=['get'])
    def pending_reimbursement(self, request):
        """Get expenses pending reimbursement."""
        expenses = self.get_queryset().filter(
            is_reimbursable=True,
            reimbursed=False
        )
        serializer = self.get_serializer(expenses, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get expense summary."""
        queryset = self.get_queryset()
        
        # Date filtering
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date and end_date:
            queryset = queryset.for_date_range(start_date, end_date)
        
        total = queryset.total_amount()
        count = queryset.count()
        
        # Payment method breakdown
        payment_methods = {}
        for method in queryset.values_list('payment_method', flat=True).distinct():
            method_total = queryset.filter(payment_method=method).total_amount()
            payment_methods[method] = float(method_total)
        
        return Response({
            'total_amount': float(total),
            'transaction_count': count,
            'average_amount': float(total / count) if count > 0 else 0.0,
            'by_payment_method': payment_methods
        })
    
    @action(detail=False, methods=['post'])
    def bulk_action(self, request):
        """Perform bulk action on expenses."""
        serializer = TransactionBulkSerializer(data=request.data)
        
        if serializer.is_valid():
            transaction_ids = serializer.validated_data['transaction_ids']
            action_type = serializer.validated_data['action']
            reason = serializer.validated_data.get('reason', '')
            
            expenses = self.get_queryset().filter(id__in=transaction_ids)
            
            if action_type == 'complete':
                for expense in expenses:
                    expense.complete()
                message = f'{expenses.count()} expenses marked as completed'
            
            elif action_type == 'cancel':
                for expense in expenses:
                    expense.cancel(reason)
                message = f'{expenses.count()} expenses cancelled'
            
            elif action_type == 'delete':
                for expense in expenses:
                    expense.soft_delete(request.user)
                message = f'{expenses.count()} expenses deleted'
            
            return Response({'message': message})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

