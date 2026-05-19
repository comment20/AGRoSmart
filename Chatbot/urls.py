from django.urls import path
from . import views

urlpatterns = [
    path('send_message/', views.send_message_api, name='send_message_api'),
    path('history/', views.chat_history_api, name='chat_history_api'),
    path('delete_message/', views.delete_message_api, name='delete_message_api'),
    path('clear_history/', views.clear_chat_history_api, name='clear_chat_history_api'),
]
