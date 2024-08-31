from django.shortcuts import render, redirect

from django.http import HttpRequest

from .forms import register

def home(request):
    return render(request, 'home.html')

def register_user(request):
    if request.method == "POST":
        form = register(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = register()
    return render(request, 'register.html', {'form': form})

def login(request):
    return render(request, 'login.html')