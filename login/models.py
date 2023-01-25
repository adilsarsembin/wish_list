from django.db import models
from django.contrib.auth import get_user_model
from django.contrib import admin

# Create your models here.

class Movie(models.Model):
    user = models.ManyToManyField(
        get_user_model(),
        related_name='movie_user'
    )
    title = models.CharField(max_length=100)
    release_date = models.CharField(max_length=15)
    rating = models.FloatField()
    is_watched = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title

