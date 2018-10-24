from django.core.management.base import BaseCommand
from core.models import TwitterMember
from core.utils import twitter


class Command(BaseCommand):

    def handle(self, *args, **options):
        if TwitterMember.objects.count() != 0:
            return

        members = twitter.get_list_members()

        count = 0
        for user in members:
            TwitterMember.objects.create(twitter_id=user.id_str,
                                         english_name=user.name)

            count += 1
        self.stdout.write(f'Initialized. {count} members added.')

