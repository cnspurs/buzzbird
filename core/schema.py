from dataclasses import dataclass
from io import BytesIO


@dataclass
class Weibo:
    text: str
    tweet_id: str
    pic: BytesIO = None
