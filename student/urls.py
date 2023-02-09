from django.urls import path, include
from .views import ActivateUser, StudentListCreateAPIView
from djoser.views import UserViewSet

app_name = 'student'

urlpatterns = [
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
    path('activate/<uid>/<token>', ActivateUser.as_view({'get': 'activation', 'post': 'activation'}), name='activate'),
    path('students', StudentListCreateAPIView.as_view(), name='student-list'),
    # path('students/activate', ActivateStudentAPIView.as_view(), name='student-activate'),
    # path('students/<str:username>/', UserUpdateAPIView.as_view(), name='user-update'),
]