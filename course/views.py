import abc
from collections import OrderedDict
import datetime
from functools import lru_cache
import json
from logging import Filter
import logging
from multiprocessing import set_forkserver_preload
from re import sub
from venv import create, logger
from django.http import HttpRequest
from rest_framework import filters
import copy
import os
from django.shortcuts import render
from rest_framework import generics, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly, AllowAny
from yaml import serialize
from course.abc import BatchVideos, CreateMultipleLessons, LessonScreen
from edufox.constants import ANDROID, IOS, WEB
from django.core.paginator import Paginator, EmptyPage
from edufox.views import printOutLogs, update_user_data
from form import serializers
from subscribe.abc import MySubscription
from subscribe.models import Subscribe
from .models import (Grade, Event, Lesson, SearchQuery, Subject, Lecturer, Thumbnail, Video,
                     Rate, Comment, Interaction, Resolution, Topic)
# from assess.models import  Test, Assessment
from .serializers import (EventSerializer, GradeSerializer, SearchQuerySerializer, SubjectSerializer, LecturerSerializer, ThumbnailSerializer, VideoSerializer, RateSerializer, CommentSerializer,
                          InteractionSerializer, ResolutionSerializer, LessonSerializer, TopicSerializer)
from .permissions import IsStaffEditorPermission
from django.core.paginator import Paginator, EmptyPage
from django.contrib.auth.models import User
from student.models import Student
from django.db.models import Q
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from rest_framework.decorators import api_view, permission_classes
from django.views import View
from client.library import AWSSignedURLGenerator, AmazonDynamoDBHLSStream, AmazonDynamoDBRepo, GoogleCloudStorageRepo2, GoogleImageStore, HLSWebStream, StorageRepoABC, GoogleCloudStorageRepo, DashStream, HLSStream, PlatformStream
from django.conf import settings as django_settings
from edufox.constants import platforms
from abc import ABC, abstractmethod
import concurrent.futures
from django.db.models import F
from django.db.models.query import QuerySet
from typing import List, Dict

# from colorama import Fore

# Create your views here.


class ListCreateAPIGrades(generics.ListCreateAPIView):
    queryset = Grade.objects.all().order_by('pk')
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        if self.request.user.is_staff:
            return super().perform_create(serializer)
        return status.HTTP_403_FORBIDDEN


class UpdateAPIGrades(generics.RetrieveUpdateDestroyAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAdminUser, IsStaffEditorPermission]


class ListCreateAPISubject(generics.ListCreateAPIView):
    queryset = Subject.objects.all().order_by('name')
    serializer_class = SubjectSerializer
    permission_classes = [IsAdminUser, IsStaffEditorPermission]


class UpdateAPISubject(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAdminUser, IsStaffEditorPermission]


class ListCreateAPILecturer(generics.ListCreateAPIView):
    queryset = Lecturer.objects.all()
    serializer_class = LecturerSerializer
    # permission_classes = [IsAdminUser, IsStaffEditorPermission]


class UpdateAPILecturer(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lecturer.objects.all()
    serializer_class = LecturerSerializer
    permission_classes = [IsAdminUser, IsStaffEditorPermission]


class ListCreateAPIVideo(generics.ListCreateAPIView):
    # queryset = Video.objects.select_related('grade', 'subject').all().order_by('pk')
    queryset = Video.objects.select_related(
        'subject', 'topic', 'lesson').all().order_by('pk')
    serializer_class = VideoSerializer
    filterset_fields = ['grade', 'subject', 'topic', 'lesson']
    ordering_fields = ['title', 'topic']
    search_fields = ['title', 'description', 'lesson__title', 'topic__title', 'tags',
                     'subject__name', 'subject__description', 'grade__name', 'grade__description']
    # permission_classes = [AllowAny]

    def perform_create(self, serializer):
        # print('USER: ', self.request.user, self.request.user.is_staff)
        if self.request.user.is_staff:
            response = super().perform_create(serializer)
            if response and response.status == status.HTTP_201_CREATED:
                update_user_data()  # update cache
            return response
        return status.HTTP_403_FORBIDDEN


class UpdateAPIVideo(generics.RetrieveUpdateDestroyAPIView):
    queryset = Video.objects.select_related('subject').all()
    serializer_class = VideoSerializer
    permission_classes = [IsAdminUser, IsStaffEditorPermission]


class ListCreateAPIRate(generics.ListCreateAPIView):
    queryset = Rate.objects.select_related('video').all().order_by('pk')
    # print(queryset)
    serializer_class = RateSerializer


class UpdateAPIRate(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rate.objects.select_related('video').all()
    serializer_class = RateSerializer


class ListCreateAPIComment(generics.ListCreateAPIView):
    queryset = Comment.objects.select_related('video').all()
    serializer_class = CommentSerializer


class UpdateAPIComment(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.select_related('video').all()
    serializer_class = CommentSerializer


class ListCreateAPIEvent(generics.ListCreateAPIView):
    queryset = Event.objects.all().order_by('pk')
    serializer_class = EventSerializer

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)

            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class UpdateAPIEvent(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all().order_by('pk')
    serializer_class = EventSerializer
    permission_classes = [IsAdminUser, IsStaffEditorPermission]


class ListCreateAPIInteraction(generics.ListCreateAPIView):
    queryset = Interaction.objects.all().order_by('pk')
    serializer_class = InteractionSerializer

    def create(self, request, *args, **kwargs):
        data = {}
        video = request.data.get('video')
        event = request.data.get('event')
        video_queryset = Video.objects.filter(pk=video)
        event_queryset = Event.objects.filter(pk=event)
        # print("video_queryset: ", request.data)
        val = request.data.pop('video')
        # print("video_queryset: ", val)
        if event_queryset.exists() and video_queryset.exists():
            serializer = self.get_serializer(
                data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save(video=video_queryset.first(),
                            event=event_queryset.first())
            data = serializer.data

        headers = self.get_success_headers(data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class UpdateAPIInteraction(generics.RetrieveUpdateDestroyAPIView):
    queryset = Interaction.objects.select_related(
        'user', 'video', 'event').order_by('pk')
    serializer_class = InteractionSerializer


class ListCreateAPIResolution(mixins.CreateModelMixin, mixins.ListModelMixin,  mixins.RetrieveModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView):
    queryset = Resolution.objects.all()
    serializer_class = ResolutionSerializer
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


class ListCreateUpdateAPILesson(mixins.CreateModelMixin, mixins.ListModelMixin,  mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    queryset = Lesson.objects.all().order_by('pk')
    serializer_class = LessonSerializer
    lookup_field = 'pk'
    search_fields = ['title', 'topic__title']
    # permission_classes = [IsStaffEditorPermission]

    def get(self, request, *args, **kwargs):
        if kwargs.get('pk') is not None:
            return self.retrieve(request, *args, **kwargs)

        return self.list(request, *args, **kwargs)

    # def create_video(self, video_data):
    #     # Perform the bulk create operation for a batch of video data
    #     with transaction.atomic():
    #         Video.objects.bulk_create([Video(**data) for data in video_data])

    def create_video(self, video_data):
        logging.error(f"creating video: ", video)
        # Create the video
        video = Video.objects.create(**video_data)

        # Get the list of grade IDs for the video
        grades = video_data.get('grade', [])

        # Set the grades for the video using the grade IDs
        video.grade.set(grades)

        logging.error(f"created video: ", video)

        # Any other post-processing for the video creation can be done here

    def createVideos(self, lessons: list, request: HttpRequest) -> None:
        batch_videos = BatchVideos()
        videos = batch_videos.generate_videos(lessons)
        try:
            videos_serializer = VideoSerializer(
                data=videos, many=True, context={'request': request})
            # print('videos_serializer: ', videos_serializer.initial_data)

            try:
                videos_serializer.is_valid(raise_exception=True)
                # videos_data = videos_serializer.validated_data
                # print("videos_data: ", videos_data, type(videos_data))

                videos_serializer.save()
            except Exception as ex:
                logger.error(
                    f'createVideos : {ex}', videos_serializer.validated_data)

            # self.create_video(videos_data)

            # Save videos to the database within the same transaction
            # Wrap the video creation in a database transaction
            # Split the videos_data into chunks for concurrent processing
            # num_workers = min(len(videos_data), concurrent.futures.cpu_count())
            # if len(videos_data):
            #     num_workers = 3
            #     chunk_size = len(videos_data) // num_workers
            # video_chunks = [videos_data[i:i+chunk_size]
            #                 for i in range(0, len(videos_data), chunk_size)]
            # with concurrent.futures.ThreadPoolExecutor() as executor:
            #     executor.map(self.create_video, videos_data)

            # videos_serializer.save()
        except ValidationError as ex:
            # Log the validation error
            logging.error(
                f"createVideos: Validation error: {ex.message}")

            # Raise an exception to propagate the error to the outer method
            raise ex

        except Exception as ex:
            logging.error(f"createVideos: {ex}")
            # Raise an exception to propagate the error to the outer method
            raise ex

    def createLessons(self, lessons: list, request: HttpRequest) -> list:

        try:
            serializer = self.get_serializer(
                data=lessons, many=True, context={'request': request})
            serializer.is_valid(raise_exception=True)
            # Wrap the lesson creation in a database transaction
            # with transaction.atomic():
            self.perform_create(serializer)

            return serializer.data

        except ValidationError as ex:
            # Log the validation error
            logging.error(f"createLessons: Validation error: {ex}")
            # Return a 400 Bad Request response with the validation error details
            return Response(data=ex.detail, status=status.HTTP_400_BAD_REQUEST)

        except Exception as ex:
            logging.error(f"createLessons: {ex}")

            # Return a 500 Internal Server Error response or raise an exception
            return Response(data={'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        multiple_lessons = CreateMultipleLessons()
        # print('data: ', multiple_lessons)
        lessons = multiple_lessons.split_titles_ids(request.data)
        print("lessons: ", lessons)
        # with transaction.atomic():
        serialized_lessons = self.createLessons(lessons, request)
        self.createVideos(serialized_lessons, request)

        headers = self.get_success_headers(serialized_lessons)
        return Response(serialized_lessons, status=status.HTTP_201_CREATED, headers=headers)

    def post(self, request, *args, **kwargs):

        if not kwargs.get('pk') and request.user.is_staff:
            return self.create(request, *args, **kwargs)

        return Response(status.HTTP_403_FORBIDDEN)

    def put(self, request, *args, **kwargs):
        if kwargs.get('pk') and request.user.is_staff:
            return self.update(request, *args, **kwargs)
        return Response(status.HTTP_403_FORBIDDEN)

    def delete(self, request, *args, **kwargs):
        # Handle DELETE request logic
        if kwargs.get('pk') and request.user.is_staff:
            return self.destroy(request, *args, **kwargs)
        return Response(status.HTTP_403_FORBIDDEN)


class ListCreateUpdateAPITopic(mixins.CreateModelMixin, mixins.ListModelMixin,  mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    queryset = Topic.objects.all().order_by('pk')
    serializer_class = TopicSerializer
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
        return Response(status.HTTP_403_FORBIDDEN)

    def delete(self, request, *args, **kwargs):
        # Handle DELETE request logic
        if kwargs.get('pk') and request.user.is_staff:
            return self.destroy(request, *args, **kwargs)
        return Response(status.HTTP_403_FORBIDDEN)


# class ListCreateAPISeek(mixins.CreateModelMixin, mixins.ListModelMixin,  mixins.RetrieveModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView):
#     queryset = Seek.objects.all()
#     serializer_class = SeekSerializer
#     # lookup_field = 'pk'
#     # permission_classes = [IsStaffEditorPermission]
#     # permission_classes = []

#     def get(self, request, *args, **kwargs):
#         if kwargs.get('pk') is not None:
#             return self.retrieve(request, *args, **kwargs)
#         return self.list(request, *args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         if not kwargs.get('pk'):
#             return self.create(request, *args, **kwargs)
#         return Response(status.HTTP_400_BAD_REQUEST)

#     def put(self, request, *args, **kwargs):
#         if kwargs.get('pk'):
#             return self.update(request, *args, **kwargs)
#         return Response(status.HTTP_400_BAD_REQUEST)

@lru_cache
def getSubjectTopics2(subject, grade):
    # print("getSubjectTopics.........", subject, grade)
    result = []
    if subject:
        topics_queryset = None
        subject_instance = None
        try:
            subject_instance = Subject.objects.get(pk=subject)
        except Subject.DoesNotExist as ex:
            logging.error('subject object error: ', ex)
        # print("subject_instance: ", subject_instance)
        if subject_instance:
            topics_queryset = subject_instance.subject_topics.all()
            # print("topics_queryset: ", topics_queryset)
            if grade:
                topics_queryset = topics_queryset.filter(
                    grade__pk__in=[grade])

        # if topics_queryset:
        #     # lessons_queryset = None
        #     result = self.process_topics(
        #         topics_queryset, grade)

    return topics_queryset


class ListDashboardAPI(mixins.CreateModelMixin, mixins.ListModelMixin,  mixins.RetrieveModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView):
    queryset = Lesson.objects.all().order_by('num')
    serializer_class = LessonSerializer
    # filterset_fields = ['grade', 'subject', 'topic', 'lesson']
    # ordering_fields = ['title', 'topic']
    # search_fields = ['title', 'descriptions', 'topic', 'lesson', 'tags', 'subject__name', 'subject__description', 'grade__name', 'grade__description']
    permission_classes = [AllowAny]

    @staticmethod
    def custom_cache_key(*args):
        return "_".join(map(str, args[1:]))

    @staticmethod
    def createTopicsDict(topics_queryset: QuerySet[Topic]):
        topics_dict = {}
        for topic in topics_queryset:
            topics_dict[topic] = []

        return topics_dict

    @staticmethod
    # @lru_cache
    def getSubjectTopics(subject: int, grade: int) -> QuerySet[Topic]:
        # result = []
        topics_queryset = Topic.objects.none()
        if subject:

            try:
                topics_queryset = Topic.objects.filter(subject=subject)
                if grade:
                    topics_queryset = topics_queryset.filter(
                        grade__pk__in=[grade])
            except Exception as ex:
                logging.error('getSubjectTopics error: ', ex)

        return topics_queryset

    @staticmethod
    def getSubjectLessons(subject: int, grade: int) -> QuerySet[Lesson]:
        # print('processing.......')

        lessons_queryset = Topic.objects.none()
        if subject:
            try:
                if grade:
                    lessons_queryset = Lesson.objects.filter(Q(subject=subject) & Q(
                        grade__pk=grade) & Q(is_active=True) & Q(topic__is_active=True)).prefetch_related('topic', 'subject').order_by('num', 'topic__chapter').distinct()

                    # lessons_queryset = Lesson.objects.filter(subject=subject,
                    #                                          grade__pk=grade).prefetch_related('topic', 'subject')
                else:
                    lessons_queryset = Lesson.objects.filter(
                        subject=subject, is_active=True, topic__is_active=True).prefetch_related('topic', 'subject').order_by('num', 'topic__chapter').distinct()

            except Exception as ex:
                logging.error('getSubjectLessons error: ', ex)

        # print("lessons_queryset: ", lessons_queryset)
        return lessons_queryset

    @staticmethod
    def getLessonTopics(lessons: QuerySet[Lesson]) -> Dict[Topic, List[Lesson]]:
        # topics_lesson: Dict[Topic, List[Lesson]] = {}
        topics_lesson = OrderedDict()

        for lesson in lessons:
            topics_lesson[lesson.topic] = topics_lesson.get(
                lesson.topic, []) + [lesson]
        # res = OrderedDict(sorted(topics_lesson.items(),
        #                          key=lambda item: item[0]))
        # return OrderedDict(sorted(topics_lesson.items()))
        return topics_lesson

    @staticmethod
    def getLessonTopics2(lessons: QuerySet[Lesson]) -> Dict[Topic, List[Lesson]]:
        topics_lesson: Dict[Topic, List[Lesson]] = {}

        # Define a function to process a single lesson
        def process_lesson(lesson: Lesson) -> None:
            # print('lessons: ', lesson.title)
            topic = lesson.topic
            if topic not in topics_lesson:
                topics_lesson[topic] = []

            topics_lesson[topic].append(lesson)

        # Use ThreadPoolExecutor to parallelize the processing of lessons
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(process_lesson, lessons)

        # print(topics_lesson)
        return dict(sorted(topics_lesson.items()))

    @staticmethod
    def makeLessons(lessons, topics_dict: dict) -> dict:
        def process_lesson(lesson):
            topic = lesson.topic
            val = topics_dict.get(topic)
            if val is not None:
                topics_dict[topic].append(lesson)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(process_lesson, lessons)

        return topics_dict

    def processLessons(self, topics_dict: dict) -> list:
        topics_lessons = []

        def process_topic(topic):
            lessons_queryset = topics_dict[topic]
            if lessons_queryset:
                serialized_lessons = self.get_serializer(
                    lessons_queryset, many=True).data
                serialized_topic = TopicSerializer(topic).data

                topics_lessons.append(
                    {"title": serialized_topic, "data": serialized_lessons})

        # Use ThreadPoolExecutor to parallelize the processing of topics
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(process_topic, topics_dict.keys())

        return sorted(topics_lessons, key=lambda item: item['title']['chapter'])

    @staticmethod
    @lru_cache
    def processSubject(subject: int, grade: int) -> dict:
        # print("getSubjectTopics.........", subject, grade)

        lessons = ListDashboardAPI.getSubjectLessons(subject, grade)
        topics_dict = ListDashboardAPI.getLessonTopics(lessons)
        # print("topics_dict: ", topics_dict)
        return topics_dict

    @lru_cache
    def process_topic(self, topic, grade=None):
        lessons = []
        lessons_queryset = topic.topic_lessons.all().distinct('pk')
        if not lessons_queryset.exists():
            lessons_queryset = Lesson.objects.filter(
                topic__title__iexact=topic.title)
        if grade:
            lessons_queryset = lessons_queryset.filter(
                grade__pk=grade)

        # logger.info('lessons_queryset: ', lessons_queryset, topic, topic.pk)

        serialized_lessons = self.get_serializer(
            lessons_queryset, many=True).data
        serialized_topic = TopicSerializer(topic).data

        return {"title": serialized_topic, "data": serialized_lessons} if serialized_lessons else {}

    # @lru_cache
    def process_topics(self, topics_queryset, grade=None):
        topics_set = set()
        topics_lessons = []
        # logger.info('topics', topics_queryset.all())

        # Function to process each topic concurrently
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_topic = {executor.submit(
                self.process_topic, topic, grade): topic for topic in topics_queryset.all()}
            for future in concurrent.futures.as_completed(future_to_topic):
                topic = future_to_topic[future]
                try:
                    obj = future.result()
                    if obj and topic.id not in topics_set:
                        topics_set.add(topic.id)
                        topics_lessons.append(obj)
                except Exception as exc:
                    print(f"Exception occurred while processing topic: {exc}")

        return topics_lessons

    def get(self, request, *args, **kwargs):
        student = platform = None
        serialized_recent = []
        serialized_subjects = []
        serialized_recommend = []
        topics_lessons = []
        recommend_arr = []
        subjects_arr = []
        result = []
        subscriptions = []
        page = 0
        subject = kwargs.get('subject')
        grade = kwargs.get('grade')
        grade_params = request.query_params.get('grade')
        platform = request.query_params.get('platform', '')
        # print("platform: ", grade_params)
        if not grade:
            grade = grade_params

        if grade is not None:
            grade = int(grade)
        user = request.user if request.user else None
        print('USER: ', grade)
        try:
            # print(user, user.is_authenticated, user.username)
            if user and user.is_authenticated:
                subscriptions = getValidSubscriptions(user)
                # print("subscriptions: ", subscriptions)
                # subscriptions = user.subscriptions_user.filter(
                #     Q(payment_method__expires_date__gt=timezone.now())
                # ).order_by("-created")

                student = Student.objects.get(phone_number=user.username)
                # print("student: ", subscriptions)

            if student and not grade:
                try:
                    grade = Grade.objects.get(name=student.grade)
                    grade = grade.pk

                except Grade.DoesNotExist as ex:
                    print('grade object error: ', ex)

            # when a subject is selected
            # print("grade: ", grade)
            # LessonScreen().get_object()
            if subject:
                topics_dict = ListDashboardAPI.processSubject(subject, grade)
                result = self.processLessons(topics_dict)
                # topics_queryset = getSubjectTopics(subject, grade)
                #     topics_queryset = None
                #     subject_instance = None
                #     try:
                #         subject_instance = Subject.objects.get(pk=subject)
                #     except Subject.DoesNotExist as ex:
                #         logging.error('subject object error: ', ex)
                #     # print("subject_instance: ", subject_instance)
                #     if subject_instance:
                #         topics_queryset = subject_instance.subject_topics.all()
                #         # print("topics_queryset: ", topics_queryset)
                #         if grade:
                #             topics_queryset = topics_queryset.filter(
                #                 grade__pk__in=[grade])

                # if topics_queryset:
                #     # lessons_queryset = None
                #     result = self.process_topics(
                #         topics_queryset, grade)
                # result_set = set()
                # result_data = []
                # for res in result:
                #     if res.get('title').get('title') not in result_set:
                #         result_set.add(res.get('title').get('title'))
                #         result_data.append(res)

                # topics_set = set()
                # # lessons_set = set()
                # for topic in topics_queryset.all():
                #     if topic.id not in topics_set:
                #         topics_set.add(topic.id)
                #         lessons_queryset = topic.topic_lessons
                #         if grade:
                #             lessons_queryset = lessons_queryset.filter(
                #                 grade__pk=grade).distinct('pk')
                #         serialized_lessons = self.get_serializer(
                #             lessons_queryset, many=True).data
                #         serialized_topic = TopicSerializer(topic).data
                #         obj = {"title": serialized_topic,
                #                "data": serialized_lessons}
                #         topics_lessons.append(obj)
                # result = topics_lessons

                # per_page = 5
                # if not page:
                #     page = 1
                # paginator = Paginator(result, per_page=per_page)
                # try:
                #     result = paginator.page(number=1)
                # except EmptyPage:
                #     result = None

                # page = self.paginate_queryset(result)
                # print("page: ", page, result)
                # if page:
                #     serializer = TopicSerializer(page, many=True)
                #     print("lessons_array: ",
                #           self.get_paginated_response(json.dumps(page)))
                # return self.get_paginated_response(json.dumps(page))
                # print('RESULT: ', result)
                return Response(result)

        except Student.DoesNotExist as ex:
            print('student object error: ', ex)
        except Subject.DoesNotExist as ex:
            print('subject object error: ', ex)
        except Exception as ex:
            print("dashboard Error: ", ex)

        # main dashboard
        try:
            # recent interactions section
            cols = 2
            # if user and user.is_authenticated:
            # user_interactions = Interaction.objects.filter(
            #     user=user).order_by('-created')
            # top_3_queryset = self.process_user_interactions(user)
            # user_interactions = user.interactions.all()

            # recent_queryset = user_interactions.select_related(
            #     'video').exclude(video__isnull=True).order_by('-created')
            # # recent_queryset = recent_queryset.filter(
            # #     user=user).distinct('id')
            # query_array = []
            # existing_set = set()

            # for recent in recent_queryset:
            #     video_pk = recent.video.pk
            #     if video_pk not in existing_set:
            #         existing_set.add(video_pk)
            #         query_array.append(recent.video.lesson)

            # top_3_queryset = query_array[:3]

            # print('interaction: ', top_3_queryset)
            # serialized_recent = self.get_serializer(
            #     top_3_queryset, many=True, context={'request': request}).data

        except Exception as ex:
            print("Recent Error: ", ex)

        try:
            # subjects section
            subjects_arr = ListDashboardAPI.processDashBoardSubjects(
                grade, platform, cols)
            # print('SUBJECTS>>>')
            # subjects_queryset = Subject.objects.filter(
            #     is_active=True).order_by('num')
            # # print('GRADE: ', grade)
            # if grade and subjects_queryset.exists():
            #     queryset = subjects_queryset.filter(
            #         grade__in=[grade])
            #     if queryset.exists():
            #         subjects_queryset = queryset
            #     # print('subjects_queryset', subjects_queryset.all())
            # serialized_subjects = SubjectSerializer(
            #     subjects_queryset, many=True).data

            # if platform:
            #     for i in range(0, len(serialized_subjects), cols):
            #         subjects_arr.append(serialized_subjects[i: i+cols])

            # print("serialized_subjects: ", result)

        except Exception as ex:
            print("Subjects Error: ", ex)

        try:
            # recommendations section
            recommend_arr = self.processRecommended(
                grade, platform, cols, request)
            # recommend_queryset = []
            # recommend_queryset = Video.objects.select_related(
            #     'subject').filter(tags__icontains='recommend')
            # if grade:
            #     queryset = Video.objects.all().select_related(
            #         'subject').filter(tags__icontains='recommend', grade__pk=grade)
            #     if queryset.exists():
            #         recommend_queryset = queryset
            # # print((recommend_queryset))
            # # lesson_array = []
            # # existing_set = set()
            # # for video in recommend_queryset:
            # #     if video.pk not in existing_set and video.lesson:
            # #         existing_set.add(video.pk)
            # #         lesson_array.append(video.lesson)
            # lesson_array = self.process_recommend(recommend_queryset)
            # # print("lesson_array: ", lesson_array)
            # serialized_recommend = self.get_serializer(
            #     lesson_array[:6], many=True, context={'request': request}).data

            # if platform:
            #     for i in range(0, len(serialized_recommend), cols):
            #         recommend_arr.append(serialized_recommend[i: i+cols])

            # if subscriptions.exists():
            # updateIsSubscribed(serialized_recommend, subscriptions)
            # print('serialized_recommend: ', recommend_arr)

        except Exception as ex:
            print("Recommend Objects Error: ", ex)

        result = [
            # {
            #     "title": 'Recent',
            #     "data": serialized_recent if serialized_recent else serialized_recommend,
            #     "is_subscribed": len(subscriptions) > 0
            # },
            {
                "title": 'Subjects',
                "data": subjects_arr,
                "columns": 2,
                "grade": grade,
                "is_subscribed": len(subscriptions) > 0

            },

            {
                "title": 'Recommended',
                "data": recommend_arr if recommend_arr else serialized_recommend
            },
        ]
        # print('RESPONSE: ', result)
        return Response(result)

    def processRecommended(self, grade: int, platform: str, cols, request) -> list:
        # recommend_arr = []
        serialized_recommend = []
        try:
            # recommendations section
            # recommend_queryset = []
            # recommend_queryset = Video.objects.select_related(
            #     'subject').filter(tags__icontains='recommend')
            # if grade:
            #     queryset = Video.objects.all().select_related(
            #         'subject').filter(tags__icontains='recommend', grade__pk=grade)
            #     if queryset.exists():
            #         recommend_queryset = queryset

            lesson_array = ListDashboardAPI.process_recommend(grade)
            serialized_recommend = self.get_serializer(
                lesson_array[:6], many=True, context={'request': request}).data

            if platform == IOS or platform == ANDROID:
                recommend_arr = [serialized_recommend[i: i+cols]
                                 for i in range(0, len(serialized_recommend), cols)]
                # for i in range(0, len(serialized_recommend), cols):
                #     recommend_arr.append(serialized_recommend[i: i+cols])

                return recommend_arr

        except Exception as ex:
            print("Recommend Objects Error: ", ex)

        # print('TESTINGS serialized_recommend>>>', serialized_recommend)

        return serialized_recommend

    def process_user_interactions(self, user):

        user_interactions = user.interactions.all()
        recent_queryset = user_interactions.select_related(
            'video').exclude(video__isnull=True).order_by('-created')

        # ... (rest of the code)

        # Set the number of threads you want to use for concurrent processing
        num_threads = 4  # You can adjust this number based on your requirements

        # Use ThreadPoolExecutor to parallelize the operation
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            # Define a function that retrieves the lesson from a single user interaction
            def get_lesson_from_interaction(user_interaction, existing_set):
                video_pk = user_interaction.video.pk
                if video_pk not in existing_set:
                    existing_set.add(video_pk)
                    return user_interaction.video.lesson
                return None

            # Create a set to keep track of existing video primary keys
            existing_set = set()

            # Use submit to asynchronously submit the tasks to the thread pool
            futures = [executor.submit(
                get_lesson_from_interaction, interaction, existing_set) for interaction in recent_queryset]

            # Use as_completed to retrieve the results as they complete
            top_3_lessons = [future.result() for future in concurrent.futures.as_completed(
                futures) if future.result() is not None]

            # Get the top 3 lessons from the processed list
            return top_3_lessons[:3]

    @lru_cache
    def process_recommend(grade: int) -> List:
        print('process_recommend: ', grade)
        num_threads = 4  # You can adjust this number based on your requirements

        recommend_queryset = []
        recommend_queryset = Video.objects.select_related(
            'subject').filter(tags__icontains='recommend')
        if grade:
            queryset = Video.objects.all().select_related(
                'subject').filter(tags__icontains='recommend', grade__pk=grade)
            if queryset.exists():
                recommend_queryset = queryset

        # Use ThreadPoolExecutor to parallelize the operation
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            # Define a function that retrieves the lesson from a single video
            def get_lesson_from_video(video, existing_set):
                try:
                    if video.pk not in existing_set and video.lesson:
                        existing_set.add(video.pk)
                        return video.lesson
                except Exception as ex:
                    print(f"Error while processing video {video.pk}: {ex}")
                return None

            # Create a set to keep track of existing video primary keys
            existing_set = set()

            # Use submit to asynchronously submit the tasks to the thread pool
            futures = [executor.submit(
                get_lesson_from_video, video, existing_set) for video in recommend_queryset]

            # Use as_completed to retrieve the results as they complete
            return [future.result() for future in concurrent.futures.as_completed(futures) if future.result() is not None]

    @lru_cache
    def processDashBoardSubjects(grade: int, platform: str, cols: int) -> list:
        print("processDashBoardSubjects..........", grade)
        # subjects_arr = []
        subjects_queryset = []
        try:
            if grade > 3:
                subjects_queryset = Subject.objects.filter(
                    is_active=True, grade__pk=grade).prefetch_related('grade').order_by('num').distinct()
            # else:
            #     subjects_queryset = Subject.objects.filter(
            #         is_active=True).prefetch_related('grade').order_by('num').distinct()

            # if grade and subjects_queryset.exists():
            #     queryset = subjects_queryset.filter(
            #         grade__pk__contains=grade)
            #     if queryset.exists():
            #         subjects_queryset = queryset
        except Exception as ex:

            logging.error(f"processDashBoardSubjects: Subject error, {ex}")

        serialized_subjects = SubjectSerializer(
            subjects_queryset, many=True).data

        if platform == IOS or platform == ANDROID:
            subjects_pair_arr = [serialized_subjects[i: i+cols]
                                 for i in range(0, len(serialized_subjects), cols)]
            # for i in range(0, len(serialized_subjects), cols):
            #     subjects_arr.append(serialized_subjects[i: i+cols])
            # print(subjects_pair_arr)

            return subjects_pair_arr
        return serialized_subjects


def updateIsSubscribed(serialized_item, subscriptions):

    for obj in serialized_item:
        # print('subscriptions: ', obj.get('grade'))
        valid_subscription = subscriptions.filter(
            Q(grade__grades__contains=obj.get('grade'))
        )
        if valid_subscription.exists():
            obj['is_subscribed'] = True


class ListDashboardLessonsAPI(mixins.CreateModelMixin, mixins.ListModelMixin,  mixins.RetrieveModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView):
    queryset = Lesson.objects.all().order_by('num')
    serializer_class = LessonSerializer
    # lookup_field = 'pk'

    def get(self, request, *args, **kwargs):
        student = None
        result = []
        grade_packs = []
        # queryset = []
        queryset = []
        serialized_lessons = []
        serialized_videos = []

        topic = kwargs.get('pk')
        grade = kwargs.get('grade')
        lesson = kwargs.get('lesson')
        if grade is not None:
            grade = int(grade)

        user = request.user if request.user else None
        # print("user: ", user.username, lesson)
        try:
            if user and user.is_authenticated:
                try:
                    student = Student.objects.get(phone_number=user.username)
                except Student.DoesNotExist as ex:
                    print("Student Error: ", ex)

                if student and not grade:

                    try:
                        grade = Grade.objects.get(name=student.grade)
                        grade = grade.pk
                    except Grade.DoesNotExist as ex:
                        print('grade object error: ', ex)

                    # if not grade:
                subscriptions = getValidSubscriptions(user)
                if subscriptions:
                    subscription = subscriptions.first()
                    grade_packs = subscription.grade

            # if topics are requested
            if topic:
                lessons_queryset = []
                try:
                    topic_obj = Topic.objects.get(pk=topic)
                    if topic_obj:
                        lessons_queryset = topic_obj.topic_lessons.all()

                except Topic.DoesNotExist as ex:
                    print('topic object error: ', ex)

                if grade_packs and lessons_queryset:
                    queryset = lessons_queryset.filter(
                        grade__in=grade_packs.grades)

                if grade and not queryset.exists():
                    queryset = lessons_queryset.filter(grade__pk=grade)

                lessons_queryset = queryset

                if lessons_queryset:
                    serialized_lessons = self.get_serializer(
                        lessons_queryset, many=True).data
                result = [
                    {
                        "title": 'Lessons',
                        "data": serialized_lessons,
                    }
                ]

            # if lessons are selected
            if lesson:
                videos_queryset = Video.objects.none()
                try:
                    lesson_obj = self.get_queryset().get(pk=lesson)
                    # print('videos_queryset2: ', lesson_obj)
                    if lesson_obj:
                        videos_queryset = lesson_obj.lesson_videos.all()
                        if videos_queryset:
                            videos_queryset = videos_queryset.filter(
                                title=lesson_obj.title, topic=lesson_obj.topic, subject=lesson_obj.subject, grade__pk=grade)

                    # print('videos_queryset2: ', videos_queryset)

                    if not videos_queryset:
                        videos_queryset = Video.objects.filter(
                            title=lesson_obj.title, topic=lesson_obj.topic, subject=lesson_obj.subject, grade__pk__contains=grade)

                except Lesson.DoesNotExist as ex:
                    print('lesson object error: ', ex)

                # print('videos_queryset1: ', videos_queryset)

                # if grade_packs and videos_queryset:
                #     queryset = videos_queryset.filter(
                #         grade__in=grade_packs.grades)

                # print("queryset: ", len(queryset))

                # if grade and not queryset:
                #     queryset = videos_queryset.filter(grade__pk=grade)

                # videos_queryset = queryset
                # if grade and videos_queryset:
                #     videos_queryset = videos_queryset.filter(
                #         grade__pk=grade)

                if videos_queryset:
                    serialized_videos = VideoSerializer(
                        videos_queryset.first(), context={'request': request}).data
                # result = {
                #         "title": 'Lesson',
                #         "data" : serialized_videos,
                #     }
                # for video in serialized_videos:
                # print('videos_queryset3: ',
                #       serialized_videos.get('is_subscribed'))

                result = serialized_videos

        except Exception as ex:

            print("Lessons Error: ", ex)

        # print('LESSON RESULT: ', result)
        return Response(result)


class ListTopicLessonAPI(mixins.CreateModelMixin, mixins.ListModelMixin,  mixins.RetrieveModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView):
    queryset = Lesson.objects.all().order_by('pk')
    serializer_class = LessonSerializer
    # lookup_field = 'pk'

    def get(self, request, *args, **kwargs):
        student = None
        grade_packs = []
        serialized_lessons = []

        # topic = kwargs.get('pk')
        grade = kwargs.get('grade')
        lesson = kwargs.get('lesson')
        if grade is not None:
            grade = int(grade)

        user = request.user if request.user else None
        # print("user: ", user.username, lesson, grade)
        try:
            if user and user.is_authenticated:
                try:
                    student = Student.objects.get(phone_number=user.username)
                except Student.DoesNotExist as ex:
                    print("Student Error: ", ex)

                if student and not grade:

                    try:
                        grade = Grade.objects.get(name=student.grade)
                        grade = grade.pk
                    except Grade.DoesNotExist as ex:
                        print('grade object error: ', ex)

                    # if not grade:
                subscriptions = getValidSubscriptions(user)
                if subscriptions:
                    subscription = subscriptions.first()
                    grade_packs = subscription.grade

            # if lessons are selected
            if lesson:
                lessons_queryset = []
                # videos_list = []
                lessons_queryset_grades = []
                try:
                    lesson_obj = self.get_queryset().filter(pk=lesson)
                    if lesson_obj.exists():
                        lesson_obj = lesson_obj.first()
                        lessons_queryset = lesson_obj.topic.topic_lessons.all()
                    # print("lesson_obj: ", lessons_queryset)
                    if grade_packs and lessons_queryset:
                        lessons_queryset_grades = lessons_queryset.filter(
                            grade__in=grade_packs.grades).distinct('num').exclude(pk=lesson_obj.pk)

                    if grade and not lessons_queryset_grades:
                        lessons_queryset_grades = lessons_queryset.filter(
                            grade__pk=grade).distinct('num').exclude(pk=lesson_obj.pk)

                except Lesson.DoesNotExist as ex:
                    print('lesson/topic object error: ', ex)

                serialized_lessons = self.get_serializer(
                    lessons_queryset, many=True, context={'request': request}).data

                # serialized_lessons = self.get_serializer(
                #     lessons_queryset_grades, many=True, context={'request': request}).data

        except Exception as ex:

            print("Lessons Error: ", ex)

        # print('RESULT: ', serialized_lessons)
        return Response(data=serialized_lessons)


class ListCreateThumbnailAPI(mixins.CreateModelMixin, mixins.ListModelMixin,  mixins.RetrieveModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView):
    queryset = Thumbnail.objects.all()
    serializer_class = ThumbnailSerializer

    def bucket_images(self, subject: Subject, folder: str) -> list:
        data = []
        if subject and folder:
            repo = GoogleCloudStorageRepo2(
                f"img/subjects/{subject.code}/{folder}", "edufox-bucket-2", 3600 * 3)
            image_objects = GoogleImageStore(repo)
            blobs = image_objects.list_images_in_bucket()

            for blob in blobs:
                if blob.content_type.startswith('image/') and blob.public_url:
                    public_url = blob.public_url
                    print('public_url: ', public_url[-1: -4: -1][:: -1])
                    # image_type = 'png' if 'png' in public_url else 'svg'
                    data.append(
                        {"subject": subject.pk, "url": public_url, "image_type": public_url[-1: -4: -1][:: -1]})

        return data

    def get(self, request, *args, **kwargs):
        subject_instance = ''
        subject = kwargs.get('subject_pk')
        data = []
        headers = {}
        if subject:
            subject_instance = Subject.objects.get(pk=subject)

        if subject_instance:
            data: list = self.bucket_images(subject_instance, 'png')
            data_svg: list = self.bucket_images(subject_instance, 'svg')
            data.extend(data_svg)

            serializer = self.get_serializer(
                data=data, many=True, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            data = serializer.data
            headers = self.get_success_headers(data)

            return Response(data, status=status.HTTP_201_CREATED, headers=headers)

        return Response({})

        #         serializer = self.get_serializer(instance)
        #         Response(serializer.data)
        #     return self.retrieve(request, *args, **kwargs)

        # return self.list(request, *args, **kwargs)

    # def post(self, request, *args, **kwargs):
    #     if not kwargs.get('pk') and request.user.is_staff:
    #         subject = request.POST.get('subject')
    #         items = request.POST.getlist('items')

    #             return self.create(request, *args, **kwargs)
    #         headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def put(self, request, *args, **kwargs):
        if kwargs.get('pk') and request.user.is_staff:
            return self.update(request, *args, **kwargs)
        return None


class VideoSearchListViewAPI(generics.ListAPIView):
    queryset = Video.objects.select_related(
        'subject', 'topic', 'lesson').all().order_by('pk').distinct()
    serializer_class = VideoSerializer()
    # filter_backends = [filters.SearchFilter]
    search_fields = ['tags', 'title', 'description', 'lesson__title',
                     'topic__title', 'subject__name', 'subject__description', 'grade__name', 'grade__code', 'grade__description']

    def __hash__(self) -> int:
        return hash('VideoSearchListViewAPI')

    def list(self, request, *args, **kwargs):
        grade = request.query_params.get('grade')
        query = request.query_params.get('search')
        queryset = self.filter_queryset(self.get_queryset())
        user = request.user

        if grade is not None:
            grade = int(grade)

        if user and user.is_authenticated:

            student = Student.objects.get(phone_number=user.username)
            # print("student: ", student, grade, not grade == False)
            if student and not grade:
                try:
                    grade = Grade.objects.get(name=student.grade)
                    grade = grade.pk

                except Grade.DoesNotExist as ex:
                    print('grade object error: ', ex)

        #         # print("grade 2: ", grade)

        # if grade:
        #     queryset = queryset.filter(grade__pk__contains=grade).prefetch_related(
        #         'lesson', 'topic', 'subject', 'grade')

        # # lessons_set = set()
        # lessons_array = [query.lesson for query in queryset]

        # for query in queryset:
        #     if query.pk not in lessons_set and query.lesson:
        #         lessons_set.add(query.pk)
        #         lessons_array.append(query.lesson)

        # page = self.paginate_queryset(lessons_array)

        # if page is not None:
        #     serializer = LessonSerializer(page, many=True)
        #     # print("lessons_array: ", self.get_paginated_response(serializer.data))
        #     return self.get_paginated_response(serializer.data)
        lessons_array = VideoSearchListViewAPI.getLessons(queryset, grade)
        serialized_lessons = LessonSerializer(
            lessons_array, many=True, context={'request': request}).data
        # lessons_arr = []
        cols = 2
        lessons_arr = [serialized_lessons[i: i+cols]
                       for i in range(0, len(serialized_lessons), cols)]

        subjects_arr = VideoSearchListViewAPI.get_subjects(
            user, grade, query, cols)

        result = [
            {
                "title": 'Subjects' if len(subjects_arr) else '',
                "data": subjects_arr,

            },
            {
                "title": "Lessons" if len(lessons_arr) else '',
                "data": lessons_arr
            }
        ]
        # print(result)
        self.saveQuery(query, user)
        return Response(result)

    def saveQuery(self, query: str, user: User) -> None:
        data = {"query": query}

        try:
            serializer = SearchQuerySerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user)

        except Exception as ex:
            print("Lessons Error: ", ex)

    def getLessons(queryset, grade):
        # print("getLessons..........")
        if grade and queryset.exists():
            queryset = queryset.filter(grade__pk__contains=grade).prefetch_related(
                'lesson', 'topic', 'subject', 'grade')

        return [query.lesson for query in queryset]

    @lru_cache
    def get_subjects(user, grade, search_query, cols=1):
        # print("get_subjects..........")
        serialized_subjects = []
        subjects_queryset = []
        subjects_arr = []

        if search_query:
            try:
                if grade:
                    subjects_queryset = Subject.objects.filter(
                        name__icontains=search_query, grade__pk__contains=grade).prefetch_related('grade')
                else:
                    subjects_queryset = Subject.objects.filter(
                        name__icontains=search_query).prefetch_related('grade')

                serialized_subjects = SubjectSerializer(
                    subjects_queryset, many=True).data

                subjects_arr = [serialized_subjects[i: i+cols]
                                for i in range(0, len(serialized_subjects), cols)]

            except Subject.DoesNotExist as ex:
                print('get_subjects error: ', ex)

        return subjects_arr

    def get(self, request, *args, **kwargs):
        if kwargs.get('pk') is not None:
            return self.retrieve(request, *args, **kwargs)

        return self.list(request, *args, **kwargs)
# @api_view(['GET'])
# @permission_classes([AllowAny])
# def GenerateSignedUrl(request, *args, **kwargs) -> Response:


class ListCreateAPISearchQuery(mixins.CreateModelMixin, mixins.ListModelMixin,  mixins.RetrieveModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView):
    queryset = SearchQuery.objects.all().order_by('query').distinct()
    serializer_class = SearchQuerySerializer
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


class GenerateSignedUrl(generics.GenericAPIView):
    '''
    Get the signed URL for the requested resource
    provide subject_code and video_id
    '''

    def get(self, request, *args, **kwargs) -> Response:

        signed_url = ''
        # print(self.request.user)
        # amazondb = AmazonDynamoDBRepo('7a935736-bd4c-4f9d-8ba5-4803f789970b')
        # amazondb.getSignedUrl()

        factory_stream = readRequest(request)
        if factory_stream:
            stream = factory_stream.getPlatformStream()
            signed_url = stream.getSignedUrl()
            # signed_url = "https://d3sf15wolo885z.cloudfront.net/out/v1/6f13342624a54b1e97d42d2ac1fcafef/4e1206dd7b4541959ba155f0a8c1f13a/f5e513f27e684e90b22ab100ad5de3b7/index.m3u8"
            # signed_url = "https://d3sf15wolo885z.cloudfront.net/out/v1/612676e447b241dc895a9c9fb6ebc4be/4e1206dd7b4541959ba155f0a8c1f13a/f5e513f27e684e90b22ab100ad5de3b7/index.m3u8"
            # signed_url = "https://d3sf15wolo885z.cloudfront.net/out/v1/451342fc17124367aa8d4bf2b770248e/4e1206dd7b4541959ba155f0a8c1f13a/f5e513f27e684e90b22ab100ad5de3b7/index.m3u8"
        print('SIGNED: ', signed_url)
        # signed_url = 'https://d1xjy7y2cyqkhc.cloudfront.net/3f8e8ff0-9bda-4c70-804a-d9f76b783b81/hls/PERSONAL_HYGIENE.m3u8'
        # signed_url = "https://d3sf15wolo885z.cloudfront.net/1a863c3d-0cb3-4e6f-ba47-48b4b05e1ad4/hls/PERSONAL_HYGIENE.m3u8"
        # signed_url = "https://d3sf15wolo885z.cloudfront.net/14d2cb7f-1a4d-4837-abff-673f45127c80/hls/VERBS.m3u8"
        # signed_url = "https://d3sf15wolo885z.cloudfront.net/out/v1/7b4d21343f8e4ef6a89dcc68c6d96c90/4e1206dd7b4541959ba155f0a8c1f13a/f5e513f27e684e90b22ab100ad5de3b7/index.m3u8"
        return Response({
            'signed_url': signed_url,
        })


def readRequest(request) -> PlatformStream:
    print("video_id: ", request)
    data = request.GET
    subject = data.get('subject')
    video_id = data.get('video_id')
    platform = data.get('platform')
    subject_code = get_first_obj(subject)
    print("video_id: ", video_id)
    hls_url = getVideoUrl('url', video_id=video_id)

    url = AmazonDynamoDBRepo().getHlsUrl(video_id)

    subscription = MySubscription(request.user, video_id)

    # print(subscription.isValidSubForVideo())
    # if subscription and not subscription.isValidSubForVideo():
    #     return ''

    if url and hls_url:
        return getStream(hls_url, datetime.datetime.now() + datetime.timedelta(hours=3))
        # return AmazonDynamoDBHLSStream(hls_url, datetime.datetime.now() + datetime.timedelta(hours=3))

    return ''

    # path = f"lessons-videos/{subject_code}/{video_id}"
    # print('PATH: ', path)
    # # factory = {IOS: HLSStream(path), ANDROID: HLSStream(
    # #     path), WEB: HLSStream(path)}
    # factory = {IOS: HLSWebStream(path, "edufox-bucket-2"), ANDROID: HLSWebStream(
    #     path, "edufox-bucket-2"), WEB: HLSWebStream(path, "edufox-bucket-2")}

    # return factory.get(platform) if platform and platform in factory else factory.get(WEB)


def getStream(hls_url: str, duration: datetime):
    return AmazonDynamoDBHLSStream(hls_url, datetime.datetime.now() + datetime.timedelta(hours=3))


@lru_cache
def get_first_obj(subject):
    # print('get_first_obj......')
    subject_code = ''
    # subject_obj = Subject.objects.all().filter(**kwargs)
    subject_obj = Subject.objects.all().filter(pk=subject)
    if subject_obj.exists():
        subject_code = subject_obj.first().code
    return subject_code


@lru_cache
def getVideoUrl(prop: str, video_id: str) -> str:
    try:
        obj_instance = Video.objects.filter(video_id=video_id)
        if obj_instance.exists():
            if prop == 'url':
                hls_url = obj_instance.first().url
                hls_url2 = obj_instance.first().url2
                return hls_url if hls_url else hls_url2
    except Video.DoesNotExist as ex:
        logging.error(f"getVideoUrl: video does not exist, {ex}")
    except Exception as ex:
        logging.error(f"getVideoUrl: {ex}")
    return ''


def getValidSubscriptions(user):
    subscription = MySubscription(user)
    return subscription.get_all_user_subscriptions()
    # return subscription.get_user_subscriptions()
    # subscriptions = user.subscriptions_user.filter(Q(payment_method__expires_date__gt=timezone.now())
    #    ).order_by("-created")
    # return subscriptions


# def isValidSubscription(subscriptions, video_id, user):
#     grades = ''
#     subscriptions = getValidSubscriptions(user)
#     video_obj = Video.objects.get(video_id=video_id)
#     if video_obj:
#         grades = video_obj.grade.all()
#         video_grades = [grade.pk for grade in grades]

#     subscription_obj = subscriptions.filter(
#         Q(grade__grades__overlap=video_grades) &
#         Q(
#             payment_method__expires_date__gt=timezone.now())
#     )
#     if subscription_obj.exists():
#         return True
