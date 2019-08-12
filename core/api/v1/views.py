import instaloader

from rest_framework import generics
from rest_framework import status

from rest_framework.decorators import api_view
from rest_framework.response import Response

from core import utils
from core import weibo
from core.instagram_v2 import ins
from core.models import Feed
from core.serializer import FeedSerializer, QueryUserSerializer


@api_view()
def ping(request):
    return Response({'message': 'pong!'})


class BBListModelMixin:
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({'length': len(serializer.data), 'data': serializer.data})


class BBDetailModelMixin(object):
    """
    Retrieve a model instance.
    """

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({'data': serializer.data})


class BBListAPIView(BBListModelMixin, generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class BBDetailAPIView(BBDetailModelMixin, generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class FeedList(BBListAPIView):
    queryset = (
        Feed.objects.all()
        .select_related('user')
        .prefetch_related('media')
        .order_by('-created_at')[:100]
    )
    serializer_class = FeedSerializer


class FeedDetail(BBDetailAPIView):
    queryset = Feed.objects.all().select_related('user').prefetch_related('media')
    serializer_class = FeedSerializer


@api_view()
def query_user_id(request):
    serializer = QueryUserSerializer(data=request.query_params)
    if not serializer.is_valid():
        return Response({'errors': serializer.errors}, status=status.HTTP_404_NOT_FOUND)

    type = serializer.data['type']
    username = serializer.data['username']

    if type == 'instagram':
        try:
            profile = instaloader.Profile.from_username(ins.context, username)
            user_id = str(profile.userid)
            return Response({'type': type, 'user_id': user_id})
        except Exception as e:
            return Response({'errors': str(e)}, status=status.HTTP_404_NOT_FOUND)

    if type == 'twitter':
        try:
            user_id = utils.twitter.get_userid(username)
            return Response({'type': type, 'user_id': user_id})
        except Exception as e:
            return Response({'errors': str(e)}, status=status.HTTP_404_NOT_FOUND)

    if type == 'weibo':
        try:
            user_id = weibo.get_userid(username)
            return Response({'type': type, 'user_id': user_id})
        except Exception as e:
            return Response({'errors': str(e)}, status=status.HTTP_404_NOT_FOUND)
