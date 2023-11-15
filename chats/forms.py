from django import forms
from django.contrib.auth.models import User

from chats.models import Profile, Conversation


class UpdateProfileForm(forms.ModelForm):
    photo = forms.ImageField(
        label='Escolha outra foto de perfil:', required=False)
    username = forms.CharField(max_length=100, label='Nome de Usuário:')

    class Meta:
        model = Profile
        fields = []

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        current_username = self.instance.name

        if len(username) < 3:
            raise forms.ValidationError(
                'O nome de usuario deve ter pelo menos 3 letras.')
        elif User.objects.filter(username=username).exclude(username=current_username).exists():
            # verify if the username is already in use, excluding the current username of query
            raise forms.ValidationError(
                'Este nome de usuário já está em uso. Por favor, escolha outro.')
        return username


class ConversationForm(forms.ModelForm):
    class Meta:
        model = Conversation
        fields = ['participants', 'is_group']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')

        # current_uuid verify if it's editing or creating a chat
        self.current_uuid = instance.uuid if instance else None

    def clean(self):
        is_group = self.cleaned_data.get('is_group')
        participants = self.cleaned_data.get('participants', None)

        if not is_group and participants:
            if participants.count() != 2:
                raise forms.ValidationError({
                    "participants": "You have to assign two participants in a private chat",
                })
            else:
                chat = Conversation.objects.filter(participants=participants[0]).filter(
                    participants=participants[1]).first()
                if self.current_uuid and chat.uuid == self.current_uuid:
                    return self.cleaned_data
                if chat:
                    raise forms.ValidationError("This chat already exists")
        return self.cleaned_data
