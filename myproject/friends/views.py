from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages 
from .models import Profile, friend_request
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import Serializer_User
import json

user = User.objects.all()
profile = Profile.objects.all()
request_friend = friend_request.objects.all()
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

# class Search(APIView):
#     def post(self, request):
#         _username = request.data.get("user")
#         if (user.filter(username=_username).exists()):
#             theuser = user.get(username=_username)
#             serializer = Serializer_User(theuser)
#             return Response(serializer.data)
#         return Response(None)
def Unblock_user(P_user : Profile ,s_user : User ,s_user_id : int):
    if P_user.block.filter(id=s_user_id):
        P_user.block.remove(s_user)

def Accept_method(sender : friend_request):
    sender.status = True
    sender.save()

def Reject_method(P_user : Profile, s_user_id : int, s_user : User):
    if P_user.waiting.filter(id=s_user_id).exists():
                P_user.waiting.remove(s_user)

def Block_user(user : User, P_user : Profile, s_user_id : int,  s_user : User):
    if P_user.friends.filter(id=s_user_id).exists():
       P_user.friends.remove(user)
    elif P_user.waiting.filter(id=s_user_id).exists():
        P_user.waiting.remove(s_user)
    P_user.block.add(s_user)

def  ADD_method(_user, _reciver):
    if user.filter(username=_reciver).exists():
        friend_reciver : User = user.get(username=_reciver)
        user_P : Profile = profile.get(user=_user)
        resiver_user_P : Profile = profile.get(user=friend_reciver)
        if not user_P.block.filter(id=friend_reciver.id).exists():
            if not resiver_user_P.block.filter(id=_user.id).exists():
                if not user_P.friends.filter(id=friend_reciver.id).exists():
                    if not user_P.waiting.filter(id=friend_reciver.id).exists():
                        if not resiver_user_P.waiting.filter(id=_user.id).exists():
                            friend = friend_request.objects.create(sender=_user, reciver=friend_reciver)
                            friend.save()
                        else:
                            return Response({"message" : " You have allredy sent request wait for response. "})
                    else:
                        return Response({"message" : " This User Alrady Invite You And Waiting Your Confirm. "})
                else:
                    return Response({"message" : " Already Have This User As Friend. "})
            else:
                return Response({"message" : " You Get Blocked From This User. "})
        else:
            return Response({"message" : " You Can't add This User. "})
    else:
        return Response({"message" : " Invalid username. "})
    return Response({"message" : " request send . "})
    
class Request_methods(APIView):
    def post(self, request):
        status = request.data.get("status")
        _user : User =  request.user
        _reciver : str = request.data.get('user')
        P_user : Profile = profile.get(user=_user)
        if status == "ADD":
            return ADD_method(_user, _reciver)
        elif status == "REJECT" or status == "BLOCK" or status == "ACCEPT" or status == "UNBLOCK":
            s_user_id : str = request.data.get('user_id')
            s_user : User = user.get(id=s_user_id)
            sender : friend_request = request_friend.get(sender=s_user, reciver=_user)
            if status == "REJECT":
                return Reject_method(P_user, s_user_id, s_user)
            elif status == "ACCEPT":
                return Accept_method(sender)
            elif status == "BLOCK":
                return Block_user(user, P_user, s_user_id, s_user)
            elif status == "UNBLOCK":
                return Unblock_user(P_user, s_user, s_user_id)
            sender.delete()
        P_user.save()
        return Response(None)
    
@login_required
def statusfriend_request(request):
    _user = request.user
    P_user : Profile = Profile.objects.get(user=_user)
    list_user : Profile = P_user.waiting.all()
    if request.method == "POST":
        s_user_id : str = request.POST.get('user_id')
        s_user : User = user.get(id=s_user_id)
        sender : friend_request = friend_request.objects.get(sender=s_user, reciver=_user)
        if request.POST.get('case') == 'accept': # if user accept friend request ?
            sender.status = True
            sender.save()
        elif request.POST.get('case') == 'reject': # if user reject friend request ?
            if P_user.waiting.filter(id=s_user_id).exists():
                P_user.waiting.remove(s_user)
        else: # if user block friend request ?
            Block_user(user, P_user, s_user_id, s_user)
        sender.delete()
        P_user.save()
    return render(request, 'waiting_list.html', {'waiting_user' : list_user})

