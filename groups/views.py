import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View

from chats.models import Conversation
from groups.forms import CreateGroupForm
from groups.models import GroupNames
from profiles.models import Profile


class CreateGroup(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        form = CreateGroupForm(request.POST)
        if form.is_valid():
            current_profile = Profile.objects.get(user=request.user)

            chat = Conversation.objects.create(is_group=True)
            chat.participants.add(current_profile)

            group_name = form.cleaned_data['name']
            participants = self.request.POST.get('participants', None)

            if participants:
                for p_id in participants.split(','):
                    profile = Profile.objects.get(id=int(p_id))
                    chat.participants.add(profile)

            photo = self.request.FILES.get('photo', None)
            if photo:
                group = GroupNames.objects.create(
                    chat=chat, name=group_name, photo=photo)
            else:
                group = GroupNames.objects.create(chat=chat, name=group_name)
            group.admin.add(current_profile)

            return JsonResponse({
                "chatUuid": chat.uuid,
                "photo": group.photo.thumb.url,
                "name": group.name,
            })


class ModifyGroup(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        chat = Conversation.objects.get(uuid=data['chat_uuid'])
        chat.participants.clear()
        for profile_id in data['listProfiles']:
            profile = Profile.objects.get(id=int(profile_id))
            chat.participants.add(profile)
        chat.save()

        return JsonResponse({'status': 'Success'})
