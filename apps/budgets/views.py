"""
Views for budget management.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from apps.budgets.models import Budget, BudgetAlert
from apps.budgets.serializers import (
    BudgetSerializer, BudgetCreateSerializer, BudgetAlertSerializer,
    BudgetSummarySerializer, BudgetForecastSerializer
)
from apps.budgets.services import BudgetService, NotificationService


class BudgetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing budgets.
    
    Provides CRUD operations and additional actions for budget management.
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = BudgetSerializer
    
    def get_queryset(self):
        """Return budgets for the current user."""
        return Budget.objects.for_user(self.request.user)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return BudgetCreateSerializer
        return BudgetSerializer
    
    def perform_create(self, serializer):
        """Create budget for current user."""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current active budgets."""
        budgets = BudgetService.get_current_budgets(request.user)
        serializer = self.get_serializer(budgets, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get budget summary for current period."""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
        if end_date:
            end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
        
        summary = BudgetService.calculate_budget_summary(
            request.user, start_date, end_date
        )
        
        # Don't serialize the full budgets queryset
        budgets_data = summary.pop('budgets')
        serializer = BudgetSummarySerializer(summary)
        
        return Response({
            **serializer.data,
            'budgets': BudgetSerializer(budgets_data, many=True).data
        })
    
    @action(detail=False, methods=['get'])
    def forecast(self, request):
        """Get budget forecast based on historical spending."""
        months = int(request.query_params.get('months', 3))
        forecast = BudgetService.get_budget_forecast(request.user, months)
        serializer = BudgetForecastSerializer(forecast, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reset_alerts(self, request, pk=None):
        """Reset alert flags for a budget."""
        budget = self.get_object()
        budget.reset_alerts()
        return Response({
            'message': 'Alerts reset successfully'
        })
    
    @action(detail=False, methods=['post'])
    def create_recurring(self, request):
        """Create recurring monthly budgets."""
        category_id = request.data.get('category')
        amount = request.data.get('amount')
        months = int(request.data.get('months', 12))
        
        if not category_id or not amount:
            return Response(
                {'error': 'Category and amount are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from apps.categories.models import ExpenseCategory
        
        try:
            category = ExpenseCategory.objects.get(id=category_id)
        except ExpenseCategory.DoesNotExist:
            return Response(
                {'error': 'Category not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        budgets = BudgetService.create_recurring_budgets(
            request.user, category, amount, months
        )
        
        serializer = self.get_serializer(budgets, many=True)
        return Response({
            'message': f'Created {len(budgets)} recurring budgets',
            'budgets': serializer.data
        }, status=status.HTTP_201_CREATED)


class BudgetAlertViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing budget alerts.
    
    Provides read-only access to budget alerts for the current user.
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = BudgetAlertSerializer
    
    def get_queryset(self):
        """Return alerts for the current user."""
        return BudgetAlert.objects.filter(user=self.request.user).select_related('budget')
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread alerts."""
        alerts = NotificationService.get_unread_alerts(request.user)
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def mark_read(self, request):
        """Mark alerts as read."""
        alert_ids = request.data.get('alert_ids', [])
        
        if alert_ids:
            NotificationService.mark_alerts_as_read(request.user, alert_ids)
        else:
            NotificationService.mark_alerts_as_read(request.user)
        
        return Response({
            'message': 'Alerts marked as read'
        })
    
    @action(detail=True, methods=['post'])
    def mark_read_single(self, request, pk=None):
        """Mark a single alert as read."""
        alert = self.get_object()
        alert.mark_as_read()
        return Response({
            'message': 'Alert marked as read'
        })

