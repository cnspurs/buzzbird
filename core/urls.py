from core import views
from django.urls import path

urlpatterns = (
    path("", views.index),
    path("oauth", views.oauth),
    path("logout", views.logout_view, name="logout"),
)
