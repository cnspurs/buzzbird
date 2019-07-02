from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

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
    english_name = models.CharField(max_length=64, primary_key=True)
    chinese_name = models.CharField(max_length=16)
    type = models.CharField(max_length=16, choices=FEED_TYPES)
    twitter_id = models.CharField(max_length=128, null=True)

    objects = FeedManager()


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
    media_url = models.URLField(max_length=1024)
    link = models.URLField(db_index=True)
    created_at = models.DateTimeField()
    title = models.CharField(blank=True, max_length=1024)
    user = models.ForeignKey('core.Member', related_name='posts', null=True, on_delete=models.SET_NULL)
    type = models.CharField(max_length=16, choices=FEED_TYPES)
    metadata = JSONField(null=True)

    objects = FeedManager()

    def __str__(self):
        return f'<{self.__class__.__name__}: {self.id}, {self.user.english_name}:{self.title}, {self.created_at},' \
            f'is_buzzbird: {self.is_buzzbird}, is_discourse: {self.is_discourse}>'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
