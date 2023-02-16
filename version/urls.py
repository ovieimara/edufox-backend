from django.urls import path, re_path, include
from student.views import apiViewManager
from student.views import CreateAPIUser


# app_name = 'version'

urlpatterns = [
    path('v1/courses/', include('course.urls')),
    path('users', CreateAPIUser.as_view(), name="api-user"),
    path('v1/auth/', include('student.urls')),
]