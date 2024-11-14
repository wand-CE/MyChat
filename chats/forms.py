from django import forms

from chats.models import Conversation


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
                    "participants": "Você deve adicionar pelo menos no grupo",
                })

            chat = Conversation.objects.filter(participants=participants[0]).filter(
                participants=participants[1]).first()
            if self.current_uuid and chat.uuid == self.current_uuid:
                return self.cleaned_data
            if chat:
                raise forms.ValidationError("This chat already exists")
        return self.cleaned_data
