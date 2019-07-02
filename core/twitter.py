import io
import logging

import requests
from dateutil.parser import parse
from django.conf import settings

from core.models import Feed, Member
from core.schema import Weibo
from core.utils import Status
from core.utils import twitter as t

logger = logging.getLogger('core.twitter')


def create_user(twitter: Status):
    tm, created = Member.objects.get_or_create(twitter_id=twitter.twitter_user_id, english_name=twitter.username,
                                               type='twitter')
    tm.save()
    return tm


def save_content(user, item: Status):
    # if saved, then don't duplicate
    link = item.link
    twitter = Feed.objects.twitter().filter(metadata__id_str=item.raw_json['id_str']).first()
    if twitter:
        return twitter

    created_at = parse(item.created_at)
    twitter = Feed.objects.create(author=item.author, link=link, media_url=item.first_image_url,
                                  created_at=created_at, title=item.text, user=user, type='twitter',
                                  metadata=item.raw_json)
    logger.info(f'Twitter: {twitter} saved')
    return twitter


def save_contents():
    tl = t.get_timeline()
    for twitter in tl:
        user = create_user(twitter)
        save_content(user, twitter)


def get_image(url):
    r = requests.get(url)
    image_data = io.BytesIO(r.content)
    return image_data


def ig_to_weibo(ig: Feed):
    text = f'【{ig.user.chinese_name} Ins】{ig.title[:110]}... https://spursnews.net/weibo/instagrams/{ig.id}'
    data = {
        'text': text,
        'pic': get_image(ig.media_url),
        'tweet_id': ig.id,
    }
    return Weibo(**data)


def send_to_discourse_as_post(twitter: Feed):
    data = {
        'api_username': 'SpursBuzzbird',
        'api_key': settings.DISCOURSE_API_KEY,
        'topic_id': 7569,
        'raw': f'【{twitter.user.chinese_name} Ins】' + '\n'
               + twitter.title + '\n'
               + twitter.link
    }

    r = requests.post('https://discourse.cnspurs.com/posts.json', data=data)
    if r.status_code == 200:
        logger.info(r.text)
        return True
    else:
        logger.error(f'Error while sending Twitter {twitter.id}: {r.text}')
        return False
