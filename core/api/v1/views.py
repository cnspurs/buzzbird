from rest_framework import generics

from rest_framework.decorators import api_view
from rest_framework.response import Response

from core.models import Feed
from core.serializer import FeedSerializer


@api_view()
def ping(request):
    return Response({
        'message': 'pong!'
    })


class BBListModelMixin:
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'length': len(serializer.data),
            'data': serializer.data,
        })


class BBDetailModelMixin(object):
    """
    Retrieve a model instance.
    """

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'data': serializer.data,
        })


class BBListAPIView(BBListModelMixin, generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class BBDetailAPIView(BBDetailModelMixin, generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class FeedList(BBListAPIView):
    queryset = Feed.objects.all().order_by('-created_at')[:100]
    serializer_class = FeedSerializer


class FeedDetail(BBDetailAPIView):
    queryset = Feed.objects.all()
    serializer_class = FeedSerializer
