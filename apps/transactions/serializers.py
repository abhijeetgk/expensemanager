"""
Serializers for transactions app.
"""

from rest_framework import serializers
from apps.transactions.models import Income, Expense
from apps.categories.serializers import IncomeCategorySerializer, ExpenseCategorySerializer


class IncomeSerializer(serializers.ModelSerializer):
    """Serializer for Income model."""
    
    category_detail = IncomeCategorySerializer(source='category', read_only=True)
    net_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    tax_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    formatted_amount = serializers.CharField(read_only=True)
    created_by_name = serializers.CharField(source='creator_name', read_only=True)
    
    class Meta:
        model = Income
        fields = [
            'id', 'amount', 'description', 'transaction_date', 'status',
            'category', 'category_detail', 'source', 'is_recurring',
            'recurrence_period', 'next_occurrence', 'tax_amount',
            'net_amount', 'tax_percentage', 'reference_number',
            'metadata', 'tags', 'formatted_amount', 'created_by',
            'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Create income with creator tracking."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        income = super().create(validated_data)
        
        # Set next occurrence if recurring
        if income.is_recurring:
            income.set_next_occurrence()
        
        return income


class ExpenseSerializer(serializers.ModelSerializer):
    """Serializer for Expense model."""
    
    category_detail = ExpenseCategorySerializer(source='category', read_only=True)
    formatted_amount = serializers.CharField(read_only=True)
    is_pending_reimbursement = serializers.BooleanField(read_only=True)
    created_by_name = serializers.CharField(source='creator_name', read_only=True)
    
    class Meta:
        model = Expense
        fields = [
            'id', 'amount', 'description', 'transaction_date', 'status',
            'category', 'category_detail', 'payment_method', 'vendor',
            'location', 'receipt', 'is_reimbursable', 'reimbursed',
            'reimbursement_date', 'reference_number', 'metadata', 'tags',
            'formatted_amount', 'is_pending_reimbursement', 'created_by',
            'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Create expense with creator tracking."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        return super().create(validated_data)


class TransactionBulkSerializer(serializers.Serializer):
    """Serializer for bulk transaction operations."""
    
    transaction_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1
    )
    action = serializers.ChoiceField(choices=['complete', 'cancel', 'delete'])
    reason = serializers.CharField(required=False, allow_blank=True)

