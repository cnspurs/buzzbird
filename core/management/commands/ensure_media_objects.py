from django.core.management.base import BaseCommand
from django_q.tasks import async_task

from core.models import *


class Command(BaseCommand):
    """
    covert single image to multi images
    """

    def handle(self, *args, **options):
        feeds = Feed.objects.all().exclude(type='twitter', media_url=None).prefetch_related('media')
        for feed in feeds:
            media = Media.objects.filter(feed=feed, original_url=feed.media_url)
            if media:
                for m in media:
                    if m.downloaded is False:
                        async_task(m.download_to_local)

            if not media and feed.media_url:
                media = Media.objects.create(
                    feed=feed,
                    original_url=feed.media_url,
                )
                async_task(media.download_to_local)
