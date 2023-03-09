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
                'phone_number' : '+23407048536974',
                # 'grade': self.grade.pk,
                # 'age': 6,
                # 'gender' : 'male',
                # 'image_url' : '',
                # 'name_institution' : 'uniben',
                # 'country': self.country.pk,
        }

    # def test_signup(self):
        
    #     response = self.client.post(reverse('api:user-list'), data=self.data)
    #     # print('FIRST', response.json())
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #     user = User.objects.get(username='+23407048536974')
    #     self.assertEqual(user.username, '+23407048536974')
    #     self.assertEqual(user.email, 'imaraovie@gmail.com')

    def test_student_list_create_api_view(self):
        response = self.client.post(reverse('student:student-list'), data=self.data, format='json')
        instance = response.json()
        if instance and instance.get('phone_number') and not settings.FILE:
            otp = input("input otp: ")
            data = {
                "otp" : otp,
                "username" : instance.get('phone_number'),
                'email': instance.get('user').get('email')
            }
            response = self.client.post(reverse('student:otp-activate', kwargs=data))
            # print(response.json())
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            user = response.json()
            print('user', user)
            self.assertEqual(user.get('email'), 'imaraovie@gmail.com')
            self.assertEqual(user.get('username'), '+23407048536974')
            instance = User.objects.get(username=user.get('username'))
            self.assertEqual(instance.is_active, True)

            #test user exists
            response = self.client.post(reverse('student:student-list'), data=self.data, format='json')
            self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

            #test update newly registered student
            student = {
                    'first_name': 'test',
                    'last_name': 'user',
                    'username': '+23407048536974',
                    'email': 'imaraovie@gmail.com',
                    'password': 'password@123A',
                    'phone_number' : '+23407048536974',
                    'grade': 'Grade 1',
                    'age': 6,
                    'gender' : 'male',
                    'image_url' : '',
                    'name_institution' : 'uniben',
                    # 'country': self.country.pk,
            }
            response = self.client.post(reverse('api:login'), data={
                'username': '+23407048536974',
                'password': 'password@123A',
            })
            # print(response.json())
            token = response.json()['auth_token']
            self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

            response = self.client.patch(reverse('student:student-list'), data=student, format='json')
            # print('response_stu', response.json())
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            user = response.json()
            self.assertEqual(user.get('user').get('email'), 'imaraovie@gmail.com')
            self.assertEqual(user.get('user').get('username'), '+23407048536974')
            self.assertEqual(user.get('grade'), student.get('grade'))
        