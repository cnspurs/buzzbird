import logging

from dateutil.parser import parse
import requests

from django_q.tasks import async_task

from core.models import Profile, Feed, Member, Media

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
    def user(self):
        return self.status['user']

    @property
    def author(self):
        return self.user['screen_name']

    @property
    def mid(self):
        return self.status['mid']

    @property
    def text(self):
        return self.status['text']

    @property
    def created_at(self):
        return parse(self.status['created_at'])

    @property
    def url(self):
        user_id = self.user['id']
        post_url = f'https://weibo.com/{user_id}/{mid_to_url(self.mid)}'
        return post_url

    @property
    def pic_urls(self):
        urls = []
        for item in self.status['pic_urls']:
            thumbnail_url = item['thumbnail_pic']
            urls.append(thumbnail_url.replace('/thumbnail/', '/large/'))
        return urls


def get_home_timeline(profile: Profile):
    url = 'https://api.weibo.com/2/statuses/home_timeline.json'
    data = {
        'access_token': profile.access_token,
        'count': 100,
    }

    r = requests.get(url, data)
    if not r.ok:
        return None
    return r.json()


def get_or_create_user(user_id: int, username: str, avatar_url: str) -> Member:
    wm, created = Member.objects.get_or_create(chinese_name=username)
    if created:
        wm.weibo_id = str(user_id)

        # Now the avatar won't be updated after this Member is created
        avatar = Media.objects.create(original_url=avatar_url)
        wm.avatar = avatar
        async_task(avatar.download_to_local)

        wm.save(update_fields=['weibo_id', 'avatar'])
    return wm


def save_content(user: Member, post: WeiboPost) -> (Feed, bool):
    weibo = Feed.objects.weibo().filter(status_id=post.id).first()
    if weibo:
        return weibo, False

    weibo = Feed.objects.create(author=post.author, link=post.url, created_at=post.created_at, title=post.text,
                                user=user, type='weibo', metadata=post.status, status_id=post.id)

    for url in post.pic_urls:
        media = Media.objects.create(feed=weibo, original_url=url)
        async_task(media.download_to_local)

    logger.info(f'Weibo: {weibo} saved')
    return weibo, True


def save_contents():
    profile = Profile.objects.filter(user__username='5833511420').first()
    home_timeline = get_home_timeline(profile)
    if not home_timeline:
        return

    posts = [WeiboPost(status) for status in home_timeline['statuses']]
    for post in posts:
        # Skip Weibo posts posted by buzzbird
        if post.user['id'] == 5833511420:
            continue

        user = get_or_create_user(post.user['idstr'], post.author, post.user['avatar_hd'])
        _, created = save_content(user, post)
        if not created:
            break
