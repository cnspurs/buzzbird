import logging

import requests
from requests_toolbelt import MultipartEncoder

from core.schema import Weibo

logger = logging.getLogger('core.oauth_weibo')

class OAuthWeibo:
    def __init__(self, app_id: str = None, app_secret: str = None, redirect_uri: str = None):
        self.app_id = app_id
        self.app_secret = app_secret
        self.redirect_uri = redirect_uri

    def get_access_token(self, code: str) -> str:
        url = f'https://api.weibo.com/oauth2/access_token?client_id={self.app_id}' \
            f'&client_secret={self.app_secret}&grant_type=authorization_code' \
            f'&redirect_uri={self.redirect_uri}&code={code}'

        r = requests.post(url)

        if 'access_token' in r.json():
            return r.json()

        raise ValueError(r.text)

    @staticmethod
    def get_uid(access_token: str) -> str:
        url = 'https://api.weibo.com/oauth2/get_token_info'
        data = {
            'access_token': access_token
        }

        r = requests.post(url, data)

        if 'uid' in r.json():
            uid = r.json()['uid']
            return str(uid)

        raise ValueError(r.text)

    def post(self, profile, weibo: Weibo):
        data = {
            'access_token': profile.access_token,
            'status': weibo.text,
        }
        url = 'https://api.weibo.com/2/statuses/share.json'
        if weibo.pic is None:
            r = requests.post(url, data=data)

        else:
            data.update({'pic': ('share.jpg', weibo.pic, 'image/jpeg')})
            m = MultipartEncoder(fields=data)

            r = requests.post(url, data=m, headers={'Content-Type': m.content_type})

        if 'created_at' in r.json():
            logger.info(r.text)
            return True

        logger.error(f'error: {r.text}, weibo.text: {weibo.text}')
