from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=100)
    score = models.IntegerField(default=0)
    image  = models.ImageField(upload_to='./upload')

    def __str__(self):
        return f'{self.user.username} Profile'