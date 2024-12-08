from django.urls import path
from .views import RestaurantListView, AvailableTimesView, register, UserReservationListView, MakeReservationView, CancelReservationView, UserReservationListView, CreateReviewView
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
urlpatterns = [
    path('', RestaurantListView.as_view(), name='restaurant_list'),
    path('restaurants/<int:pk>/times/', AvailableTimesView.as_view(), name='available_times'),
    path('login/', LoginView.as_view(template_name='project/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('restaurant_list')), name='logout', kwargs={'next_page': '/'}),
    path('register/', register, name='register'),
    path('make-reservation/', MakeReservationView.as_view(), name='make_reservation'),
    path('cancel-reservation/<int:pk>/', CancelReservationView.as_view(), name='cancel_reservation'),
    path('my-reservations/', UserReservationListView.as_view(), name='user_reservations'),
    path('restaurants/<int:pk>/reviews/add/', CreateReviewView.as_view(), name='add_review'),

]
