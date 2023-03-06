from django.urls import path, include
from .views import (ListCreateUpdateAPITest, ListCreateUpdateAPIAssessment, 
                    ListCreateUpdateAPILevel)

app_name = 'assess'

urlpatterns = [
    path('tests', ListCreateUpdateAPITest.as_view(), name='tests-list'),
    path('tests/<pk>', ListCreateUpdateAPITest.as_view(), name='test-detail'),
    path('assess', ListCreateUpdateAPIAssessment.as_view(), name='assess-list'),
    path('assess/<pk>', ListCreateUpdateAPIAssessment.as_view(), name='assess-detail'),
    path('levels', ListCreateUpdateAPILevel.as_view(), name='levels-list'),
    path('levels/<pk>', ListCreateUpdateAPILevel.as_view(), name='level-detail'),
]