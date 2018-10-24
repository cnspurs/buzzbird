from django.contrib import admin
from core.models import Profile
from core.models import TwitterMember


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'access_token', 'access_token_expired_at')


@admin.register(TwitterMember)
class TwitterMemberAdmin(admin.ModelAdmin):
    list_display = ('twitter_id', 'english_name', 'chinese_name')
    readonly_fields = ('twitter_id',)