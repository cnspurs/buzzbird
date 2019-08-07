import sys
import json
from datetime import datetime, timedelta

from core import weibo
from core.models import Member
from core.utils import requests_get

url = 'https://m.weibo.cn/api/container/getIndex'


def standardize_info(info_dict: dict) -> dict:
    for k, v in info_dict.items():
        if 'int' not in str(type(v)) and 'long' not in str(type(v)) and 'bool' not in str(type(v)):
            info_dict[k] = v.replace(u"\u200b", "").encode(sys.stdout.encoding, "ignore").decode(sys.stdout.encoding)
    return info_dict


def get_user_info(user_id: int) -> dict or None:
    data = {
        'containerid': '100505' + str(user_id)
    }
    r = requests_get(url, data)
    returned_json = r.json()

    if not returned_json['ok']:
        return None

    info = returned_json['data']['userInfo']
    if info.get('toolbar_menus'):
        del info['toolbar_menus']
    user_info = standardize_info(info)
    return user_info


def get_long_weibo(weibo_id_str: str) -> dict:
    long_weibo_url = f'https://m.weibo.cn/detail/{weibo_id_str}'
    html = requests_get(long_weibo_url).text
    html = html[html.find('"status":'):]
    html = html[:html.rfind('"hotScheme"')]
    html = html[:html.rfind(',')]
    html = '{' + html + '}'
    weibo_info = json.loads(html, strict=False)
    return weibo_info


def get_one_page(weibo_id_str: str, page_id: int) -> list or None:
    data = {
        'containerid': '107603' + weibo_id_str,
        'page': page_id
    }
    r = requests_get(url, data)
    returned_json = r.json()

    if not returned_json['ok']:
        return None

    weibo_cards = returned_json['data']['cards']
    weibo_posts = []
    for weibo_card in weibo_cards:
        if weibo_card['card_type'] != 9:
            continue

        weibo_post_info = weibo_card['mblog']
        # Skips sticky post
        # TODO: return sticky post if it has not been saved
        if weibo_post_info.get('isTop'):
            continue
        # Skips retweeted posts
        # TODO: expect Jedi to forget about this
        if weibo_post_info.get('retweeted_status'):
            continue

        # Processes long Weibo post
        if weibo_post_info['isLongText']:
            weibo_post_id_str: str = weibo_post_info['id']
            weibo_post_info = get_long_weibo(weibo_post_id_str)
            post = weibo.WeiboPost(standardize_info(weibo_post_info['status']))
        else:
            post = weibo.WeiboPost(standardize_info(weibo_post_info))
        weibo_posts.append(post)

    return weibo_posts


def save_contents() -> None:
    weibo_members = Member.objects.exclude(weibo_id=None)
    for weibo_member in weibo_members:
        weibo_id_str: str = weibo_member.weibo_id

        page_id: int = 0
        found_saved: bool = False
        while not found_saved:
            page_id += 1
            posts = get_one_page(weibo_id_str, page_id)
            for post in posts:
                # Avoids saving excessive past posts for the first time
                # TODO: remove this later
                delta = datetime.now() - post.created_at_v2
                if delta > timedelta(days=1):
                    found_saved = True
                    break

                user = weibo.get_or_create_user(post.user['idstr'], post.author, post.user['avatar_hd'])
                _, created = weibo.save_content(user, post, version=2)
                if not created:
                    found_saved = True
                    break
