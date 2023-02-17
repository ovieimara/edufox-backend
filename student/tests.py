from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient
from .models import TempStudent
from course.models import Grade

User = get_user_model()

class SignupTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.data = {
                'first_name': 'test',
                'last_name': 'user',
                'username': 'testuser',
                'email': 'imaraovie@gmail.com',
                'password': 'testpassword@123A',
                'phone_number' : '08023168805',
                'grade': 'Grade 1',
                'age': 6,
                'gender' : 'male',
                'image_url' : '',
                'name_institution' : 'uniben'
        }
        Grade.objects.create(
            code='grade1', 
            name='Grade 1', 
            description='Grade 1'
        )

    def test_signup(self):

        response = self.client.post(reverse('student:user-list'), data=self.data)
        # print('FIRST', response.json())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(username='testuser')
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'imaraovie@gmail.com')

    def test_student_list_create_api_view(self):

        response = self.client.post(reverse('student:student-list'), data=self.data, format='json')
        print('resp', response.json())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TempStudent.objects.count(), 1)
        self.assertEqual(TempStudent.objects.get().username, 'testuser')
