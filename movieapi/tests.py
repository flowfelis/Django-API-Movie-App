import json

from django.core.serializers.json import DjangoJSONEncoder
from django.test import TestCase
from django.urls import reverse

from movieapi.models import Movie


class MoviesTests(TestCase):
    fixtures = ['test_data.json']

    def test_post_movie(self):
        """
        POST /movies successfully posts a movie with a title
        :return: json response
        """
        r = self.client.post(reverse('movieapi:movies'), {'movie_title': 'fight club'})
        self.assertJSONEqual(
            r.content,
            '{"success": "fight club successfully added to DB"}'
        )

    def test_post_movie_without_data(self):
        """
        POST /movies without data, returns error
        :return: {"error": "Please provide a movie title"}
        """

        r = self.client.post(reverse('movieapi:movies'))
        self.assertJSONEqual(
            r.content,
            '{"error": "Please provide a movie title"}'
        )

    def test_post_movie_not_exist_in_api(self):
        """
        POST /movies with some garbage movie title name
        :return: "error": "There is no movie like fight clubqwerasdfasrwer"
        """

        r = self.client.post(reverse('movieapi:movies'), {'movie_title': 'fight clubqwerasdfasrwer'})
        self.assertJSONEqual(
            r.content,
            '{"error": "There is no movie like fight clubqwerasdfasrwer"}'
        )

    def test_post_movie_exist_in_api(self):
        """
        POST /movies already exists in database
        :return: "error": "braveheart already exists in DB"
        """

        r = self.client.post(reverse('movieapi:movies'), {'movie_title': 'braveheart'})
        self.assertJSONEqual(
            r.content,
            '{"error": "braveheart already exists in DB"}'
        )

    def test_get_movies(self):
        """
        GET /movies gets all movies
        :return: all movies in json
        """

        all_values = Movie.objects.values()
        all_json = json.dumps(list(all_values), cls=DjangoJSONEncoder)

        r = self.client.get(reverse('movieapi:movies'))
        self.assertJSONEqual(
            r.content,
            all_json
        )
