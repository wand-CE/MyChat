import json

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Max

from django.http import HttpResponseNotFound, JsonResponse, Http404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View, FormView
from django.contrib.auth.mixins import LoginRequiredMixin

from chats.forms import UpdateProfileForm
from chats.models import Contact, Conversation, Message, Profile


class ChatView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = Profile.objects.get(user_id=self.request.user.id)
        context['current_profile_id'] = profile.id
        context['chats'] = []
        chats = self.get_chats(profile)
        for chat in chats:
            # it's temp while the app only accepts individual chats
            try:
                last_message = chat.get_last_message()
            except ObjectDoesNotExist:
                last_message = None

            context['chats'].append({
                'chat': chat.participants.filter(~Q(id=profile.id))[0],
                'last_message': last_message.content if last_message else '',
            })

        return context

    def get_chats(self, profile):
        return Conversation.objects.filter(participants=profile).annotate(
            last_message_timestamp=Max("messages__timestamp")).order_by("-last_message_timestamp")


class SearchView(LoginRequiredMixin, View):
    def get(self, request):
        current_user = request.user
        searched = request.GET.get('searched')
        users = User.objects.filter(
            Q(username__icontains=searched) & ~Q(id=current_user.id)
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

            user1 = Profile.objects.get(user=request.user)
            user2 = Profile.objects.get(id=int(data.get('chat_id')))

            conversation = Conversation.objects.filter(
                participants=user1).filter(participants=user2).first()
            if not conversation:
                conversation = Conversation.objects.create()
                conversation.participants.add(user1, user2)

            chat_uuid = conversation.uuid
            return JsonResponse({
                'chat_uuid': chat_uuid,
                'current_user_id': user1.id,
                'current_user_name': request.user.username
            })
        except Exception as e:
            print(e)
            return HttpResponseNotFound()


class GetOldMessages(LoginRequiredMixin, View):
    def post(self, request):
        data = json.loads(request.body)
        chat_uuid = data["chat_uuid"]
        user = Profile.objects.get(id=data["current_user_id"])

        conversation = Conversation.objects.get(uuid=chat_uuid)
        friend_profile = conversation.participants.get(~Q(id=user.id))

        messages = Message.objects.filter(conversation=conversation.id)

        messages = [[message.sender.id, message.content,
                     message.timestamp.strftime("%d/%m/%Y|%H:%M")] for message in messages]

        return JsonResponse({'messages': messages, "friend_status": friend_profile.status_display()})


class UpdateProfile(LoginRequiredMixin, FormView):
    template_name = 'update_profile.html'
    form_class = UpdateProfileForm

    success_url = reverse_lazy('profileSettings')

    def get_object(self):
        try:
            return Profile.objects.get(user=self.request.user)
        except Profile.DoesNotExist:
            raise Http404("Perfil não existe")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()
        return kwargs

    def get(self, request, *args, **kwargs):
        profile = self.get_object()
        form = self.form_class(initial={
            'username': profile.user.username
        }, instance=profile)
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        profile = self.get_object()
        context = super().get_context_data(**kwargs)

        context['currentPhoto'] = profile.photo.thumb

        return context

    def form_valid(self, form):
        user = User.objects.get(username=self.request.user)
        user.username = self.request.POST.get('username')
        user.save()

        if self.request.FILES.get('photo', False):
            profile = self.get_object()
            profile.photo = self.request.FILES['photo']
            profile.save()

        return super(UpdateProfile, self).form_valid(form)

    def form_invalid(self, form):
        return super(UpdateProfile, self).form_invalid(form)
