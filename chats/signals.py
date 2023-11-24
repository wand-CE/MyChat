from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.utils import timezone
from django.contrib.auth.models import User

from myChat.consumers import NotificationConsumer
from .models import Profile, Message, MessageReadStatus, Conversation


# these signals make a profile for every user created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


# the signals below was created to verify if Profile is online or not
@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    current_profile = Profile.objects.get(user=user)
    current_profile.is_online = True
    current_profile.save()


@receiver(user_logged_out)
def user_logged_out_handler(sender, request, user, **kwargs):
    current_profile = Profile.objects.get(user=user)
    current_profile.is_online = False
    current_profile.last_activity = timezone.now()
    current_profile.save()


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

    chat_participants = Conversation.objects.get(
        uuid=instance.conversation.uuid).participants.all()
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
