from django.contrib.auth import get_user_model
from django.db import models
from stdimage import StdImageField
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, ObjectDoesNotExist

import uuid


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = StdImageField(upload_to='profile_photos',
                          variations={'thumb': {'width': 600,
                                                'height': 600, 'crop': True}},
                          default='profile_photos/defaultProfile.png',
                          verbose_name='Foto de Perfil')
    is_online = models.BooleanField(default=False, verbose_name='online')
    last_activity = models.DateTimeField(blank=True, auto_now_add=True)

    @property
    def name(self):
        return self.user.username

    def get_last_activity(self):
        return {
            'day': self.last_activity.strftime('%d/%m/%Y'),
            'hour': self.last_activity.strftime('%H:%M')
        }

    def status_display(self):
        return "Online" if self.is_online else f"Visto por ultimo as {self.get_last_activity()['hour']}" \
                                               f" do dia {self.get_last_activity()['day']}"

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def __str__(self):
        return f'Profile of {self.name}'


class Conversation(models.Model):
    participants = models.ManyToManyField(
        Profile, related_name='conversations')
    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, null=False)
    is_group = models.BooleanField(
        null=False, default=False, verbose_name='grupo')

    class Meta:
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'

    def __str__(self):
        return f'Chat: {self.uuid}'

    def get_last_message(self):
        last_message = self.messages.order_by('-timestamp').first()
        return last_message


class GroupNames(models.Model):
    name = models.CharField(null=False, unique=False, max_length=100)
    chat = models.OneToOneField(Conversation, on_delete=models.CASCADE, null=False,
                                limit_choices_to={'is_group': True})
    photo = StdImageField(upload_to='profile_photos',
                          variations={'thumb': {'width': 600,
                                                'height': 600, 'crop': True}},
                          default='profile_photos/default_group_profile.png',
                          verbose_name='Foto de Perfil')

    class Meta:
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'


class Message(models.Model):
    sender = models.ForeignKey(
        Profile, related_name='sent_messages', on_delete=models.CASCADE, editable=False)
    conversation = models.ForeignKey(
        Conversation, related_name='messages', on_delete=models.CASCADE, editable=False)
    content = models.TextField(editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'

    def __str__(self):
        return f'Mensagem {self.conversation}'

    def getMessageTime(self):
        return self.timestamp.strftime("%d/%m/%Y|%H:%M")


class MessageReadStatus(models.Model):
    recipientProfile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, editable=False)
    message = models.ForeignKey(
        Message, related_name='read_status', on_delete=models.CASCADE, editable=False)
    is_read = models.BooleanField(default=False)

    class Meta:
        unique_together = ['recipientProfile', 'message']


class Contact(models.Model):
    user = models.ForeignKey(
        Profile, related_name='contacts', on_delete=models.CASCADE)
    friend = models.ForeignKey(
        Profile, related_name='friends', on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'

    def clean(self):
        try:
            if self.friend == self.user:
                raise ValidationError(
                    'fields friend and user must be different')
        except ObjectDoesNotExist:
            return False
        return True

    def save(self, *args, **kwargs):
        if self.clean():
            relation_exists = Contact.objects.filter(
                user=self.user, friend=self.friend).exists()
            if not relation_exists:
                super(Contact, self).save(*args, **kwargs)

            inverse_relation_exists = Contact.objects.filter(
                user=self.friend, friend=self.user).exists()
            if not inverse_relation_exists:
                Contact.objects.create(user=self.friend, friend=self.user)

# class Notification(models.Model):
#    user = models.ForeignKey(User, on_delete=models.CASCADE)
#    message = models.ForeignKey(
#        Message, null=True, blank=True, on_delete=models.CASCADE)
#    type = models.CharField(max_length=50)
#    timestamp = models.DateTimeField(auto_now_add=True)
#    is_read = models.BooleanField(default=False)
