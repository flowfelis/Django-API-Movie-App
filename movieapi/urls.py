from django.urls import path

from . import views

app_name = 'movieapi'
urlpatterns = [

    # Movies
    path('movies', views.MoviesView.as_view(), name='movies'),

    # Comments
    path('comments', views.CommentsView.as_view(), name='comments'),

    # top
    path('top', views.top, name='top'),
]
