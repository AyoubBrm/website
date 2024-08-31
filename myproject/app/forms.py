from django import forms
from django.contrib.auth.forms import User


class register(forms.ModelForm):
   class Meta:
      model = User
      fields = ('username', 'email', 'password')
      widgets = {
            'password': forms.PasswordInput(),
        }