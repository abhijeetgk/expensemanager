"""
Serializers for categories app.
"""

from rest_framework import serializers
from apps.categories.models import IncomeCategory, ExpenseCategory


class IncomeCategorySerializer(serializers.ModelSerializer):
    """Serializer for IncomeCategory model."""
    
    full_path = serializers.CharField(read_only=True)
    depth = serializers.IntegerField(read_only=True)
    is_root = serializers.BooleanField(read_only=True)
    created_by_name = serializers.CharField(source='creator_name', read_only=True)
    
    class Meta:
        model = IncomeCategory
        fields = [
            'id', 'name', 'description', 'icon', 'color',
            'parent', 'sort_order', 'is_active', 'is_recurring',
            'tax_applicable', 'full_path', 'depth', 'is_root',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Create category with creator tracking."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        return super().create(validated_data)


class ExpenseCategorySerializer(serializers.ModelSerializer):
    """Serializer for ExpenseCategory model."""
    
    full_path = serializers.CharField(read_only=True)
    depth = serializers.IntegerField(read_only=True)
    is_root = serializers.BooleanField(read_only=True)
    created_by_name = serializers.CharField(source='creator_name', read_only=True)
    budget_utilization = serializers.SerializerMethodField()
    
    class Meta:
        model = ExpenseCategory
        fields = [
            'id', 'name', 'description', 'icon', 'color',
            'parent', 'sort_order', 'is_active', 'budget_limit',
            'is_essential', 'allows_split', 'full_path', 'depth',
            'is_root', 'budget_utilization', 'created_by',
            'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_budget_utilization(self, obj):
        """Get budget utilization percentage."""
        return obj.get_budget_utilization()
    
    def create(self, validated_data):
        """Create category with creator tracking."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        return super().create(validated_data)


class CategoryQuickCreateSerializer(serializers.Serializer):
    """Serializer for quick category creation by power users."""
    
    name = serializers.CharField(max_length=100)
    description = serializers.CharField(required=False, allow_blank=True)
    color = serializers.CharField(max_length=7, required=False)
    icon = serializers.CharField(max_length=50, required=False, allow_blank=True)

