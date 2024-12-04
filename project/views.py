from django.http import HttpResponse
from django.views.generic.edit import CreateView, DeleteView
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404
from .models import Restaurant, AvailableTime
from django.urls import reverse
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserRegisterForm, ReservationForm,AvailableTimeForm
from .models import Reservation
from django.core.exceptions import ValidationError
from django.utils import timezone




class AvailableTimesView(LoginRequiredMixin, DetailView):
    model = Restaurant
    template_name = 'project/available_times.html'
    context_object_name = 'restaurant'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        times = AvailableTime.objects.filter(restaurant=self.object, seats_available__gt=0).order_by('available_time')
        print("Available times:", times)  # Debugging statement
        context['available_times_forms'] = [
            {'time': time, 'form': AvailableTimeForm(initial={'number_of_seats': 1})} for time in times
        ]
        return context




    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = AvailableTimeForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.customer = request.user.customer
            available_time_id = request.POST.get('available_time_id')
            if available_time_id:
                reservation.available_time = get_object_or_404(AvailableTime, id=available_time_id)
                reservation.save()
                return redirect('user_reservations')
            else:
                form.add_error(None, "Available time is required.")
        context = self.get_context_data()
        context['form_error'] = form.errors
        return render(request, self.template_name, context)





class MakeReservationView(LoginRequiredMixin, CreateView):
    model = Reservation
    form_class = ReservationForm
    template_name = 'project/make_reservation.html'
    success_url = reverse_lazy('user_reservations')

    def form_valid(self, form):
        reservation = form.save(commit=False)
        reservation.customer = self.request.user.customer
        reservation.available_time.seats_available -= reservation.number_of_seats
        reservation.available_time.save()
        reservation.save()
        return super().form_valid(form)

class CancelReservationView(LoginRequiredMixin, DeleteView):
    model = Reservation
    template_name = 'project/confirm_cancel.html'
    success_url = reverse_lazy('user_reservations')

    def get_queryset(self):
        return super().get_queryset().filter(customer__user=self.request.user)

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        reservation = self.get_object()
        available_time = reservation.available_time
        available_time.is_reserved = False
        available_time.save()
        return response

class UserReservationListView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = 'project/user_reservations.html'
    context_object_name = 'reservations'

    def get_queryset(self):
        customer = self.request.user.customer
        return Reservation.objects.filter(customer=customer).order_by('-available_time__available_time')

class RestaurantListView(ListView):
    model = Restaurant
    template_name = 'project/restaurant_list.html'
    context_object_name = 'restaurants'

# class AvailableTimesView(LoginRequiredMixin, DetailView):
#     def get_login_url(self) -> str:
#         '''return the URL required for login'''
#         return reverse('login') 
    

#     model = Restaurant
#     template_name = 'project/available_times.html'
#     context_object_name = 'restaurant'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         restaurant = self.get_object()
#         context['times'] = AvailableTime.objects.filter(restaurant=restaurant).order_by('available_time')
#         return context
    


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('restaurant_list')
    else:
        form = UserRegisterForm()
    return render(request, 'project/register.html', {'form': form})