import logging
import random
import time

from core import instagram
from core.models import Profile, Settings, Instagram
from core.utils import twitter

from django.conf import settings

logger = logging.getLogger('core.cron')
oauth_weibo = settings.WEIBO


def sync():
    profile = Profile.objects.filter(user__username='5833511420').first()

    if profile is None:
        return

    last_tweet_id = Settings.last_tweet_id()

    timeline = twitter.get_timeline(since_id=last_tweet_id.value)
    timeline.reverse()

    count = 0
    for tweet in timeline:
        weibo = tweet.to_weibo()
        if weibo is not None:
            result = oauth_weibo.post(profile, weibo)

            if result:
                last_tweet_id.value = weibo.tweet_id
                last_tweet_id.save()
                count += 1
            seconds = random.randint(15, 45)
            time.sleep(seconds)
            logger.info(f'Tweets: Published. Sleep {seconds} seconds')

    logger.info(f'Cron job finished. Length: {len(timeline)}, sent: {count}')


def sync_instagram():
    sync_instagram_to_weibo()
    sync_instagram_to_discourse()


def sync_instagram_to_weibo():
    profile = Profile.objects.filter(user__username='5833511420').first()
    qs = Instagram.objects.filter(is_buzzbird=False).order_by('created_at')
    for ig in qs:
        weibo = instagram.ig_to_weibo(ig)
        result = oauth_weibo.post(profile, weibo)
        if result:
            ig.is_buzzbird = True
            ig.save()
            logger.info(f'Instagram: synced {ig.author}: {ig.title}.')
        seconds = random.randint(15, 45)
        time.sleep(seconds)
        logger.info(f'Published. Sleep {seconds} seconds.')


def sync_instagram_to_discourse():
    qs = Instagram.objects \
        .filter(is_discourse=False) \
        .order_by('created_at')
    for ig in qs:
        result = instagram.send_to_discourse_as_post(ig)
        if result:
            ig.is_discourse = True
            ig.save()
            logger.info(f'Instagram synced to discourse: {ig.author}, {ig.title}')
