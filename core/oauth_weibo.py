import requests

HAHA = 'https://api.weibo.com/oauth2/authorize?response_type=code&client_id=3542800494&redirect_uri=https://spurssh.com'


class OAuthWeibo:
    def __init__(self, app_id: str = None, app_secret: str = None, redirect_uri: str = None):
        self.app_id = app_id
        self.app_secret = app_secret
        self.redirect_uri = redirect_uri

    def get_access_token(self, code: str) -> str:
        URL = f'https://api.weibo.com/oauth2/access_token?client_id={self.app_id}' \
              f'&client_secret={self.app_secret}&grant_type=authorization_code' \
              f'&redirect_uri={self.redirect_uri}&code={code}'

        r = requests.post(URL)

        if 'access_token' in r.json():
            return r.json()['access_token']

        raise ValueError(r.text)

    @staticmethod
    def get_uid(access_token: str) -> str:
        URL = 'https://api.weibo.com/oauth2/get_token_info'
        data = {
            'access_token': access_token
        }

        r = requests.post(URL, data)

        if 'uid' in r.json():
            uid = r.json()['uid']
            return str(uid)

        raise ValueError(r.text)
