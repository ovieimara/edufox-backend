import json
import logging
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient
from .models import TempStudent
from course.models import Grade
from .models import Country
import os
from django.conf import settings

User = get_user_model()


class SignupTestCase(TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.INFO)
        self.client = APIClient()
        self.grade = Grade.objects.create(
            code='grade1',
            name='Grade 1',
            description='Grade 1'
        )
        self.country = Country.objects.create(
            code='+234',
            name='Nigeria',
        )
        self.data = {
            # 'first_name': 'test',
            # 'last_name': 'user',
            # 'username': '+23407048536974',
            'email': 'imaraovie@gmail.com',
            'password': 'password@123A',
            'phone_number': '+23407048536974',
            # 'grade': self.grade.pk,
            # 'age': 6,
            # 'gender' : 'male',
            # 'image_url' : '',
            # 'name_institution' : 'uniben',
            # 'country': self.country.pk,
        }

    # def test_verifyOTPCode(self):
        # data = {

        #     "otp" : '1234',
        #     "username" : "+23407048536974",
        #     'email': "imaraovie@gmail.com"
        # }
        # print(reverse('student:otp-activate'))
        # response = self.client.post(reverse('student:otp-activate'), data=data)
        # print(response.json())

    # def test_signup(self):

    #     response = self.client.post(reverse('api:user-list'), data=self.data)
    #     # print('FIRST', response.json())
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #     user = User.objects.get(username='+23407048536974')
    #     self.assertEqual(user.username, '+23407048536974')
    #     self.assertEqual(user.email, 'imaraovie@gmail.com')

    def test_student_list_create_api_view(self):
        print(reverse('students-list'))
        response = self.client.post(
            reverse('students-list'), data=self.data, format='json')
        instance = response.json()
        # print('instance: ', instance)
        if instance and instance.get('phone_number') and not settings.FILE:
            otp = input("input otp: ")
            data = {
                # "otp" : otp,
                # "username" : instance.get('phone_number'),
                # 'email': instance.get('user').get('email')
                "otp": otp,
                "username": "+23407048536974",
                'email': "imaraovie@gmail.com"
            }
            # print('URL: ', reverse('student:otp-activate', kwargs=data))
            # url = f"/api/v1/students/{otp}/{instance.get('phone_number')}/{instance.get('user').get('email')}"
            # response = self.client.post(url)
            response = self.client.post(
                reverse('student:otp-activate'), data=data, format='json')
            # print('ACTIVATE RESPONSE', response.json())
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            user = response.json()
            # print('user', user)
            self.assertEqual(user.get('email'), 'imaraovie@gmail.com')
            self.assertEqual(user.get('username'), '+23407048536974')
            instance = User.objects.get(username=user.get('username'))
            self.assertEqual(instance.is_active, True)

            # test user exists
            response = self.client.post(
                reverse('students-list'), data=self.data, format='json')
            self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

            # test update newly registered student
            student = {
                'first_name': 'test',
                'last_name': 'user',
                'username': '+23407048536974',
                'email': 'imaraovie@gmail.com',
                'password': 'password@123A',
                'phone_number': '+23407048536974',
                'grade': self.grade.pk,
                'age': 6,
                'dob': '2023-07-19',
                'gender': 'male',
                'image_url': '',
                'name_institution': 'uniben',
                # 'country': self.country.pk,
            }

            login_response = self.client.post(reverse('student:students-login'), data={
                'username': '08023168805',  # use a valid registered number
                'password': 'password',
                'country_code': '+234'
            }, format='json')
            # token = login_response.json()
            # logging.info(f"{login_response.json()}")
            self.assertIsNotNone(login_response.json().get('auth_token'))

            login_response = self.client.post(reverse('student:students-login'), data={
                'username': '8023168805',
                'password': 'password',
                'country_code': '+234'
            })
            self.assertIsNotNone(login_response.json().get('auth_token'))

            response = self.client.post(reverse('api:login'), data={
                'username': '+23407048536974',
                'password': 'password@123A',
            })
            # print('GRADE: ', self.grade, type(self.grade))
            token = response.json()['auth_token']
            self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

            # self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

            # # print('GRADE: ', self.grade, type(self.grade))
            # token = response.json()
            # self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

            response = self.client.patch(
                reverse('students-list'), data=student, format='json')
            # print('response_stu', response.json())
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            user = response.json()
            self.assertEqual(user.get('user').get(
                'email'), 'imaraovie@gmail.com')
            self.assertEqual(user.get('user').get(
                'first_name'), data.get('first_name'))
            self.assertEqual(user.get('user').get(
                'last_name'), data.get('last_name'))
            self.assertEqual(user.get('user').get(
                'username'), '+23407048536974')
            self.assertEqual(user.get('grade'), self.grade.pk)

            # test deletion of user
            # self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
            # response = self.client.delete(reverse('students-list'), data={
            #     'current_password': 'password@123A',
            # })
            # # print('DELETE: ', response)
            # self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
