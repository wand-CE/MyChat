from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from chats.models import Conversation, Message, Profile


class Home(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profiles'] = Profile.objects.all()

        return context


class ChatView(LoginRequiredMixin, TemplateView):
    template_name = 'teste.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chat_uuid'] = self.kwargs['chat_uuid']
        chat_id = Conversation.objects.get(uuid=context['chat_uuid'])

        context['messages'] = Message.objects.filter(conversation_id=chat_id)
        context['profiles'] = Profile.objects.all()

        return context


class SearchView(LoginRequiredMixin, TemplateView):
    template_name = 'search.html'

    def post(self, request):
        searched = request.POST.get('searched')
        users = User.objects.filter(username__contains=searched)

        # profiles = [Profile.objects.get(user=user) for user in users]
        profiles = [Profile.objects.get(user=user).name for user in users]

        return JsonResponse({'profiles': profiles})

      
class RedirectChat(LoginRequiredMixin, TemplateView):
    
    
    def get(self, request, *args, **kwargs):
        user1 = User.objects.get(username=self.kwargs['user1'])
        user2 = User.objects.get(username=self.kwargs['user2'])
        
        
        user1 = Profile.objects.get(user=user1)
        user2 = Profile.objects.get(user=user2)

        conversation = Conversation.objects.filter(participants=user1).filter(participants=user2).first()
        if conversation:
            return redirect('chat', chat_uuid=conversation.uuid)
        conversation = Conversation.objects.create()
        conversation.participants.add(user1, user2)
        return redirect('chat', chat_uuid=conversation.uuid)

