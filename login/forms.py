from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

from .models import Movie


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password1', 'password2', ]

class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ['title', ]
