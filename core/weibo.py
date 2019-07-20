import logging

from dateutil.parser import parse
import requests

from core.models import Profile, Feed, Member

logger = logging.getLogger('core.weibo')


def base62_encode(num, alphabet='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    if num == 0:
        return alphabet[0]

    arr = []
    base = len(alphabet)
    while num:
        rem = num % base
        num = num // base
        arr.append(alphabet[rem])
    arr.reverse()
    return ''.join(arr)


def mid_to_url(mid):
    mid_int = str(mid)[::-1]
    size = int(len(mid_int) // 7) if len(mid_int) % 7 == 0 else int(len(mid_int) // 7) + 1
    result = []
    for i in range(size):
        s = mid_int[i * 7: (i + 1) * 7][::-1]
        s = base62_encode(int(s))
        s_len = len(s)
        if i < size - 1 and len(s) < 4:
            s = '0' * (4 - s_len) + s
        result.append(s)
    result.reverse()
    return ''.join(result)


class WeiboPost:
    def __init__(self, status):
        self.status = status

    @property
    def id(self):
        return self.status['id']

    @property
    def author(self):
        return self.user['screen_name']

    @property
    def text(self):
        return self.status['text']

    @property
    def user(self):
        return self.status['user']

    @property
    def mid(self):
        return self.status['mid']

    @property
    def created_at(self):
        return parse(self.status['created_at'])

    @property
    def url(self):
        user_id = self.user['id']
        post_url = f'https://weibo.com/{user_id}/{mid_to_url(self.mid)}'
        return post_url


def get_home_timeline(profile: Profile):
    url = 'https://api.weibo.com/2/statuses/home_timeline.json'
    data = {
        'access_token': profile.access_token,
        'count': 100,
    }

    r = requests.get(url, data)
    return r.json()


def create_user(post: WeiboPost) -> Member:
    wm, _ = Member.objects.get_or_create(chinese_name=post.author)
    wm.twitter_id = post.user['idstr']
    return wm


def save_content(user: Member, post: WeiboPost) -> Feed or None:
    weibo = Feed.objects.weibo().filter(status_id=post.id).first()
    if weibo:
        return weibo

    weibo = Feed.objects.weibo(author=post.author, link=post.url, create_at=post.created_at, title=post.text,
                               user=user, type='weibo', metadata=post.status, status_id=post.id)

    logger.info(f'Weibo: {weibo} saved')
    return weibo


def save_contents():
    pass
