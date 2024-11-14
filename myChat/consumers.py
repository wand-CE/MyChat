import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from chats.models import Conversation, Message, Profile, MessageReadStatus


class ChatRoomConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.chat_group_name = None
        self.chat_uuid = None

    async def connect(self):
        self.chat_uuid = self.scope['url_route']['kwargs']['chat_uuid']
        self.chat_group_name = f'chat_{self.chat_uuid}'

        await self.channel_layer.group_add(
            self.chat_group_name,
            self.channel_name
        )

        await self.accept()
        messages = await self.return_unread_messages(self.chat_uuid)
        self.mark_messages_as_read(messages)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.chat_group_name,
            self.channel_name
        )
        await self.close()

    # deal with the data received by websocket and send to own group
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user_id = text_data_json['user_id']
        is_group = text_data_json['is_group']
        chat_uuid = text_data_json["chat_uuid"]

        profile = await self.get_profile(user_id)

        if self.is_in_chat(user_id, chat_uuid):
            message = await self.save_message(message, user_id, chat_uuid)
            profile_name = await self.get_profile_name(profile)

            await self.channel_layer.group_send(
                self.chat_group_name,
                {
                    'type': 'send_message',
                    'message': message,
                    'user_id': profile.id,
                    'name': profile_name,
                    'is_group': is_group,
                    'chat_uuid': chat_uuid,
                }
            )
        else:

            await self.close()

    # send the data to consumers of current chat

    async def send_message(self, event):
        message = event["message"]
        user_id = event["user_id"]
        name = event["name"]
        is_group = event["is_group"]
        message_time = message.getMessageTime()
        self.mark_messages_as_read([message])

        await self.send(text_data=json.dumps({
            "type": "send_message",
            "user": {'id': user_id, "name": name},
            "is_read": await database_sync_to_async(message.is_read)(),
            "message": message.content,
            "message_time": message_time,
            "is_group": is_group,
        }))

    # save the message on database
    @database_sync_to_async
    def save_message(self, message, user_id, chat_uuid):
        user_profile = Profile.objects.get(id=user_id)
        chat = Conversation.objects.get(uuid=chat_uuid)

        return Message.objects.create(sender=user_profile, content=message, conversation_id=chat.id)

    # verify if the profile have unread messages in the chat
    @database_sync_to_async
    def return_unread_messages(self, chat_uuid):
        chat = Conversation.objects.get(uuid=chat_uuid)
        profile = Profile.objects.get(user=self.scope["user"])
        messages = Message.objects.filter(
            Q(conversation=chat) & ~Q(sender=profile))

        return messages

    # pass a list of messages from chat to mark as read
    @database_sync_to_async
    def mark_messages_as_read(self, messages):
        user = self.scope['user']
        for message in messages:
            if message.sender.user != user:
                recipient = Profile.objects.get(user=user)
                try:
                    message = MessageReadStatus.objects.get(
                        Q(message=message) & Q(recipientProfile=recipient))
                    if not message.is_read:
                        message.is_read = True
                        message.save()
                except ObjectDoesNotExist:
                    pass

    @database_sync_to_async
    def get_profile(self, profile_id):
        return Profile.objects.get(id=int(profile_id))

    @database_sync_to_async
    def get_profile_name(self, profile):
        return profile.get_name()

    @database_sync_to_async
    def is_in_chat(self, profile_id, chat_uuid):
        chat = Conversation.objects.get(uuid=chat_uuid)
        profile = Profile.objects.get(id=int(profile_id))

        return profile in chat.participants.all()

    async def mark_message_read_on_page(self, event):
        await self.send(text_data=json.dumps(event))


class NotificationConsumer(AsyncWebsocketConsumer):
    list_of_groups = {}

    current_chat_friend = None

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.chat_group_name = None
        self.profile_id = None

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

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        self.current_chat_friend = text_data_json['chat_uuid']

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

        sender = await self.get_sender_data(sender_id)

        if self.profile_id != sender_id:
            await self.send_message(
                type_event,
                message,
                message_time,
                await self.get_current_profile(),
                sender,
                str(chat_uuid)
            )
        else:
            await self.send_message(
                type_event,
                message,
                message_time,
                sender,
                await self.get_current_profile(),
                str(chat_uuid)
            )

    async def send_message(self, type_event, message, message_time, recipient, sender, chat_uuid):
        await self.send(text_data=json.dumps({
            "type": type_event,
            "message": message,
            "message_time": message_time,
            "sender": await self.get_profile_data(sender),
            "recipient": await self.get_profile_data(recipient),
            "chat": await self.get_chat_data(chat_uuid),
        }))

    @database_sync_to_async
    def get_chat_data(self, chat_uuid):
        chat = Conversation.objects.get(uuid=chat_uuid)
        is_group = chat.is_group
        chat_data = chat.get_group_data() if chat.is_group else ''

        return {
            'uuid': str(chat.uuid),
            'photo': chat_data.photo.thumb.url if is_group else '',
            'name': chat_data.name if is_group else '',
            'is_group': is_group,
        }

    @database_sync_to_async
    def get_sender_data(self, sender_id):
        return Profile.objects.get(id=sender_id)

    @database_sync_to_async
    def get_current_profile(self):
        return Profile.objects.get(id=self.profile_id)

    @database_sync_to_async
    def get_profile_data(self, profile: Profile):
        # make to accept only Profile object
        return {
            'id': profile.id,
            'name': profile.name,
            'photo': profile.photo.thumb.url,
        }
