# Generated by Django 4.1.4 on 2023-01-25 05:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0002_remove_movie_genres'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='is_watched',
            field=models.BooleanField(default=False),
        ),
    ]
