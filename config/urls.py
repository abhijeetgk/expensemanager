"""
URL configuration for Expense Manager project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from apps.dashboard import web_views

urlpatterns = [
    # Web Interface (User-facing)
    path('', web_views.dashboard_view, name='dashboard'),
    path('login/', web_views.login_view, name='login'),
    path('logout/', web_views.logout_view, name='logout'),
    path('income/add/', web_views.add_income_view, name='add_income'),
    path('expense/add/', web_views.add_expense_view, name='add_expense'),
    path('income/', web_views.income_list_view, name='income_list'),
    path('expense/', web_views.expense_list_view, name='expense_list'),
    path('reports/', web_views.reports_view, name='reports'),
    path('income/<uuid:pk>/delete/', web_views.delete_income_view, name='delete_income'),
    path('expense/<uuid:pk>/delete/', web_views.delete_expense_view, name='delete_expense'),
    
    # Admin
    path("admin/", admin.site.urls),
    
    # API Authentication
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # API Endpoints
    path('api/accounts/', include('apps.accounts.urls')),
    path('api/categories/', include('apps.categories.urls')),
    path('api/transactions/', include('apps.transactions.urls')),
    path('api/reports/', include('apps.reports.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customize admin site
admin.site.site_header = "Expense Manager Administration"
admin.site.site_title = "Expense Manager Admin"
admin.site.index_title = "Welcome to Expense Manager Administration"
