from django.urls import path, include
from djoser.views import UserViewSet
from .views import (ActivateUser, CleanUpAPIViewStudent, ListCreateAPIEarnView, StudentListCreateAPIView,
                    ActivatePhoneNumberAPIView, ListCreateAPICountry, RetrieveUpdateAPIViewStudent, StudentViewSet, createPhoneVerificationOTP,
                    verifyOTPCode, StudentLogin)

app_name = 'student'

urlpatterns = [
    # path('', include('djoser.urls')),
    # path('', include('djoser.urls.authtoken')),

    path('me', CleanUpAPIViewStudent.as_view(), name='students-delete'),
    path('otp', createPhoneVerificationOTP, name='otp-activate'),
    path('login', StudentLogin, name='students-login'),

    # path('activate/<uid>/<token>', ActivateUser.as_view({'get': 'activation', 'post': 'activation'}), name='activate'),
    path('activate', verifyOTPCode, name='otp-activate'),
    path('earn', ListCreateAPIEarnView.as_view(), name="earn-list"),
    path('update/<phone_number>',
         RetrieveUpdateAPIViewStudent.as_view(), name='student-detail'),
    path('country', ListCreateAPICountry.as_view(), name='country-list'),
    path('country/<int:pk>', ListCreateAPICountry.as_view(), name='country-detail'),
    path('reset_password', StudentViewSet.as_view(
        {'post': 'reset_password'}), name='user-reset-password'),
    path('reset_password_confirm', StudentViewSet.as_view(
        {'post': 'reset_password_confirm'}), name='user-reset-password-confirm'),

    path('', StudentListCreateAPIView.as_view(), name='students-list'),
    path('<username>', ActivatePhoneNumberAPIView.as_view(),
         name='student-activate'),
    # do not place any api under this last api, the last api will consume all other urls
    #     path('thisuser', DeactivateUser().as_view(), name='this-user-update'),
]
