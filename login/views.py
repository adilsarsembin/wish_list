from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.paginator import Paginator

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
            messages.error(
                request, 'Your username or password must be incorrect! Try again!')

    return render(request, 'login/login.html')


def signup(request):
    form = CreateUserForm()

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'User was created successfully! Redirecting you to a login page!')
            return redirect('login')
        else:
            messages.error(request, form.errors)

    context = {'form': form}
    return render(request, 'login/signup.html', context)

@login_required(login_url='login')
def user_logout(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def home(request):
    if request.method == 'POST':
        film = request.POST.get('film_name')

        return redirect('search', name=film)

    auth_user = get_user_model()
    cur_user = auth_user.objects.get(username=request.user.username)

    movie_list = Movie.objects.filter(user=cur_user)
    context = {"movie_list": movie_list}

    return render(request, 'login/home.html', context)


@login_required(login_url='login')
def search(request, name):
    if request.method == 'POST':
        film = request.POST.get('film_name')

        return redirect('search', name=film)

    film_url = '+'.join(name.split(' '))
    results = get_data(film_url)

    paginator = Paginator(results, 20)
    pag_len = paginator.num_pages
    page = request.GET.get('page')
    pag_obj = paginator.get_page(page)

    context = {"name": name, "pag_obj": pag_obj, "pag_len": pag_len}
    return render(request, 'login/search.html', context)


def get_data(film_url):
    api_key = env('API_KEY')
    results = []
    url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={film_url}'
    page_nums = requests.get(url).json()['total_pages']
    if page_nums >= 5:
        page_nums = 5
    for i in range(1, page_nums+1):
        new_url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={film_url}&page={i}'
        result = requests.get(new_url).json()['results']
        for res in result:
            results.append(res)
    return results


@login_required(login_url='login')
def movie_delete(request, pk):
    if request.method == "POST":
        auth_user = get_user_model()
        cur_user = auth_user.objects.get(username=request.user.username)

        my_movie = Movie.objects.get(user=cur_user, id=pk)
        my_movie.delete()
        messages.success(request, 'Deleting has been done successfully!')

    return redirect('home')


@login_required(login_url='login')
def movie_add(request):
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
        messages.success(request, 'Adding has been done successfully!')

    return redirect('home')
