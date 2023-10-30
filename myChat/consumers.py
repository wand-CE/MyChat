import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User

from chats.models import Conversation, Message, Profile


class ChatRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_uuid = self.scope['url_route']['kwargs']['chat_uuid']
        self.chat_group_name = f'chat_{self.chat_uuid}'

        await self.channel_layer.group_add(
            self.chat_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.chat_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']
        chat_uuid = text_data_json["chat_uuid"]

        await self.save_message(message, username, chat_uuid)

        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'sendMessage',
                'message': message,
                'username': username,
                "chat_uuid": chat_uuid,
            }
        )

    async def sendMessage(self, event):
        message = event["message"]
        username = event["username"]
        await self.send(text_data=json.dumps({
            "message": message,
            "username": username,
        }))

    @sync_to_async
    def save_message(self, message, username, chat_uuid):
        print(username, chat_uuid, "----------------------")
        user = User.objects.get(username=username)
        user_profile = Profile.objects.get(user=user)
        chat = Conversation.objects.get(uuid=chat_uuid)

        Message.objects.create(sender=user_profile, content=message, conversation_id=chat.id)
