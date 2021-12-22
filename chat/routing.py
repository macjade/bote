from django.urls import path
from .consumers import ConversationMessageConsumer, UserOnlineStatusConsumer, ChatCallRoomConsumer

ws_urlpatterns = [
    path('ws/chat/room/<room_name>/', ConversationMessageConsumer.as_asgi()),
    path('ws/user/visibility_status/<user_email>/', UserOnlineStatusConsumer.as_asgi()),
    path('ws/chat/callroom/<call_id>/', ChatCallRoomConsumer.as_asgi()),
]