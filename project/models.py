# File: views.py
# Author: Songwen Zhao (samzhao@bu.edu)
# Description: The models of my project

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import datetime
from django.utils import timezone
import random 
import datetime
from django.conf import settings
class Customer(models.Model):
    """
    Represents a customer with a one-to-one link to the User model.
    
    Attributes:
        user (OneToOneField): A one-to-one link to Django's User model.
        last_name (CharField): Customer's last name.
        first_name (CharField): Customer's first name.
        address (CharField): Customer's address.
        email (EmailField): Customer's email address.
        date_of_birth (DateField): Customer's date of birth.
        phone_number (CharField): Customer's phone number.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    email = models.EmailField()
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=15)



    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Restaurant(models.Model):
    """
    Represents a restaurant.
    
    Attributes:
        restaurant_name (CharField): Name of the restaurant.
        address (CharField): Address of the restaurant.
        phone_number (CharField): Contact number of the restaurant.
        image (ImageField): Image of the restaurant.
        description (TextField): Description of the restaurant.
        category (CharField): Category of the restaurant cuisine.
    """

    restaurant_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    image = models.ImageField(upload_to='restaurant_images/')
    description = models.TextField(blank=True, null=True)
    CATEGORY_CHOICES = [
        ('Asian', 'Asian Food'),
        ('Italian', 'Italian Food'),
        ('Mexican', 'Mexican Food'),
        ('American', 'American Food'),
        ('French', 'French Food'),
    ]
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.restaurant_name

class AvailableTime(models.Model):
    """
    Represents time slots available for reservations at a restaurant.
    
    Attributes:
        restaurant (ForeignKey): Link to the Restaurant model.
        available_time (DateTimeField): Specific date and time the slot is available.
        seats_available (IntegerField): Number of seats available for this time slot.
        is_reserved (BooleanField): Indicates if the time slot is already reserved.
    """

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    available_time = models.DateTimeField()
    seats_available = models.IntegerField()
    is_reserved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.restaurant.restaurant_name} at {self.available_time.strftime('%Y-%m-%d %H:%M')}"

class Reservation(models.Model):
    """
    Represents a reservation made by a customer.
    
    Attributes:
        available_time (ForeignKey): Link to the AvailableTime model indicating the reserved slot.
        customer (ForeignKey): Link to the Customer model for the customer who made the reservation.
        number_of_seats (IntegerField): Number of seats reserved.
    """

    available_time = models.ForeignKey(AvailableTime, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    number_of_seats = models.IntegerField()

    def __str__(self):
        return (f"Reservation for {self.customer} at {self.available_time.restaurant.restaurant_name} "
                f"on {self.available_time.available_time.strftime('%Y-%m-%d %H:%M')}")

    def save(self, *args, **kwargs):
        if self.pk is None:  
            self.available_time.seats_available -= self.number_of_seats
            self.available_time.save()
        super().save(*args, **kwargs)

def load_boston_restaurants():
    boston_restaurants = [
        {"restaurant_name": "Boston Harbor Dining", "address": "101 Harbor Dr, Boston, MA", "phone_number": "617-001-0001", "description": "Seafood and more with a view of Boston Harbor.", "category": "American"},
        {"restaurant_name": "Little Italy Eats", "address": "202 Hanover St, Boston, MA", "phone_number": "617-002-0002", "description": "Authentic Italian dishes in Boston's North End.", "category": "Italian"},
        {"restaurant_name": "Szechuan Chef", "address": "350 Washington St, Boston, MA", "phone_number": "617-003-0003", "description": "Spicy and original Szechuan cuisine.", "category": "Asian"},
        {"restaurant_name": "Le Parisien Bistrot", "address": "59 Temple Pl, Boston, MA", "phone_number": "617-004-0004", "description": "French cuisine with a cozy ambiance.", "category": "French"},
        {"restaurant_name": "El Burrito Loco", "address": "477 Cambridge St, Boston, MA", "phone_number": "617-005-0005", "description": "Vibrant Mexican flavors and giant burritos.", "category": "Mexican"},
        {"restaurant_name": "The Lobster Pot", "address": "303 Congress St, Boston, MA", "phone_number": "617-006-0006", "description": "Fresh lobster and seafood specialties.", "category": "American"},
        {"restaurant_name": "Tokyo Japanese Steakhouse", "address": "22 Kneeland St, Boston, MA", "phone_number": "617-007-0007", "description": "Japanese sushi and hibachi.", "category": "Asian"},
        {"restaurant_name": "The North End Bakery", "address": "215 Hanover St, Boston, MA", "phone_number": "617-008-0008", "description": "Homemade pastries and Italian coffee.", "category": "Italian"},
        {"restaurant_name": "Tandoori Palace", "address": "416 Boylston St, Boston, MA", "phone_number": "617-009-0009", "description": "Traditional Indian dishes and tandoori oven specialties.", "category": "Asian"},
        {"restaurant_name": "Boston Brewery", "address": "306 Northern Ave, Boston, MA", "phone_number": "617-010-0010", "description": "Craft beers and classic American pub food.", "category": "American"},
        {"restaurant_name": "Green Dragon Tavern", "address": "11 Marshall St, Boston, MA", "phone_number": "617-011-0011", "description": "Historic pub with local brews and spirits.", "category": "American"},
        {"restaurant_name": "Pasta Piazza", "address": "45 Winter St, Boston, MA", "phone_number": "617-012-0012", "description": "Fresh pasta and Italian wines.", "category": "Italian"},
        {"restaurant_name": "Canton Dim Sum", "address": "10 Tyler St, Boston, MA", "phone_number": "617-013-0013", "description": "Authentic Cantonese dim sum and teas.", "category": "Asian"},
        {"restaurant_name": "Boston Chop House", "address": "320 Summer St, Boston, MA", "phone_number": "617-014-0014", "description": "Steaks and chops in a sophisticated setting.", "category": "American"},
        {"restaurant_name": "Baja Taco Truck", "address": "12 Carleton St, Boston, MA", "phone_number": "617-015-0015", "description": "Street-style tacos and Mexican sodas.", "category": "Mexican"},
        {"restaurant_name": "Beantown Pho and Grill", "address": "255 State St, Boston, MA", "phone_number": "617-016-0016", "description": "Pho, banh mi, and Vietnamese grills.", "category": "Asian"},
        {"restaurant_name": "The Codfather", "address": "666 Atlantic Ave, Boston, MA", "phone_number": "617-017-0017", "description": "Seafood platters and fish & chips.", "category": "American"},
        {"restaurant_name": "The French Connection", "address": "101 Arch St, Boston, MA", "phone_number": "617-018-0018", "description": "Elegant French dining and wine bar.", "category": "French"},
        {"restaurant_name": "Curry House", "address": "1234 Commonwealth Ave, Boston, MA", "phone_number": "617-019-0019", "description": "Spicy South Indian curry and naan bread.", "category": "Asian"},
        {"restaurant_name": "Bavarian Beerhaus", "address": "789 Boylston St, Boston, MA", "phone_number": "617-020-0020", "description": "German beers and sausages in a rustic setting.", "category": "European"}
    ]

    Restaurant.objects.all().delete()


    for restaurant in boston_restaurants:
        Restaurant.objects.create(**restaurant)

    print("Sample restaurants in Boston loaded successfully!")




def generate_time_slots(start_time, end_time, date):
    """ Helper function to generate time slots for a given date within the operating hours. """
    time_slots = []
    current_time = datetime.datetime.combine(date, start_time)
    while current_time.time() <= end_time:
        time_slots.append(current_time)
        current_time += datetime.timedelta(hours=1)  
    return time_slots

def generate_available_times(seats):
    start_date = timezone.now().date()
    end_date = datetime.date(2025, 1, 1)
    date_delta = datetime.timedelta(days=1)

    default_open_time = datetime.time(11, 0)  # 11 AM
    default_close_time_weekday = datetime.time(21, 0)  # 9 PM
    default_close_time_weekend = datetime.time(22, 0)  # 10 PM

    entries = []
    current_date = start_date
    while current_date <= end_date:
        weekend = current_date.weekday() >= 5  # Weekend check
        close_time = default_close_time_weekend if weekend else default_close_time_weekday
        
        for restaurant in Restaurant.objects.all():
            # Randomly decide if a restaurant opens early
            open_time = datetime.time(8, 0) if random.choice([True, False]) else default_open_time
            
            time_slots = [datetime.datetime.combine(current_date, datetime.time(hour=hour))
                          for hour in range(open_time.hour, close_time.hour + 1)]

            for slot in time_slots:
                entries.append(AvailableTime(
                    restaurant=restaurant,
                    available_time=slot,
                    seats_available=seats,
                    is_reserved=False
                ))
        
        current_date += date_delta

    AvailableTime.objects.bulk_create(entries)
    print("Optimized available times generated successfully!")


class Review(models.Model):
    """
    Represents a review submitted by a customer for a restaurant.
    
    Attributes:
        restaurant (ForeignKey): Link to the Restaurant model the review is about.
        customer (ForeignKey): Link to the User model who submitted the review.
        text (TextField): The content of the review.
        rating (IntegerField): Rating given by the customer.
        created_at (DateTimeField): Date and time when the review was created.
    """
    
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    rating = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.rating} stars by {self.customer} for {self.restaurant}'