import logging

import instaloader
from django.conf import settings
from django.utils import timezone
from django_q.tasks import async_task

from core import func
from core.models import Feed, Member, Media
from core.schema import Weibo

logger = logging.getLogger("core.instagram_v2")


def get_ins():
    ins = instaloader.Instaloader()
    ins.login(settings.INSTAGRAM_NAME, settings.INSTAGRAM_PASSWORD)

    return ins


def create_user(profile: instaloader.Post) -> Member:
    im, created = Member.objects.get_or_create(
        english_name=profile.owner_profile.full_name
    )
    if created:
        im.instagram_id = str(profile.owner_id)
        im.save(update_fields=["instagram_id"])
    return im


def save_content(user: Member, post: instaloader.Post) -> Feed or None:
    ig = Feed.objects.instagram_v2().filter(status_id=post.shortcode).first()
    if ig:
        return ig

    profile = post.owner_profile
    created_at = post.date.replace(tzinfo=timezone.utc)

    # handle caption
    caption = ""
    if post.caption is not None:
        caption = post.caption
    ig = Feed.objects.create(
        author=profile.username,
        created_at=created_at,
        title=caption,
        user=user,
        type="instagram_v2",
        status_id=post.shortcode,
        link=f"https://www.instagram.com/p/{post.shortcode}",
    )

    # Only an image
    if post.typename == "GraphImage":
        m = Media.objects.create(feed=ig, original_url=post.url)
        async_task(m.download_to_local)

    # Multi images
    elif post.typename == "GraphSidecar":
        for image in post.get_sidecar_nodes():
            m = Media.objects.create(feed=ig, original_url=image.display_url)
            async_task(m.download_to_local)

    elif post.typename == "GraphVideo":
        ig.is_video = True
        ig.save(update_fields=["is_video"])
        m = Media.objects.create(feed=ig, original_url=post.url)

    logger.info(f"Instagram: {ig} saved")
    return ig


def save_contents():
    ins = get_ins()
    members = Member.objects.exclude(instagram_id="").filter(archived=False)
    for member in members:
        instagram_id = int(member.instagram_id)
        profile = instaloader.Profile.from_id(ins.context, instagram_id)
        posts = profile.get_posts()
        for post in posts:
            two_days_before = timezone.now() + timezone.timedelta(days=-1)
            created_at = post.date.replace(tzinfo=timezone.utc)
            if created_at < two_days_before:
                logger.info(
                    f"Instagram: https://instagram.com/p/{post.shortcode} is too old."
                )
                break
            save_content(member, post)


def convert_username_to_id(username) -> str or None:
    ins = get_ins()

    profile = instaloader.Profile.from_username(ins.context, username)
    return str(profile.userid)
