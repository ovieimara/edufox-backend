from django.urls import path, include
from .views import (ListCreateAPITest, UpdateAPITest, ListCreateAPIAssessment, UpdateAPIAssessment,
                    ListCreateUpdateAPILevel)
from django.views.decorators.cache import cache_page

app_name = 'assess'

urlpatterns = [
    path('tests', cache_page(60 * 30)
         (ListCreateAPITest.as_view()), name='tests-list'),
    path('tests/<pk>', UpdateAPITest.as_view(), name='test-detail'),
    path('assess', ListCreateAPIAssessment.as_view(), name='assess-list'),
    path('assess/<pk>', UpdateAPIAssessment.as_view(), name='assess-detail'),
    path('levels', ListCreateUpdateAPILevel.as_view(), name='levels-list'),
    path('levels/<pk>', ListCreateUpdateAPILevel.as_view(), name='level-detail'),
]
