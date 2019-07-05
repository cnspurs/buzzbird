from rest_framework import serializers

from core.models import Feed


class FeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feed
        exclude = ('metadata', 'is_buzzbird', 'is_discourse', 'author',)
        depth = 2
