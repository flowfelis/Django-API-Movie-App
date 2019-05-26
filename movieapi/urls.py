from django.urls import path

from . import views

app_name = 'movieapi'
urlpatterns = [

    # Movies
    path('movies', views.movies, name='movies'),

    # Comments
    path('comments', views.comments, name='comments'),

    # top
    path('top', views.top, name='top'),
]
