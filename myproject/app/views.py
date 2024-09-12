from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Profile

def home(request):
    return render(request, 'home.html')


def register_user(request):
    if request.method == "POST":
        username : str = request.POST["username"]
        email : str = request.POST["email"]
        password : str = request.POST["password"]
        confirm_password : str = request.POST["confirm_password"]
        if password == confirm_password:
            if not User.objects.filter(username=username).exists():
                if not User.objects.filter(email=email).exists():
                    user = User.objects.create_user(username=username, email=email, password=password)
                    user.save()
                    messages.info(request, "Account created Successfully!")
                    return redirect('profile')
                else:
                    messages.error(request, "email alredy used")
            else:
                messages.error(request, "username alredy used")
        else:
            messages.error(request, "password are not matched")
    return render(request, 'register.html')


def log_in(request):
    if request.method == "POST":
        username : str = request.POST.get("username")
        password : str = request.POST.get("password")
        user : User = authenticate(username=username, password=password)
        if user is not None:
            messages.info(request, "Account login Successfully!")
            login(request ,user)
        else:
            messages.error(request, "Invalid username or password")
            return redirect('login')
        
    return render(request, 'login.html')

@login_required
def my_profile(request):
    if request.method == "POST":
        image : str = request.FILES.get("profileImage")
        bio : str = request.POST.get("bio")
        Profile.objects.create(user=request.user, bio=bio ,image=image)
    return render(request, 'profile.html')

def user_home(request):
    pass
