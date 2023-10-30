from django.urls import path, include, re_path
from .consumers import ChatRoomConsumer

websocket_urlpatterns = [
    path("<chat_uuid>", ChatRoomConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<chat_uuid>[\w-]+)/$', ChatRoomConsumer.as_asgi()),
]
