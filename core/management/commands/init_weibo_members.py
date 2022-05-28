from core import weibo, weibo_v2
from django.core.management.base import BaseCommand

id_list = [
    2694295913,  # 热刺节操巷
    3065243713,  # 托特纳姆热刺足球俱乐部
    2747143811,  # 爆棚仓鼠
]


class Command(BaseCommand):
    def handle(self, *args, **options):
        for user_id in id_list:
            user_info = weibo_v2.get_user_info(user_id)
            author = user_info["screen_name"]
            avatar_url = user_info["avatar_hd"]

            weibo.get_or_create_user(user_id, author, avatar_url)
            self.stdout.write(f"{author} with weibo_id {user_id}")
