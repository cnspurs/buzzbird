from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField('Access Token', max_length=64)
    access_token_expired_at = models.DateTimeField('Access Token 过期时间', null=True)

    @property
    def expired(self):
        if self.access_token_expired_at:
            return timezone.now() > self.access_token_expired_at
        return True


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
