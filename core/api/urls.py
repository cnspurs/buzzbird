from django.urls import include, path

urlpatterns = [
    path('v1/', include('core.api.v1.urls'))
]
