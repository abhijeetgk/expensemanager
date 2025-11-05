"""
Serializers for budget models.
"""

from rest_framework import serializers
from apps.budgets.models import Budget, BudgetAlert
from apps.categories.serializers import ExpenseCategorySerializer


class BudgetSerializer(serializers.ModelSerializer):
    """Serializer for Budget model."""
    
    category_detail = ExpenseCategorySerializer(source='category', read_only=True)
    spent_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    remaining_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    utilization_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    is_over_budget = serializers.BooleanField(read_only=True)
    is_near_limit = serializers.BooleanField(read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)
    is_active_period = serializers.BooleanField(read_only=True)
    formatted_amount = serializers.SerializerMethodField()
    formatted_spent = serializers.SerializerMethodField()
    formatted_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = Budget
        fields = [
            'id', 'user', 'category', 'category_detail', 'name', 'amount',
            'period', 'start_date', 'end_date', 'status',
            'alert_threshold_80', 'alert_threshold_100',
            'alerted_at_80', 'alerted_at_100', 'rollover_unused', 'notes',
            'spent_amount', 'remaining_amount', 'utilization_percentage',
            'is_over_budget', 'is_near_limit', 'days_remaining', 'is_active_period',
            'formatted_amount', 'formatted_spent', 'formatted_remaining',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'alerted_at_80', 'alerted_at_100', 'created_at', 'updated_at']
    
    def get_formatted_amount(self, obj):
        """Get formatted budget amount."""
        return f"₹{obj.amount:,.2f}"
    
    def get_formatted_spent(self, obj):
        """Get formatted spent amount."""
        return f"₹{obj.spent_amount:,.2f}"
    
    def get_formatted_remaining(self, obj):
        """Get formatted remaining amount."""
        return f"₹{obj.remaining_amount:,.2f}"
    
    def validate(self, data):
        """Validate budget data."""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError({
                'end_date': 'End date must be after start date.'
            })
        
        return data


class BudgetCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating budgets."""
    
    class Meta:
        model = Budget
        fields = [
            'category', 'name', 'amount', 'period',
            'start_date', 'end_date', 'alert_threshold_80',
            'alert_threshold_100', 'rollover_unused', 'notes'
        ]
    
    def create(self, validated_data):
        """Create budget with current user."""
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class BudgetAlertSerializer(serializers.ModelSerializer):
    """Serializer for BudgetAlert model."""
    
    budget_detail = BudgetSerializer(source='budget', read_only=True)
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = BudgetAlert
        fields = [
            'id', 'budget', 'budget_detail', 'user', 'alert_type',
            'message', 'is_read', 'sent_via_email', 'created_at',
            'time_ago'
        ]
        read_only_fields = ['user', 'created_at']
    
    def get_time_ago(self, obj):
        """Get human-readable time since alert."""
        from django.utils.timesince import timesince
        return timesince(obj.created_at)


class BudgetSummarySerializer(serializers.Serializer):
    """Serializer for budget summary data."""
    
    total_budget = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_spent = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_remaining = serializers.DecimalField(max_digits=12, decimal_places=2)
    utilization_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    budget_count = serializers.IntegerField()
    over_budget_count = serializers.IntegerField()
    near_limit_count = serializers.IntegerField()


class BudgetForecastSerializer(serializers.Serializer):
    """Serializer for budget forecast data."""
    
    category = ExpenseCategorySerializer()
    avg_monthly_spending = serializers.DecimalField(max_digits=12, decimal_places=2)
    suggested_budget = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_spent_period = serializers.DecimalField(max_digits=12, decimal_places=2)

