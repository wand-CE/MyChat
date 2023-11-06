from django.db import models
from stdimage import StdImageField
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, ObjectDoesNotExist

import uuid


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = StdImageField(upload_to='profile_photos',
                          variations={'thumb': {'width': 600, 'height': 600, 'crop': True}},
                          default='profile_photos/defaultProfile.png')
    status = models.CharField(max_length=50, choices=[(
        'online', 'Online'), ('offline', 'Offline')], default='offline')

    @property
    def name(self):
        return self.user.username

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def __str__(self):
        return self.name


class Conversation(models.Model):
    participants = models.ManyToManyField(
        Profile, related_name='conversations')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, null=False)

    class Meta:
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'

    def __str__(self):
        return f'Chat: {self.uuid}'


class Message(models.Model):
    sender = models.ForeignKey(Profile, related_name='sent_messages', on_delete=models.CASCADE, editable=False)
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE, editable=False)
    content = models.TextField(editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'

    def __str__(self):
        return f'Mensagem {self.conversation}'


class Contact(models.Model):
    user = models.ForeignKey(Profile, related_name='contacts', on_delete=models.CASCADE)
    friend = models.ForeignKey(Profile, related_name='friends', on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'

    def clean(self):
        try:
            if self.friend == self.user:
                raise ValidationError('fields friend and user must be different')
        except ObjectDoesNotExist:
            return False
        return True

    def save(self, *args, **kwargs):
        if self.clean():
            relation_exists = Contact.objects.filter(user=self.user, friend=self.friend).exists()
            if not relation_exists:
                super(Contact, self).save(*args, **kwargs)

            inverse_relation_exists = Contact.objects.filter(user=self.friend, friend=self.user).exists()
            if not inverse_relation_exists:
                Contact.objects.create(user=self.friend, friend=self.user)

# class Notification(models.Model):
#    user = models.ForeignKey(User, on_delete=models.CASCADE)
#    message = models.ForeignKey(
#        Message, null=True, blank=True, on_delete=models.CASCADE)
#    type = models.CharField(max_length=50)
#    timestamp = models.DateTimeField(auto_now_add=True)
#    is_read = models.BooleanField(default=False)
