import logging
import os

import instaloader
from dateutil.parser import parse
from django.conf import settings
from django.utils import timezone
from django_q.tasks import async_task

from core import func
from core.models import Feed, Member, Media
from core.schema import Weibo

logger = logging.getLogger('core.instagram_v2')

ins = instaloader.Instaloader()
session_name = os.path.join(settings.INSTAGRAM_SESSION_DIR, settings.INSTAGRAM_NAME)
try:
    ins.load_session_from_file(settings.INSTAGRAM_NAME, session_name)
except FileNotFoundError:
    logger.warning('No session file. Will log in Instagram via user/password.')
    ins.login(settings.INSTAGRAM_NAME, settings.INSTAGRAM_PASSWORD)
    ins.save_session_to_file(session_name)


def create_user(profile: instaloader.Post) -> Member:
    im, created = Member.objects.get_or_create(english_name=profile.owner_profile.full_name)
    if created:
        im.instagram_id = str(profile.owner_id)
        im.save(update_fields=['instagram_id'])
    return im


def save_content(user: Member, post: instaloader.Post) -> Feed or None:
    ig = Feed.objects.instagram_v2().filter(status_id=post.shortcode).first()
    if ig:
        return ig

    profile = post.owner_profile
    created_at = post.date.replace(tzinfo=timezone.utc)

    # handle caption
    caption = ''
    if post.caption is not None:
        caption = post.caption
    ig = Feed.objects.create(author=profile.username, created_at=created_at, title=caption, user=user,
                             type='instagram_v2', status_id=post.shortcode,
                             link=f'https://www.instagram.com/p/{post.shortcode}')

    # Only an image
    if post.typename == 'GraphImage':
        m = Media.objects.create(feed=ig, original_url=post.url)
        async_task(m.download_to_local)

    # Multi images
    elif post.typename == 'GraphSidecar':
        for image in post.get_sidecar_nodes():
            m = Media.objects.create(feed=ig, original_url=image.display_url)
            async_task(m.download_to_local)

    elif post.typename == 'GraphVideo':
        ig.is_video = True
        ig.save(update_fields=['is_video'])
        m = Media.objects.create(feed=ig, original_url=post.url, )

    logger.info(f'Instagram: {ig} saved')
    return ig


def save_contents():
    members = Member.objects.exclude(instagram_id=None)
    for member in members:
        instagram_id = int(member.instagram_id)
        profile = instaloader.Profile.from_id(ins.context, instagram_id)
        posts = profile.get_posts()
        for post in posts:
            two_days_before = timezone.now() + timezone.timedelta(days=-1)
            created_at = post.date.replace(tzinfo=timezone.utc)
            if created_at < two_days_before:
                logger.info(f'Instagram: https://instagram.com/p/{post.shortcode} is too old.')
                break
            save_content(member, post)


def ig_to_weibo(ig: Feed):
    text = f'【{ig.user.chinese_name} Ins】{ig.title[:110]}... https://spursnews.net/weibo/instagrams/{ig.id}'
    media = None
    if ig.media.count() > 0:
        media = ig.media.all()[0]
    data = {
        'text': text,
        'pic': func.get_local_image(media.local_path),
        'tweet_id': ig.id,
    }
    return Weibo(**data)


def convert_username_to_id(username) -> str or None:
    profile = instaloader.Profile.from_username(ins.context, username)
    return str(profile.userid)
