import logging

from django.conf import settings

import core.func

from core.models import Feed
from core.schema import Weibo

logger = logging.getLogger("core.feed")


def feed_to_weibo(feed: Feed) -> Weibo or None:
    text = f'【{feed.user.name} Ins】{feed.title[:120]} ... {settings.BUZZBIRD_FEED_URL}/{feed.id}'
    media = None
    if feed.media.count() > 0:
        media = feed.media.all()[0]

    if media is None and feed.type == 'instagram_v2':
        logger.warning(f"{feed.type} {feed.id} missing media. Stop generating Weibo data.")
        return None

    data = {
        'text': text,
        'pic': core.func.get_local_image(media.local_path) if media is not None else None,
        'tweet_id': feed.id,
    }
    return Weibo(**data)
