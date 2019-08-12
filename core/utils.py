import logging
import os
from io import BytesIO

import requests
import twitter as t

from django.conf import settings

from core.models import Member, Profile
from core.schema import Weibo

logger = logging.getLogger('core.utils')

CONSUMER_KEY = os.getenv('TWITTER_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('TWITTER_CONSUMER_SECRET')
ACCESS_TOKEN_KEY = os.getenv('TWITTER_ACCESS_TOKEN_KEY')
ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')


def get_weibo_access_token() -> str:
    profile = Profile.objects.get(user__username=settings.WEIBO_BUZZBIRD_ID)
    return profile.access_token


class TwitterAPI:
    def __init__(self, consumer_key, consumer_secret, access_token_key, access_token_secret, **kwargs):
        self._api = t.Api(consumer_key, consumer_secret, access_token_key, access_token_secret, **kwargs)

    def get_timeline(self, list_id=77158478, **kwargs) -> list:
        timeline = self._api.GetListTimeline(list_id, **kwargs)

        return [Status(status) for status in timeline]

    def get_list_members(self, list_id=77158478, **kwargs):
        members = self._api.GetListMembers(list_id, **kwargs)

        return members

    def get_userid(self, username):
        user: t.User = self._api.GetUser(screen_name=username)
        return user.id_str


class Status:

    def __init__(self, status: t.models.Status):
        self._status = status

    def __str__(self):
        return self._status.__str__()

    def __repr__(self):
        return self._status.__repr__()

    def to_weibo(self):
        # 原创和转推，text 格式不一样
        if self.retweet is None:
            text = f'【{self.screen_name} 推特】{self.text}'
            image = self.first_image()
        else:
            # text = f'【{self.screen_name} 推特】{self.text} RT @{self.retweeted_status._status.user.screen_name} {self.retweeted_status.text}'
            # image = self.first_image(retweet=True)
            return None

        text = text if len(text) < 140 else text[:125] + '...' + 'https://t.co/diu'
        if 'https://t.co' not in text:
            text += ' https://t.co/diu'
        data = {
            'text': text,
            'pic': image,
            'tweet_id': self.tweet_id,
        }

        logger.info(f'text: {text}, image: {True if image else False}, tweet_id: {self.tweet_id}')
        return Weibo(**data)

    @property
    def screen_name(self):
        try:
            twitter_member: Member = Member.objects.filter(twitter_id=self.twitter_user_id, type='twitter').first()

            if twitter_member:
                if twitter_member.chinese_name is not None:
                    return twitter_member.chinese_name
                return self.username

            Member.objects.create(twitter_id=self.twitter_user_id, english_name=self.username)
            return self.username
        except Exception:
            return self.username

    @property
    def text(self):
        return self._status.full_text

    def first_image(self, retweet=False):
        image_url = ''

        if retweet is False:
            if self._status.media is None:
                return None

            image_url = self._status.media[0].media_url_https

        else:
            if self.retweeted_status._status.media is None:
                return None

            image_url = self.retweeted_status._status.media[0].media_url_https

        r = requests.get(image_url)
        image_data = BytesIO(r.content)
        return image_data

    @property
    def twitter_user_id(self) -> str:
        return self._status.user.id_str

    @property
    def tweet_id(self) -> str:
        return self._status.id_str

    @property
    def username(self):
        return self._status.user.name

    @property
    def images(self):
        result = []
        media: list = self._status.media
        if media is not None:
            for m in media:
                if m.video_info is None:
                    result.append(m.media_url_https)

        return result

    @property
    def retweet(self):
        return self._status.quoted_status or self._status.retweeted_status

    @property
    def retweeted_status(self):
        # retweet with comment == quoted_status
        # retweet with no comment == retweeted_status

        quoted = self._status.quoted_status
        retweeted = self._status.retweeted_status

        if quoted is None and retweeted is None:
            return None

        elif quoted:
            return Status(self._status.quoted_status)

        elif retweeted:
            return Status(self._status.retweeted_status)

    @property
    def created_at(self):
        return self._status.created_at

    @property
    def link(self):
        if self._status.media is None:
            return None
        return self._status.media[0].url

    @property
    def author(self):
        return self._status.user.screen_name

    @property
    def first_image_url(self):
        if self._status.media is None:
            return None
        return self._status.media[0].media_url_https

    @property
    def raw_json(self):
        return self._status._json


twitter = TwitterAPI(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET, tweet_mode='extended')


def requests_get(url: str, params: dict = None, **kwargs) -> requests.models.Response or None:
    if 'headers' not in kwargs or type(kwargs['headers']) is not dict:
        kwargs['headers'] = {}
    kwargs['headers']['user-agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
                                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    kwargs['timeout'] = 10

    try:
        r = requests.get(url, params, **kwargs)
        return r
    except requests.exceptions.Timeout:
        # TODO: Handle the time out
        return None
