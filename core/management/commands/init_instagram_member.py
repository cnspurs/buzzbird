import instaloader

from django.core.management.base import BaseCommand
from django_q.tasks import async_task

from core import instagram_v2
from core.models import Member, Media

ins_list = ['llorente_fer',
            'ndombele_22',
            'daosanchez13',
            'spursofficial',
            'vincentjanssenofficial',
            'eriklamela',
            'gazzanigapaulo',
            'hm_son7',
            'harrykane',
            'jrclarke_',
            'ericdier15',
            'jvertonghen',
            'victorwanyama',
            'moussasissokoofficiel',
            'sergeaurier',
            'bendavies33',
            'tobyalderweireld',
            'lucasmoura7',
            'ktrippier2',
            'harrywinks',]


class Command(BaseCommand):

    def handle(self, *args, **options):
        d = {}

        for username in ins_list:
            try:
                profile = instaloader.Profile.from_username(instagram_v2.ins.context, username)
                d[profile.full_name] = (profile.userid, profile.profile_pic_url)
            except Exception as e:
                self.stderr.write(e)

        for k, v in d.items():
            m: Member = Member.objects.filter(english_name__icontains=k).first()
            if m:
                user_id, profile_pic_url = v
                m.instagram_id = str(user_id)

                if not m.avatar:
                    media = Media.objects.create(original_url=profile_pic_url)
                    m.avatar = media
                    m.save()
                    async_task(media.download_to_local)

                self.stdout.write(f'{m.english_name} with instagram_id {m.instagram_id}')

