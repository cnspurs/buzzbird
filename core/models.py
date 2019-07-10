import logging
import os

import requests

from urllib.parse import urlparse

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

logger = logging.getLogger('core.models')

FEED_TYPES = [
    ('instagram', 'Instagram'),
    ('twitter', 'Twitter'),
]


class FeedManager(models.Manager):
    def instagram(self):
        return super().get_queryset().filter(type='instagram')

    def twitter(self):
        return super().get_queryset().filter(type='twitter')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField('Access Token', max_length=64)
    access_token_expired_at = models.DateTimeField('Access Token 过期时间', null=True)

    @property
    def expired(self):
        if self.access_token_expired_at:
            return timezone.now() > self.access_token_expired_at
        return True


class Member(models.Model):
    english_name = models.CharField(max_length=64)
    chinese_name = models.CharField(max_length=16)
    twitter_id = models.CharField(max_length=128, null=True)

    objects = FeedManager()

    def __str__(self):
        return f'{self.english_name, self.chinese_name}'

    @property
    def name(self):
        return self.chinese_name or self.english_name


class Settings(models.Model):
    key = models.CharField(max_length=16, primary_key=True)
    value = models.CharField(max_length=255, null=True)

    @classmethod
    def last_tweet_id(cls):
        last_tweet_id, _ = cls.objects.get_or_create(key='last_tweet_id')
        return last_tweet_id


class Feed(models.Model):
    author = models.CharField(max_length=64)
    collected_at = models.DateTimeField(auto_now_add=True)
    is_buzzbird = models.BooleanField('Published to buzzbird Weibo?', default=False)
    is_discourse = models.BooleanField('Published to discourse?', default=False)
    media_url = models.URLField(max_length=1024, null=True)
    link = models.URLField(db_index=True, null=True)
    created_at = models.DateTimeField()
    title = models.CharField(blank=True, max_length=1024)
    user = models.ForeignKey('core.Member', related_name='posts', null=True, on_delete=models.SET_NULL)
    type = models.CharField(max_length=16, choices=FEED_TYPES)
    metadata = JSONField(null=True)

    objects = FeedManager()

    def __str__(self):
        return f'<{self.__class__.__name__}: {self.id}, {self.user.english_name}:{self.title}, {self.created_at},' \
            f'is_buzzbird: {self.is_buzzbird}, is_discourse: {self.is_discourse}>'

    @property
    def downloaded_media(self):
        return self.media.exclude(filename=None)


class Media(models.Model):
    feed = models.ForeignKey('core.Feed', related_name='media', null=True, on_delete=models.SET_NULL)
    filename = models.CharField(max_length=512, null=True)
    original_url = models.URLField(max_length=1024)

    @property
    def local_path(self):
        if not self.filename:
            return ''
        return os.path.join(settings.MEDIA_ROOT, self.filename)

    @property
    def url(self):
        if not self.filename:
            return ''
        return settings.MEDIA_URL + self.filename

    @property
    def downloaded(self):
        if os.path.isfile(self.local_path):
            return True
        return False

    @property
    def path(self):
        result = urlparse(self.original_url)
        return result.path

    @property
    def original_name(self):
        return self.path.split('/')[-1]

    @property
    def ext(self):
        return self.original_name.split('.')[-1]

    def download_to_local(self):
        # saved as $name
        name = self.original_name
        path = os.path.join(settings.MEDIA_ROOT, name)

        # save time
        if os.path.isfile(path):
            if not self.filename:
                self.filename = name
                self.save(update_fields=['filename'])
            return

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        }
        r = requests.get(self.original_url, timeout=3, headers=headers)
        with open(path, 'wb') as f:
            f.write(r.content)

        logger.info(f'Media {self.id} save to local, filename: {name}')
        self.filename = name
        self.save(update_fields=['filename'])
        return


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
