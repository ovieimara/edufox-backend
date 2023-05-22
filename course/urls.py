from django.urls import path, include
from .views import (ListCreateAPIGrades, UpdateAPIGrades, ListCreateAPISubject, ListCreateAPIComment, UpdateAPIComment,
                    UpdateAPISubject, ListCreateAPILecturer, UpdateAPILecturer, ListCreateAPIRate,
                    UpdateAPIRate, ListCreateAPIInteraction, UpdateAPIInteraction,
                    ListCreateAPIVideo, UpdateAPIVideo, ListCreateAPIResolution,
                    ListDashboardAPI, ListCreateUpdateAPILesson, ListCreateUpdateAPITopic, ListDashboardLessonsAPI)
from djoser.views import UserViewSet
from django.views.decorators.cache import cache_page


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
    # path('interaction_types', ListCreateAPIInteractionType.as_view(), name='interaction_types-list'),
    # path('interaction_types/<pk>', UpdateAPIInteractionType.as_view(), name='interaction_type-detail'),
    path('interactions', ListCreateAPIInteraction.as_view(),
         name='interactions-list'),
    path('interactions/<pk>', UpdateAPIInteraction.as_view(),
         name='interaction-detail'),
    # path('seeks', ListCreateAPISeek.as_view(), name='seeks-list'),
    # path('seeks/<pk>', ListCreateAPISeek.as_view(), name='seek-detail'),
    # path('assessments', ListCreateAPIComment.as_view(), name='assessments-list'),
    # path('assessments/<pk>', UpdateAPIComment.as_view(), name='assessment-detail'),
    path('videos', ListCreateAPIVideo.as_view(), name='videos-list'),
    path('videos/<pk>', UpdateAPIVideo.as_view(), name='video-detail'),
    path('videos/topics/<int:subject>',
         ListCreateAPIVideo.as_view(), name='videos-list'),
    path('resolutions', ListCreateAPIResolution.as_view(), name='resolutions-list'),
    path('resolutions/<pk>', ListCreateAPIResolution.as_view(),
         name='resolution-detail'),
    path('dashboard', cache_page(60 * 15)
         (ListDashboardAPI.as_view()), name='dashboard-list'),
    path('dashboard/<int:subject>/<int:grade>',
         cache_page(60 * 15)(ListDashboardAPI.as_view()), name='dashboard-detail'),
    path('dashboard/topics/<int:pk>/<int:grade>',
         cache_page(60 * 15)(ListDashboardLessonsAPI.as_view()), name='dashboard-topics-list'),
    path('dashboard/lessons/<int:lesson>/<int:grade>',
         cache_page(60 * 15)(ListDashboardLessonsAPI.as_view()), name='dashboard-lessons-list'),
    path('lessons', ListCreateUpdateAPILesson.as_view(), name='lessons-list'),
    path('lessons/<pk>', ListCreateUpdateAPILesson.as_view(), name='lessons-detail'),
    path('lessons/topics/<int:subject>',
         ListCreateUpdateAPILesson.as_view(), name='lesson-subject-detail'),
    path('topics', ListCreateUpdateAPITopic.as_view(), name='topics-list'),
    path('topics/<pk>', ListCreateUpdateAPITopic.as_view(), name='topic-detail'),

]
