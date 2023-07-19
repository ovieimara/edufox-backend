import abc
import json
from logging import Filter
from multiprocessing import set_forkserver_preload
from re import sub
from venv import create
from rest_framework import filters
import copy
import os
from django.shortcuts import render
from rest_framework import generics, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly, AllowAny
from course.abc import CreateMultipleLessons
from edufox.constants import ANDROID, IOS, WEB

from edufox.views import printOutLogs, update_user_data
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
from rest_framework.decorators import api_view, permission_classes
from django.views import View
from client.library import StorageRepoABC, GoogleCloudStorageRepo, DashStream, HLSStream, PlatformStream
from django.conf import settings as django_settings
from edufox.constants import platforms
from abc import ABC, abstractmethod

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
    queryset = Subject.objects.all()
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

    def create(self, request, *args, **kwargs):
        multiple_lessons = CreateMultipleLessons()
        # print('data: ', json.dumps(request.POST))
        lessons = multiple_lessons.split_titles_ids(request.data)
        serializer = self.get_serializer(
            data=lessons, many=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

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

    def get(self, request, *args, **kwargs):
        student = None
        serialized_recent = []
        serialized_subjects = []
        serialized_recommend = []
        topics_lessons = []
        result = []
        subscriptions = []

        subject = kwargs.get('subject')
        grade = kwargs.get('grade')
        if grade is not None:
            grade = int(grade)
        user = request.user if request.user else None

        try:

            if user and user.is_authenticated:
                subscriptions = user.subscriptions_user.filter(
                    Q(payment_method__expires_date__gt=timezone.now())
                ).order_by("-created")
                # print("subscriptions1: ", subscriptions)

                student = Student.objects.get(phone_number=user.username)

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
                    print('subject object error: ', ex)
                # print("subject_instance: ", subject_instance)
                if subject_instance:
                    topics_queryset = subject_instance.subject_topics.all()
                    # print("topics_queryset: ", topics_queryset)
                    if grade:
                        topics_queryset = topics_queryset.filter(
                            grade__pk__in=[grade])

                if topics_queryset:
                    # lessons_queryset = None
                    for topic in topics_queryset.all():
                        lessons_queryset = topic.topic_lessons.all()
                        if grade:
                            lessons_queryset = lessons_queryset.filter(
                                grade__pk=grade)
                        serialized_lessons = self.get_serializer(
                            lessons_queryset, many=True).data
                        serialized_topic = TopicSerializer(topic).data
                        obj = {"title": serialized_topic,
                               "data": serialized_lessons}
                        topics_lessons.append(obj)
                result = topics_lessons
                # print("result: ", result)
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

                user_interactions = user.interactions.all()

                recent_queryset = user_interactions.select_related(
                    'video').exclude(video__isnull=True).order_by('-created')
                # recent_queryset = recent_queryset.filter(
                #     user=user).distinct('id')
                query_array = []
                existing_set = set()

                for recent in recent_queryset:
                    video_pk = recent.video.pk
                    if video_pk not in existing_set:
                        existing_set.add(video_pk)
                        query_array.append(recent.video.lesson)

                top_3_queryset = query_array[:3]

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
            lesson_array = []
            existing_set = set()
            for video in recommend_queryset:
                if video.pk not in existing_set and video.lesson:
                    existing_set.add(video.pk)
                    lesson_array.append(video.lesson)

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

    # def post(self, request, *args, **kwargs):
    #     if not kwargs.get('pk'):
    #         return self.create(request, *args, **kwargs)
    #     return Response(status.HTTP_400_BAD_REQUEST)

    # def put(self, request, *args, **kwargs):
    #     if kwargs.get('pk'):
    #         return self.update(request, *args, **kwargs)
    #     return Response(status.HTTP_400_BAD_REQUEST)


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
        # print("user: ", user.username)
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
                    lesson_obj = Lesson.objects.get(pk=lesson)
                    if lesson_obj:
                        videos_queryset = lesson_obj.lesson_videos.all()
                except Lesson.DoesNotExist as ex:
                    print('lesson object error: ', ex)
                print('videos_queryset1: ', videos_queryset, grade_packs)
                if grade_packs and videos_queryset:
                    queryset = videos_queryset.filter(
                        grade__in=grade_packs.grades)

                print("queryset: ", len(queryset))

                if grade and not queryset:
                    queryset = videos_queryset.filter(grade__pk=grade)

                videos_queryset = queryset
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
                # print('videos_queryset3: ', (serialized_videos))
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
                    print("lesson_obj: ", lessons_queryset)
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
    serializer_class = VideoSerializer
    # filter_backends = [filters.SearchFilter]
    search_fields = ['tags', 'title', 'description', 'lesson__title',
                     'topic__title', 'subject__name', 'subject__description', 'grade__name', 'grade__code', 'grade__description']


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
        factory_stream = readRequest(request)
        if factory_stream:
            stream = factory_stream.getPlatformStream()
            signed_url = stream.getSignedUrl()
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

    subscription = MySubscription(request.user, video_id)
    print(subscription.isValidSubForVideo())
    # if subscription and not subscription.isValidSubForVideo():
    #     return ''

    path = f"lessons-videos/{subject_code}/{video_id}"
    # print('PATH: ', path)
    factory = {IOS: HLSStream(path), ANDROID: HLSStream(
        path), WEB: HLSStream(path)}

    return factory.get(platform) if platform and platform in factory else factory.get(IOS)


def get_first_obj(**kwargs):
    subject_code = ''
    subject_obj = Subject.objects.all().filter(**kwargs)
    if subject_obj.exists():
        subject_code = subject_obj.first().code
    return subject_code


def getValidSubscriptions(user):
    subscription = MySubscription(user)
    return subscription.get_all_user_subscriptions()
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


class UserSubscriptionABC(ABC):
    def __init__(self, user: str, video_id: str = '') -> None:
        self.user = user
        self.video_id = video_id

    @abstractmethod
    def get_user_subscriptions(self):
        """ fetch subscriptions that are valid after timezone.now"""

    @abstractmethod
    def isValidSubForVideo(self) -> bool:
        """check if subscription is valid for a video"""

    @abstractmethod
    def get_all_user_subscriptions(self):
        """return all subscriptions for this user"""


class MySubscription(UserSubscriptionABC):

    def get_user_subscriptions(self):
        return self.user.subscriptions_user.filter(Q(payment_method__expires_date__gt=timezone.now())).order_by("-created")

    def get_all_user_subscriptions(self):
        # print('subscriptions: ', self.user.subscriptions_user)
        queryset = Subscribe.objects.all()
        return queryset.filter(payment_method__expires_date__gt=timezone.now(), user=self.user).order_by("-created") if self.user.is_authenticated else []

    def get_video_grades(self) -> list:
        video_grades = {}
        try:
            video_queryset = Video.objects.filter(video_id=self.video_id)
            if video_queryset.exists():
                video_obj = video_queryset.first()
                grades = video_obj.grade.all()
                video_grades = {grade.pk for grade in grades}
        except Exception as ex:
            print('video object error: ', ex)

        return video_grades

    def isValidSubForVideo(self) -> bool:
        subscriptions = self.get_all_user_subscriptions()
        if subscriptions:
            video_grades = self.get_video_grades()
            for sub in subscriptions.all():
                subscription_grades = set(sub.grade.grades)
                grades_intersection = subscription_grades & video_grades
                print(grades_intersection, subscription_grades, video_grades)

                if grades_intersection:
                    return True
        return False

        # subscriptions = subscriptions.objects.filter(
        #     grade__grades__contains=values)
        # print("subscriptions: ", subscriptions.all(),
        #       self.get_video_grades(), type(self.get_video_grades()))

        # if subscriptions.exists():
        # subscription_obj = subscriptions.filter(
        #     # Q(grade__grades__contains=self.get_video_grades()) &
        #     Q(
        #         payment_method__expires_date__gt=timezone.now())
        # )
        # print("subscriptions2: ", subscription_obj)
        # if subscription_obj.exists():
        # return True
