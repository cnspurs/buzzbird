from django.contrib import admin
from core.models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'access_token', 'access_token_expired_at')
