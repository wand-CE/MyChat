import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save
from django.dispatch import receiver

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
                'type': 'send_message',
                'message': message,
                'user_id': user_id,
                'chat_uuid': chat_uuid,
            }
        )

    async def send_message(self, event):
        message = event["message"]
        user_id = event["user_id"]
        await self.send(text_data=json.dumps({
            "message": message,
            "user_id": user_id,
        }))

    @database_sync_to_async
    def save_message(self, message, user_id, chat_uuid):
        print(user_id, chat_uuid, "----------------------")
        user = User.objects.get(id=user_id)
        user_profile = Profile.objects.get(user=user)
        chat = Conversation.objects.get(uuid=chat_uuid)

        Message.objects.create(sender=user_profile, content=message, conversation_id=chat.id)


class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope['user']
        await self.accept() if not self.user.is_anonymous else await self.close()
        self.chat_group_name = 'notifications'

        await self.channel_layer.group_add(
            self.chat_group_name,
            self.channel_name
        )

    async def disconnect(self, close_code):
        print('foi desconectado')

    async def notify_users(self, event):
        await self.search_participants(event['chat_uuid'])
        print('ENTROU')

    @database_sync_to_async
    def search_profile(self, profile_id):
        try:
            return Profile.objects.get(user_id=profile_id).id
        except ObjectDoesNotExist:
            return None

    @database_sync_to_async
    def search_participants(self, chat_id):
        try:
            for participant in Conversation.objects.get(uuid=chat_id).participants.all():
                print(participant)
            return Conversation.objects.get(uuid=chat_id).participants
        except ObjectDoesNotExist:
            return None

    """
    async def receive(self, text_data):
    """



@receiver(post_save, sender=Message)
def message_post_save(sender, instance, **kwargs):
    # Extraia os detalhes da mensagem
    message = {
        "message": instance.content,
        "user_id": instance.sender.user.id,
        "chat_uuid": instance.conversation.uuid,
    }

    # Envie a notificação para o grupo de chat correspondente
    channel_layer = get_channel_layer()
    print(*message)
    async_to_sync(channel_layer.group_send)(
        'notifications',
        {
            "type": "notify_users",
            **message,
        }
    )
