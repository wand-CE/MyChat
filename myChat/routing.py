from django.urls import path, include, re_path
from .consumers import ChatRoomConsumer, NotificationConsumer


class DatabaseUpdateConsumer:
    pass


websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<chat_uuid>[\w-]+)/$', ChatRoomConsumer.as_asgi()),
    path('ws/notify/', NotificationConsumer.as_asgi()),
]
