import datetime as dt
import logging

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.admin import User
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone

logger = logging.getLogger("core.views")
weibo = settings.WEIBO


def index(request):
    return render(request, "index.html")


def oauth(request):
    code = request.GET.get("code")

    if code:
        data = weibo.get_access_token(code)
        access_token = data["access_token"]
        expires_in = data["expires_in"]

        weibo_uid = weibo.get_uid(access_token)

        user = User.objects.filter(username=weibo_uid).first()
        if user:
            user.profile.access_token = access_token
            user.profile.access_token_expired_at = timezone.now() + dt.timedelta(
                seconds=expires_in
            )
            login(request, user)
            return redirect("/")

        else:
            user = User.objects.create_user(weibo_uid)
            user.set_unusable_password()
            user.profile.access_token = access_token
            user.profile.access_token_expired_at = timezone.now() + dt.timedelta(
                seconds=expires_in
            )
            user.profile.weibo_uid = weibo_uid
            user.save()

            login(request, user)
            return redirect("/")

    return JsonResponse({"error": "missing code"})


def logout_view(request):
    logout(request)
    return redirect("/")
