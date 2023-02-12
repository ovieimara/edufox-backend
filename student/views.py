from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import HttpResponsePermanentRedirect
from djoser.views import UserViewSet
from djoser import email
from django.http import HttpRequest
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from .permissions import IsStaffEditorPermission
from django.contrib.auth.models import User
from .serializers import StudentSerializer, TempStudentSerializer, UserSerializer
from .models import Student, TempStudent
import requests
from datetime import datetime
# from decouple import config
from djoser import signals, utils
from djoser.compat import get_user_email
from djoser.conf import settings
from django.conf import settings as django_settings
from rest_framework.test import APIClient

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
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')
        data = {
            "username" : username,
            "email" : email,
            "password" : password,
        }
        if django_settings.DOMAIN == "127.0.0.1:8000":
            response = client.post(reverse('student:user-list'), data=data)
        else:
            response = requests.post(getUrl('user-list', "student"), data=data)
        # print('RESPONSE: ', response)
        if response.status_code == status.HTTP_201_CREATED:
            super().perform_create(serializer)

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

        print('USER', user, get_user_email(user))

        signals.user_activated.send(
            sender=self.__class__, user=user, request=self.request
        )

        if settings.SEND_CONFIRMATION_EMAIL:
            context = {"user": user}
            to = [get_user_email(user)]
            settings.EMAIL.confirmation(self.request, context).send(to)
            updateActivatedUser(user)                

        return Response(status=status.HTTP_204_NO_CONTENT)

class ActivationEmail(email.ActivationEmail):
    template_name = 'activation.html'

class ConfirmationEmail(email.ConfirmationEmail):
    template_name = 'confirmation.html'

def updateActivatedUser(temp_user):
    # print('TOKEN', token)
    email = get_user_email(temp_user)
    temp_student = TempStudent.objects.filter(email=email, username=temp_user.username).first()
    user = User.objects.get(username=temp_user.username, email=email)
    if temp_student:
        data = {
            "phone_number": temp_student.phone_number,
            "grade" : temp_student.grade,
            "age" : temp_student.age,
            "image_url" : temp_student.image_url,
            "registration_date" : temp_student.registration_date,
            "last_updated" : datetime.utcnow()
        }
        user.first_name = temp_student.first_name
        user.last_name = temp_student.last_name
        serialized_student = StudentSerializer(data=data)
        serialized_student.is_valid(raise_exception=True)
        serialized_student.save(user=user)
        temp_student.delete()
    # print(serialized_student.data)

        # return serialized_student.data.get('user')
    
    # return dict
    # data = {
    #     'username' : username,
    #     'password' : user.password
    # }
    # response = requests.post(getUrl('login'), data=data)
    # print('RESPONSE TOKENS: ', response.json().get('auth_token'))
    # token = f"Token {response.json().get('auth_token')}" 
    # print("TOOOOKKENS: ", token)
    # header = {
    #     'Authorization': token
    # }
    # data = {'uid': uid}

    # return requests.post(getUrl('student-activate'), headers=header)


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


def getUrl(url, app):
    # print(settings.__dict__)
    host = django_settings.DOMAIN
    protocol = django_settings.PROTOCOL
    # host = "0.0.0.0:8000"
    # try:
    #     host, *_ = socket.gethostbyaddr(socket.gethostname())
    # except socket.herror:
    #    pass

    # protocol = 'https://' if request.is_secure() else 'http://'
    name = f"{app}:{url}"
    print('USER LIST', f"{protocol}://{host}{reverse(name)}")

    # return f"DOMAIN{reverse(name)}"
    return f"{protocol}://{host}{reverse(name)}"