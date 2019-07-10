from rest_framework import serializers

from core.models import Feed, Media


class MediaSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    url = serializers.URLField()

    class Meta:
        model = Media
        fields = ('id', 'url')


class FeedSerializer(serializers.ModelSerializer):
    media = MediaSerializer(source='downloaded_media', many=True)

    class Meta:
        model = Feed
        exclude = ('metadata', 'is_buzzbird', 'is_discourse', 'author',)
        depth = 2
