from datetime import datetime

from django.db.models import Count, Window, F, Q
from django.db.models.functions import DenseRank
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict

from .models import Movie, Comment
from .helpers import all_json_response, qs_json_response
from .serializers import MovieSerializer
from django.conf import settings
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
            'apikey': settings.OMDB_API_KEY,
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

        return JsonResponse(model_to_dict(movie))

    # GET /movies
    elif request.method == 'GET':

        order_by = request.GET.get('order_by')
        desc = request.GET.get('desc')

        # change to 'imdbrating' if 'rating' is provided
        order_by = 'imdbrating' if order_by == 'rating' else order_by

        # Send movies without ordering if order_by not provided
        if not order_by:
            return all_json_response(Movie)
        else:
            # if code is here, it means order_by is provided

            # order_by accepts'title' and 'rating' only
            if order_by != 'imdbrating' and order_by != 'title':
                order_by = 'id'  # default to order_by id

            if desc == 'true':
                order_by = '-' + order_by

            qs = Movie.objects.all().order_by(order_by).values()

            serializer = MovieSerializer(qs, many=True)
            return JsonResponse(serializer.data, safe=False)
            # return qs_json_response(qs)


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
                'error': 'Movie with movie id {movie_id}, doesn\'t exist in DB. Make sure to enter imdb id'.format
                (movie_id=movie_id)
            }
            return JsonResponse(response)

        # Save comment to DB
        movie = Movie.objects.get(imdbid=movie_id)
        new_comment = Comment(comment=comment, movie=movie)
        new_comment.save()

        # Return newly saved comment
        return JsonResponse(model_to_dict(new_comment))

    # GET /comments
    elif request.method == 'GET':

        movie_id = request.GET.get('movie_id')

        # Filter by movie ID, if user provided
        if movie_id:
            qs = Comment.objects.filter(movie__imdbid=movie_id).values()
            return qs_json_response(qs)

        # No filter provided by user, so return all
        return all_json_response(Comment)


def top(request):
    if request.method == 'GET':
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        # Filter by specified date range, if provided
        if start_date and end_date:
            qs = Movie.objects \
                .filter(comment__added_on__range=(start_date, end_date)) \
                .annotate(total_comments=Count('comment__comment'),
                          rank=Window(
                              expression=DenseRank(),
                              order_by=F('total_comments').desc(),
                          )
                          ).values('id', 'total_comments', 'rank')

            return qs_json_response(qs)

        else:
            qs = Movie.objects \
                .annotate(total_comments=Count('comment__comment'),
                          rank=Window(
                              expression=DenseRank(),
                              order_by=F('total_comments').desc(),
                          )
                          ).values('id', 'total_comments', 'rank')

            return qs_json_response(qs)
