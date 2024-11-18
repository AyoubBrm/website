from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_user, name='register'),
    path('login/', views.log_in, name='login'),
    path('profile/', views.creatprofile, name='profile'),
    path('methods/', views.Request_methods.as_view(), name='methods'),
    # path('waiting/', views.statusfriend_request, name='wait'),
    path('search/', views.Search.as_view(), name='hi'),
]
