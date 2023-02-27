from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import HttpResponsePermanentRedirect, get_object_or_404
from djoser.views import UserViewSet
from djoser import email
from django.http import HttpRequest
from rest_framework import generics, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.decorators import api_view, permission_classes
from .permissions import IsStaffEditorPermission
from django.contrib.auth.models import User
from .serializers import StudentSerializer, TempStudentSerializer, UserSerializer, CountrySerializer
from .models import Student, TempStudent, Grade, Country
import requests
from datetime import datetime
# from decouple import config
from djoser import signals, utils
from djoser.compat import get_user_email
from djoser.conf import settings
from django.conf import settings as django_settings
from rest_framework.test import APIClient
from notify.views import createOTP, verifyOTP
from notify.constants import OTP_APPROVED
from .constants import country_codes

# import socket

# HOST = config('HOST')
client = APIClient()
class StudentListCreateAPIView(generics.ListCreateAPIView):
    """
    Signup a new student, with a POST request. user receives a verification link, after verification they are activated.
    """
    queryset = TempStudent.objects.all()
    serializer_class = TempStudentSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        # username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')
        # grade = serializer.validated_data.get('grade')
        phone_number = serializer.validated_data.get('phone_number')
        country = serializer.validated_data.get('country')
        # print('country', country.name)
        # obj = Country.objects.get(name__iexact=country.name)
        obj = get_object_or_404(Country, name__iexact=country.name)
        # print(obj.code)
        phone = f"{obj.code}{phone_number}"
        data = {
            "username" : phone,
            "email" : email,
            "password" : password,
        }
        
        if django_settings.DOMAIN == "127.0.0.1:8000":
            response = client.post(reverse('student:user-list'), data=data)
        else:
            response = requests.post(getUrl('user-list', "student"), data=data)
        
        if response.status_code == status.HTTP_201_CREATED:
            # if grade:
            #     instance = Grade.objects.get(name=grade)
            #     print('instance', type(instance))
            #     serializer.save(grade=instance)
            createOTP(phone)
            return super().perform_create(serializer)

        return status.HTTP_400_BAD_REQUEST


# class TempStudentCreateAPIView(generics.ListCreateAPIView):
#     queryset = TempStudent.objects.all()
#     serializer_class = TempStudentSerializer

#     def perform_create(self, serializer):
#         if self.request.user:
#             serializer.validated_data.get()
#         return super().perform_create(serializer)
 
# class ActivateUser(UserViewSet):
#     def activation(self, request, *args, **kwargs):
#         # print(request.data)
#         new_request = HttpRequest()
#         for key, value in request.__dict__.items():
#             setattr(new_request, key, value)

#         new_request.method = 'POST'
#         uid = self.kwargs.get('uid')
#         token = self.kwargs.get('token')
#         new_request.data = {"uid": uid, "token": token}

#         response = super().activation(new_request, *args, **kwargs)
#         print('RESPONSE', response.status_code)
#         if response.status_code == status.HTTP_204_NO_CONTENT:
#             resp = updateActivatedUser(token, uid)
#             print('RESP', resp)

#         return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def verifyOTPCode(request, *args, **kwargs):
    otp = kwargs.get('otp')
    print('otp: ', otp)
    username = kwargs.get('username')
    data = {
       'username': username
    }
    
    if otp:
        response = verifyOTP(otp)
        if response.status == OTP_APPROVED:
            # print('DOMAIN', django_settings.DOMAIN)
            url = getUrl('student-activate', "student", data)
            if django_settings.DOMAIN == "127.0.0.1:8000":
               return client.put(url)

            return requests.put(url)
        return status.HTTP_401_UNAUTHORIZED
    
    return status.HTTP_400_BAD_REQUEST

class ActivatePhoneNumberAPIView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = [AllowAny]

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(is_active=True)
        signals.user_activated.send(
            sender=self.__class__, user=user, request=self.request
        )

        serializer_updated = updateActivatedUser(user)
        if settings.SEND_CONFIRMATION_EMAIL and serializer_updated:
            context = {"user": user}
            to = [get_user_email(user)]
            settings.EMAIL.confirmation(self.request, context).send(to)

        if getattr(user, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            user._prefetched_objects_cache = {}
        return Response(serializer.data)

class ActivateUser(UserViewSet):
    def activation(self, request, *args, **kwargs):
        new_request = HttpRequest()
        for key, value in request.__dict__.items():
            setattr(new_request, key, value)

        new_request.method = 'POST'
        uid = self.kwargs.get('uid')
        token = self.kwargs.get('token')
        new_request.data = {"uid": uid, "token": token}

        serializer = self.get_serializer(data=new_request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        user.is_active = True
        user.save()

        signals.user_activated.send(
            sender=self.__class__, user=user, request=self.request
        )
        serialized = updateActivatedUser(user)  
        if settings.SEND_CONFIRMATION_EMAIL and serialized:
            context = {"user": user}
            to = [get_user_email(user)]
            settings.EMAIL.confirmation(self.request, context).send(to)

        return Response(serialized, status=status.HTTP_204_NO_CONTENT)

class ActivationEmail(email.ActivationEmail):
    template_name = 'activation.html'

class ConfirmationEmail(email.ConfirmationEmail):
    template_name = 'confirmation.html'

def updateActivatedUser(temp_user):
    
    email = get_user_email(temp_user)
    # print('TOKEN', email)
    temp_student = TempStudent.objects.filter(email=email, username=temp_user.username).first()
    user = User.objects.get(username=temp_user.username, email=email)
    if temp_student:
        data = {
            "phone_number": temp_student.phone_number,
            "gender" : temp_student.gender,
            "age" : temp_student.age,
            "image_url" : temp_student.image_url,
            "registration_date" : temp_student.registration_date,
            "last_updated" : datetime.utcnow()
        }
        user.first_name = temp_student.first_name
        user.last_name = temp_student.last_name
        serialized_student = StudentSerializer(data=data)
        serialized_student.is_valid(raise_exception=True)
        serialized_student.save(user=user, grade=temp_student.grade)
        temp_student.delete()

        return serialized_student.data

    return dict

class CreateAPIUser(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        serializer.save(is_active=False)

@api_view(['GET'])
@permission_classes([IsStaffEditorPermission, IsAdminUser])
def apiViewManager(request, *args, **kwargs):
    if not request.user:
        return HttpResponsePermanentRedirect('/token/login')
    return HttpResponsePermanentRedirect('/')

class ListCreateAPICountry(mixins.CreateModelMixin, mixins.ListModelMixin,  mixins.RetrieveModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    lookup_field = 'pk'
    # permission_classes = [IsStaffEditorPermission]

    def get(self, request, *args, **kwargs):
        if kwargs.get('pk') is not None:
            return self.retrieve(request, *args, **kwargs)

        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not kwargs.get('pk') and request.user.is_staff:
            return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        if kwargs.get('pk') and request.user.is_staff:
            return self.update(request, *args, **kwargs)
        return None

    

    


# class ActivateStudentAPIView(generics.ListCreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = StudentSerializer
#     lookup_field = 'username'
#     authentication_classes = []
#     # permission_classes = [AllowAny]

#     def perform_create(self, serializer):
#         # requests.post(getUrl('user-list'), data=serializer.validated_data)
#         # print('USER22', self.request.user.username)
#         if self.request.user.is_active:
#             temp_student = TempStudent.objects.filter(username = self.request.user.username).first()
#             data = {
#                 "user" : self.request.user,
#                 "phone_number": temp_student.phone_number,
#                 "grade" : temp_student.grade,
#                 "age" : temp_student.age,
#                 "image_url" : temp_student.image_url,
#                 "registration_date" : temp_student.registration_date,
#                 "last_updated" : datetime.utcnow()
#                 }
#             serialized_student = StudentSerializer(data=data)
#             serialized_student.is_valid(raise_exception=True)
#             serialized_student.save()
#             temp_student.delete()


def getUrl(url, app, data=None):
    if not data:
        data = {}
    host = django_settings.DOMAIN
    protocol = django_settings.PROTOCOL
    name = f"{app}:{url}"
    return f"{protocol}://{host}{reverse(name, kwargs=data)}"
