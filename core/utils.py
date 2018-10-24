import os
from io import BytesIO

import requests
import twitter as t

from core.models import TwitterMember
from core.schema import Weibo

CONSUMER_KEY = os.getenv('TWITTER_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('TWITTER_CONSUMER_SECRET')
ACCESS_TOKEN_KEY = os.getenv('TWITTER_ACCESS_TOKEN_KEY')
ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')


class TwitterAPI:
    def __init__(self, consumer_key, consumer_secret, access_token_key, access_token_secret, **kwargs):
        self._api = t.Api(consumer_key, consumer_secret, access_token_key, access_token_secret, **kwargs)

    def get_timeline(self, list_id=77158478, **kwargs) -> list:
        timeline = self._api.GetListTimeline(list_id, **kwargs)

        return [Status(status) for status in timeline]


class Status:

    def __init__(self, status: t.models.Status):
        self._status = status

    def __str__(self):
        return self._status.__str__()

    def __repr__(self):
        return self._status.__repr__()

    def to_weibo(self):
        data = {
            'text': f'【{self.screen_name} 推特】{self.text}',
            'pic': self.first_image,
            'tweet_id': self.tweet_id,
        }

        return Weibo(**data)

    @property
    def screen_name(self):
        twitter_member: TwitterMember = TwitterMember.objects.filter(twitter_id=self.twitter_user_id).first()

        if twitter_member:
            if twitter_member.chinese_name is not None:
                return twitter_member.chinese_name
            return self.username

        TwitterMember.objects.create(twitter_id=self.twitter_user_id, english_name=self.username)
        return self.username

    @property
    def text(self):
        return self._status.full_text

    @property
    def first_image(self):
        if self._status.media is None:
            return None

        image_url = self._status.media[0].media_url_https

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
        # 反正现在又用不上
        return None


twitter = TwitterAPI(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET, tweet_mode='extended')
