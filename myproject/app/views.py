from django.shortcuts import render, redirect

from django.http import HttpRequest
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from .models import profile

def home(request):
    return render(request, 'home.html')


def register_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]
        if password == confirm_password:
            if not User.objects.filter(username=username).exists():
                if not User.objects.filter(email=email).exists():
                    user = User.objects.create_user(username=username, email=email, password=make_password(password))
                    user.save()
                    messages.info(request, "Account created Successfully!")
                    return redirect('home')
                else:
                    messages.error(request, "email alredy used")
            else:
                messages.error(request, "username alredy used")
        else:
            messages.error(request, "password are not matched")
    return render(request, 'register.html')
    
def log_in(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        if User.objects.filter(username=username).exists():
            user = authenticate(username=username, password=password)
            messages.info(request, "Account login Successfully!")
            login(request ,user)
            return redirect('profile')
        else:
            messages.error(request, "Invalid username or password")
            return redirect('login')
        
    return render(request, 'login.html')

def my_profile(request):
    if request.method == "POST":
        username = request.POST["username"]
        bio = request.POST["bio"]
        user = User.objects.get(username)
        userprofile = profile(user=user)
        userprofile.bio = bio
        userprofile.save()
    return render(request, 'profile.html')
