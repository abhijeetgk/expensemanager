"""
URL configuration for transactions app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.transactions.views import IncomeViewSet, ExpenseViewSet

router = DefaultRouter()
router.register(r'income', IncomeViewSet, basename='income')
router.register(r'expense', ExpenseViewSet, basename='expense')

urlpatterns = [
    path('', include(router.urls)),
]

