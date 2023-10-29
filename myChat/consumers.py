import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User

from chats.models import Conversation, Message, Profile


class ChatRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']
        room_name = text_data_json["room_name"]

        await self.save_message(message, username, room_name)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'sendMessage',
                'message': message,
                'username': username,
                "room_name": room_name,
            }
        )

    async def sendMessage(self, event):
        message = event["message"]
        username = event["username"]
        await self.send(text_data=json.dumps({"message": message, "username": username}))

    @sync_to_async
    def save_message(self, message, username, room_name):
        print(username, room_name, "----------------------")
        user = User.objects.get(username=username)
        user_profile = Profile.objects.get(user=user)
        # room = Room.objects.get(name=room_name)

        # id 3 was the id of conversation_model created to test
        Message.objects.create(sender=user_profile, content=message, conversation_id=3)
