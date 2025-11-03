"""
URL configuration for dashboard app.
"""

from django.urls import path
from apps.dashboard import views, admin_views

urlpatterns = [
    # Admin dashboard web interface
    path('admin/', admin_views.admin_dashboard_view, name='admin-dashboard'),
    
    # Admin dashboard endpoints
    path('stats/', views.dashboard_stats, name='dashboard-stats'),
    path('charts/income-expense/', views.income_expense_chart, name='income-expense-chart'),
    path('charts/category-breakdown/', views.category_breakdown_chart, name='category-breakdown-chart'),
    path('widgets/top-users/', views.top_users_widget, name='top-users-widget'),
    path('widgets/recent-transactions/', views.recent_transactions_widget, name='recent-transactions-widget'),
    
    # User dashboard endpoints
    path('user/stats/', views.user_dashboard_stats, name='user-dashboard-stats'),
]

