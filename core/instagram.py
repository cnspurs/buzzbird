import io
import logging
import re

import requests
from dateutil.parser import parse
from django.conf import settings
from django_q.tasks import async_task

from core import func
from core.models import Feed, Member, Media
from core.schema import Weibo

logger = logging.getLogger('core.instagram')


def get_feeds_list():
    url = f'https://fetchrss.com/api/v1/feed/list?auth={settings.FETCHRSS_API_KEY}'
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
    url = f'https://fetchrss.com/rss/{rss_id}.json'
    r = requests.get(url)
    return r.json()


def create_user(content):
    english_name = content['title']
    chinese_name = content['description']

    im, _ = Member.objects.get_or_create(english_name=english_name)
    im.chinese_name = chinese_name
    im.save()

    return im


def save_content(user, item):
    # if saved, then don't duplicate
    link = item['link']
    ig = Feed.objects.instagram().filter(link=link).first()
    if ig:
        return ig

    created_at = parse(item['pubDate'])
    ig = Feed.objects.create(author=item['author'], link=link, created_at=created_at, title=item['title'],
                             user=user, type='instagram')

    media_url = item.get('media:content')
    if media_url is not None:
        m = Media.objects.create(feed=ig, original_url=media_url)
        async_task(m.download_to_local)

    logger.info(f'Instagram: {ig} saved')
    return ig


def save_contents():
    feeds = get_feeds_list()
    for feed in feeds:
        content = get_feed_content(feed)
        user = create_user(content)
        for item in reversed(content['items']):
            save_content(user, item)


def get_image(url):
    r = requests.get(url)
    image_data = io.BytesIO(r.content)
    return image_data


def ig_to_weibo(ig: Feed):
    text = f'【{ig.user.name} Ins】{ig.title[:120]} ... https://spursnews.net/feeds/{ig.id}'
    media = None
    if ig.media.count() > 0:
        media = ig.media.all()[0]
    data = {
        'text': text,
        'pic': func.get_local_image(media.local_path),
        'tweet_id': ig.id,
    }
    return Weibo(**data)


def send_to_discourse_as_post(ig: Feed):
    data = {
        'api_username': 'SpursBuzzbird',
        'api_key': settings.DISCOURSE_API_KEY,
        'topic_id': 7569,
        'raw': f'【{ig.user.chinese_name} Ins】' + '\n'
               + ig.title + '\n'
               + ig.link
    }

    r = requests.post('https://discourse.cnspurs.com/posts.json', data=data)
    if r.status_code == 200:
        logger.info(r.text)
        return True
    else:
        logger.error(f'Error while sending Instagram {ig.id}: {r.text}')
        return False
