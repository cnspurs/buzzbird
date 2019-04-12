from django.contrib import admin
from core.models import *


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'access_token', 'access_token_expired_at')


@admin.register(TwitterMember)
class TwitterMemberAdmin(admin.ModelAdmin):
    list_display = ('twitter_id', 'english_name', 'chinese_name')
    readonly_fields = ('twitter_id',)


@admin.register(InstagramMember)
class InstagramMemberAdmin(admin.ModelAdmin):
    pass


@admin.register(Instagram)
class InstagramAdmin(admin.ModelAdmin):
    pass
