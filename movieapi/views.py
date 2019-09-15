from datetime import datetime

from django.db.models import Count, Window, F
from django.db.models.functions import DenseRank
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Movie, Comment
from .serializers import MovieSerializer, CommentSerializer, TopSerializer
from django.conf import settings

import requests


class MoviesView(APIView):
    def post(self, request, format=None):

        # Get User Input
        movie_title = request.data.get('movie_title')

        # Validate User Input
        if not movie_title:
            response = {
                'error': 'Please provide a movie title'
            }
            return Response(response, status.HTTP_400_BAD_REQUEST)

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
            return Response(response, status.HTTP_400_BAD_REQUEST)

        # Validate duplicate movie doesn't exist in DB
        if r.get('imdbID') in [str(q) for q in Movie.get_all()]:
            response = {
                'error': '{movie_title} already exists in DB'.format(movie_title=movie_title)
            }
            return Response(response, status.HTTP_400_BAD_REQUEST)

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

        serializer = MovieSerializer(movie)
        return Response(serializer.data)

    def get(self, request, format=None):

        order_by = request.GET.get('order_by')
        desc = request.GET.get('desc')

        # change to 'imdbrating' if 'rating' is provided
        order_by = 'imdbrating' if order_by == 'rating' else order_by

        # Send movies without ordering if order_by not provided
        if not order_by:
            # return all_json_response(Movie)
            serializer = MovieSerializer(Movie.get_all(), many=True)
            return Response(serializer.data)
        else:
            # if code is here, it means order_by is provided

            # order_by accepts'title' and 'rating' only
            if order_by != 'imdbrating' and order_by != 'title':
                order_by = 'id'  # default to order_by id

            if desc == 'true':
                order_by = '-' + order_by

            qs = Movie.get_all().order_by(order_by)

            serializer = MovieSerializer(qs, many=True)
            return Response(serializer.data)


class CommentsView(APIView):
    def post(self, request, format=None):

        # Get user input
        movie_id = request.data.get('movie_id')
        comment = request.data.get('comment')

        # Validate User Input
        if not movie_id or not comment:
            response = {
                'error': 'Please provide movie ID and comment'
            }
            return Response(response, status.HTTP_400_BAD_REQUEST)

        # Validate movie exists
        qs = Movie.get_all()
        if movie_id not in [str(q) for q in qs]:
            response = {
                'error': 'Movie with movie id {movie_id}, doesn\'t exist in DB. Make sure to enter imdb id'.format
                (movie_id=movie_id)
            }
            return Response(response, status.HTTP_400_BAD_REQUEST)

        # Save comment to DB
        movie = Movie.objects.get(imdbid=movie_id)
        new_comment = Comment(comment=comment, movie=movie)
        new_comment.save()

        # Return newly saved comment
        serializer = CommentSerializer(new_comment)
        return Response(serializer.data)

    def get(self, request, format=None):
        movie_id = request.GET.get('movie_id')

        # Filter by movie ID, if user provided
        if movie_id:
            qs = Comment.objects.filter(movie__imdbid=movie_id)
            serializer = CommentSerializer(qs, many=True)
            return Response(serializer.data)

        # No filter provided by user, so return all
        serializer = CommentSerializer(Comment.get_all(), many=True)
        return Response(serializer.data)


class TopView(APIView):
    def create_qs_for_top(self, with_filter=False, start_date='', end_date=''):
        """
        Creates query string according to date filter, if provided by the user.
        :param with_filter: boolean, to create with filter or not.
        :param start_date: string, start date of the filter.
        :param end_date: string, end date of the filter
        :return: Query String for Top, according to date filter.
        """
        qs = Movie.objects
        if with_filter:
            qs = qs.filter(comment__added_on__range=(start_date, end_date))

        return qs.annotate(total_comments=Count('comment__comment'),
                           rank=Window(
                               expression=DenseRank(),
                               order_by=F('total_comments').desc(),
                           )
                           ).values('id', 'total_comments', 'rank')

    def get(self, request, format=None):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        qs = self.create_qs_for_top()

        # Filter by specified date range, if provided
        if start_date and end_date:
            qs = self.create_qs_for_top(with_filter=True, start_date=start_date, end_date=end_date)

        serializer = TopSerializer(qs, many=True)
        return Response(serializer.data)
