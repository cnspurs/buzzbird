from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.admin import User
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone

weibo = settings.WEIBO


def index(request):
    return render(request, 'index.html')


def oauth(request):
    code = request.GET.get('code')

    if code:
        access_token = weibo.get_access_token(code)
        weibo_uid = weibo.get_uid(access_token)

        user = User.objects.filter(username=weibo_uid).first()
        if user:
            login(request, user)
            return redirect('/')

        else:
            user = User.objects.create_user(weibo_uid)
            user.set_unusable_password()
            user.profile.access_token = access_token
            user.profile.access_token_expired_at = timezone.now()
            user.profile.weibo_uid = weibo_uid
            user.save()

            login(request, user)
            return redirect('/')

    return JsonResponse({'error': 'missing code'})


def logout_view(request):
    logout(request)
    return redirect('/')
