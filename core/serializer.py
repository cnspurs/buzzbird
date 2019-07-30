from rest_framework import serializers

from core.models import Feed, Media, Member


class MemberSerializer(serializers.ModelSerializer):
    avatar_url = serializers.URLField()

    class Meta:
        model = Member
        exclude = ('avatar',)


class MediaSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    url = serializers.URLField()

    class Meta:
        model = Media
        fields = ('id', 'url')


class FeedSerializer(serializers.ModelSerializer):
    media = MediaSerializer(source='downloaded_media', many=True)
    user = MemberSerializer()
    type = serializers.CharField(source='readable_type')

    class Meta:
        model = Feed
        exclude = ('metadata', 'is_buzzbird', 'is_discourse', 'author')
