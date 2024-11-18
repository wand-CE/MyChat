from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.signals import user_logged_out, user_logged_in
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from myChat.consumers import NotificationConsumer
from profiles.models import Profile


# these signals make a profile for every user created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # instance.profile.save()
    pass


# the signals below was created to verify if Profile is online or not
@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    current_profile, created = Profile.objects.get_or_create(user=user)
    current_profile.is_online = True
    current_profile.save()


@receiver(user_logged_out)
def user_logged_out_handler(sender, request, user, **kwargs):
    current_profile = Profile.objects.get(user=user)
    current_profile.is_online = False
    current_profile.last_activity = timezone.now()
    current_profile.save()


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
