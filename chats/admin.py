from django.contrib import admin
from chats.models import Message, Profile, Conversation


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'content', 'timestamp']


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = []


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'status']
