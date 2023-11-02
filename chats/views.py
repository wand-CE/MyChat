import json
from django.contrib.auth.models import User

from django.http import HttpResponseNotFound, JsonResponse
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin

from chats.models import Contact, Conversation, Message, Profile


class ChatView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = Profile.objects.get(user_id=self.request.user.id)
        context['contacts'] = Contact.objects.filter(user_id=user.id)

        return context


class SearchView(LoginRequiredMixin, TemplateView):
    template_name = 'search.html'

    def post(self, request):
        searched = request.POST.get('searched')
        users = User.objects.filter(username__contains=searched)

        profiles = [Profile.objects.get(user=user).name for user in users]

        return JsonResponse({'profiles': profiles})


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
            return JsonResponse({'chat_uuid': chat_uuid, 'current_user_id': request.user.id, })
        except Exception as e:
            print(e)
            return HttpResponseNotFound()
