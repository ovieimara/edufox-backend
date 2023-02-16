from django.urls import path, include
from .views import (ListCreateAPIGrades, UpdateAPIGrades, ListCreateAPISubject, 
UpdateAPISubject, ListCreateAPILecturer, UpdateAPILecturer)
from djoser.views import UserViewSet

app_name = 'course'

urlpatterns = [
    path('grades', ListCreateAPIGrades.as_view(), name='grades-list'),
    path('grades/<pk>', UpdateAPIGrades.as_view(), name='grades-list'),
    path('subjects', ListCreateAPISubject.as_view(), name='grades-list'),
    path('subjects/<pk>', UpdateAPISubject.as_view(), name='grades-list'),
    path('lecturers', ListCreateAPILecturer.as_view(), name='grades-list'),
    path('lecturers/<pk>', UpdateAPILecturer.as_view(), name='grades-list'),
]