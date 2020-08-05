import io
import logging

import requests
from dateutil.parser import parse

from django.db.models import Q
from django_q.tasks import async_task

from core.models import Feed, Member, Media
from core.utils import Status
from core.utils import twitter as t

logger = logging.getLogger("core.twitter")


def create_user(twitter: Status):
    tm = Member.objects.filter(
        Q(twitter_id=twitter.twitter_user_id) | Q(english_name=twitter.screen_name)
    ).first()
    if not tm:
        tm = Member.objects.create(
            twitter_id=twitter.twitter_user_id, english_name=twitter.screen_name
        )
    tm.twitter_id = twitter.twitter_user_id
    tm.save()
    return tm


def save_content(user, item: Status):
    # if saved, then don't duplicate
    link = item.link
    twitter = (
        Feed.objects.twitter()
        .filter(
            Q(status_id=item.tweet_id) | Q(metadata__id_str=item.raw_json["id_str"])
        )
        .first()
    )
    if twitter:
        return twitter

    created_at = parse(item.created_at)
    twitter = Feed.objects.create(
        author=item.author,
        link=link,
        created_at=created_at,
        title=item.text,
        user=user,
        type="twitter",
        metadata=item.raw_json,
        status_id=item.tweet_id,
    )

    for url in item.images:
        m = Media.objects.create(feed=twitter, original_url=url)
        async_task(m.download_to_local)

    logger.info(f"Twitter: {twitter} saved")
    return twitter


def save_contents():
    members = Member.objects.exclude(
        Q(twitter_id='') | Q(twitter_id__isnull=True) | Q(archived=True)
    )
    for m in members:
        kwargs = {}
        last_feed: Feed = Feed.objects.twitter().filter(user_id=m.id).order_by('-status_id').first()
        if last_feed:
            kwargs = {'since_id': last_feed.status_id}

        tl = t.get_user_timelime(m, **kwargs)
        for twitter in tl:
            save_content(m, twitter)


def get_image(url):
    r = requests.get(url)
    image_data = io.BytesIO(r.content)
    return image_data
