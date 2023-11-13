from django import forms
from django.contrib.auth.models import User

from chats.models import Profile


class UpdateProfileForm(forms.ModelForm):
    photo = forms.ImageField(label='Escolha outra foto de perfil:', required=False)
    username = forms.CharField(max_length=100, label='Nome de Usuário:')

    class Meta:
        model = Profile
        fields = []

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        current_username = self.instance.name

        if len(username) < 3:
            raise forms.ValidationError('O nome de usuario deve ter pelo menos 3 letras.')
        elif User.objects.filter(username=username).exclude(username=current_username).exists():
            # verify if the username is already in use, excluding the current username of query
            raise forms.ValidationError('Este nome de usuário já está em uso. Por favor, escolha outro.')
        return username
