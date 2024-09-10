from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_user, name='register'),
    path('login/', views.log_in, name='login'),
    path('profile/', views.my_profile, name='profile')
]
