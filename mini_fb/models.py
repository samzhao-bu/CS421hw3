from django.db import models
from django.utils import timezone
from django.urls import reverse

class Profile(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    email = models.EmailField()
    profile_image_url = models.URLField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_status_messages(self):
        return self.status_messages.order_by('-timestamp')
    
    def get_absolute_url(self):
        return reverse('show_profile', args=[str(self.pk)])
    
class StatusMessage(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    message = models.TextField()
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='status_messages')

    def __str__(self):
        return f"{self.message} ({self.timestamp})"

