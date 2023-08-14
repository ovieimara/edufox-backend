import abc
import datetime
import json
from logging import Filter
import logging
from multiprocessing import set_forkserver_preload
from re import sub
from venv import create
from django.http import HttpRequest
from rest_framework import filters
import copy
import os
from django.shortcuts import render
from rest_framework import generics, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly, AllowAny
from yaml import serialize
from course.abc import BatchVideos, CreateMultipleLessons
from edufox.constants import ANDROID, IOS, WEB
from django.core.paginator import Paginator, EmptyPage
from edufox.views import printOutLogs, update_user_data
from subscribe.abc import MySubscription
from subscribe.models import Subscribe
from .models import (Grade, Event, Lesson, Subject, Lecturer, Video,
                     Rate, Comment, Interaction, Resolution, Topic)
# from assess.models import  Test, Assessment
from .serializers import (EventSerializer, GradeSerializer, SubjectSerializer, LecturerSerializer, VideoSerializer, RateSerializer, CommentSerializer,
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
from client.library import AWSSignedURLGenerator, AmazonDynamoDBHLSStream, AmazonDynamoDBRepo, HLSWebStream, StorageRepoABC, GoogleCloudStorageRepo, DashStream, HLSStream, PlatformStream
from django.conf import settings as django_settings
from edufox.constants import platforms
from abc import ABC, abstractmethod
import concurrent.futures

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
        video = request.data.get('video')
        event = request.data.get('event')
        video_queryset = Video.objects.filter(pk=video)
        event_queryset = Event.objects.filter(pk=event)
        if event_queryset.exists():
            event = event_queryset.first()
        if video_queryset.exists():
            video = video_queryset.first()

        serializer = self.get_serializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(video=video, event=event)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


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
                data=videos, many=True)
            # print('videos_serializer: ', videos_serializer.initial_data)

            videos_serializer.is_valid(raise_exception=True)
            # videos_data = videos_serializer.validated_data
            # print("videos_data: ", videos_data, type(videos_data))

            videos_serializer.save()
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
            logging.error(f"createVideos: Validation error: {ex.message}")

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


class ListDashboardAPI(mixins.CreateModelMixin, mixins.ListModelMixin,  mixins.RetrieveModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView):
    queryset = Lesson.objects.all().order_by('pk')
    serializer_class = LessonSerializer
    # filterset_fields = ['grade', 'subject', 'topic', 'lesson']
    # ordering_fields = ['title', 'topic']
    # search_fields = ['title', 'descriptions', 'topic', 'lesson', 'tags', 'subject__name', 'subject__description', 'grade__name', 'grade__description']
    permission_classes = [AllowAny]

    def process_topic(self, topic, grade=None):
        lessons_queryset = topic.topic_lessons
        if grade:
            lessons_queryset = lessons_queryset.filter(
                grade__pk=grade).distinct('pk')
        serialized_lessons = self.get_serializer(
            lessons_queryset, many=True).data
        serialized_topic = TopicSerializer(topic).data
        return {"title": serialized_topic, "data": serialized_lessons}

    def process_topics(self, topics_queryset, grade=None):
        topics_set = set()
        topics_lessons = []

        # Function to process each topic concurrently
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_topic = {executor.submit(
                self.process_topic, topic, grade): topic for topic in topics_queryset.all()}
            for future in concurrent.futures.as_completed(future_to_topic):
                topic = future_to_topic[future]
                try:
                    obj = future.result()
                    if topic.id not in topics_set:
                        topics_set.add(topic.id)
                        topics_lessons.append(obj)
                except Exception as exc:
                    print(f"Exception occurred while processing topic: {exc}")

        return topics_lessons

    def get(self, request, *args, **kwargs):
        student = None
        serialized_recent = []
        serialized_subjects = []
        serialized_recommend = []
        topics_lessons = []
        result = []
        subscriptions = []
        page = 0
        subject = kwargs.get('subject')
        grade = kwargs.get('grade')
        if grade is not None:
            grade = int(grade)
        user = request.user if request.user else None

        try:
            print(user, user.is_authenticated, user.username)
            if user and user.is_authenticated:
                subscriptions = getValidSubscriptions(user)
                # subscriptions = user.subscriptions_user.filter(
                #     Q(payment_method__expires_date__gt=timezone.now())
                # ).order_by("-created")

                student = Student.objects.get(phone_number=user.username)
                # print("student: ", subscriptions)

            # if student and not grade:
            #     try:
            #         grade = Grade.objects.get(name=student.grade)
            #         grade = grade.pk
            #     except Grade.DoesNotExist as ex:
            #         print('grade object error: ', ex)

            # when a subject is selected
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

                if topics_queryset:
                    # lessons_queryset = None
                    result = self.process_topics(
                        topics_queryset, grade)
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
                print('RESULT: ', result)
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

            if user and user.is_authenticated:
                # user_interactions = Interaction.objects.filter(
                #     user=user).order_by('-created')
                top_3_queryset = self.process_user_interactions(user)
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
                serialized_recent = self.get_serializer(
                    top_3_queryset, many=True, context={'request': request}).data

        except Exception as ex:
            print("Recent Error: ", ex)

        try:
            # subjects section
            subjects_queryset = Subject.objects.all()
            # print('GRADE: ', grade)
            if grade:
                queryset = subjects_queryset.filter(
                    grade__in=[grade])
                if queryset.exists():
                    subjects_queryset = queryset
                # print('subjects_queryset', subjects_queryset.all())
            serialized_subjects = SubjectSerializer(
                subjects_queryset, many=True).data
            # print("serialized_subjects: ", serialized_subjects)
        except Exception as ex:
            print("Subjects Error: ", ex)

        try:
            # recommendations section
            recommend_queryset = []
            recommend_queryset = Video.objects.select_related(
                'subject').filter(tags__icontains='recommend')
            if grade:
                queryset = Video.objects.all().select_related(
                    'subject', 'video').filter(tags__icontains='recommend', grade__pk=grade)
                if queryset.exists():
                    recommend_queryset = queryset
            # print((recommend_queryset))
            # lesson_array = []
            # existing_set = set()
            # for video in recommend_queryset:
            #     if video.pk not in existing_set and video.lesson:
            #         existing_set.add(video.pk)
            #         lesson_array.append(video.lesson)
            lesson_array = self.process_recommend(recommend_queryset)
            # print("lesson_array: ", lesson_array)
            serialized_recommend = self.get_serializer(
                lesson_array[:10], many=True, context={'request': request}).data

            # if subscriptions.exists():
            # updateIsSubscribed(serialized_recommend, subscriptions)
            # print('serialized_recommend: ', serialized_recommend)

        except Exception as ex:
            print("Recommend Objects Error: ", ex)

        result = [
            {
                "title": 'Recent',
                "data": serialized_recent if serialized_recent else serialized_recommend,
                "is_subscribed": len(subscriptions) > 0
            },
            {
                "title": 'Subjects',
                "data": serialized_subjects,
                "columns": 2,
                "grade": grade,

            },

            {
                "title": 'Recommended',
                "data": serialized_recommend
            },
        ]
        # print('RESPONSE: ', result)
        return Response(result)

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

    def process_recommend(self, recommend_queryset):
        num_threads = 4  # You can adjust this number based on your requirements

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


def updateIsSubscribed(serialized_item, subscriptions):

    for obj in serialized_item:
        print('subscriptions: ', obj.get('grade'))
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
        queryset = []
        queryset = []
        serialized_lessons = []
        serialized_videos = []

        topic = kwargs.get('pk')
        grade = kwargs.get('grade')
        lesson = kwargs.get('lesson')
        if grade is not None:
            grade = int(grade)

        user = request.user if request.user else None
        print("user: ", user.username, lesson)
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
                videos_queryset = []
                try:
                    lesson_obj = self.get_queryset().get(pk=lesson)
                    if lesson_obj:
                        videos_queryset = lesson_obj.lesson_videos.all()
                except Lesson.DoesNotExist as ex:
                    print('lesson object error: ', ex)

                # print('videos_queryset1: ', videos_queryset, grade_packs)

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

                # print('videos_queryset2: ', videos_queryset.grade.all())
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

        # print('RESULT: ', result)
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
                    lessons_queryset_grades, many=True, context={'request': request}).data

        except Exception as ex:

            print("Lessons Error: ", ex)

        # print('RESULT: ', serialized_lessons)
        return Response(serialized_lessons)


class VideoSearchListViewAPI(generics.ListAPIView):
    queryset = Video.objects.select_related(
        'subject', 'topic', 'lesson').all().order_by('pk')
    serializer_class = VideoSerializer()
    # filter_backends = [filters.SearchFilter]
    search_fields = ['tags', 'title', 'description', 'lesson__title',
                     'topic__title', 'subject__name', 'subject__description', 'grade__name', 'grade__code', 'grade__description']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        lessons_array = []
        lessons_set = set()
        for query in queryset:
            if query.pk not in lessons_set and query.lesson:
                lessons_set.add(query.pk)
                lessons_array.append(query.lesson)

        page = self.paginate_queryset(lessons_array)

        if page is not None:
            serializer = LessonSerializer(page, many=True)
            # print("lessons_array: ", self.get_paginated_response(serializer.data))
            return self.get_paginated_response(serializer.data)

        serializer = LessonSerializer(lessons_array, many=True)

        return Response(serializer.data)

    def get(self, request, *args, **kwargs):
        if kwargs.get('pk') is not None:
            return self.retrieve(request, *args, **kwargs)

        return self.list(request, *args, **kwargs)
# @api_view(['GET'])
# @permission_classes([AllowAny])
# def GenerateSignedUrl(request, *args, **kwargs) -> Response:


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
        print(signed_url)

        return Response({
            'signed_url': signed_url,
        })


def readRequest(request) -> PlatformStream:

    data = request.GET
    subject = data.get('subject')
    video_id = data.get('video_id')
    platform = data.get('platform')
    subject_code = get_first_obj(pk=subject)
    hls_url = getVideoUrl(Video, 'url', video_id=video_id)

    url = AmazonDynamoDBRepo().getHlsUrl(video_id)

    subscription = MySubscription(request.user, video_id)

    # print(subscription.isValidSubForVideo())
    # if subscription and not subscription.isValidSubForVideo():
    #     return ''

    if url and hls_url:
        return AmazonDynamoDBHLSStream(hls_url, datetime.datetime.now() + datetime.timedelta(hours=3))

    path = f"lessons-videos/{subject_code}/{video_id}"
    print('PATH: ', path)
    # factory = {IOS: HLSStream(path), ANDROID: HLSStream(
    #     path), WEB: HLSStream(path)}
    factory = {IOS: HLSWebStream(path, "edufox-bucket-2"), ANDROID: HLSWebStream(
        path, "edufox-bucket-2"), WEB: HLSWebStream(path, "edufox-bucket-2")}

    return factory.get(platform) if platform and platform in factory else factory.get(WEB)


def get_first_obj(**kwargs):
    subject_code = ''
    subject_obj = Subject.objects.all().filter(**kwargs)
    if subject_obj.exists():
        subject_code = subject_obj.first().code
    return subject_code


def getVideoUrl(obj: object, prop, **kwargs) -> str:
    try:
        obj_instance = obj.objects.filter(**kwargs)
        if obj_instance.exists():
            if prop == 'url':
                hls_url = obj_instance.first().url
                hls_url2 = obj_instance.first().url2
                return hls_url if hls_url else hls_url2
    except obj.DoesNotExist as ex:
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
