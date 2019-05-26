import json

from django.core.serializers.json import DjangoJSONEncoder
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

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

    class CommentTests(TestCase):
        fixtures = ['test_data.json']

    def test_post_comment_user_data_validation(self):
        """
        POST /comments user data validation
        :return: error message
        """

        # omit both input
        r1 = self.client.post(reverse('movieapi:comments'))
        self.assertJSONEqual(
            r1.content,
            '{"error": "Please provide movie ID and comment"}'
        )

        # omit only comment
        r2 = self.client.post(reverse('movieapi:comments'), {'movie_id': 'tt0112573'})
        self.assertJSONEqual(
            r2.content,
            '{"error": "Please provide movie ID and comment"}'
        )

        r3 = self.client.post(reverse('movieapi:comments'), {'comment': 'test comment'})
        self.assertJSONEqual(
            r3.content,
            '{"error": "Please provide movie ID and comment"}'
        )

    def test_post_comment_movie_not_exist(self):
        """
        POST /comments movie doesn't exist for the comment
        :return: error message
        """

        r = self.client.post(reverse('movieapi:comments'), {'movie_id': 'testid', 'comment': 'test_comment'})
        self.assertJSONEqual(
            r.content,
            '{"error": "Movie with movie id testid, doesn\'t exist in DB. Make sure to enter imdb id"}'
        )

    def test_post_comment_successful(self):
        """
        POST /comment successful post
        :return:  success message
        """

        r = self.client.post(reverse('movieapi:comments'), {'movie_id': 'tt0112573', 'comment': 'test comment'})
        self.assertJSONEqual(
            r.content,
            ('\n'
             '            {\n'
             '                "id": 18,\n'
             '                "comment": "test comment",\n'
             '                "movie": 3,\n'
             '                "added_on": "' + str(timezone.localdate()) + '"\n'
             )
        )

    # get comments
