from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages 
from .models import Profile, friend_request

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
                    login(request ,user)
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
            return redirect('friend')
        else:
            messages.error(request, "Invalid username or password")
            return redirect('add_friend')
    return render(request, 'login.html')

@login_required
def creatprofile(request):
    if request.method == "POST":
        if not Profile.objects.filter(user=request.user).exists():
            image : str = request.FILES.get("profileImage")
            bio : str = request.POST.get("bio")
            Profile.objects.create(user=request.user, image=image, bio=bio)
            return redirect('login')
    return render(request, 'profile.html')


@login_required
def add_friend(request):
    if request.method == "POST":
        _reciver : str = request.POST.get('add')
        _user : User =  request.user
        if User.objects.filter(username=_reciver).exists():
            friend_reciver : User = User.objects.get(username=_reciver)
            user_P : Profile = Profile.objects.get(user=_user)
            resiver_user_P : Profile = Profile.objects.get(user=friend_reciver)
            if not user_P.block.filter(id=friend_reciver.id).exists():
                if not resiver_user_P.block.filter(id=_user.id).exists():
                    if not user_P.friends.filter(id=friend_reciver.id).exists():
                        if not user_P.waiting.filter(id=friend_reciver.id).exists():
                            if not resiver_user_P.waiting.filter(id=_user.id).exists():
                                friend = friend_request.objects.create(sender=_user, reciver=friend_reciver)
                                friend.save()
                            else:
                                messages.info(request, " You have sent request wait for response. ")
                        else:
                            messages.info(request, " This User Alrady Invite You And Waiting Your Confirm. ")
                    else:
                        messages.info(request, "Already Have This User As Friend. ")
                else:
                    messages.info(request, " You Get Blocked From This User. ")
            else:
                messages.info(request, " You Can't add This User. ")
        else:
            messages.error(request, " Invalid username. ")
    return render(request, 'friends.html')

@login_required
def statusfriend_request(request):
    user = request.user
    P_user : Profile = Profile.objects.get(user=user)
    list_user : Profile = P_user.waiting.all()
    if request.method == "POST":
        s_user_id : str = request.POST.get('user_id')
        s_user : User = User.objects.get(id=s_user_id)
        sender : friend_request = friend_request.objects.get(sender=s_user, reciver=user)
        if request.POST.get('case') == 'accept': # if user accept friend request ?
            sender.status = True
            sender.save()
        elif request.POST.get('case') == 'reject': # if user reject friend request ?
            if P_user.waiting.filter(id=s_user_id).exists():
                P_user.waiting.remove(s_user)
        else: # if user block friend request ?
            block_user(user, P_user, s_user_id, s_user)
        sender.delete()
        P_user.save()
    return render(request, 'waiting_list.html', {'waiting_user' : list_user})

def block_user(user : User, P_user : Profile, s_user_id : int,  s_user : User):
    if P_user.friends.filter(id=s_user_id).exists():
       P_user.friends.remove(user)
    elif P_user.waiting.filter(id=s_user_id).exists():
        P_user.waiting.remove(s_user)
    P_user.block.add(s_user)

def unblock_user(P_user : Profile ,s_user : User ,s_user_id : int):
    if P_user.block.filter(id=s_user_id):
        P_user.block.remove(s_user)
    P_user.save()