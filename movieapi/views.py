from datetime import datetime

from django.http import HttpResponse
from django.http import JsonResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt

from .models import Movie, Comment

import requests


@csrf_exempt
def movies(request):
    # POST /movies
    if request.method == 'POST':

        # Get User Input
        movie_title = request.POST.get('movie_title')

        # Validate User Input
        if not movie_title:
            response = {
                'error': 'Please provide a movie title'
            }
            return JsonResponse(response)

        # Fetch movie from API
        payload = {
            'apikey': 'dda316e4',
            't': movie_title
        }
        url = 'http://www.omdbapi.com'

        r = requests.get(url, params=payload)
        r = r.json()

        # Validate movie exists in API
        if r.get('Response') == 'False':
            response = {
                'error': 'There is no movie like {movie_title}'.format(movie_title=movie_title)
            }
            return JsonResponse(response)

        # Validate duplicate movie doesn't exist in DB
        qs = Movie.objects.all()
        if r.get('imdbID') in [str(q) for q in qs]:
            response = {
                'error': '{movie_title} already exists in DB'.format(movie_title=movie_title)
            }
            return JsonResponse(response)

        # Save Fetched movie from API to DB
        movie = Movie()
        for key, value in r.items():

            # not saving Year Ratings and Response due to being duplicate
            if key == 'Year' or key == 'Ratings' or key == 'Response':
                continue

            # For Date fields, Convert to date type
            elif key == 'Released' or key == 'DVD':
                value = datetime.strptime(value, '%d %b %Y').date() if value != 'N/A' else None

            # For Int and Decimal types, convert and Remove '$' and ','
            elif key == 'imdbVotes' or key == 'BoxOffice' or key == 'Metascore':
                if ',' in value:
                    value = value.replace(',', '')
                if '$' in value:
                    value = value.replace('$', '')
                value = int(value) if value != 'N/A' else 0
            elif key == 'imdbRating':
                value = float(value) if value != 'N/A' else 0

            # lowercase, because my fields are lowercase
            key = key.lower()

            setattr(movie, key, value)
        movie.save()

        # Return success msg
        response = {
            'success': '{movie_title} successfully added to DB'.format(movie_title=movie_title)
        }
        return JsonResponse(response)

    # GET /movies
    else:

        # Get all movies
        qs = Movie.objects.all()

        # serialize to JSON
        qs_json = serializers.serialize('json', qs)

        return HttpResponse(qs_json, content_type='application/json')


@csrf_exempt
def comments(request):
    # POST /comments
    if request.method == 'POST':

        # Get user input
        movie_id = request.POST.get('movie_id')
        comment = request.POST.get('comment')

        # Validate User Input
        if not movie_id or not comment:
            response = {
                'error': 'Please provide movie ID and comment'
            }
            return JsonResponse(response)

        # Validate movie exists
        qs = Movie.objects.all()
        if movie_id not in [str(q) for q in qs]:
            response = {
                'error': 'Movie with movie id {movie_id}, doesn\'t exist in DB'.format(movie_id=movie_id)
            }
            return JsonResponse(response)

        # Save comment to DB
        movie = Movie.objects.get(imdbid=movie_id)
        new_comment = Comment(comment=comment, movie=movie)
        new_comment.save()

        # Return newly saved comment
        new_comment_json = serializers.serialize('json', [new_comment])[1:-1]
        return HttpResponse(new_comment_json, content_type='application/json')

    # GET /comments
    else:

        # Filter by movie ID, if user provided
        movie_id = request.GET.get('movie_id')
        if movie_id:
            qs = Comment.objects.filter(movie__imdbid=movie_id)
            qs_json = serializers.serialize('json', qs)
            return HttpResponse(qs_json, content_type='application/json')

        # return all comments
        all_comments = Comment.objects.all()
        all_comments_json = serializers.serialize('json', all_comments)
        return HttpResponse(all_comments_json, content_type='application/json')
