# File: views.py
# Author: Songwen Zhao (samzhao@bu.edu)
# Description: The views of my project


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
from django.views.generic import TemplateView
from django.views.generic import UpdateView
from .forms import CustomerProfileForm



class AvailableTimesView(LoginRequiredMixin, DetailView):
    """
    Displays available time slots for a restaurant for users to make reservations.

    Attributes:
        model (Model): Django model, Restaurant, associated with the view.
        template_name (str): Path to the HTML template used to render the view.
        context_object_name (str): Context name used in the template to refer to the object.
    """

    model = Restaurant
    template_name = 'project/available_times.html'
    context_object_name = 'restaurant'

    def get_login_url(self) -> str:
        '''return the URL required for login'''
        return reverse('login') 


    def get_context_data(self, **kwargs):
        """
        Extends the base implementation to add additional context for the template.

        Generates a list of hours for the dropdown and filters available times based on the user's date and time selection.

        Returns:
            dict: Context dictionary.
        """

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
        # Setup for reviews
        reviews = Review.objects.filter(restaurant=self.object)
        context['reviews'] = reviews
        context['user_review'] = reviews.filter(customer=self.request.user).first()

        # Calculate stars for average rating
        if reviews.exists():
            average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
            filled_stars = round(average_rating)
            unfilled_stars = 5 - filled_stars
        else:
            filled_stars = 0
            unfilled_stars = 5
        average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        context['average_rating'] = average_rating
        context['filled_stars'] = range(filled_stars)
        context['unfilled_stars'] = range(unfilled_stars)

        return context

        
    def post(self, request, *args, **kwargs):
        """
        Handles POST request for making a reservation. Validates the form and updates database accordingly.

        Args:
            request (HttpRequest): The request object containing POST data.
            *args: Variable arguments.
            **kwargs: Keyword arguments.

        Returns:
            HttpResponse or HttpResponseRedirect: Redirects to user reservations on success or renders the form with errors.
        """

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
    
    """
    Handles the creation of new reservations through a form submission for authenticated users.

    Attributes:
        model (Model): Django model, Reservation, associated with the view.
        form_class (Form): Form class, ReservationForm, used for creating a reservation.
        template_name (str): Path to the HTML template used to render the view.
        success_url (str): URL to redirect to after successfully creating a reservation.
    """
    model = Reservation
    form_class = ReservationForm
    template_name = 'project/make_reservation.html'
    success_url = reverse_lazy('user_reservations')

    def form_valid(self, form):
        """
        Extends the form_valid method to add custom handling, ensuring that the reservation details are correct and the associated AvailableTime is updated.

        Args:
            form (Form): The validated form instance.

        Returns:
            HttpResponseRedirect: Redirects to the success URL defined for the view.
        """

        reservation = form.save(commit=False)
        reservation.customer = self.request.user.customer
        # reservation.available_time.seats_available -= reservation.number_of_seats
        reservation.available_time.seats_available -= 0
        reservation.available_time.save()
        reservation.save()
        return super().form_valid(form)

class CancelReservationView(LoginRequiredMixin, DeleteView):
    """
    Handles the deletion of reservations for authenticated users, ensuring database integrity with transactions.

    Attributes:
        model (Model): Django model, Reservation, associated with the view.
        template_name (str): Path to the HTML template used to confirm the deletion.
        success_url (str): URL to redirect to after successfully deleting a reservation.
    """

    model = Reservation
    template_name = 'project/confirm_cancel.html'
    success_url = reverse_lazy('user_reservations')

    def get_queryset(self):
        """
        Filters the queryset to only include reservations of the currently logged-in user.

        Returns:
            QuerySet: Filtered queryset.
        """
        return super().get_queryset().filter(customer__user=self.request.user)

    def form_valid(self, form):
        """
        Extends the form_valid method to handle reservation deletion with transactional integrity, 
        and to update the associated AvailableTime object.

        Args:
            form (Form): The form instance, not typically used in DeleteView.

        Returns:
            HttpResponseRedirect: Redirects to the success URL defined for the view.
        """

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
    """
    Displays a list of reservations for the currently logged-in user.

    Attributes:
        model (Model): Django model, Reservation, associated with the view.
        template_name (str): Path to the HTML template used to render the list.
        context_object_name (str): Name of the context object used in the template.
    """

    model = Reservation
    template_name = 'project/user_reservations.html'
    context_object_name = 'reservations'

    def get_queryset(self):
        """
        Filters the queryset to only include reservations of the currently logged-in user's customer account.

        Returns:
            QuerySet: Filtered queryset sorted by reservation time in descending order.
        """

        customer = self.request.user.customer
        return Reservation.objects.filter(customer=customer).order_by('-available_time__available_time')

class RestaurantListView(ListView):
    """
    Displays a list of restaurants, optionally filtered by category or search query.

    Attributes:
        model (Model): Django model, Restaurant, associated with the view.
        template_name (str): Path to the HTML template used to render the list.
        context_object_name (str): Name of the context object used in the template.
    """

    model = Restaurant
    template_name = 'project/restaurant_list.html'
    context_object_name = 'restaurants'

    def get_queryset(self):
        """
        Optionally filters the queryset based on category or a search term provided by the user.

        Returns:
            QuerySet: The filtered or unfiltered queryset.
        """


        queryset = super().get_queryset()
        category = self.request.GET.get('category')
        name_query = self.request.GET.get('search_name')

        if category:
            queryset = queryset.filter(category=category)
        if name_query:
            queryset = queryset.filter(restaurant_name__icontains=name_query)
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        Extends base implementation to add additional context for the template.

        Adds form options and current search terms to the context.

        Returns:
            dict: Context dictionary with additional search-related data.
        """

        context = super().get_context_data(**kwargs)
        context['category_choices'] = Restaurant.CATEGORY_CHOICES
        context['search_name'] = self.request.GET.get('search_name', '')  # Add the search query to context
        return context

    



def register(request):
    """
    Handles user registration and creates a corresponding customer profile.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object, redirect on successful registration, or render on GET or invalid form.
    """

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
    """
    View for creating a review for a specific restaurant by a logged-in user.

    Attributes:
        model (Model): The Review model.
        form_class (Form): The ReviewForm to handle input data.
        template_name (str): Path to the HTML template.
    """

    model = Review
    form_class = ReviewForm
    template_name = 'project/create_review.html'


    def get_success_url(self):
        """
        Defines the URL to redirect to after successfully creating a review.

        Returns:
            str: URL to redirect to.
        """
        if hasattr(self, 'object') and self.object is not None:
            return reverse('available_times', kwargs={'pk': self.object.restaurant.pk})
        else:
            return reverse('restaurant_list') 


   
    def dispatch(self, request, *args, **kwargs):
        """
        Prevents multiple reviews by the same user for the same restaurant.

        Returns:
            HttpResponse: Redirects if a review already exists, otherwise processes the request normally.
        """

        if Review.objects.filter(restaurant_id=self.kwargs['pk'], customer=request.user).exists():
            return HttpResponseRedirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Assigns the restaurant and customer to the form instance before saving.

        Args:
            form (Form): The validated form.

        Returns:
            HttpResponse: Redirects to the success URL.
        """

        form.instance.customer = self.request.user  # Assigning the logged-in user directly
        form.instance.restaurant = get_object_or_404(Restaurant, pk=self.kwargs['pk'])
        return super().form_valid(form)



    def get_context_data(self, **kwargs):
        """
        Adds restaurant data to the context.

        Returns:
            dict: The context data.
        """

        context = super().get_context_data(**kwargs)
        if 'restaurant' not in context:
            context['restaurant'] = get_object_or_404(Restaurant, pk=self.kwargs['pk'])
        return context
    

class MyProfileView(LoginRequiredMixin, TemplateView):
    """
    Displays the profile of the logged-in user.

    Attributes:
        template_name (str): Path to the HTML template.
    """

    template_name = 'project/my_profile.html'

    def get_context_data(self, **kwargs):
        """
        Adds the customer data to the context.

        Returns:
            dict: The context data.
        """

        context = super().get_context_data(**kwargs)
        try:
            customer = self.request.user.customer  # Access the customer profile linked to the user
        except Customer.DoesNotExist:
            customer = None  # Handle case where no customer profile exists
        context['customer'] = customer
        return context

class UpdateProfileView(LoginRequiredMixin, UpdateView):
    """
    Allows users to update their profile information.

    Attributes:
        model (Model): The Customer model.
        form_class (Form): The CustomerProfileForm.
        template_name (str): Path to the HTML template.
    """

    model = Customer
    form_class = CustomerProfileForm
    template_name = 'project/update_profile.html'
    
    def get_object(self):
        """
        Retrieves the Customer instance associated with the logged-in user.

        Returns:
            Customer: The Customer instance of the logged-in user.
        """

        return self.request.user.customer
    
    def get_success_url(self):
        """
        Defines the URL to redirect to after successfully updating the profile.

        Returns:
            str: URL to redirect to.
        """
        
        return reverse_lazy('my-profile')  # Redirect to the profile page after update