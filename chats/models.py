import uuid

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import models

from groups.models import GroupNames
from profiles.models import Profile


class Conversation(models.Model):
    participants = models.ManyToManyField(Profile, related_name='conversations')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, null=False)
    is_group = models.BooleanField(null=False, default=False, verbose_name='grupo')

    class Meta:
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'

    def __str__(self):
        return f'Chat: {self.uuid}'

    def get_last_message(self):
        last_message = self.messages.order_by('-timestamp').first()
        return last_message

    def get_group_data(self):
        if self.is_group:
            try:
                return self.chat_data
            except ObjectDoesNotExist:
                GroupNames.objects.create(name='Generic Name', chat=self)
                return self.chat_data


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

    def is_read(self):
        for element in self.read_status.all():
            if not element.is_read:
                return False
        return True

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
