from django.urls import path, include
from djoser.views import UserViewSet

app_name = 'api'

urlpatterns = [
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
    path('students/', include('student.urls')),
]