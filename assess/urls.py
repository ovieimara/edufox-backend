from django.urls import path, include
from .views import (APITestSize, ListCreateAPITest, UpdateAPITest, ListCreateAPIAssessment, UpdateAPIAssessment,
                    ListCreateUpdateAPILevel)
from django.views.decorators.cache import cache_page

app_name = 'assess'

urlpatterns = [
    # path('tests', cache_page(60 * 30)
    #      (ListCreateAPITest.as_view()), name='tests-list'),
    path('tests', ListCreateAPITest.as_view(), name='tests-list'),
    path('tests/<int:pk>', UpdateAPITest.as_view(), name='test-detail'),
    path('tests/lessons/<pk>', ListCreateAPITest.as_view(),
         name='test-lessons-detail'),
    path('tests/lessons/size/<pk>/', APITestSize.as_view(),
         name='test-lessons-size-detail'),
    path('assess', ListCreateAPIAssessment.as_view(), name='assess-list'),
    path('assess/<pk>', UpdateAPIAssessment.as_view(), name='assess-detail'),
    path('levels', ListCreateUpdateAPILevel.as_view(), name='levels-list'),
    path('levels/<pk>', ListCreateUpdateAPILevel.as_view(), name='level-detail'),
]
