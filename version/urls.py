from django.urls import path, re_path, include
from student.views import apiViewManager
from student.views import CreateAPIUser
from student.views import StudentListCreateAPIView


# app_name = 'version'

urlpatterns = [
    path('v1/autocomplete/', include('autocomplete.urls')),
    path('v1/courses/', include('course.urls')),
    path('users', CreateAPIUser.as_view(), name="api-user"),
    path('v1/auth/', include('api.urls'), name='students-auth'),
    path('v1/subscribe/', include('subscribe.urls')),
    path('students', StudentListCreateAPIView.as_view(), name="students-list"),
    path('v1/students/', include('student.urls')),
    path('v1/assess/', include('assess.urls')),
    path('v1/contacts/', include('contact.urls')),
    path('v1/banners/', include('banner.urls')),
    path('v1/forms/', include('form.urls')),
    path('v1/file/', include('fileUpload.urls')),

]
