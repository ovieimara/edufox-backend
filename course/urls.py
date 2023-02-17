from django.urls import path, include
from .views import (ListCreateAPIGrades, UpdateAPIGrades, ListCreateAPISubject, ListCreateAPIComment, UpdateAPIComment,
UpdateAPISubject, ListCreateAPILecturer, UpdateAPILecturer, ListCreateAPIRate, 
UpdateAPIRate, ListCreateAPIInteractionType, ListCreateAPIInteraction, 
ListCreateAPITest, ListCreateAPIAssessment, UpdateAPIInteractionType, 
UpdateAPIInteraction, UpdateAPITest, UpdateAPIAssessment)
from djoser.views import UserViewSet

app_name = 'course'

urlpatterns = [
    path('grades', ListCreateAPIGrades.as_view(), name='grades-list'),
    path('grades/<pk>', UpdateAPIGrades.as_view(), name='grade-detail'),
    path('subjects', ListCreateAPISubject.as_view(), name='subjects-list'),
    path('subjects/<pk>', UpdateAPISubject.as_view(), name='subject-detail'),
    path('lecturers', ListCreateAPILecturer.as_view(), name='lecturers-list'),
    path('lecturers/<pk>', UpdateAPILecturer.as_view(), name='lecturer-detail'),
    path('rates', ListCreateAPIRate.as_view(), name='rates-list'),
    path('rates/<pk>', UpdateAPIRate.as_view(), name='rate-detail'),
    path('comments', ListCreateAPIComment.as_view(), name='comments-list'),
    path('comments/<pk>', UpdateAPIComment.as_view(), name='comment-detail'),
    path('interaction_types', ListCreateAPIInteractionType.as_view(), name='interaction_types-list'),
    path('interaction_types/<pk>', UpdateAPIInteractionType.as_view(), name='interaction_type-detail'),
    path('interactions', ListCreateAPIInteraction.as_view(), name='interactions-list'),
    path('interactions/<pk>', UpdateAPIInteraction.as_view(), name='interaction-detail'),
    path('tests', ListCreateAPIComment.as_view(), name='tests-list'),
    path('tests/<pk>', UpdateAPIComment.as_view(), name='test-detail'),
    path('assessments', ListCreateAPIComment.as_view(), name='assessments-list'),
    path('assessments/<pk>', UpdateAPIComment.as_view(), name='assessment-detail'),
]