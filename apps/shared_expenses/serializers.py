"""
Serializers for shared expenses models.
"""

from rest_framework import serializers
from apps.shared_expenses.models import ExpenseGroup, SharedExpense, SharedExpenseSplit, Debt, DebtPayment
from apps.accounts.serializers import UserSerializer
from apps.transactions.serializers import ExpenseSerializer


class ExpenseGroupSerializer(serializers.ModelSerializer):
    """Serializer for ExpenseGroup model."""
    
    admin_detail = UserSerializer(source='admin', read_only=True)
    member_details = UserSerializer(source='members', many=True, read_only=True)
    member_count = serializers.IntegerField(read_only=True)
    total_expenses = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = ExpenseGroup
        fields = [
            'id', 'name', 'description', 'members', 'member_details',
            'admin', 'admin_detail', 'icon', 'color', 'is_active',
            'member_count', 'total_expenses', 'created_at', 'updated_at'
        ]
        read_only_fields = ['admin', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Create group with current user as admin."""
        user = self.context['request'].user
        members = validated_data.pop('members', [])
        validated_data['admin'] = user
        group = ExpenseGroup.objects.create(**validated_data)
        group.members.set(members)
        return group


class SharedExpenseSplitSerializer(serializers.ModelSerializer):
    """Serializer for SharedExpenseSplit model."""
    
    user_detail = UserSerializer(source='user', read_only=True)
    formatted_amount = serializers.CharField(read_only=True)
    
    class Meta:
        model = SharedExpenseSplit
        fields = [
            'id', 'shared_expense', 'user', 'user_detail', 'amount',
            'percentage', 'is_settled', 'settled_at', 'settlement_notes',
            'formatted_amount', 'created_at'
        ]
        read_only_fields = ['settled_at', 'created_at']


class SharedExpenseSerializer(serializers.ModelSerializer):
    """Serializer for SharedExpense model."""
    
    expense_detail = ExpenseSerializer(source='expense', read_only=True)
    paid_by_detail = UserSerializer(source='paid_by', read_only=True)
    splits = SharedExpenseSplitSerializer(many=True, read_only=True)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    is_fully_settled = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = SharedExpense
        fields = [
            'id', 'expense', 'expense_detail', 'group', 'paid_by',
            'paid_by_detail', 'split_method', 'notes', 'splits',
            'amount', 'is_fully_settled', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class DebtPaymentSerializer(serializers.ModelSerializer):
    """Serializer for DebtPayment model."""
    
    formatted_amount = serializers.CharField(read_only=True)
    
    class Meta:
        model = DebtPayment
        fields = [
            'id', 'debt', 'amount', 'payment_method', 'reference_number',
            'notes', 'formatted_amount', 'created_at'
        ]
        read_only_fields = ['created_at']


class DebtSerializer(serializers.ModelSerializer):
    """Serializer for Debt model."""
    
    creditor_detail = UserSerializer(source='creditor', read_only=True)
    debtor_detail = UserSerializer(source='debtor', read_only=True)
    payments = DebtPaymentSerializer(many=True, read_only=True)
    remaining_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Debt
        fields = [
            'id', 'creditor', 'creditor_detail', 'debtor', 'debtor_detail',
            'amount', 'description', 'group', 'shared_expense_split',
            'status', 'due_date', 'settled_amount', 'settled_at',
            'payments', 'remaining_amount', 'is_overdue',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['settled_at', 'created_at', 'updated_at']

