from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField('Access Token', max_length=64)
    access_token_expired_at = models.DateTimeField('Access Token 过期时间', null=True)

    def __str__(self):
        return f'user={self.user.username if self.user else None}, access_token={self.access_token}, ' \
               f'expired_at={self.access_token_expired_at.strftime() if self.access_token_expired_at else None}'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
