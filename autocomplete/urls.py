from django.urls import path, re_path
from djoser.views import UserViewSet
from autocomplete.views import AutoComplete
# from django.views.decorators.cache import cache_page

from banner.views import ListCreateAPIBanner


app_name = 'autocomplete'

urlpatterns = [
    path('', AutoComplete.as_view(), name='autocomplete-list'),
    # path('banners/<pk>', ListCreateAPIBanner.as_view(), name='banners-detail'),
]
