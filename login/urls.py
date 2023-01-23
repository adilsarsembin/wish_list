from django.urls import path, include
from django.views.decorators.cache import cache_page

from . import views

urlpatterns = [
    path('', views.user_login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
    path('home/', views.home, name='home'),
    path('search/<str:name>', cache_page(120)(views.search), name='search'),
    path('movie/<str:pk>', views.movie_delete, name='movie_delete'),
    path('movie_add/', views.movie_add, name='movie_add'),
]
