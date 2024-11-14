from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic import FormView

from profiles.forms import UpdateProfileForm
from profiles.models import Profile


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

        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)
