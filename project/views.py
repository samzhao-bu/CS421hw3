from django.http import HttpResponse
from django.views.generic.edit import CreateView, DeleteView
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404
from .models import Restaurant, AvailableTime, Customer
from django.urls import reverse
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserRegisterForm, ReservationForm,AvailableTimeForm, ReviewForm
from .models import Reservation, Review
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_time
import datetime
from datetime import timedelta 
from django.http import HttpResponseRedirect
from django.db.models import Avg




class AvailableTimesView(LoginRequiredMixin, DetailView):
    model = Restaurant
    template_name = 'project/available_times.html'
    context_object_name = 'restaurant'

    def get_login_url(self) -> str:
        '''return the URL required for login'''
        return reverse('login') 


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Generate hours list for the time dropdown
        hours_list = [f"{hour:02}:00" for hour in range(8, 23)]  # This is just a basic hour list (8 AM - 10 PM)
        context['hours_list'] = hours_list

        selected_date = self.request.GET.get('selected_date')
        selected_time = self.request.GET.get('selected_time')

        if selected_date and selected_time:
            selected_date = parse_date(selected_date)
            selected_time = datetime.datetime.strptime(selected_time, "%H:%M").time()  # Parse the selected time

            # Combine date and time into a full datetime object
            start_datetime = datetime.datetime.combine(selected_date, selected_time)
            end_datetime = start_datetime + datetime.timedelta(hours=1)  # Assuming a 1-hour slot

            # Now filter available times using this datetime range
            times = AvailableTime.objects.filter(
                restaurant=self.object,
                seats_available__gt=0,
                is_reserved=False,
                available_time__range=(start_datetime, end_datetime)
            ).order_by('available_time')

            context['available_times_forms'] = [
                {'time': time, 'form': AvailableTimeForm(initial={'number_of_seats': 1})} for time in times
            ]
        else:
            context['available_times_forms'] = []
        reviews = Review.objects.filter(restaurant=self.object)
        context['reviews'] = reviews
        context['user_review'] = reviews.filter(customer=self.request.user).first()

        average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        context['average_rating'] = round(average_rating, 1) if average_rating else None

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
                if reservation.available_time.is_reserved:
                    return HttpResponse("This time is no longer available.", status=400)
                reservation.available_time.is_reserved = True
                reservation.available_time.save()
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
        # reservation.available_time.seats_available -= reservation.number_of_seats
        reservation.available_time.seats_available -= 0
        reservation.available_time.save()
        reservation.save()
        return super().form_valid(form)

class CancelReservationView(LoginRequiredMixin, DeleteView):
    model = Reservation
    template_name = 'project/confirm_cancel.html'
    success_url = reverse_lazy('user_reservations')

    def get_queryset(self):
        return super().get_queryset().filter(customer__user=self.request.user)

    def form_valid(self, form):
        # Start a transaction to ensure database integrity
        with transaction.atomic():
            # Get the reservation object before it's deleted
            reservation = self.get_object()
            available_time = reservation.available_time

            # Call the super to perform the actual deletion
            response = super().form_valid(form)

            # Update the available time to mark it as not reserved
            available_time.is_reserved = False
            available_time.seats_available += 1
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

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.GET.get('category')
        name_query = self.request.GET.get('search_name')

        if category:
            queryset = queryset.filter(category=category)
        if name_query:
            queryset = queryset.filter(restaurant_name__icontains=name_query)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_choices'] = Restaurant.CATEGORY_CHOICES
        context['search_name'] = self.request.GET.get('search_name', '')  # Add the search query to context
        return context

    

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
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']  # Make sure email is set correctly
            user.save()
            Customer.objects.create(
                user=user,
                last_name=form.cleaned_data['last_name'],
                first_name=form.cleaned_data['first_name'],
                address=form.cleaned_data['address'],
                email=form.cleaned_data['email'],
                date_of_birth=form.cleaned_data['date_of_birth'],
                phone_number=form.cleaned_data['phone_number']
            )
            login(request, user)
            return redirect('restaurant_list')
    else:
        form = UserRegisterForm()
    return render(request, 'project/register.html', {'form': form})

class CreateReviewView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'project/create_review.html'
    def get_success_url(self):
        if hasattr(self, 'object') and self.object is not None:
            return reverse('available_times', kwargs={'pk': self.object.restaurant.pk})
        else:
            return reverse('restaurant_list') 


   
    def dispatch(self, request, *args, **kwargs):
        if Review.objects.filter(restaurant_id=self.kwargs['pk'], customer=request.user).exists():
            return HttpResponseRedirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.customer = self.request.user  # Assigning the logged-in user directly
        form.instance.restaurant = get_object_or_404(Restaurant, pk=self.kwargs['pk'])
        return super().form_valid(form)



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'restaurant' not in context:
            context['restaurant'] = get_object_or_404(Restaurant, pk=self.kwargs['pk'])
        return context