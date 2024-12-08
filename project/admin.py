from django.contrib import admin
from .models import Customer, Restaurant, AvailableTime, Reservation, Review

admin.site.register(Customer)
admin.site.register(Restaurant)
admin.site.register(AvailableTime)
admin.site.register(Reservation)
admin.site.register(Review)
