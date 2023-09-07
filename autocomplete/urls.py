from django.urls import path, re_path
from djoser.views import UserViewSet
from autocomplete.tasks import my_background_task
from autocomplete.views import AutoCompleteAPIView
# from django.views.decorators.cache import cache_page


app_name = 'autocomplete'

urlpatterns = [
    path('suggest', AutoCompleteAPIView.as_view(), name='autocomplete-list'),
    # path('tasks', my_background_task),
    # path('banners/<pk>', ListCreateAPIBanner.as_view(), name='banners-detail'),
]
