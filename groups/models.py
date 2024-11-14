from django.db import models
from stdimage import StdImageField

from profiles.models import Profile


class GroupNames(models.Model):
    name = models.CharField(null=False, unique=False, max_length=100)
    chat = models.OneToOneField("chats.Conversation", related_name='chat_data', on_delete=models.CASCADE,
                                null=False,
                                editable=False)
    photo = StdImageField(upload_to='profile_photos',
                          variations={'thumb': {'width': 600,
                                                'height': 600, 'crop': True}},
                          default='profile_photos/default_group_profile.png',
                          verbose_name='Foto de Perfil')
    admin = models.ManyToManyField(Profile, related_name='group_admins')

    class Meta:
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'
