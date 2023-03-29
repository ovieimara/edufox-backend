import json
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient
import os

User = get_user_model()

class SignupTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            is_staff=True,
            username='+23407048536974', 
            email='testuser@example.com', 
            password='password@123A'
        )
        self.user.is_staff=True

        self.data = {
            'email': 'imaraovie@gmail.com',
            'password': 'password@123A',
            'phone_number' : '+23407048536974',

        }

    def test_BillingProduct_list_create_api_view(self):
        print(reverse('students-list'))
        
        response = self.client.post(reverse('api:login'), data={
            'username': '+23407048536974',
            'password': 'password@123A',
        })
        data = {
            'name' : 'monthly',
            'product_id': 'monthly',
            'platform': 'ios'
        }
        # print('GRADE: ', self.grade, type(self.grade))
        token = response.json()['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        response = self.client.post(reverse('subscribe:products-list'), data=data, format='json')
        print('response', response.json())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # user = response.json()
        # self.assertEqual(user.get('user').get('email'), 'imaraovie@gmail.com')
        # self.assertEqual(user.get('user').get('username'), '+23407048536974')
        # self.assertEqual(user.get('grade'), 'Grade 1')

        # #test deletion of user
        # self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.get(reverse('subscribe:products-list'))
        print('GET PRODUCTS: ', response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    