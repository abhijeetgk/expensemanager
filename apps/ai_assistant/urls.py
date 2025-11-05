"""
URL routing for AI assistant app.
"""

from django.urls import path
from apps.ai_assistant import views

app_name = 'ai_assistant'

urlpatterns = [
    path('chat/', views.chat_assistant_view, name='chat_assistant'),
    path('api/parse/', views.parse_transaction_api, name='parse_transaction'),
    path('api/create/', views.create_transaction_from_chat_api, name='create_transaction'),
    path('api/suggestions/', views.quick_suggestions_api, name='quick_suggestions'),
]

