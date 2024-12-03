from django.urls import path, re_path


def get_consumers():
    from .consumers import ChatRoomConsumer, NotificationConsumer
    return [
        re_path(r'ws/chat/(?P<chat_uuid>[\w-]+)/$', ChatRoomConsumer.as_asgi()),
        path('ws/notify/<int:profile_id>', NotificationConsumer.as_asgi()),
    ]


websocket_urlpatterns = get_consumers()
