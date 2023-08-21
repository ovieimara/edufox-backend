from django.urls import path, re_path
from djoser.views import UserViewSet
from autocomplete.views import AutoCompleteAPIView
# from django.views.decorators.cache import cache_page


app_name = 'autocomplete'

urlpatterns = [
    path('suggest', AutoCompleteAPIView.as_view(), name='autocomplete-list'),
    # path('banners/<pk>', ListCreateAPIBanner.as_view(), name='banners-detail'),
]
