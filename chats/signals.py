from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Message, MessageReadStatus, Conversation


# the signal below create a message_read object when a Message is created
@receiver(post_save, sender=Message)
def message_read(sender, instance, created, **kwargs):
    if created:
        try:
            chat = Conversation.objects.get(pk=instance.conversation.id)
            for participant in chat.participants.all():
                if participant.id != instance.sender.id:
                    MessageReadStatus.objects.create(
                        recipientProfile=participant, message=instance)
        except ObjectDoesNotExist:
            pass


@receiver(post_save, sender=Message)
def message_post_save(sender, instance, **kwargs):
    # Extract details of message
    message = {
        "message": instance.content,
        "message_time": instance.getMessageTime(),
        "profile_id": instance.sender.id,
        "chat_uuid": instance.conversation.uuid,
    }

    chat_participants = Conversation.objects.get(uuid=instance.conversation.uuid).participants.all()
    for participant in chat_participants:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'notification_user{participant.id}',
            {
                "type": "notify_user",
                **message,
            }
        )


@receiver(post_save, sender=MessageReadStatus)
def get_read_message(sender, instance, **kwargs):
    if instance.is_read:
        message = instance.message
        if message.is_read():
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'chat_{message.conversation.uuid}',
                {
                    "type": "mark_message_read_on_page",
                    "owner_of_message": message.sender.id,
                }
            )
