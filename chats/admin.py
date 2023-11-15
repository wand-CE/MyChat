from django.contrib import admin
from chats.models import Message, Profile, Conversation, Contact
from chats.forms import ConversationForm


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'timestamp', 'conversation_id']


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    form = ConversationForm
    list_display = ['uuid', 'is_group']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_online']


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['user', 'friend', 'added_on']
