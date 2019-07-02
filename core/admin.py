from django.contrib import admin
from core.models import *


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'access_token', 'access_token_expired_at')


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('english_name', 'chinese_name', 'twitter_id')


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    pass
