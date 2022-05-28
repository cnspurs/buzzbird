from core.models import Member
from core.utils import twitter
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        members = twitter.get_list_members()

        count = 0
        for user in members:
            if Member.objects.filter(english_name=user.name).first() is None:
                Member.objects.create(twitter_id=user.id_str, english_name=user.name)

                count += 1
        self.stdout.write(f"Initialized. {count} members added.")
