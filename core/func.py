import os
import datetime
import pathlib

from django.conf import settings


def create_date_dir(date: datetime.date):
    date_str = date.strftime('%Y-%m-%d')
    path = os.path.join(settings.MEDIA_ROOT, date_str)
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    return path


def get_local_image(path):
    if not path:
        return

    f = open(path, 'rb')
    return f
