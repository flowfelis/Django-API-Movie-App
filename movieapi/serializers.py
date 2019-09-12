from rest_framework import serializers

from movieapi.models import Movie


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
