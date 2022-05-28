import logging
import re

import core.func
from core.models import Feed
from core.schema import Weibo
from django.conf import settings

logger = logging.getLogger("core.feed")


def text_processing(string):
    pattern = r"https://t.co(/?\w*)"
    result = re.sub(pattern, "", string)

    # remove duplicate space
    result = " ".join(result.split())
    return result


def feed_to_weibo(feed: Feed) -> Weibo or None:
    mapping = {"instagram_v2": "ins", "twitter": "推特"}
    feed_type = mapping[feed.type]
    text = f'【{feed.user.name} {feed_type}】{feed.title[:140]} {"..." if len(feed.title) > 140 else ""} {settings.BUZZBIRD_FEED_URL}/{feed.id}'
    text = text_processing(text)
    media = None
    if feed.media.count() > 0:
        media = feed.media.all()[0]

    if media is None and feed.type == "instagram_v2":
        logger.warning(
            f"{feed.type} {feed.id} missing media. Stop generating Weibo data."
        )
        return None

    data = {
        "text": text,
        "pic": core.func.get_local_image(media.local_path)
        if media is not None
        else None,
        "tweet_id": feed.id,
    }
    return Weibo(**data)
