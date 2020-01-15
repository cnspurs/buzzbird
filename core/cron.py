import logging
import random
import time

from core import instagram, instagram_v2, twitter
from core.models import Profile, Feed

from django.conf import settings

logger = logging.getLogger("core.cron")
oauth_weibo = settings.WEIBO


def sync_instagram_to_discourse():
    qs = Feed.objects.instagram().filter(is_discourse=False).order_by("created_at")
    for ig in qs:
        result = instagram.send_to_discourse_as_post(ig)
        if result:
            ig.is_discourse = True
            ig.save()
            logger.info(f"Instagram synced to discourse: {ig.author}, {ig.title}")


def sync_twitter_to_buzzbird():
    profile = Profile.objects.filter(user__username="5833511420").first()
    qs = (
        Feed.objects.twitter()
        .filter(is_buzzbird=False)
        .prefetch_related("media")
        .order_by("created_at")
    )
    for t in qs:
        weibo = twitter.twitter_to_weibo(t)
        result = oauth_weibo.post(profile, weibo)
        if result:
            t.is_buzzbird = True
            t.save()
        seconds = random.randint(15, 45)
        logger.info(f"Twitter: synced {t.author}: {t.title}. Sleep {seconds} seconds.")
        time.sleep(seconds)


def sync_instagram_v2_to_buzzbird():
    profile = Profile.objects.filter(user__username="5833511420").first()
    qs = (
        Feed.objects.instagram_v2()
        .filter(is_buzzbird=False)
        .prefetch_related("media")
        .order_by("created_at")
    )

    for ig in qs:
        weibo = instagram_v2.ig_to_weibo(ig)
        if weibo is None:
            continue
        result = oauth_weibo.post(profile, weibo)
        if result:
            ig.is_buzzbird = True
            ig.save(update_fields=["is_buzzbird"])
        seconds = random.randint(15, 45)
        logger.info(
            f"Instagram V2: synced {ig.author}: {ig.title}. Sleep {seconds} seconds."
        )
        time.sleep(seconds)
