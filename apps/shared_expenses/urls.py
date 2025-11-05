"""
URL routing for shared expenses app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.shared_expenses.views import ExpenseGroupViewSet, SharedExpenseViewSet, DebtViewSet

router = DefaultRouter()
router.register(r'expense-groups', ExpenseGroupViewSet, basename='expense-group')
router.register(r'shared-expenses', SharedExpenseViewSet, basename='shared-expense')
router.register(r'debts', DebtViewSet, basename='debt')

app_name = 'shared_expenses'

urlpatterns = [
    path('', include(router.urls)),
]

