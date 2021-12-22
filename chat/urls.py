from django.urls import path
from . import views

app_name='chat'

urlpatterns = [
    path('', views.ChatConversations.as_view(), name='conversations'),
    path('room/<room>/', views.ConversationMessage.as_view(), name='messages'),
    path('clear/', views.ClearChatView.as_view(), name='clear-chat'),
    path('list/', views.GetNewChatList.as_view(), name='new-chat-list'),
    path('has_read/', views.ReadMessage.as_view(), name='messages-read'),
]