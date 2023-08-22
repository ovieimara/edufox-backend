from genericpath import exists
import logging
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
from rest_framework.exceptions import ValidationError

from edufox.views import printOutLogs
from subscribe.models import Discount
from .permissions import IsStaffEditorPermission
from django.contrib.auth.models import User
from .serializers import EarnSerializer, ReferralSerializer, StudentSerializer, UserSerializer, CountrySerializer
from .models import Earn, Referral, Student, TempStudent, Grade, Country
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
from django.db.models import Q


# import socket
address = ["127.0.0.1:8000", "0.0.0.1:8000"]
# HOST = config('HOST')
client = APIClient()


@api_view(['POST'])
@permission_classes([AllowAny])
def StudentLogin(request, *args, **kwargs):
    '''
    This API is for OTP verification, it supports GET and POST methods. e.g 
    '/api/v1/student/activate/<otp>/<username>/<email>'
    '''
    query = request.data
    country_code = query.get('country_code')
    password = query.get('password')
    username = query.get('username')

    username = createPhoneNumber(country_code, username)

    data = {
        'username': username,
        'password': password
    }
    # logging.info(f"LOGIN DATA: {data}")
    login_url = "api/v1/auth/token/login"
    response = requests.post(createUrl(login_url), data=data)
    response = response.json() if response.json() else response
    return Response(response)


def createPhoneNumber(countryCode, phoneNumber):
    number_size = len(phoneNumber)
    if countryCode and number_size:
        return f"{countryCode}{phoneNumber[1:]}" if int(phoneNumber[:1]) == 0 else f"{countryCode}{phoneNumber}"

    return phoneNumber if number_size and phoneNumber[:1] == '+' else None


class StudentListCreateAPIView(generics.ListCreateAPIView, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    """
    Signup a new student, with a POST request. user receives a verification otp via email and sms, after verification they are activated.
    After user verifies via OTP, the new student records are updated via patch
    """
    queryset = Student.objects.all().order_by('pk')
    serializer_class = StudentSerializer
    ordering_fields = ['pk']
    permission_classes = [AllowAny]

    # def destroy(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     if instance:
    #         auth_token = request.auth
    #         current_password = request.data.get('current_password')
    #         if current_password:
    #             response = {}
    #             data = {
    #                 'current_password': current_password
    #             }
    #             if django_settings.DOMAIN == "127.0.0.1:8000":
    #                 client.credentials(
    #                     HTTP_AUTHORIZATION=f"Token {auth_token}")
    #                 response = client.delete(reverse('api:user-me'), data=data)
    #             else:
    #                 headers = {'Authorization': f"Token {auth_token}"}
    #                 response = requests.delete(
    #                     getUrl('user-me', "api"), data=data, headers=headers)

    #             print('delete: ', response.json())
    #             if response and response.status_code == status.HTTP_204_NO_CONTENT:
    #                 self.perform_destroy(instance)
    #                 return Response(status=status.HTTP_204_NO_CONTENT)

    #     return Response(status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        auth_token = request.auth
        current_password = request.data.get('current_password')

        if not current_password:
            raise ValidationError("Current password is required for deletion.")

        response = {}
        data = {
            'current_password': current_password
        }

        if django_settings.DOMAIN == "127.0.0.1:8000":
            client.credentials(HTTP_AUTHORIZATION=f"Token {auth_token}")
            response = client.delete(reverse('api:user-me'), data=data)
        else:
            headers = {'Authorization': f"Token {auth_token}"}
            response = requests.delete(
                getUrl('user-me', "api"), data=data, headers=headers)

        if response and response.status_code == status.HTTP_204_NO_CONTENT:
            # Call the parent class method to perform the actual deletion
            return super().destroy(request, *args, **kwargs)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        email = password = phone_number = student = None
        data = {}
        try:
            email = request.data.pop('email', None)
            password = request.data.pop('password', None)
            country_code = request.data.get('country_code')
            phone_number = request.data.get('phone_number')
            phone_number = createPhoneNumber(country_code, phone_number)
            # print('email: ', email, password, phone_number)

            response = {}
        except Exception as ex:
            print('request.data error', ex)

        if email and password and phone_number:
            data = {
                "username": phone_number,
                "email": email,
                "password": password,
            }
            # print('DATA1: ', data)
        try:
            student = Student.objects.get(phone_number=phone_number)
        except Student.DoesNotExist as ex:
            print('student object error: ', ex)

        if student:
            message = {"is_active": student.user.is_active,
                       "message": "mobile already exists"}
            return Response(message, status.HTTP_409_CONFLICT)

        if data:
            resp = {}
            response = {}
            try:
                if django_settings.DOMAIN == "127.0.0.1:8000":
                    resp = client.post(reverse('api:user-list'), data=data)
                    response = resp.json()
                    if resp and resp.status_code == status.HTTP_400_BAD_REQUEST:
                        return Response(response)
                else:
                    resp = requests.post(getUrl('user-list', "api"), data=data)
                    # printOutLogs('USERS: ', resp)
                if resp and resp.status_code == status.HTTP_400_BAD_REQUEST:
                    return Response(resp.json())

                # if django_settings.DOMAIN not in address :
                # print('RESP: ', resp)
                if resp and resp.status_code == status.HTTP_201_CREATED:
                    response = resp.json()
                    # print(response)

                    if not django_settings.FILE:
                        pass
                        # createOTP(phone_number)
                        # emailOTP(email)
                    return super().create(request, *args, **kwargs)

                return Response(response)
            except Exception as exception:
                print('exception: ', exception)

        return Response(status.HTTP_400_BAD_REQUEST)

    # def get_object(self):
    #     student = None
    #     try:
    #         if self.request and self.request.user.is_authenticated:
    #             user = self.request.user
    #             student = get_object_or_404(Student, user=user)
    #     except Student.DoesNotExist as ex:
    #         print("Student Object Error: ", ex)

    #     return student

    def get_object(self):
        student = None
        try:
            user = self.request.user
            print('user: ', user)
            if user and user.is_authenticated:
                student = user.profile
        except Student.DoesNotExist as ex:
            print("Student Object Error: ", ex)

        return student

    def get(self, request, *args, **kwargs):
        user = request.user
        if not user.is_staff:
            student = self.get_object()
            serializer = self.get_serializer(student)
            return Response(serializer.data)

        return super().get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        return self.update(request, *args, partial=partial, **kwargs)

    def patch(self, request, *args, **kwargs):
        params = {}
        partial = kwargs.pop('partial', True)
        instance = self.get_object()

        user = request.user
        # print(f"instance: {instance.my_referral}")

        if instance:
            data = request.data
            grade = data.pop('grade', None)
            first_name = data.pop('first_name', '')
            last_name = data.pop('last_name', '')
            referral = data.pop('referral', '')

            referral_data = createReferral(referral)
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

            serializer = self.get_serializer(
                instance, data=data, partial=partial)
            serializer.is_valid(raise_exception=True)

            if referral_data and isinstance(referral_data, Referral):
                serializer.save(grade=grade, referral=referral_data)
            else:
                serializer.save(grade=grade)

            if user.is_authenticated:
                user.first_name = first_name
                user.last_name = last_name
                user.save()

            return Response(serializer.data)

        return Response({"message": 'anonymous user'}, status.HTTP_403_FORBIDDEN)

        # return Response({"message": "NoneType object - user likely anonymous"}, status.HTTP_404_NOT_FOUND)


def createReferral(referral):
    # print(referral)
    data = {}
    if referral:
        student_instance = earn_queryset = discount_queryset = ''
        try:
            student_instance = Student.objects.get(
                my_referral__iexact=referral)
        except Student.DoesNotExist as ex:
            logging.error(f"Student error: {ex}")
            student_instance = Student.objects.none()

        if student_instance:
            try:
                earn_queryset = Earn.objects.filter(user=student_instance.user)

            except Earn.DoesNotExist as ex:
                logging.error(f"Earn error: {ex}")
                earn_queryset = Earn.objects.none()
            except Exception as ex:
                logging.error(f"Earn error2: {ex}")

        if student_instance:
            try:
                # Check if a Discount exists with the username or referral_code
                discount_queryset = Discount.objects.filter(
                    Q(name=student_instance.user.username) |
                    Q(name=student_instance.my_referral)
                )
            except Discount.DoesNotExist as ex:
                logging.error(f"Discount: {ex}")
                discount_queryset = Discount.objects.none()
            except Exception as ex:
                logging.error(f"Discount error: {ex}")

        if student_instance:
            data = {
                "user": student_instance.user.pk if student_instance else 1,
                "code": referral,
                "status": "active",
                "earn": earn_queryset.first() if earn_queryset and earn_queryset.exists() else 1,
                "discount": discount_queryset.first() if discount_queryset and discount_queryset.exists() else 1
            }
        try:
            serializer = ReferralSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            data = serializer.save()
        except Exception as ex:
            logging.info(f"ReferralSerializer error {ex}")

    return data


class CleanUpAPIViewStudent(generics.DestroyAPIView):
    queryset = Student.objects.all().order_by('pk')
    serializer_class = StudentSerializer
    permission_classes = [AllowAny]

    # def get_object(self):
    #     student = None
    #     try:
    #         if self.request and self.request.user.is_authenticated:
    #             user = self.request.user
    #             print('user:', user)
    #             student = get_object_or_404(Student, user=user.username)
    #     except Student.DoesNotExist as ex:
    #         logging.error("Student Object Error: ", ex)

    #     return student

    def get_object(self):
        student = ''
        try:
            user = self.request.user
            print('user: ', user)
            if user and user.is_authenticated:
                student = user.profile
                print(student)
        except Student.DoesNotExist as ex:
            print("Student Object Error: ", ex)

        return student

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:
            auth_token = request.auth
            current_password = request.data.get('current_password')
            print("current_password: ", current_password)
            if not current_password:
                raise ValidationError(
                    "Current password is required for deletion.")

            response = {}
            data = {
                'current_password': current_password
            }
            if django_settings.DOMAIN == "127.0.0.1:8000":
                client.credentials(
                    HTTP_AUTHORIZATION=f"Token {auth_token}")
                response = client.delete(reverse('api:user-me'), data=data)
            else:
                headers = {'Authorization': f"Token {auth_token}"}
                response = requests.delete(
                    getUrl('user-me', "api"), data=data, headers=headers)

            print('delete: ', response)
            if response and response.status_code == status.HTTP_204_NO_CONTENT:
                self.perform_destroy(instance)
                return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status.HTTP_400_BAD_REQUEST)


class RetrieveUpdateAPIViewStudent(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all().order_by('pk')
    serializer_class = StudentSerializer
    lookup_field = 'phone_number'
    # permission_classes = [AllowAny]

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
            # If OTP is authentic
        if True:
            logging.info(f"server: {django_settings.DOMAIN}")
            url = getUrl('student-activate', "student", data)
            if django_settings.DOMAIN == "127.0.0.1:8000":
                return client.put(url)

            result = requests.put(url)
            # print(result.json())
            return Response(result.json())
        # return Response(response, status.HTTP_400_BAD_REQUEST)

    return Response(response, status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def createPhoneVerificationOTP(request, *args, **kwargs):
    phone_number = request.data.get("phone_number")
    country_code = request.data.get("country_code")
    verify = ''
    state = status.HTTP_400_BAD_REQUEST

    phone_number = createPhoneNumber(country_code, phone_number)
    if phone_number:
        verify = createOTP(phone_number)
        if verify:
            state = status.HTTP_201_CREATED

    return Response(data={"message": verify}, status=state)


@api_view(['POST'])
@permission_classes([AllowAny])
def createEmailVerificationOTP(request, *args, **kwargs):
    email = request.data.get("email")
    state = status.HTTP_400_BAD_REQUEST
    verify = ''
    state = status.HTTP_400_BAD_REQUEST

    if email:
        response = emailOTP(email)
        if response.sid:
            state = status.HTTP_201_CREATED

    return Response(data={"message": response}, status=state)


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


# class DeactivateUser(generics.UpdateAPIView):
#     queryset = User.objects.all('pk')
#     serializer_class = UserSerializer

#     def partial_update(self, request, *args, **kwargs):
#         user = request.user
#         data = {}
#         if user and user.is_authenticated:
#             try:
#                 user_instance = self.get_queryset().get(user=user)
#                 serializer = self.get_serializer(
#                     user_instance, data={"is_active": False}, partial=True)
#                 serializer.is_valid(raise_exception=True)
#                 self.perform_update(serializer)
#                 data = serializer.data

#             except Student.DoesNotExist as ex:
#                 print('student does not exist error', ex)

#             except Exception as ex:
#                 print('exception error', ex)

#         return Response(data)


class ActivationEmail(email.ActivationEmail):
    template_name = 'activation.html'


class ConfirmationEmail(email.ConfirmationEmail):
    template_name = 'confirmation.html'


def updateActivatedUser(temp_user):

    email = get_user_email(temp_user)
    # print('TOKEN', email)
    temp_student = TempStudent.objects.filter(
        email=email, username=temp_user.username).first()
    user = User.objects.get(username=temp_user.username, email=email)
    if temp_student:
        data = {
            "phone_number": temp_student.phone_number,
            "gender": temp_student.gender,
            "age": temp_student.age,
            "image_url": temp_student.image_url,
            "registration_date": temp_student.registration_date,
            "last_updated": datetime.utcnow()
        }
        user.first_name = temp_student.first_name
        user.last_name = temp_student.last_name
        serialized_student = StudentSerializer(data=data)
        serialized_student.is_valid(raise_exception=True)
        serialized_student.save(user=user, grade=temp_student.grade)
        temp_student.delete()

        return serialized_student.data

    return dict


class CreateAPIUser(generics.CreateAPIView, mixins.UpdateModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        serializer.save(is_active=False)

    def patch(self, request, *args, **kwargs):
        user = request.user
        data = {}
        if user and user.is_authenticated:
            try:
                user_instance = self.get_queryset().get(username=user.username)
                serializer = self.get_serializer(
                    user_instance, data={"is_active": False}, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save(is_active=False)
                # self.perform_update(serializer)
                # data = serializer.data
                # print(serializer.data)
                data = {"message": 'User deleted'}

            except Student.DoesNotExist as ex:
                logging.error('student does not exist error', ex)

            except Exception as ex:
                print('exception error', ex)

        return Response(data, status.HTTP_204_NO_CONTENT)


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


class ListCreateAPIEarnView(mixins.CreateModelMixin, mixins.ListModelMixin,  mixins.RetrieveModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView):
    queryset = Earn.objects.all().order_by('pk')
    serializer_class = EarnSerializer
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


class ListCreateAPIReferralView(mixins.CreateModelMixin, mixins.ListModelMixin,  mixins.RetrieveModelMixin):
    queryset = Student.objects.all().order_by('pk')
    serializer_class = StudentSerializer
    lookup_field = 'pk'

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        referral_code = kwargs.get('referral_code')
        page = referral_queryset = ''
        user = request.user

        if referral_code and user.is_staff:
            # query_set = Student.objects.all().order_by('pk')
            student_queryset = self.get_queryset.filter(
                referral_code=referral_code)
            page = self.paginate_queryset(student_queryset)

            if page:
                serializer = StudentSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = StudentSerializer(student_queryset, many=True)

            return Response(serializer.data)
            # return self.retrieve(request, *args, **kwargs)
        # if user.is_staff:
        #     return self.list(request, *args, **kwargs)

        if user.is_authenticated and not user.is_staff:
            referral_queryset = self.get_queryset.filter(
                referral_code=user.my_referral_code)

        page = self.paginate_queryset(referral_queryset)

        if page:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(referral_queryset, many=True)
        return Response(serializer.data)


class StudentViewSet(UserViewSet):

    """
    Reset user password. To use phone number for reset, send phone number,
    do not send email and vice versa e.g to use email:
    request should contain email. {"email": 'abc@gmail.com'}
    """
    permission_classes = []

    # Override the password reset method
    def reset_password(self, request, *args, **kwargs):
        state = status.HTTP_400_BAD_REQUEST
        verify = {'detail': 'Invalid Phone Number'}
        user = ''

        phone_number = request.data.get('phone_number')
        email = request.data.get('email')
        country_code = request.data.get('country_code')

        if phone_number:
            phone_number = createPhoneNumber(country_code, phone_number)
            if not phone_number:
                return Response({'detail': 'Invalid Phone Number'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if phone_number:
                user = User.objects.get(username=phone_number)
            if email and not phone_number:
                user = User.objects.get(email__iexact=email)

        except User.DoesNotExist as ex:
            user = ''
            logging.error(f"User not found:, {ex}")
        except Exception as ex:
            user = ''
            logging.error(f"reset_password: {ex}")

        # if True:
        if user:
            if phone_number:
                verify = createOTP(user.username)
            if email and not phone_number:
                verify = emailOTP(email)

            if verify:
                state = status.HTTP_201_CREATED
        # print(verify)
        return Response(status=state)

    # Override the password reset confirm method

    def reset_password_confirm(self, request, *args, **kwargs):
        # Verify the OTP provided by the user
        user = ''
        otp = request.data.get('otp')
        password = request.data.get('password')
        phone_number = request.data.get('phone_number')
        email = request.data.get('email')
        country_code = request.data.get('country_code')

        if phone_number:
            phone_number = createPhoneNumber(country_code, phone_number)

        if not phone_number and not email:
            return Response({'detail': 'Invalid Phone Number/Email', "msg_code": 0}, status=status.HTTP_400_BAD_REQUEST)

        if not password:
            return Response({'detail': 'Invalid Password', "msg_code": 0}, status=status.HTTP_400_BAD_REQUEST)

        if phone_number:
            response = verifyOTP(otp, phone_number)
        if email and not phone_number:
            response = verifyEmail(otp, email)

        if response and response.status == OTP_APPROVED:
            # if True:
            # print(email, phone_number)
            try:
                if phone_number:
                    user = User.objects.get(username=phone_number)
                if email and not phone_number:
                    user = User.objects.get(email__iexact=email)

            except User.DoesNotExist as ex:
                logging.error(f"User not found:,{ex}")
                user = ''
            except Exception as ex:
                logging.error(f"reset_password:, {ex}")
                user = ''

            if user:
                user.set_password(password)
                user.save()
                return Response({'detail': 'Password reset successful', "msg_code": 1}, status=status.HTTP_200_OK)

            return Response({'detail': 'Invalid user', "msg_code": 0}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'detail': 'Invalid OTP', "msg_code": 0}, status=status.HTTP_400_BAD_REQUEST)


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
    name = f"{app}:{url}" if app else url
    return f"{protocol}://{host}{reverse(name, kwargs=data)}"


def createUrl(url):
    host = django_settings.DOMAIN
    protocol = django_settings.PROTOCOL

    return f"{protocol}://{host}/{url}"

# @api_view(['GET'])
# @permission_classes([AllowAny])
# def PrivacyPolicy(request, *args, **kwargs):
#     return render(request, 'privacy.html')
