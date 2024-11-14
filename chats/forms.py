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
        cleaned_data = super().clean()
        is_group = cleaned_data.get('is_group')
        participants = cleaned_data.get('participants', None)

        if not is_group:
            try:
                chat = Conversation.objects.filter(participants=participants[0]).filter(
                    participants=participants[1]).first()
                if chat:
                    raise forms.ValidationError("Essa conversa já existe")
            except IndexError:
                pass
        return cleaned_data
