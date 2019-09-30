from django.contrib import admin
from core.models import *


def make_archived(modeladmin, request, queryset):
    queryset.update(archived=True)


def make_unarchived(modeladmin, request, queryset):
    queryset.update(archived=False)


make_archived.short_description = 'Archive selected members'
make_unarchived.short_description = 'Unarchive selected members'


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'access_token', 'access_token_expired_at')


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'archived',
        'english_name',
        'chinese_name',
        'twitter_id',
        'instagram_id',
    )
    actions = [make_archived, make_unarchived]


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'is_buzzbird',
        'is_discourse',
        'is_video',
        'type',
        'user',
        'title',
        'link',
        'collected_at',
        'created_at',
        'status_id',
    )
