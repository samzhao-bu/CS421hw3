from django.views.generic import ListView
from django.views.generic import DetailView
from django.views.generic.edit import CreateView
from .models import Profile
from django.views import View
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from .forms import CreateProfileForm
from .forms import CreateStatusMessageForm, UpdateStatusMessageForm
from .models import Profile, StatusMessage, Image
from .forms import UpdateProfileForm
from django.views.generic.edit import DeleteView
from django.shortcuts import redirect, get_object_or_404

class ShowAllProfilesView(ListView):
    model = Profile
    template_name = 'mini_fb/show_all_profiles.html'
    context_object_name = 'profiles'

class ShowProfilePageView(DetailView):
    model = Profile
    template_name = 'mini_fb/show_profile.html'
    context_object_name = 'profile'

class CreateProfileView(CreateView):
    model = Profile
    form_class = CreateProfileForm
    template_name = 'mini_fb/create_profile_form.html'

    def get_success_url(self):
        return reverse_lazy('show_profile', kwargs={'pk': self.object.pk})

class CreateStatusMessageView(CreateView):
    model = StatusMessage
    form_class = CreateStatusMessageForm
    template_name = 'mini_fb/create_status_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = Profile.objects.get(pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        form.instance.profile = Profile.objects.get(pk=self.kwargs['pk'])
        self.object = form.save(commit=False)
        self.object.profile = Profile.objects.get(pk=self.kwargs['pk'])
        self.object.save()
        files = self.request.FILES.getlist('files')
        for file in files:
            Image.objects.create(status_message=self.object, image_file=file)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('show_profile', kwargs={'pk': self.kwargs['pk']})

class UpdateProfileView(UpdateView):
    model = Profile
    form_class = UpdateProfileForm
    template_name = 'mini_fb/update_profile_form.html'

    def get_success_url(self):
        return reverse_lazy('show_profile', kwargs={'pk': self.object.pk})

class DeleteStatusMessageView(DeleteView):
    model = StatusMessage
    template_name = 'mini_fb/delete_status_form.html'
    context_object_name = 'status'

    def get_success_url(self):
        return reverse_lazy('show_profile', args=[self.object.profile.pk])

class UpdateStatusMessageView(UpdateView):
    model = StatusMessage
    form_class = UpdateStatusMessageForm
    template_name = 'mini_fb/update_status_form.html'

    def get_success_url(self):
        return reverse_lazy('show_profile', args=[self.object.profile.pk])

class CreateFriendView(View):
    def get(self, request, *args, **kwargs):
        profile = get_object_or_404(Profile, pk=kwargs['pk'])
        other_profile = get_object_or_404(Profile, pk=kwargs['other_pk'])
        profile.add_friend(other_profile)
        return redirect('friend_suggestions', pk=profile.pk)
class ShowFriendSuggestionsView(DetailView):
    model = Profile
    template_name = 'mini_fb/friend_suggestions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['suggestions'] = self.object.get_friend_suggestions()
        return context
    
class ShowNewsFeedView(DetailView):
    model = Profile
    template_name = 'mini_fb/news_feed.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()
        context['news_feed'] = profile.get_news_feed()
        return context