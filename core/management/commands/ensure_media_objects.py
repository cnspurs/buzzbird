from django.core.management.base import BaseCommand
from django_q.tasks import async_task

from core.models import *


class Command(BaseCommand):
    """
    covert single image to multi images
    """

    def handle(self, *args, **options):
        feeds = Feed.objects.all().exclude(type='twitter').prefetch_related('media')
        for feed in feeds:
            media = Media.objects.filter(feed=feed)
            if media:
                for m in media:
                    if m.downloaded is False:
                        async_task(m.download_to_local)
