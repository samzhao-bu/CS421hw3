from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Reservation, AvailableTime, Review
from django.core.exceptions import ValidationError

class UserRegisterForm(UserCreationForm):
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
    class Meta:
        model = Reservation
        fields = ['number_of_seats']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['number_of_seats'].widget = forms.HiddenInput()
        self.fields['number_of_seats'].initial = 1  # Default to 1 seat

    def clean_number_of_seats(self):
        number_of_seats = self.cleaned_data.get('number_of_seats', 1)  # Default to 1 if not provided
        return number_of_seats



class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'rating']
        
    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating < 0 or rating > 5:
            raise forms.ValidationError("Rating must be between 0 and 5.")
        return rating