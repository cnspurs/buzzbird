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


class QueryUserSerializer(serializers.Serializer):
    type = serializers.CharField(required=True)
    username = serializers.CharField(required=True)

    def validate_type(self, value):
        types = [
            'instagram',
            'twitter',
            'weibo',
        ]
        if value not in types:
            raise serializers.ValidationError('Invalid type')
        return value
