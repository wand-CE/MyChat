import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Max
from django.http import HttpResponseNotFound, JsonResponse
from django.views.generic import TemplateView, View

from chats.models import Conversation, Message, Profile, MessageReadStatus
from groups.forms import CreateGroupForm


class ChatView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = Profile.objects.get(user_id=self.request.user.id)
        context['current_profile_id'] = profile.id
        context['chats'] = []
        context['form_create_group'] = CreateGroupForm
        chats = self.get_chats(profile)
        for chat in chats:
            # it's temp while the app only accepts individual chats
            try:
                last_message = chat.get_last_message()
                status = None
                if last_message and last_message.sender != profile:
                    status = MessageReadStatus.objects.filter(Q(message=last_message) & Q(recipientProfile=profile))
                    status = (status.first())
            except ObjectDoesNotExist:
                last_message = None
                status = None

            if chat.is_group:
                group_element = chat.get_group_data()
                name = group_element.name
                photo = group_element.photo
            else:
                profile_element = chat.participants.get(~Q(id=profile.id))
                name = profile_element.user.username
                photo = profile_element.photo

            context['chats'].append({
                'data': {
                    'uuid': chat.uuid,
                    'is_group': chat.is_group,
                    'name': name,
                    'photo': photo.thumb.url,
                },
                'last_message': last_message if last_message else '',
                'status_message': status.is_read if status else True
            })

        return context

    def get_chats(self, profile):
        return Conversation.objects.filter(participants=profile).annotate(
            last_message_timestamp=Max("messages__timestamp")).order_by("-last_message_timestamp")


class SearchView(LoginRequiredMixin, View):
    def get(self, request):
        current_user = request.user
        profiles = request.GET.get('profiles', None)

        if profiles:
            users = User.objects.filter(Q(username__icontains=profiles) & ~Q(id=current_user.id))
            current_user_profile = Profile.objects.get(user=current_user)

            profiles = [Profile.objects.get(user=user) for user in users]
            list_profiles = []

            for profile in profiles:
                search_chat = Conversation.objects.filter(Q(is_group=False) & Q(participants=current_user_profile))
                search_chat = (search_chat.filter(participants=profile).first())

                current_profile = {
                    'uuid': f'uuid:{search_chat.uuid}' if search_chat else f'profile_id:{profile.id}',
                    'profile_id': profile.id,
                    'name': profile.name,
                    'photo': profile.photo.thumb.url,
                }

                list_profiles.append(current_profile)
            return JsonResponse({'profiles': list_profiles})
        return JsonResponse({'erro': 'argumento profiles faltando'})


class ReturnChat(LoginRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request):
        try:
            data = json.loads(request.body)

            user1 = Profile.objects.get(user=request.user)
            data = data.get('chat_data').split(':')

            if 'profile_id' == data[0]:
                user2 = Profile.objects.get(id=int(data[1]))

                chat = Conversation.objects.create()
                chat.participants.add(user1, user2)
            else:
                chat = Conversation.objects.get(uuid=data[1])

            return JsonResponse({
                'chat_uuid': chat.uuid,
                'is_group': chat.is_group,
                'current_user_id': user1.id,
                'current_user_name': request.user.username
            })
        except Exception as e:
            return HttpResponseNotFound()


class GetOldMessages(LoginRequiredMixin, View):
    def post(self, request):
        data = json.loads(request.body)
        chat_uuid = data["chat_uuid"]
        user = Profile.objects.get(id=data["current_user_id"])
        is_group = data["is_group"]

        dicio = {}

        chat = Conversation.objects.get(uuid=chat_uuid)

        if not is_group:
            friend_profile = chat.participants.get(~Q(id=user.id))
            dicio["friend_status"] = friend_profile.status_display()

        messages = Message.objects.filter(conversation=chat.id)

        dicio["messages"] = [[
            {
                'id': message.sender.id,
                'name': message.sender.name,
            },
            message.is_read(),
            message.content,
            message.timestamp.strftime("%d/%m/%Y|%H:%M")] for message in messages]
        dicio['is_group'] = chat.is_group

        if dicio['is_group']:
            dicio['participants'] = {'names': [],
                                     'profiles_ids': [],
                                     'photos': []}

            for p in chat.participants.all():
                dicio['participants']['names'].append(f' {p.name}'),
                dicio['participants']['profiles_ids'].append(p.id),
                dicio['participants']['photos'].append(p.photo.thumb.url)

        return JsonResponse(dicio)
