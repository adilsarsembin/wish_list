from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.urls import reverse

import requests
import environ

from .forms import CreateUserForm
from .models import Movie

# Create your views here.

env = environ.Env()
environ.Env.read_env()


def user_login(request):

    if request.user.is_authenticated:
        return redirect(reverse('home'))

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'User was authenticated successfully!')
            return redirect(reverse('home'))
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
            return redirect(reverse('login'))
        else:
            messages.error(request, form.errors)

    context = {'form': form}
    return render(request, 'login/signup.html', context)

@login_required(login_url='login')
def user_logout(request):
    logout(request)
    return redirect(reverse('login'))


@login_required(login_url='login')
def home(request):
    if request.method == 'POST':
        film = request.POST.get('film_name')

        return redirect('search', name=film)

    auth_user = get_user_model()
    cur_user = auth_user.objects.get(username=request.user.username)

    movie_list = Movie.objects.filter(user=cur_user, is_watched=False)
    context = {"movie_list": movie_list}

    return render(request, 'login/home.html', context)


@login_required(login_url='login')
def search(request, name):
    if request.method == 'POST':
        film = request.POST.get('film_name')

        return redirect('search', name=film)

    film_url = '+'.join(name.split(' '))
    results = get_data(film_url)

    paginator = Paginator(results, 10)
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
def movie(request, pk):
    auth_user = get_user_model()
    cur_user = auth_user.objects.get(username=request.user.username)

    if request.method == "POST" and 'delete' in request.POST:

        my_movie = Movie.objects.get(user=cur_user, id=pk)
        my_movie.delete()
        messages.success(request, 'Deleting has been done successfully!')

    if request.method == "POST" and 'update' in request.POST:
        my_movie = Movie.objects.get(user=cur_user, id=pk)
        my_movie.is_watched = True
        my_movie.save()

        messages.success(request, 'Film was added to watched successfully!')

    if request.method == 'POST' and 'add' in request.POST:
        title = request.POST.get('title')
        rating = request.POST.get('rating')
        release_date = request.POST.get('date')

        auth_user = get_user_model()
        cur_user = auth_user.objects.get(username=request.user.username)

        if not Movie.objects.filter(user=cur_user, title=title, release_date=release_date):
            my_movie = Movie(
                title=title, release_date=release_date, rating=float(rating))
            my_movie.save()
            my_movie.user.add(cur_user)
            my_movie.save()
            messages.success(request, 'Adding has been done successfully!')
        else:
            my_movie = Movie.objects.get(
                title=title, release_date=release_date)
            my_movie.user.add(cur_user)
            messages.info(request, 'Film is already in wish list or watched ones!')
        


    return redirect(reverse('home'))


@login_required(login_url='login')
def watched_movies(request):
    if request.method == 'POST':
        film = request.POST.get('film_name')

        return redirect('search', name=film)
    my_movies = Movie.objects.filter(is_watched=True)
    context = {'my_movies': my_movies}

    return render(request, 'login/watched_movies.html', context=context)
