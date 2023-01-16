from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages

import requests
import environ

from .forms import CreateUserForm
from .models import Movie

# Create your views here.

env = environ.Env()
environ.Env.read_env()


def user_login(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None: 
            login(request, user)
            messages.success(request, 'User was authenticated successfully!')
            return redirect('home')  
        else:
            messages.error(request, 'Your username or password must be incorrect! Try again!')

    return render(request, 'login/login.html')


def signup(request):
    form = CreateUserForm()

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User was created successfully! Redirecting you to a login page!')
            return redirect('login')
        else:
            messages.error(request, form.errors)

    context = {'form': form}
    return render(request, 'login/signup.html', context)


def user_logout(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def home(request):
    if request.method == 'POST':
        film = request.POST.get('film_name')

        return redirect('search', name=film)

    return render(request, 'login/home.html')


@login_required(login_url='login')
def search(request, name):

    if request.method == 'POST':
        title = request.POST.get('title')
        rating = request.POST.get('rating')
        release_date = request.POST.get('date')

        auth_user = get_user_model()
        cur_user = auth_user.objects.get(username=request.user.username)

        if not Movie.objects.filter(title=title, release_date=release_date):
            my_movie = Movie(
                title=title, release_date=release_date, rating=float(rating))
            my_movie.save()
            my_movie.user.add(cur_user)
            my_movie.save()
        else:
            my_movie = Movie.objects.get(
                title=title, release_date=release_date)
            my_movie.user.add(cur_user)

    film_url = '+'.join(name.split(' '))
    results = get_data(film_url)

    context = {"name": name, "results": results}
    return render(request, 'login/search.html', context)


def get_data(film_url):
    api_key = env('API_KEY')
    url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={film_url}'
    results = requests.get(url).json()['results']
    return results
