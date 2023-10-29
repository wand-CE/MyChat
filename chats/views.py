from django.views.generic import TemplateView

from chats.models import Message, Profile


class Home(TemplateView):
    template_name = "home.html"


class RoomView(TemplateView):
    template_name = 'teste.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['room_name'] = self.kwargs['room_name']
        context['messages'] = Message.objects.filter(conversation_id=3)
        context['profiles'] = Profile.objects.all()

        return context
