from django.core.management.base import BaseCommand
from django_q.tasks import async_task

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
            source_user.delete()

        else:
            self.stdout.write(self.style.ERROR('source or target does not exist!'))
