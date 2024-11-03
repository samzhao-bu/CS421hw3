from django.urls import path
from django.conf import settings
from .views import CreateProfileView, ShowAllProfilesView, ShowProfilePageView, DeleteStatusMessageView, UpdateStatusMessageView
from .views import CreateStatusMessageView
from .views import UpdateProfileView
from .views import CreateFriendView
from django.urls import reverse_lazy
from .views import ShowFriendSuggestionsView, ShowNewsFeedView, register
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('', ShowAllProfilesView.as_view(), name='show_all_profiles'),
    path('profile/<int:pk>', ShowProfilePageView.as_view(), name='show_profile'),
    path('create_profile', CreateProfileView.as_view(), name='create_profile'),
    path('profile/<int:pk>/create_status', CreateStatusMessageView.as_view(), name='create_status'),
    path('profile/<int:pk>/update', UpdateProfileView.as_view(), name='update_profile'),
    path('status/<int:pk>/delete', DeleteStatusMessageView.as_view(), name='delete_status'),
    path('status/<int:pk>/update', UpdateStatusMessageView.as_view(), name='update_status'),
    path('profile/<int:pk>/add_friend/<int:other_pk>', CreateFriendView.as_view(), name='add_friend'),
    path('profile/<int:pk>/friend_suggestions', ShowFriendSuggestionsView.as_view(), name='friend_suggestions'),
    path('profile/<int:pk>/news_feed', ShowNewsFeedView.as_view(), name='news_feed'),
    path('register/', register, name='register'),
    path('login/', LoginView.as_view(template_name='mini_fb/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('show_all_profiles')), name='logout'),
]
