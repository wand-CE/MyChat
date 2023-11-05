import json
from django.contrib.auth.models import User
from django.db.models import Q

from django.http import HttpResponseNotFound, JsonResponse
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin

from chats.models import Contact, Conversation, Message, Profile


class ChatView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = Profile.objects.get(user_id=self.request.user.id)
        context['current_profile_id'] = user.id
        context['contacts'] = Contact.objects.filter(user_id=user.id)

        return context


class SearchView(LoginRequiredMixin, View):
    def get(self, request):
        current_user = request.user
        searched = request.GET.get('searched')
        users = User.objects.filter(
            Q(username__contains=searched) & ~Q(id=current_user.id)
        )

        profiles = [Profile.objects.get(user=user) for user in users]

        list_profiles = []
        for profile in profiles:
            dicio = {}
            dicio['id'] = profile.id
            dicio['name'] = profile.name
            dicio['photo'] = profile.photo.url

            list_profiles.append(dicio)

        return JsonResponse({'profiles': list_profiles})


class ReturnChat(LoginRequiredMixin, View):
    http_method_names = ['get', 'post']

    def post(self, request):
        try:
            data = json.loads(request.body)

            user1 = Profile.objects.get(user=request.user.id)
            user2 = Profile.objects.get(id=data.get('contact_id'))

            conversation = Conversation.objects.filter(participants=user1).filter(participants=user2).first()
            if not conversation:
                conversation = Conversation.objects.create()
                conversation.participants.add(user1, user2)

            chat_uuid = conversation.uuid
            return JsonResponse({
                'chat_uuid': chat_uuid,
                'current_user_id': request.user.id,
                'current_user_name': request.user.username
            })
        except Exception as e:
            print(e)
            return HttpResponseNotFound()


class GetOldMessages(LoginRequiredMixin, View):
    def post(self, request):
        chat_uuid = json.loads(request.body)
        conversation = Conversation.objects.get(uuid=chat_uuid)
        messages = Message.objects.filter(conversation=conversation.id)

        messages = [[message.sender.user.id, message.content] for message in messages]

        return JsonResponse({'messages': messages})
