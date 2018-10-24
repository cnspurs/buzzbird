from core.utils import twitter
from core.models import Profile
from core.models import Settings

from django.conf import settings


def sync():
    print(twitter._api._access_token_key)

    profile = Profile.objects.filter(user__username='5833511420').first()

    if profile is None:
        return

    timeline = twitter.get_timeline()
    timeline.reverse()

    oauth_weibo = settings.WEIBO

    for tweet in timeline:
        weibo = tweet.to_weibo()
        result = oauth_weibo.post(profile, weibo)

        if result is True:
            last_tweet_id = Settings.last_tweet_id()
            last_tweet_id.value = weibo.tweet_id
            last_tweet_id.save()



