# File: views.py
# Author: Songwen Zhao (samzhao@bu.edu)
# Description: The forms of my project

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Reservation, AvailableTime, Review, Customer
from django.core.exceptions import ValidationError

class UserRegisterForm(UserCreationForm):
    """
    Custom user registration form extending Django's built-in UserCreationForm.
    
    Attributes:
        first_name (CharField): First name field, required.
        last_name (CharField): Last name field, required.
        email (EmailField): Email field, required.
        address (CharField): Address field.
        date_of_birth (DateField): Date of birth field, with a date picker widget.
        phone_number (CharField): Phone number field.
    """

    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    address = forms.CharField(max_length=255)
    date_of_birth = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    phone_number = forms.CharField(max_length=15)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'address', 'date_of_birth', 'phone_number']

class ReservationForm(forms.ModelForm):
    """
    Form for creating and validating a reservation.
    
    """

    class Meta:
        model = Reservation
        fields = ['available_time', 'number_of_seats']

    def clean(self):
        cleaned_data = super().clean()
        available_time = cleaned_data.get('available_time')
        number_of_seats = cleaned_data.get('number_of_seats')
        if available_time and number_of_seats:
            if available_time.seats_available < number_of_seats:
                raise ValidationError("Not enough seats available.")
        return cleaned_data

class AvailableTimeForm(forms.ModelForm):
    """
    Form for booking a specific number of seats (hidden input by default).

    Initialized with 1 seat for simplicity.
    """
     
    class Meta:
        model = Reservation
        fields = ['number_of_seats']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['number_of_seats'].widget = forms.HiddenInput()
        self.fields['number_of_seats'].initial = 1  # Default to 1 seat

    def clean_number_of_seats(self):
        """
        Validates that the number of seats is a positive integer.

        Returns:
            int: The validated number of seats.
        """

        number_of_seats = self.cleaned_data.get('number_of_seats', 1)  # Default to 1 if not provided
        return number_of_seats



class ReviewForm(forms.ModelForm):
    """
    Form for creating and validating a review.

    Attributes:
        text (TextField): Field for the review text.
        rating (IntegerField): Field for the review rating, must be between 0 and 5.
    """

    class Meta:
        model = Review
        fields = ['text', 'rating']

    def clean_rating(self):
        """
        Validates that the rating is between 0 and 5.

        Returns:
            int: The validated rating value.

        Raises:
            ValidationError: If the rating is outside the allowed range.
        """
         
        rating = self.cleaned_data.get('rating')
        if rating < 0 or rating > 5:
            raise forms.ValidationError("Rating must be between 0 and 5.")
        return rating
    
class CustomerProfileForm(forms.ModelForm):
    """
    Form for editing a customer's profile.
    
    Allows editing of first name, last name, address, email, date of birth, and phone number.
    """
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'address', 'email', 'date_of_birth', 'phone_number']
