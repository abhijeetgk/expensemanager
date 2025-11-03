"""
URL configuration for categories app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.categories.views import IncomeCategoryViewSet, ExpenseCategoryViewSet

router = DefaultRouter()
router.register(r'income', IncomeCategoryViewSet, basename='income-category')
router.register(r'expense', ExpenseCategoryViewSet, basename='expense-category')

urlpatterns = [
    path('', include(router.urls)),
]

