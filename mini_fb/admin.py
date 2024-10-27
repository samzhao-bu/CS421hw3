from django.contrib import admin

from .models import Profile

from .models import StatusMessage
from .models import Image,Friend
admin.site.register(StatusMessage)

admin.site.register(Profile)
admin.site.register(Image)
admin.site.register(Friend)