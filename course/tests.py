from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
import requests
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient

from course.abc import TitleEditor
from .models import Event, Grade, Lesson, Subject, Lecturer, Topic, Video, Resolution
import json

User = get_user_model()


class SignupTestCase(TestCase, TitleEditor):
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
        self.user.is_staff = True
        self.user.save()

        self.user2 = User.objects.create_user(
            # is_staff=True,
            username='+23407048536974',
            email='testuser@example.com',
            password='password@123A'
        )

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
        self.event = Event.objects.create(
            name="PLAY",
            description="PLAY"
        )

        self.discount = {
            "name": "0%",
            "value": "0.00",
            "symbol": "%"
        }

        self.plan = {
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

        self.video = Video.objects.create(
            title="Tears of Steel",
            description="Tears of Steel",
            duration="2:00",
            thumbnail="https://picsum.photos/200/300",
            topic=None,
            lesson=None,
            url="https://demo.unified-streaming.com/k8s/features/stable/video/tears-of-steel/tears-of-steel.ism/.m3u8",
            tags="recommend",
            resolution=self.resolution,
            subject=self.subject,
            # grade = [self.grade.pk] ,
        )
        self.video.grade.set([self.grade.pk])
        self.data = {
            'email': 'imaraovie@gmail.com',
            'password': 'password@123A',
            'phone_number': '+23407048536974',
        }

        self.topic = Topic.objects.create(
            chapter=1,
            title="Elements",
            subject=None,
            # grade = None
        )
        self.topic.grade.set([self.grade.pk, self.grade1.pk])

        self.lesson = Lesson.objects.create(
            num=1,
            title="Elements 1",
            topic=self.topic,
            subject=self.subject,
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

    def test_create_lessons(self):

        lesson = {
            "num": 1,
            "title": "Elements One Test",
            "subject": self.subject.pk,
            "grade": [self.grade.pk, self.grade1.pk],
            # "topic": self.topic.pk,
            "topics": self.topic.title

        }

        response = self.client.post(reverse('api:login'), data={
            'username': 'testuser',
            'password': 'password@123A',
        })
        token = response.json()['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        post_response = self.client.post(
            reverse('course:lessons-list'), data=lesson, format='json')
        list_response = self.client.get(reverse('course:lessons-list'))

        detail_response = self.client.get(
            reverse('course:lessons-detail', kwargs={'pk': post_response.json()[0].get('pk')}))

        # print('post_lesson: ', post_response.json())

        # print('detail_lesson: ', detail_response.json())

        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        # self.assertEqual(post_response.json().get('topic'), 'Tears of Steel')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(list_response.json().get('results')), 0)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(detail_response.json()), 0)
        # video_id = detail_response.json().get('video_id')

    def test_create_lessons_videoId_in_title(self):

        lesson = {
            "num": 1,
            "title": "BASIC_ECOLOGICAL_CONCEPT_converted.mp4-2f0szWI8H2",
            "subject": self.subject.pk,
            "grade": [self.grade.pk, self.grade1.pk],
            # "topic": self.topic.pk,
            "topics": self.topic.title

        }

        response = self.client.post(reverse('api:login'), data={
            'username': 'testuser',
            'password': 'password@123A',
        })
        token = response.json()['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        post_response = self.client.post(
            reverse('course:lessons-list'), data=lesson, format='json')
        list_response = self.client.get(reverse('course:lessons-list'))

        detail_response = self.client.get(
            reverse('course:lessons-detail', kwargs={'pk': post_response.json()[0].get('pk')}))

        # print('post_lesson: ', post_response.json())

        # print('detail_lesson: ', detail_response.json())

        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        # self.assertEqual(post_response.json().get('topic'), 'Tears of Steel')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(list_response.json().get('results')), 0)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)

        self.assertGreater(len(detail_response.json()), 0)
        self.assertEqual(detail_response.json().get('title'),
                         "Basic Ecological Concept-2f0szWI8H2")

    def test_create_multiple_lessons(self):

        lesson = {
            "num": 1,
            "title": "BASIC_ECOLOGICAL_CONCEPT_converted.mp4-2f0szWI8H2, BASIC_ECOLOGICAL_CONCEPTII_converted.mp4-3f0szWI4H2",
            "subject": self.subject.pk,
            "grade": [self.grade.pk, self.grade1.pk],
            # "topic": self.topic.pk,
            "topics": self.topic.title

        }

        response = self.client.post(reverse('api:login'), data={
            'username': 'testuser',
            'password': 'password@123A',
        })
        token = response.json()['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        post_response = self.client.post(
            reverse('course:lessons-list'), data=lesson, format='json')
        list_response = self.client.get(reverse('course:lessons-list'))

        # print("post_response_multiple: ", post_response.json())

        detail_response = self.client.get(
            reverse('course:lessons-detail', kwargs={'pk': post_response.json()[1].get('pk')}))

        print('post_lesson_multiple: ', post_response.json())

        # print('detail_lesson_multiple: ', detail_response.json())

        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(post_response.json()[
                         0].get('topic'), self.topic.title)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(list_response.json().get('results')), 1)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)

        self.assertGreater(len(detail_response.json()), 0)
        self.assertEqual(detail_response.json().get('title'),
                         "Basic Ecological Conceptii-3f0szWI4H2")

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
        lesson = Lesson.objects.create(
            num=1,
            title="Elements One Test",
            # title="Elements One Test-hyWexc5t6",
            topic=self.topic,
            subject=self.subject,

        )
        video = {
            "id": 1,
            "title": "",
            "description": "Tears of Steel",
            "duration": "2:00",
            "thumbnail": "https://picsum.photos/200/300",
            "video_id": "",
            # "topic": self.topic.id,
            # "lesson": self.lesson.id,
            "url": "https://demo.unified-streaming.com/k8s/features/stable/video/tears-of-steel/tears-of-steel.ism/.m3u8",
            "tags": "recommend",
            "resolution": self.resolution.pk,
            "subject": self.subject.pk,
            "grade": [self.grade.pk, self.grade1.pk],
            "lessons": lesson.title,
            "topics": self.topic.title
        }

        response = self.client.post(reverse('api:login'), data={
            'username': 'testuser',
            'password': 'password@123A',
        })
        token = response.json()['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        post_response = self.client.post(
            reverse('course:videos-list'), data=video, format='json')
        list_response = self.client.get(reverse('course:videos-list'))

        detail_response = self.client.get(
            reverse('course:video-detail', kwargs={'pk': post_response.json().get('id')}))

        # print('post_video1: ', post_response.json())
        self.assertEqual(post_response.status_code,
                         status.HTTP_201_CREATED)
        # self.assertEqual(post_response.json().get('topic'), 'Tears of Steel')
        # self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        # self.assertGreater(len(list_response.json().get('results')), 0)
        # self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        # self.assertGreater(len(detail_response.json()), 0)
        # video_id = detail_response.json().get('video_id')

        # length = len(video_id) - 1 if '-' in lesson.title else len(video_id)

        # self.assertEqual(detail_response.json().get(
        #     'title'), lesson.title[:len(lesson.title) - length])

        # url = f"{reverse('course:videos-list')}?subject={self.subject.pk}"
        # response = self.client.get(url)

        # response = self.client.get(
        #     reverse('course:videos-list'), params={'subject': {self.subject.pk}})
        # # print('FILTER', (response.request))

        # response = self.client.get(reverse('course:dashboard-list'))
        # print('RESPONSE', (response.json()))

        # dashboard_response = self.client.get(
        #     reverse('course:dashboard-detail', kwargs={'subject': 0, 'grade': 3}))
        # dashboard_response2 = self.client.get(
        #     reverse('course:dashboard-detail', kwargs={'subject': '0', 'grade': 1}))

        # print('dashboard_response: ', dashboard_response.json())
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertGreater(len(response.json()), 0)
        # self.assertEqual(dashboard_response.status_code, status.HTTP_200_OK)
        # self.assertGreater(len(dashboard_response.json()), 0)
        # self.assertEqual(len(dashboard_response2.json()[1].get('data')), 0)

        path = reverse('api:login')
        host = "http://127.0.0.1:8000"
        url = f"{host}{path}"

        response = requests.post(url, data={
            'username': '+2348023168805',
            'password': 'password@123A',
        })
        token = response.json()['auth_token']
        # print('token: ', token)
        path = reverse('course:dashboard-detail',
                       kwargs={'subject': '0', 'grade': 1})

        url = f"{host}{path}"
        response = requests.get(url, headers={
            'Authorization': f"Token {token}",
            'Content-Type': 'application/json'
        })
        # print('dashboard_response: ', response.json()[0].get('data'))

    # def test_ListDashboardAPI(self):
    #     response = self.client.get(reverse('course:dashboard-list'))
    #     print('post_video: ', response.json(), self.grade.pk)

    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertGreater(len(response.json()), 0)

    def test_ListCreateAPIVideoWithVideoIdInTitle(self):
        lesson = Lesson.objects.create(
            num=1,
            # title="Elements One Test",
            title="Elements One Test-hyWexc5t6",
            topic=self.topic,
            subject=self.subject,

        )
        video = {
            "id": 1,
            "title": "",
            "description": "Tears of Steel",
            "duration": "2:00",
            "thumbnail": "https://picsum.photos/200/300",
            "video_id": "",
            # "topic": self.topic.id,
            # "lesson": self.lesson.id,
            "url": "https://demo.unified-streaming.com/k8s/features/stable/video/tears-of-steel/tears-of-steel.ism/.m3u8",
            "tags": "recommend",
            "resolution": self.resolution.pk,
            "subject": self.subject.pk,
            "grade": [self.grade.pk, self.grade1.pk],
            "lessons": lesson.title,
            "topics": self.topic.title
        }

        response = self.client.post(reverse('api:login'), data={
            'username': 'testuser',
            'password': 'password@123A',
        })
        token = response.json()['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        post_response = self.client.post(
            reverse('course:videos-list'), data=video, format='json')
        list_response = self.client.get(reverse('course:videos-list'))

        detail_response = self.client.get(
            reverse('course:video-detail', kwargs={'pk': post_response.json().get('id')}))

        # print('post_video1: ', post_response.json(), self.grade.pk)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        # self.assertEqual(post_response.json().get('topic'), 'Tears of Steel')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(list_response.json().get('results')), 0)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(detail_response.json()), 0)
        video_id = detail_response.json().get('video_id')

        # length = len(video_id) - 1 if '-' in lesson.title else len(video_id)

        self.assertEqual(detail_response.json().get(
            'title'), lesson.title.split('-')[0])

        url = f"{reverse('course:videos-list')}?subject={self.subject.pk}"
        response = self.client.get(url)

        response = self.client.get(
            reverse('course:videos-list'), params={'subject': {self.subject.pk}})
        # print('FILTER', (response.request))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.json()), 0)

    def test_ListCreateAPIVideoWithVideoId(self):
        lesson = Lesson.objects.create(
            num=1,
            # title="Elements One Test",
            title="Elements One Test-hyWexc5t6",
            topic=self.topic,
            subject=self.subject,

        )
        video = {
            "id": 1,
            "title": "",
            "description": "Tears of Steel",
            "duration": "2:00",
            "thumbnail": "https://picsum.photos/200/300",
            "video_id": "hyWexc5t6",
            # "topic": self.topic.id,
            # "lesson": self.lesson.id,
            "url": "https://demo.unified-streaming.com/k8s/features/stable/video/tears-of-steel/tears-of-steel.ism/.m3u8",
            "tags": "recommend",
            "resolution": self.resolution.pk,
            "subject": self.subject.pk,
            "grade": [self.grade.pk, self.grade1.pk],
            "lessons": lesson.title,
            "topics": self.topic.title
        }

        response = self.client.post(reverse('api:login'), data={
            'username': 'testuser',
            'password': 'password@123A',
        })
        token = response.json()['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        post_response = self.client.post(
            reverse('course:videos-list'), data=video, format='json')
        list_response = self.client.get(reverse('course:videos-list'))

        detail_response = self.client.get(
            reverse('course:video-detail', kwargs={'pk': post_response.json().get('id')}))

        # print('post_video1: ', post_response.json(), self.grade.pk)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        # self.assertEqual(post_response.json().get('topic'), 'Tears of Steel')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(list_response.json().get('results')), 0)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(detail_response.json()), 0)
        video_id = detail_response.json().get('video_id')

        length = len(video_id) - 1 if '-' in lesson.title else len(video_id)

        self.assertEqual(detail_response.json().get(
            'title'), lesson.title.split('-')[0])

        url = f"{reverse('course:videos-list')}?subject={self.subject.pk}"
        response = self.client.get(url)

        response = self.client.get(
            reverse('course:videos-list'), params={'subject': {self.subject.pk}})
        # print('FILTER', (response.request))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.json()), 0)

    def test_interaction(self):
        video = Video.objects.create(
            title="Tears of Steel",
            description="Tears of Steel",
            duration="2:00",
            thumbnail="https://picsum.photos/200/300",
            topic=None,
            lesson=None,
            url="https://demo.unified-streaming.com/k8s/features/stable/video/tears-of-steel/tears-of-steel.ism/.m3u8",
            tags="recommend",
            resolution=self.resolution,
            subject=self.subject,
            # grade = [self.grade.pk] ,
        )
        video.grade.set([self.grade.pk])
        response = self.client.post(reverse('api:login'), data={
            'username': '+23407048536974',
            'password': 'password@123A',
        })
        token = response.json()['auth_token']
        # print(token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        data = {
            "begin_duration": "5.00",
            "end_duration": "5.00",
            "event": self.event.pk,
            "video": video.pk,
        }
        print("data: ", data)
        response = self.client.post(
            reverse('course:interactions-list'), data=data, format='json')
        response = response.json()
        print("Interaction Response: ", response)
        self.assertEqual(video.pk, response.get('video').get('id'))
        self.assertEqual(self.user2.username, response.get('user'))

    def test_VideoSearchListViewAPI(self):
        response = self.client.post(reverse('api:login'), data={
            'username': '+23407048536974',
            'password': 'password@123A',
        })
        token = response.json()['auth_token']
        # print(token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        response = self.client.get(
            reverse('course:query-list'), params={'search': 'Tears'})
        # print('QUERY', response.json())

    def test_Rate(self):
        response = self.client.post(reverse('api:login'), data={
            'username': '+23407048536974',
            'password': 'password@123A',
        })
        token = response.json()['auth_token']
        # print(token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        data = {
            "rating": 5,
            "video": self.video.pk,
        }
        response = self.client.post(
            reverse('course:rates-list'), data=data, format='json')
        response = response.json()
        self.assertEqual(self.video.pk, response.get('video'))
        self.assertEqual(self.user2.username, response.get('user'))
        self.assertEqual(data.get('rate'), response.get('rate'))

        data = {
            "rating": 3,
            "video": self.video.pk,
        }

        response = self.client.post(
            reverse('course:rates-list'), data=data, format='json')
        response = response.json()
        self.assertEqual(self.video.pk, response.get('video'))
        self.assertEqual(self.user2.username, response.get('user'))
        self.assertEqual(data.get('rate'), response.get('rate'))

        data = {
            "rating": '',
            "video": self.video.pk,
        }
        response = self.client.post(
            reverse('course:rates-list'), data=data, format='json')
        response = response.json()
        self.assertEqual(self.video.pk, response.get('video'))
        self.assertEqual(self.user2.username, response.get('user'))
        self.assertEqual(-1, response.get('rate'))

    def test_get_lesson_title(self):
        # title_editor = TitleEditor()

        # Test cases for get_lesson_title
        test_cases = [
            # Test case 1: Standard case with video ID
            {
                'input_title': 'lesson_1_converted.mp4',
                'expected_output': 'Lesson 1'
            },
            # Test case 2: Video ID with hyphen and converted.mp4
            {
                'input_title': 'lesson_2_converted.mp4-ID12345',
                'expected_output': 'Lesson 2-ID12345'
            },
            # Test case 3: Multiple underscores
            {
                'input_title': 'lesson_3_some_extra_info_converted.mp4',
                'expected_output': 'Lesson 3 Some Extra Info'
            },
            # Test case 4: No converted.mp4 and no video_id
            {
                'input_title': 'lesson_4_some_extra_info.mp4',
                'expected_output': 'Lesson 4 Some Extra Info'
            },
            # Test case 5: No converted.mp4
            {
                'input_title': 'lesson_5_some_extra_info.mp4-ID12345',
                'expected_output': 'Lesson 5 Some Extra Info-ID12345'
            },

            # Test case 3: No converted.mp4, no _
            {
                'input_title': 'lesson 3 some extra info.mp4-ID12345',
                'expected_output': 'Lesson 3 Some Extra Info-ID12345'
            },

            # Test case 3: No converted.mp4, no _, no id, no -
            {
                'input_title': 'lesson 3 some extra info.mp4',
                'expected_output': 'Lesson 3 Some Extra Info'
            },

            # Test case 3: &
            {
                'input_title': 'lesson 3 & some extra info.mp4',
                'expected_output': 'Lesson 3 Some Extra Info'
            },
        ]

        for test_case in test_cases:
            input_title = test_case['input_title']
            expected_output = test_case['expected_output']

            with self.subTest(input_title=input_title):
                output = self.get_lesson_title(input_title)
                self.assertEqual(output, expected_output)
