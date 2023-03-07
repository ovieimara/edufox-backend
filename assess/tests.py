from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient
from course.models import Grade, Subject
from .models import Level, Test

User = get_user_model()

class SignupTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            is_staff=True,
            username='testuser', 
            email='testuser@example.com', 
            password='password@123A'
        )
        self.user.is_staff=True
        self.user.save()
        self.level = Level.objects.create(
            code = "easy",
            name = "easy"
        )
        self.subject = Subject.objects.create(
            code='maths251', 
            name='Maths', 
            description='Mathematics',
        )
        self.grade = Grade.objects.create(
            code='grade1', 
            name='Grade 1', 
            description='Grade 1'
        )
        self.test = Test.objects.create(
            code = "question1",
            question = "why did the chicken try crossing d road?",
            options = {
                "a": "cause he he wanted to get to the other side",
                "b": "to dance",
                "c": "to play",
                "d": "to kiss",
                "e": "to talk"
            },
            topic = "Tears of Steel",
            lesson = 1,
            created = "2023-03-03T17:06:45.188305",
            updated = "2023-03-03T20:25:50.722117",
            subject = self.subject,
            grade = self.grade,
            level = self.level
        )

    def test_ListCreateUpdateAPITest(self):
        data = {
            "code": "question2",
            "question": "why did the chicken cross d road?",
            "options": {
                "a": "cause he he wanted to get to the other side",
                "b": "to dance",
                "c": "to play",
                "d": "to kiss",
                "e": "to talk"
            },
            "topic": "Tears of Steel",
            "lesson": 1,
            "created": "2023-03-03T17:06:45.188305",
            "updated": "2023-03-03T20:25:50.722117",
            "subject": self.subject.pk,
            "grade": self.grade.pk,
            "level": self.level.pk
        }

        response = self.client.post(reverse('api:login'), data={
            'username': 'testuser',
            'password': 'password@123A',
        })
        token = response.json()['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        post_response = self.client.post(reverse('assess:tests-list'), data=data, format='json')
        list_response = self.client.get(reverse('assess:tests-list'))
        detail_response = self.client.get(reverse('assess:test-detail', kwargs={'pk': self.test.pk}))

        # print('get_video_detail: ', (detail_response.json()))
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(post_response.json().get('topic'), 'Tears of Steel')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(list_response.json().get('results')), 0)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(detail_response.json()), 0)
        self.assertEqual(detail_response.json().get('lesson'), 1)


    def test_ListCreateUpdateAPIAssessment(self):
        data = {
            # "status": true,
            # "user": {
            #     "email": "oimara@enprohsoft.com",
            #     "username": "admin"
            # },
            "answer": {
                "1": "A"
            },
            "test": self.test.pk
        }
        response = self.client.post(reverse('api:login'), data={
            'username': 'testuser',
            'password': 'password@123A',
        })
        token = response.json()['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        post_response = self.client.post(reverse('assess:assess-list'), data=data, format='json')
        list_response = self.client.get(reverse('assess:assess-list'))
        detail_response = self.client.get(reverse('assess:assess-detail', kwargs={'pk': post_response.json().get('id')}))

        # print('get_response_assessment: ', (list_response.json()))
        # print('get_response_assessment: ', (detail_response.json()))
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(post_response.json().get('answer').get('1'), 'A')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(list_response.json().get('results')), 0)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(detail_response.json()), 0)
        self.assertEqual(detail_response.json().get('status'), True)
