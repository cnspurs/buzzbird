from django.urls import path
from django.contrib import admin
from core import views

urlpatterns = (
    path('', views.index),
    path('oauth', views.oauth),
    path('logout', views.logout_view, name='logout'),
    path('whosyourdaddy', admin.site.urls)
)
