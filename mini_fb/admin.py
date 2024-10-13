from django.contrib import admin

from .models import Profile

from .models import StatusMessage

admin.site.register(StatusMessage)

admin.site.register(Profile)