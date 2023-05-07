import datetime
import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient
from course.models import Grade, Lesson, Subject, Topic
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

        self.topic = Topic.objects.create(
            chapter = 1,
            title = "Elements",
            subject = None,
            # grade = None
        )
        self.topic.grade.set([self.grade.pk, self.grade.pk])

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

        self.test = Test.objects.create(
            code = "question1",
            question = "why did the chicken try crossing d road?",
            options = [
                "cause he he wanted to get to the other side",
                "to dance",
                "to play",
                "to kiss",
                "to talk"
            ],
            valid_answers = [1,2],
            topic = self.topic,
            lesson = self.lesson,
            # created = datetime.datetime.now,
            # updated = "2023-03-03T20:25:50.722117",
            subject = self.subject,
            grade = self.grade,
            level = self.level
        )

    def test_ListCreateUpdateAPITest(self):
        data = {
            "code": "question2",
            "question": "why did the chicken cross d road?",
            "option1" : "cause he he wanted to get to the other side",
            'option2': "to dance", 
            'option3': "to kiss", 
            'option4': "to talk",
            'option5': "to kiss", 
            'option6': "to talk",
            "answers": "1, 2",
            "topic": self.topic.pk,
            "lesson": self.lesson.pk,
            # "created": "2023-03-03T17:06:45.188305",
            # "updated": "2023-03-03T20:25:50.722117",
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

        # print('get_video_detail: ', (post_response.json()))
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(post_response.json().get('topic'), self.topic.pk)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(list_response.json().get('results')), 0)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(detail_response.json()), 0)
        self.assertEqual(detail_response.json().get('lesson'), self.lesson.pk)


    def test_ListCreateUpdateAPIAssessment(self):
        data = [
                {
                "answer": [1],
                "test": self.test.pk
                }
            ]
        
        # data = json.dumps(data)
        response = self.client.post(reverse('api:login'), data={
            'username': 'testuser',
            'password': 'password@123A',
        })
        token = response.json()['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        post_response = self.client.post(reverse('assess:assess-list'), data=data, format='json')
        # list_response = self.client.get(reverse('assess:assess-list'))
        # detail_response = self.client.get(reverse('assess:assess-detail', kwargs={'pk': post_response.json().get('id')}))

        # print('get_response_assessment: ', (list_response.json()))
        print('get_response_assessment: ', (post_response.json()))
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(post_response.json()[0].get('answer')[0], data[0].get('answer')[0])
        # self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        # self.assertGreater(len(list_response.json().get('results')), 0)
        # self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        # self.assertGreater(len(detail_response.json()), 0)
        # self.assertEqual(detail_response.json().get('status'), True)
