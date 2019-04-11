import io
import logging
import re

import requests
from dateutil.parser import parse
from django.conf import settings

from core.models import Instagram, InstagramMember
from core.schema import Weibo

logger = logging.getLogger('core.instagram')


def get_feeds_list():
    url = f'http://fetchrss.com/api/v1/feed/list?auth={settings.FETCHRSS_API_KEY}'
    r = requests.get(url)
    data = r.json()

    if data['success'] is False:
        logger.error(f'fetchrss: {data["error"]}')
        return

    return data['feeds']


def extract_url_id(url):
    return re.split(r'[/.]', url)[-2]


def get_feed_content(feed):
    url = feed['rss_url']
    rss_id = extract_url_id(url)
    url = f'http://fetchrss.com/rss/{rss_id}.json'
    r = requests.get(url)
    return r.json()


def create_user(content):
    english_name = content['title']
    chinese_name = content['description']

    im, _ = InstagramMember.objects.get_or_create(english_name=english_name)
    im.chinese_name = chinese_name
    im.save()

    return im


def save_content(user, item):
    published_at = parse(item['pubDate'])
    ig = Instagram.objects.create(author=item['author'], link=item['link'], media_url=item['media:content'],
                                  published_at=published_at, title=item['title'], user=user)
    logger.info(f'Instagram: {ig} saved')
    return ig


def save_contents():
    feeds = get_feeds_list()
    for feed in feeds:
        content = get_feed_content(feed)
        user = create_user(content)
        for item in content['items']:
            save_content(user, item)


def get_image(url):
    r = requests.get(url)
    image_data = io.BytesIO(r.content)
    return image_data


def ig_to_weibo(ig: Instagram):
    data = {
        'text': ig.title,
        'pic': get_image(ig.media_url),
        'tweet_id': ig.id,
    }
    return Weibo(**data)
