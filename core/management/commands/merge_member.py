from django.core.management.base import BaseCommand

from core.models import *


class Command(BaseCommand):
    """
    merge member
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '-s', '--source', type=int, help='Member that will be merged and deleted'
        )
        parser.add_argument('-t', '--target', type=int)

    def handle(self, *args, **kwargs):
        source = kwargs['source']
        target = kwargs['target']

        source_user = Member.objects.filter(id=source).first()
        target_user = Member.objects.filter(id=target).first()

        if source_user and target_user:
            Feed.objects.filter(user=source_user).update(user=target_user)

            if not target_user.weibo_id and source_user.weibo_id:
                target_user.weibo_id = source_user.weibo_id
            if not target_user.twitter_id and source_user.twitter_id:
                target_user.twitter_id = source_user.twitter_id
            if not target_user.instagram_id and source_user.instagram_id:
                target_user.instagram_id = source_user.instagram_id

            target_user.save()
            source_user.delete()

        else:
            self.stdout.write(self.style.ERROR('source or target does not exist!'))
