from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Profile


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
