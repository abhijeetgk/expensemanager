"""
URL configuration for reports app.
"""

from django.urls import path
from apps.reports import views

urlpatterns = [
    path('summary/', views.summary_report, name='summary-report'),
    path('monthly/', views.monthly_report, name='monthly-report'),
    path('category-wise/', views.category_wise_report, name='category-wise-report'),
    path('trend-analysis/', views.trend_analysis, name='trend-analysis'),
    path('top-expenses/', views.top_expenses, name='top-expenses'),
    path('budget-analysis/', views.budget_analysis, name='budget-analysis'),
    path('spending-patterns/', views.spending_patterns, name='spending-patterns'),
    path('export/excel/', views.export_excel, name='export-excel'),
    path('export/pdf/', views.export_pdf, name='export-pdf'),
]

