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
    
    def get_friends(self):
        friends_list = set()
        friends_as_profile1 = self.friends_from_profile1.all()
        friends_as_profile2 = self.friends_from_profile2.all()

        for friend in friends_as_profile1:
            friends_list.add(friend.profile2)
        for friend in friends_as_profile2:
            friends_list.add(friend.profile1)
        return list(friends_list)
    
    def add_friend(self, other):
        if self == other:
            return "Cannot friend yourself."
        

        existing_friendship = Friend.objects.filter(
            (models.Q(profile1=self) & models.Q(profile2=other)) | 
            (models.Q(profile1=other) & models.Q(profile2=self))
        )
        if existing_friendship.exists():
            return "Friendship already exists."
        Friend.objects.create(profile1=self, profile2=other)
        return "Friendship created successfully."
    
    def get_friend_suggestions(self):
        all_profiles = Profile.objects.exclude(id=self.id)  
        friends = self.get_friends()
        friend_ids = [friend.id for friend in friends]
        suggestions = all_profiles.exclude(id__in=friend_ids)
        return suggestions
    
    def get_news_feed(self):
        friends = self.get_friends()
        friend_ids = [friend.pk for friend in friends]
        friend_ids.append(self.pk) 
        return StatusMessage.objects.filter(profile__pk__in=friend_ids).order_by('-timestamp')
    
class StatusMessage(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    message = models.TextField()
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='status_messages')

    def __str__(self):
        return f"{self.message} ({self.timestamp})"
    
    def get_images(self):
        return self.images.all()

class Image(models.Model):
    status_message = models.ForeignKey('StatusMessage', related_name='images', on_delete=models.CASCADE)
    image_file = models.ImageField(upload_to='status_images/')
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Image for {self.status_message} uploaded at {self.timestamp}"


class Friend(models.Model):
    profile1 = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='friends_from_profile1')
    profile2 = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='friends_from_profile2')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.profile1.first_name} {self.profile1.last_name} & {self.profile2.first_name} {self.profile2.last_name}'

