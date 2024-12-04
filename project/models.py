from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
class Customer(models.Model):
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
    restaurant_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    image = models.ImageField(upload_to='restaurant_images/')

    def __str__(self):
        return self.restaurant_name

class AvailableTime(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    available_time = models.DateTimeField()
    seats_available = models.IntegerField()
    is_reserved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.restaurant.restaurant_name} at {self.available_time.strftime('%Y-%m-%d %H:%M')}"

class Reservation(models.Model):
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
