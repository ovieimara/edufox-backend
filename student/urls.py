from django.urls import path, include
from djoser.views import UserViewSet
from .views import (ActivateUser, StudentListCreateAPIView,
                    ActivatePhoneNumberAPIView, ListCreateAPICountry, RetrieveUpdateAPIViewStudent,
                    verifyOTPCode, StudentLogin)

app_name = 'student'

urlpatterns = [
    # path('', include('djoser.urls')),
    # path('', include('djoser.urls.authtoken')),
    path('login', StudentLogin, name='students-login'),
    # path('activate/<uid>/<token>', ActivateUser.as_view({'get': 'activation', 'post': 'activation'}), name='activate'),
    path('activate', verifyOTPCode, name='otp-activate'),
    path('<username>', ActivatePhoneNumberAPIView.as_view(),
         name='student-activate'),
    path('update/<phone_number>',
         RetrieveUpdateAPIViewStudent.as_view(), name='student-detail'),
    path('country', ListCreateAPICountry.as_view(), name='country-list'),
    path('country/<int:pk>', ListCreateAPICountry.as_view(), name='country-detail'),
    path('', StudentListCreateAPIView.as_view(), name='students-list'),


    # path('students/<str:username>/', UserUpdateAPIView.as_view(), name='user-update'),
]
