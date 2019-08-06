import sys
import requests

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
    r = requests.get(url, data)
    json = r.json()

    if not json['ok']:
        return None

    info = json['data']['userInfo']
    if info.get('toolbar_menus'):
        del info['toolbar_menus']
    user_info = standardize_info(info)
    return user_info
