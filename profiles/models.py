from django.contrib.auth.models import User

from django.db import models
from stdimage import StdImageField


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

    def get_name(self):
        return self.name

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
        return self.name
