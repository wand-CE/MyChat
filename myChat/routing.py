from django.urls import path, include, re_path
from .consumers import ChatRoomConsumer

websocket_urlpatterns = [
    path("<room_name>", ChatRoomConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<room_name>\w+)/$', ChatRoomConsumer.as_asgi()),
]
