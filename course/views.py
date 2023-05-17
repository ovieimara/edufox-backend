import copy
from django.shortcuts import render
from rest_framework import generics, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly, AllowAny
from .models import (Grade, Lesson, Subject, Lecturer, Video,
                     Rate, Comment, Interaction, Resolution, Topic)
# from assess.models import  Test, Assessment
from .serializers import (GradeSerializer, SubjectSerializer, LecturerSerializer, VideoSerializer, RateSerializer, CommentSerializer,
                          InteractionSerializer, ResolutionSerializer, LessonSerializer, TopicSerializer)
from .permissions import IsStaffEditorPermission
from django.core.paginator import Paginator, EmptyPage
from django.contrib.auth.models import User
from student.models import Student


# Create your views here.
class ListCreateAPIGrades(generics.ListCreateAPIView):
    queryset = Grade.objects.all().order_by('name')
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
    queryset = Video.objects.select_related('subject').all().order_by('pk')
    serializer_class = VideoSerializer
    filterset_fields = ['grade', 'subject', 'topic', 'lesson']
    ordering_fields = ['title', 'topic']
    search_fields = ['title', 'descriptions', 'topic', 'lesson', 'tags',
                     'subject__name', 'subject__description', 'grade__name', 'grade__description']
    # permission_classes = [AllowAny]

    def perform_create(self, serializer):
        # print('USER: ', self.request.user, self.request.user.is_staff)
        if self.request.user.is_staff:
            return super().perform_create(serializer)
        return status.HTTP_403_FORBIDDEN


class UpdateAPIVideo(generics.RetrieveUpdateDestroyAPIView):
    queryset = Video.objects.select_related('subject').all()
    serializer_class = VideoSerializer
    permission_classes = [IsAdminUser, IsStaffEditorPermission]


class ListCreateAPIRate(generics.ListCreateAPIView):
    queryset = Rate.objects.select_related('video').all()
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

# class ListCreateAPIInteractionType(generics.ListCreateAPIView):
#     queryset = InteractionType.objects.all()
#     serializer_class = InteractionTypeSerializer

# class UpdateAPIInteractionType(generics.RetrieveUpdateDestroyAPIView):
#     queryset = InteractionType.objects.all()
#     serializer_class = InteractionTypeSerializer
#     permission_classes = [IsAdminUser, IsStaffEditorPermission]


class ListCreateAPIInteraction(generics.ListCreateAPIView):
    queryset = Interaction.objects.select_related(
        'user', 'video', 'type').all()
    serializer_class = InteractionSerializer


class UpdateAPIInteraction(generics.RetrieveUpdateDestroyAPIView):
    queryset = Interaction.objects.select_related(
        'user', 'video', 'type').all()
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


class ListCreateUpdateAPILesson(mixins.CreateModelMixin, mixins.ListModelMixin,  mixins.RetrieveModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView):
    queryset = Lesson.objects.all().order_by('pk')
    serializer_class = LessonSerializer
    lookup_field = 'pk'
    # permission_classes = [IsStaffEditorPermission]

    def get(self, request, *args, **kwargs):
        if kwargs.get('pk') is not None:
            return self.retrieve(request, *args, **kwargs)

        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not kwargs.get('pk') and request.user.is_staff:

            #     data = copy.deepcopy(request.data)
            #     topic = Topic.objects.all().first()
            #     # data['topic'] = "Use of Language"
            #     # print(data)
            #     serializer = self.get_serializer(data=data, partial=True)
            #     serializer.is_valid(raise_exception=True)
            #     self.perform_create(serializer)

            #     return Response(serializer.data, status=status.HTTP_201_CREATED)

            return self.create(request, *args, **kwargs)

        return Response(status.HTTP_403_FORBIDDEN)

    def put(self, request, *args, **kwargs):
        if kwargs.get('pk') and request.user.is_staff:
            return self.update(request, *args, **kwargs)
        return Response(status.HTTP_403_FORBIDDEN)


class ListCreateUpdateAPITopic(mixins.CreateModelMixin, mixins.ListModelMixin,  mixins.RetrieveModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView):
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
        return None
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
    queryset = Subject.objects.all().order_by('name')
    serializer_class = SubjectSerializer
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

        subject = kwargs.get('subject')
        grade = kwargs.get('grade')

        user = request.user if request.user else None
        try:
            if user and not user.is_anonymous:
                student = Student.objects.get(phone_number=user.username)

                if student and not grade:
                    grade = Grade.objects.get(name=student.grade)
                    grade = grade.pk

            if subject and grade:
                topics_queryset = None
                subject_instance = Subject.objects.get(pk=subject)
                if subject_instance:
                    topics_queryset = subject_instance.subject_topics.all().filter(grade__pk=grade)

                if topics_queryset:
                    for topic in topics_queryset.all():
                        lessons_queryset = topic.topic_lessons.all().filter(grade__pk=grade)
                        serialized_lessons = LessonSerializer(
                            lessons_queryset, many=True).data
                        serialized_topic = TopicSerializer(topic).data
                        obj = {"title": serialized_topic,
                               "data": serialized_lessons}
                        topics_lessons.append(obj)
                result = topics_lessons

                return Response(result)

        except Subject.DoesNotExist as ex:
            print('subject object error: ', ex)
        except Exception as ex:
            print("dashboard Error: ", ex)

        try:
            if user:
                user_interactions = user.interactions

                recent_queryset = user_interactions.all().select_related(
                    'video').order_by('-created')[:3]
                serialized_recent = InteractionSerializer(
                    recent_queryset, many=True).data

        except Exception as ex:
            print("Recent Error: ", ex)

        try:
            subjects_queryset = self.get_queryset()
            serialized_subjects = self.serializer_class(
                subjects_queryset, many=True).data

        except Exception as ex:
            print("Subjects Error: ", ex)

        try:
            recommend_queryset = []
            if grade:

                # print('STUDENT: ', grade.pk)
                recommend_queryset = Video.objects.select_related(
                    'subject').filter(tags__icontains='recommend', grade__pk=grade)
            else:
                recommend_queryset = Video.objects.select_related(
                    'subject').filter(tags__icontains='recommend')

            serialized_recommend = VideoSerializer(
                recommend_queryset, many=True).data

        except Exception as ex:
            print("Recommend Objects Error: ", ex)

        result = [
            {
                "title": 'Recent',
                "data": serialized_recent if serialized_recent else serialized_recommend
            },
            {
                "title": 'Subjects',
                "data": serialized_subjects,
                "columns": 2,

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


class ListDashboardLessonsAPI(mixins.CreateModelMixin, mixins.ListModelMixin,  mixins.RetrieveModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView):
    queryset = Lesson.objects.all().order_by('num')
    serializer_class = LessonSerializer
    # lookup_field = 'pk'

    def get(self, request, *args, **kwargs):
        student = None
        result = []

        topic = kwargs.get('pk')
        grade = kwargs.get('grade')
        lesson = kwargs.get('lesson')

        user = request.user if request.user else None
        try:
            if user and not user.is_anonymous:
                student = Student.objects.get(phone_number=user.username)

                if student and not grade:
                    grade = Grade.objects.get(name=student.grade)
                    grade = grade.pk

            if topic and grade:
                topic_obj = Topic.objects.get(pk=topic)
                lessons_queryset = topic_obj.topic_lessons.all().filter(grade__pk=grade)

                serialized_lessons = self.get_serializer(
                    lessons_queryset, many=True).data
                result = [
                    {
                        "title": 'Lessons',
                        "data": serialized_lessons,
                    }
                ]

            if lesson and grade:
                lesson_obj = Lesson.objects.get(pk=lesson)
                videos_queryset = lesson_obj.lesson_videos.all().filter(grade__pk=grade).first()
                # print('videos_queryset: ', videos_queryset)
                serialized_videos = VideoSerializer(videos_queryset).data
                # result = {
                #         "title": 'Lesson',
                #         "data" : serialized_videos,
                #     }
                result = serialized_videos

        except Exception as ex:

            print("Lessons Error: ", ex)

        return Response(result)
