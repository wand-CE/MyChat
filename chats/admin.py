from django.contrib import admin

from chats.forms import ConversationForm
from chats.models import Conversation, Message, Contact


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'timestamp', 'conversation_id']


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    form = ConversationForm
    list_display = ['uuid', 'is_group']


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['user', 'friend', 'added_on']
