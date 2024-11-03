from django.views.generic import ListView
from django.views.generic import DetailView
from django.views.generic.edit import CreateView
from django.contrib.auth import login
from django.shortcuts import render, redirect
from .models import Profile
from django.views import View
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from .forms import CreateProfileForm
from .forms import CreateStatusMessageForm, UpdateStatusMessageForm
from .models import Profile, StatusMessage, Image
from .forms import UpdateProfileForm, RegisterForm
from django.views.generic.edit import DeleteView
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm

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
    success_url = reverse_lazy('show_all_profiles')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_form'] = UserCreationForm()
        return context
    
    def form_valid(self, form):
        user_form = UserCreationForm(self.request.POST)

        if user_form.is_valid():
            user = user_form.save()
            form.instance.user = user 
            return super().form_valid(form)
        else:
            return self.form_invalid(form)
    
    def get_success_url(self):
        return reverse_lazy('show_profile', kwargs={'pk': self.object.pk})

class CreateStatusMessageView(CreateView):
    model = StatusMessage
    form_class = CreateStatusMessageForm
    template_name = 'mini_fb/create_status_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = Profile.objects.get(user=self.request.user)
        return context
    
    def form_valid(self, form):
        form.instance.profile = Profile.objects.get(user=self.request.user)
        self.object = form.save(commit=False)
        self.object.profile = form.instance.profile
        self.object.save()
        files = self.request.FILES.getlist('files')
        for file in files:
            Image.objects.create(status_message=self.object, image_file=file)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('show_profile', kwargs={'pk': self.request.user.profile.pk})

class UpdateProfileView(UpdateView):
    model = Profile
    form_class = UpdateProfileForm
    template_name = 'mini_fb/update_profile_form.html'

    def get_success_url(self):
        return reverse_lazy('show_profile', kwargs={'pk': self.object.pk})
    
    def get_object(self, queryset=None):
        return self.request.user.profile

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
    
    # def get_object(self, queryset=None):
    #     return self.request.user.profile

class CreateFriendView(View):
    def get(self, request, *args, **kwargs):
        # profile = get_object_or_404(Profile, pk=kwargs['pk'])
        other_profile = get_object_or_404(Profile, pk=kwargs['other_pk'])
        user_profile = request.user.profile
        user_profile.add_friend(other_profile)
        # return redirect('friend_suggestions', pk=profile.pk)
        return redirect('show_profile')
    
    def get_object(self, queryset=None):
        return self.request.user.profile

class ShowFriendSuggestionsView(DetailView):
    model = Profile
    template_name = 'mini_fb/friend_suggestions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['suggestions'] = self.object.get_friend_suggestions()
        return context
    def get_object(self, queryset=None):
        return self.request.user.profile
    
class ShowNewsFeedView(DetailView):
    model = Profile
    template_name = 'mini_fb/news_feed.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()
        context['news_feed'] = profile.get_news_feed()
        return context
    
    def get_object(self, queryset=None):
        return self.request.user.profile
    

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  
            return redirect('show_all_profiles')  
    else:
        form = RegisterForm()
    return render(request, 'mini_fb/register.html', {'form': form})