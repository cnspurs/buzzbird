from django.contrib import admin
from core.models import *


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'access_token', 'access_token_expired_at')


@admin.register(Member)
class InstagramMemberAdmin(admin.ModelAdmin):
    pass


@admin.register(Instagram)
class InstagramAdmin(admin.ModelAdmin):
    pass
