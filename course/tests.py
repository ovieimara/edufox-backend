from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient
from .models import Grade, Subject, Lecturer, Video, Resolution
import json

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
        self.resolution = Resolution.objects.create(
            name="1080p",
            size="1920 x 1080",
            aspect_ratio="16:9",
            media="HLS",
        )
        self.subject = Subject.objects.create(
            code='maths241', 
            name='Maths', 
            description='Mathematics',
        )
        self.grade = Grade.objects.create(
            code='grade2', 
            name='Grade 2', 
            description='Grade 2'
        )
        self.discount = {            
            "name": "0%",
            "value": "0.00",
            "symbol": "%"
        }

        self.plan =  {
            "name": "monthly",
            "amount": 5000,
            "currency": "=N=",
            "description": "=N=5000 monthly",
            "duration": 30,
            "discount": 1
        },
        
        self.subscribe = {
            "user": 1,
            "plan": 1,
            "grade": 1,
        }


    def test_create_grade(self):
        Grade.objects.create(
            code='grade1', 
            name='Grade 1', 
            description='Grade 1'
        )
        grade = Grade.objects.get(name='Grade 1')
        self.assertEqual(grade.name, 'Grade 1')
        self.assertEqual(grade.code, 'grade1')


    def test_create_subject(self):
        Subject.objects.create(
            code='che141', 
            name='Chemistry', 
            description='Chemistry',
        )
        grade = Subject.objects.get(name='Chemistry')
        self.assertEqual(grade.name, 'Chemistry')
        self.assertEqual(grade.code, 'che141')

    def test_create_lecturer(self):
        Lecturer.objects.create(
            first_name='ovie', 
            last_name='imara', 
        )
        lecturer = Lecturer.objects.get(first_name='ovie')
        self.assertEqual(lecturer.first_name, 'ovie')
        self.assertEqual(lecturer.last_name, 'imara')

    def test_ListCreateAPIVideo(self):
        video = {
            "id": 1,
            "title": "Tears of Steel",
            "description": "Tears of Steel",
            "duration": "2:00",
            "thumbnail": "https://picsum.photos/200/300",
            "topic": "Tears of Steel",
            "lesson": 1,
            "url": "https://demo.unified-streaming.com/k8s/features/stable/video/tears-of-steel/tears-of-steel.ism/.m3u8",
            "tags": "test",
            "resolution": self.resolution.pk,
            "subject": self.subject.pk,
            "grade": self.grade.pk
        }

        response = self.client.post(reverse('api:login'), data={
            'username': 'testuser',
            'password': 'password@123A',
        })
        token = response.json()['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        post_response = self.client.post(reverse('course:videos-list'), data=video, format='json')
        list_response = self.client.get(reverse('course:videos-list'))
        detail_response = self.client.get(reverse('course:video-detail', kwargs={'pk': post_response.json().get('id')}))

        print('get_video: ', (post_response.json()))
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(post_response.json().get('topic'), 'Tears of Steel')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(list_response.json().get('results')), 0)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(detail_response.json()), 0)
        self.assertEqual(detail_response.json().get('title'), 'Tears of Steel')
