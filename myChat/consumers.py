import json
import profile

from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
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

        message = await self.save_message(message, user_id, chat_uuid)

        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'send_message',
                'message': message.content,
                "message_time": message.getMessageTime(),
                'user_id': user_id,
                'chat_uuid': chat_uuid,
            }
        )

    async def send_message(self, event):
        message = event["message"]
        user_id = event["user_id"]
        message_time = event["message_time"]
        await self.send(text_data=json.dumps({
            "user_id": user_id,
            "message": message,
            "message_time": message_time,
        }))

    @database_sync_to_async
    def save_message(self, message, user_id, chat_uuid):
        print(user_id, chat_uuid, "----------------------")
        user_profile = Profile.objects.get(id=user_id)
        chat = Conversation.objects.get(uuid=chat_uuid)

        return Message.objects.create(sender=user_profile, content=message, conversation_id=chat.id)


class NotificationConsumer(AsyncWebsocketConsumer):
    list_of_groups = {}

    current_chat_friend = None

    async def connect(self):
        self.profile_id = self.scope['url_route']['kwargs']['profile_id']

        await self.accept() if not self.scope['user'].is_anonymous else await self.close()

        self.chat_group_name = f'notification_user{self.profile_id}'

        await self.channel_layer.group_add(
            self.chat_group_name,
            self.channel_name
        )

    async def disconnect(self, close_code):
        await self.close()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        self.current_chat_friend = text_data_json['friend_id']

        self.list_of_groups[self.chat_group_name] = self.current_chat_friend

    async def change_friend_status(self, event):
        if self.current_chat_friend == event['friend']:
            await self.send(text_data=json.dumps(event))

    async def notify_user(self, event):
        chat_uuid = event['chat_uuid']
        sender_id = event['profile_id']
        message = event["message"]
        message_time = event["message_time"],
        type_event = event['type']

        recipients = await self.get_recipients(chat_uuid, sender_id)
        sender = await self.get_sender_data(sender_id)

        async for recipient in recipients:
            if recipient.id != sender_id:
                await self.send_message(
                    type_event,
                    message,
                    message_time,
                    recipient,
                    sender,
                    str(chat_uuid)
                )

    async def send_message(self, type_event, message, message_time, recipient, sender, chat_uuid):
        sync_to_async(print)(recipient)
        await self.send(text_data=json.dumps({
            "type": type_event,
            "message": message,
            "message_time": message_time,
            "sender": await self.get_profile_data(sender),
            "recipient": await self.get_profile_data(recipient),
            "chat_uuid": chat_uuid,
        }))

    @database_sync_to_async
    def get_sender_data(self, sender_id):
        return Profile.objects.get(id=sender_id)

    @database_sync_to_async
    def get_recipients(self, chat_uuid, sender_id):
        return Conversation.objects.get(uuid=chat_uuid).participants.filter(~Q(id=sender_id))

    @database_sync_to_async
    def get_profile_data(self, profile: Profile):
        # make to accept only Profile object
        return {
            'id': profile.id,
            'name': profile.name,
            'photo': profile.photo.url,
        }


@receiver(post_save, sender=Message)
def message_post_save(sender, instance, **kwargs):
    # Extract details of message
    message = {
        "message": instance.content,
        "message_time": instance.getMessageTime(),
        "profile_id": instance.sender.id,
        "chat_uuid": instance.conversation.uuid,
    }

    chat_participants = Conversation.objects.get(uuid=instance.conversation.uuid).participants.filter(
        ~Q(id=message['profile_id']))
    for participant in chat_participants:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'notification_user{participant.id}',
            {
                "type": "notify_user",
                **message,
            }
        )


@receiver(post_save, sender=Profile)
def user_change_status(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    print(NotificationConsumer.list_of_groups.items())
    for group, friend in NotificationConsumer.list_of_groups.items():
        if friend == instance.id:
            async_to_sync(channel_layer.group_send)(
                group,
                {
                    "type": "change_friend_status",
                    "friend": instance.id,
                    "status": instance.status_display(),
                }
            )
