from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import HttpResponsePermanentRedirect, get_object_or_404
from djoser.views import UserViewSet
from djoser import email
from django.http import Http404, HttpRequest
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
from notify.views import createOTP, verifyOTP, emailOTP, verifyEmail
from notify.constants import OTP_APPROVED
from .constants import country_codes

# import socket
address = ["127.0.0.1:8000", "0.0.0.1:8000"]
# HOST = config('HOST')
client = APIClient()
    
class StudentListCreateAPIView(generics.ListCreateAPIView, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    """
    Signup a new student, with a POST request. user receives a verification otp via email and sms, after verification they are activated.
    After user verifies via OTP, the new student records are updated via patch
    """
    queryset = Student.objects.all().order_by('phone_number')
    serializer_class = StudentSerializer
    ordering_fields = ['pk']
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        email = password = phone_number = user = None
        data = {}
        try:
            email = request.data.pop('email', None)
            password = request.data.pop('password', None)
            phone_number = request.data.get('phone_number')
            # print('email: ', email)
            response = {}
        except Exception as ex:
            print('request.data error', ex)

        if email and password and phone_number:
            data = {
                    "username" : phone_number,
                    "email" : email,
                    "password" : password,
                }
        try:
            user = Student.objects.get(phone_number=phone_number)
        except Student.DoesNotExist as ex:
             print('student object error: ', ex)
        
        if user:
            return Response({"message" : "User already exists"}, status.HTTP_409_CONFLICT)
        
        if data:
        
            try:
            
                if django_settings.DOMAIN == "127.0.0.1:8000":
                    response = client.post(reverse('api:user-list'), data=data)
                else:
                    response = requests.post(getUrl('user-list', "api"), data=data)
                    # response = Response(response.json())
                #if django_settings.DOMAIN not in address :
                # print(response.status_code)
                if response and response.status_code == status.HTTP_201_CREATED:
                    
                    # print('settings: ',dir(django_settings))
                    if not django_settings.FILE:
                        pass
                        # createOTP(phone_number)
                        #emailOTP(email)
                    return super().create(request, *args, **kwargs)
                
                return response
            except Exception as exception:
                print('exception: ', exception)


        return Response(status.HTTP_400_BAD_REQUEST)
    
            
        
    
    def get_object(self):
        student = None
        try:
            user = self.request.user
            # print('user: ', user)
            if user and not user.is_anonymous:
                student = user.profile
        except Student.DoesNotExist as ex:
            print("Student Object Error: ", ex)
        
        return student
    
    def put(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        return self.update(request, *args, partial=partial, **kwargs)

    def patch(self, request, *args, **kwargs):
        params = {}
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        if instance:
            data = request.data
            grade = data.pop('grade', None)
            if grade and type(grade) == str:
                params = {"name": grade}
            elif grade and type(grade) == int:
                params = {"pk": grade}
            if params:
                try:
                    grade = Grade.objects.get(**params)
                except Grade.DoesNotExist as ex:
                    grade = None
                    print('grade error: ', Http404, ex)
    
            serializer = self.get_serializer(instance, data=data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save(grade=grade)

            return Response(serializer.data)
        
        return Response({"message" : 'anonymous user'}, status.HTTP_403_FORBIDDEN)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:
            auth_token = request.auth
            current_password = request.data.get('current_password')
            if current_password:
                response = {}
                data = {
                        'current_password': current_password
                        }
                if django_settings.DOMAIN == "127.0.0.1:8000":
                    client.credentials(HTTP_AUTHORIZATION=f"Token {auth_token}")
                    response = client.delete(reverse('api:user-me'), data=data)
                else:
                    headers = {'Authorization': 'Token ' + auth_token}
                    response = requests.delete(getUrl('user-me', "api"), data=data, headers=headers)
                
                print('delete: ', response)
                if response and response.status_code == status.HTTP_204_NO_CONTENT:
                    self.perform_destroy(instance)
                    return Response(status=status.HTTP_204_NO_CONTENT)
            
        return Response(status.HTTP_400_BAD_REQUEST)
            
        # return Response({"message": "NoneType object - user likely anonymous"}, status.HTTP_404_NOT_FOUND)

class RetrieveUpdateAPIViewStudent(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all().order_by('pk')
    serializer_class = StudentSerializer
    lookup_field = 'phone_number'
    permission_classes = [AllowAny]

    def get_object(self):
        try:
            phone_number = self.request.data.get('phone_number')
            student = Student.objects.get(phone_number=phone_number)
            return student
        except Student.DoesNotExist:
            raise Http404


@api_view(['POST'])
@permission_classes([AllowAny])
def verifyOTPCode(request, *args, **kwargs):
    '''
    This API is for OTP verification, it supports GET and POST methods. e.g 
    '/api/v1/student/activate/<otp>/<username>/<email>'
    '''
    query = request.data
    # print('query: ', dir(request), query.get('email'))
    otp = query.get('otp')
    # print('otp: ', otp)
    username = query.get('username', '').strip('+')
    username = f"{'+'}{username.strip()}"
    email = query.get('email')
    print(username, email)
    data = {
       'username': username
    }
    response = {}
    sms_resp = {}
    email_response = {}
    if otp:
        if email:
            try:
                email_response = verifyEmail(otp, email)
            except Exception as ex:
                print('otp error: ', ex)
        if (email_response and email_response.status != OTP_APPROVED and username) or not email_response:
            try:
                sms_resp = verifyOTP(otp, username)
            except Exception as ex:
                print('otp error: ', ex)

        if email_response and email_response.status == OTP_APPROVED:
            response = email_response
        
        if sms_resp and sms_resp.status == OTP_APPROVED:
            response = sms_resp

        # print('email_response', email_response)
        # print('response', response.status)
        # if response and response.status == OTP_APPROVED:
        if True:
            url = getUrl('student-activate', "student", data)
            if django_settings.DOMAIN == "127.0.0.1:8000":
                return client.put(url)

            result = requests.put(url)
            return Response(result.json())
        # return Response(response, status.HTTP_400_BAD_REQUEST)
    
    return Response(response, status.HTTP_400_BAD_REQUEST)


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

        # data = {
        # 'phone_number': user.username
        # }
        # instance = {}
        # serializer_updated = updateActivatedUser(user)
        # url = getUrl('student-detail', "student", data)
        # if django_settings.DOMAIN == "127.0.0.1:8000":
        #     instance = client.patch(url)
        # else:
        #     instance = requests.put(url)
        
        # print('UPDATED USER: ', instance.json())
        if settings.SEND_CONFIRMATION_EMAIL:
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
