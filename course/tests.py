from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient
from .models import Grade, Lesson, Subject, Lecturer, Topic, Video, Resolution
import json

User = get_user_model()

class SignupTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.grade = Grade.objects.create(
            code='grade2', 
            name='Grade 2', 
            description='Grade 2'
        )
        self.grade1 = Grade.objects.create(
            code='grade1', 
            name='Grade 1', 
            description='Grade 1'
        )
        self.user = User.objects.create_user(
            is_staff=True,
            username='testuser', 
            email='testuser@example.com', 
            password='password@123A',
            # grade = self.grade.pk
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

        self.video = Video.objects.create (
            title = "Tears of Steel",
            description = "Tears of Steel",
            duration = "2:00",
            thumbnail = "https://picsum.photos/200/300",
            topic = None,
            lesson = None,
            url = "https://demo.unified-streaming.com/k8s/features/stable/video/tears-of-steel/tears-of-steel.ism/.m3u8",
            tags = "recommend",
            resolution = self.resolution,
            subject = self.subject,
            # grade = [self.grade.pk] ,
        )
        self.video.grade.set([self.grade.pk])
        self.data = {
                'email': 'imaraovie@gmail.com',
                'password': 'password@123A',
                'phone_number' : '+23407048536974',
        }

        self.topic = Topic.objects.create(
            chapter = 1,
            title = "Elements",
            subject = None,
            # grade = None
        )
        self.topic.grade.set([self.grade.pk, self.grade1.pk])

        self.lesson = Lesson.objects.create(
            num= 1,
            title = "Elements 1",
            topic = self.topic,
            subject = self.subject,
            # grade = None
            # grades = [
            #     "Grade 1"
            # ]
        )

        self.lesson.grade.set([self.grade.pk])

    def test_create_grade(self):
        Grade.objects.create(
            code='grade3', 
            name='Grade 3', 
            description='Grade 3'
        )
        grade = Grade.objects.get(name='Grade 3')
        self.assertEqual(grade.name, 'Grade 3')
        self.assertEqual(grade.code, 'grade3')


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

    # def test_create_lessons(self):


    # def test_seek(self):
    #     obj = {
    #         # "user" : self.user,
    #         "direction" : "FW",
    #         "to_duration" : "3:00",
    #         "from_duration" : "5:00",
    #         "video" : self.video.pk
    #     } 
    #     response = self.client.post(reverse('students-list'), data=self.data, format='json')
    #     # data = {
    #     #         "otp" : '1234',
    #     #         "username" : "+23407048536974",
    #     #         'email': "imaraovie@gmail.com"
    #     #     }

    #     # response = self.client.post(reverse('student:otp-activate'), data=data, format='json')
    #     response = self.client.post(reverse('api:login'), data={
    #             'username': '+23407048536974',
    #             'password': 'password@123A',
    #     })
    #     # print('GRADE: ', response.json())
    #     token = response.json()['auth_token']
    #     self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        
    #     response = self.client.post(reverse('course:seeks-list'), data=obj)
    #     response_json = response.json()
    #     # print('RESP: ', response_json)
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(response_json.get('direction'), 'FW')

    #     response = self.client.get(reverse('course:seek-detail', kwargs={'pk': response_json.get('id')}))
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertGreater(len(response.json()), 0)

        

    def test_ListCreateAPIVideo(self):
        video = {
            "id": 1,
            "title": "Tears of Steel2",
            "description": "Tears of Steel",
            "duration": "2:00",
            "thumbnail": "https://picsum.photos/200/300",
            # "topic": self.topic.id,
            # "lesson": self.lesson.id,
            "url": "https://demo.unified-streaming.com/k8s/features/stable/video/tears-of-steel/tears-of-steel.ism/.m3u8",
            "tags": "recommend",
            "resolution": self.resolution.pk,
            "subject": self.subject.pk,
            "grade": [3, 4],
            "lessons": self.lesson.title,
            "topics": self.topic.title
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

        print('post_video1: ', post_response.json(), self.grade.pk)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        # self.assertEqual(post_response.json().get('topic'), 'Tears of Steel')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(list_response.json().get('results')), 0)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(detail_response.json()), 0)
        self.assertEqual(detail_response.json().get('title'), video.get('title'))

        url = f"{reverse('course:videos-list')}?subject={self.subject.pk}"
        response = self.client.get(url)

        response = self.client.get(reverse('course:videos-list'), params={'subject' : {self.subject.pk}})
        # print('FILTER', (response.request))

        response = self.client.get(reverse('course:dashboard-list'))
        print('post_video: ', response.json(), self.grade.pk, self.grade1.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.json()), 0)


    # def test_ListDashboardAPI(self):
    #     response = self.client.get(reverse('course:dashboard-list'))
    #     print('post_video: ', response.json(), self.grade.pk)

    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertGreater(len(response.json()), 0)