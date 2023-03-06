from django.urls import path, include
from .views import (ActivateUser, StudentListCreateAPIView, 
ActivatePhoneNumberAPIView, ListCreateAPICountry, verifyOTPCode)
from djoser.views import UserViewSet

app_name = 'student'

urlpatterns = [
    # path('', include('djoser.urls')),
    # path('', include('djoser.urls.authtoken')),
    path('activate/<uid>/<token>', ActivateUser.as_view({'get': 'activation', 'post': 'activation'}), name='activate'),
    path('', StudentListCreateAPIView.as_view(), name='student-list'),
    path('activate/<otp>/<username>', verifyOTPCode, name='otp-activate'),
    path('<username>', ActivatePhoneNumberAPIView.as_view(), name='student-activate'),
    path('country', ListCreateAPICountry.as_view(), name='country-list'),
    path('country/<int:pk>', ListCreateAPICountry.as_view(), name='country-detail'),


    # path('students/activate', ActivateStudentAPIView.as_view(), name='student-activate'),
    # path('students/<str:username>/', UserUpdateAPIView.as_view(), name='user-update'),
]