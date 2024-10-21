from django.contrib import admin
from .models import Profile, friend_request

admin.site.register(Profile)
admin.site.register(friend_request)