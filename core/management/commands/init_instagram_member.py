from django.core.management.base import BaseCommand

from core import instagram


class Command(BaseCommand):

    def handle(self, *args, **options):
        count = 0

        feeds = instagram.get_feeds_list()
        for feed in feeds:
            content = instagram.get_feed_content(feed)
            instagram.create_user(content)
            count += 1

        self.stdout.write(f'Initialized. {count} members added.')
