from rest_framework import serializers
from .models import Profile, friend_request
from django.contrib.auth.models import User

class SerializerProfile(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"

class Serializer_Friend_request(serializers.ModelSerializer):
    class Meta:
        model = friend_request
        fields = "__all__"

class Serializer_User(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]