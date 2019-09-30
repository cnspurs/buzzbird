from django.core.management.base import BaseCommand

from core.models import *


class Command(BaseCommand):
    """
    merge member
    """

    def add_arguments(self, parser):
        parser.add_argument('id', type=int, help='Member ID')
        parser.add_argument('--instagram', type=str)
        parser.add_argument('--twitter', type=str)
        parser.add_argument('--weibo', type=str)

    def handle(self, *args, **kwargs):
        member_id = kwargs.pop('id')

        member = Member.objects.filter(id=member_id).first()

        if member:
            for k, v in kwargs.items():
                setattr(member, f'{k}_id', v)
            member.save()

        else:
            self.stdout.write(self.style.ERROR('Member does not exist!'))
