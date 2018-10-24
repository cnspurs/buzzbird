from io import BytesIO
from dataclasses import dataclass

@dataclass
class Weibo:
    text: str
    tweet_id: str
    pic: BytesIO = None
