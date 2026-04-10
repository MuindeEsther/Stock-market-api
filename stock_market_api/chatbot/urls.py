from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('start/', views.start_chat_session, name='start_session'),
    path('send/', views.send_message, name='send_message'),
    path('history/', views.get_chat_history, name='get_history'),
]
