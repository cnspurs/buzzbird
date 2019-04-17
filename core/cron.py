import logging

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

    logger.info(f'Cron job finished. Length: {len(timeline)}, sent: {count}')


def sync_instagram():
    profile = Profile.objects.filter(user__username='5833511420').first()
    qs = Instagram.objects.filter(is_buzzbird=False).order_by('published_at')
    for ig in qs:
        weibo = instagram.ig_to_weibo(ig)
        result = oauth_weibo.post(profile, weibo)
        instagram.send_to_discourse_as_post(ig)
        if result:
            ig.is_buzzbird = True
            ig.save()
            logger.info(f'Instagram: synced {ig.author}: {ig.title}')
