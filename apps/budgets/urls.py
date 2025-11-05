"""
URL routing for budget app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.budgets.views import BudgetViewSet, BudgetAlertViewSet

router = DefaultRouter()
router.register(r'budgets', BudgetViewSet, basename='budget')
router.register(r'budget-alerts', BudgetAlertViewSet, basename='budget-alert')

app_name = 'budgets'

urlpatterns = [
    path('', include(router.urls)),
]

