from django.db import models
from stdimage import StdImageField
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, ObjectDoesNotExist


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

    class Meta:
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'


class Message(models.Model):
    sender = models.ForeignKey(Profile, related_name='sent_messages', on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'

    def clean(self):
        try:
            if self.sender == self.recipient:
                raise ValidationError(
                    "Sender and recipient can't be equal")
        except ObjectDoesNotExist:
            raise ValidationError("")

    def save(self, *args, **kwargs):
        # self.clean()
        super().save(*args, **kwargs)

# class Notification(models.Model):
#    user = models.ForeignKey(User, on_delete=models.CASCADE)
#    message = models.ForeignKey(
#        Message, null=True, blank=True, on_delete=models.CASCADE)
#    type = models.CharField(max_length=50)
#    timestamp = models.DateTimeField(auto_now_add=True)
#    is_read = models.BooleanField(default=False)
