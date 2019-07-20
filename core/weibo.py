from core.models import Feed, Member
from core.utils import WeiboPost


def create_user(post: WeiboPost) -> Member:
    user = post.user
    wm, _ = Member.objects.get_or_create(chinese_name=user['screen_name'])
    wm.twitter_id = user['idstr']
    return wm


def save_content(post: WeiboPost) -> Feed or None:
    weibo = Feed.objects.weibo().filter(status_id=post.id).first()
    if weibo:
        return weibo




def save_contents():
    pass
