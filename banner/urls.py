from django.urls import path, re_path
from djoser.views import UserViewSet
# from django.views.decorators.cache import cache_page

from banner.views import ListCreateAPIBanner


app_name = 'banner'

urlpatterns = [
    path('', ListCreateAPIBanner.as_view(), name='banners-list'),
    path('banners/<pk>', ListCreateAPIBanner.as_view(), name='banners-detail'),
]
