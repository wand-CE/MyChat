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
        user_id = text_data_json['user_id']
        chat_uuid = text_data_json["chat_uuid"]

        await self.save_message(message, user_id, chat_uuid)

        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'sendMessage',
                'message': message,
                'user_id': user_id,
                'chat_uuid': chat_uuid,
            }
        )

    async def sendMessage(self, event):
        message = event["message"]
        user_id = event["user_id"]
        await self.send(text_data=json.dumps({
            "message": message,
            "user_id": user_id,
        }))

    @sync_to_async
    def save_message(self, message, user_id, chat_uuid):
        print(user_id, chat_uuid, "----------------------")
        user = User.objects.get(id=user_id)
        user_profile = Profile.objects.get(user=user)
        chat = Conversation.objects.get(uuid=chat_uuid)

        Message.objects.create(sender=user_profile, content=message, conversation_id=chat.id)
